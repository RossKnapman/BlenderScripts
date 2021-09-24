################################################
# Draw skyrmion textures within a vector field #
################################################

import bpy
import numpy as np
import matplotlib.cm

# Get the colour map from matplotlib
cmap = matplotlib.cm.get_cmap('RdBu_r')
norm = matplotlib.colors.Normalize(vmin=-1, vmax=1)

# Remove all previous objects and materials from scene when we regenerate the arrows
for obj in bpy.data.objects:
    if obj.name != 'Camera' and obj.name != 'Area':  # Don't delete the camera or light
        bpy.data.objects.remove(obj)
        
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

# Dimensions of grid
Lx = 40
Ly = 20

# Number of grid points in x and y
noPointsX = Lx+1 if Lx % 2 == 0 else Lx  # Want to be odd number so that there is a central spin
noPointsY = Ly+1 if Ly % 2 == 0 else Ly

X = np.linspace(-Lx, Lx, noPointsX, dtype=np.float64)
Y = np.linspace(-Ly, Ly, noPointsY, dtype=np.float64)

# Array to store magnetization vectors
mArray = np.zeros((len(X), len(Y), 3), dtype=np.float64)


class Skyrmion:
    
    def __init__(self, centreX, centreY, w=5, R=10, m = 1, eta=np.pi/2):
        self.centreX = centreX  # Central spin coordinate
        self.centreY = centreY
        self.w = w  # Skyrmion domain wall width
        self.R = R  # Skyrmion radius
        self.m = m  # Vorticity
        self.eta = eta  # Helicity (e.g. pi/2 for Bloch-type, 0 for Néel-type, -pi/2 for Bloch type, reversed chirality)
    
    def getDistance(self, x, y):
        """ Get the distance between the input point and the skyrmion's centre """
        return np.sqrt((x - self.centreX)**2 + (y - self.centreY)**2)
    
    def Theta(self, x, y):
        """ Spin angle to z-axis """
        X = x - self.centreX
        Y = y - self.centreY
        rho = np.sqrt(X**2 + Y**2)
        return 2 * np.arctan2(np.sinh(self.R/self.w), np.sinh(rho/self.w))
    
    def Phi(self, x, y):
        """ Spin angle in xy-plane """
        X = x - self.centreX
        Y = y - self.centreY
        phi = np.arctan2(Y, X)
        return self.m * phi + self.eta
    

# Create a list of skyrmions at given coordinates
skyrmions = []
skyrmions.append(Skyrmion(-20, 0))
skyrmions.append(Skyrmion(20, 0, eta=-np.pi/2))


for i in range(len(X)):
    print(i, end='\r')
    for j in range(len(Y)):
        
        x = X[i]
        y = Y[j]
        
        # Work out which skyrmion in skyrmions list is closest to this point
        distances = np.array([skyrmion.getDistance(x, y) for skyrmion in skyrmions])
        leastIdx = np.argmin(distances)
        skyrmion = skyrmions[leastIdx]
        
        # Calculate angles using closest skyrmion 
        Phi = skyrmion.Phi(x, y)
        Theta = skyrmion.Theta(x, y)
        
        # Magnetization vector components
        mx = np.cos(Phi) * np.sin(Theta)
        my = np.sin(Phi) * np.sin(Theta)
        mz = np.cos(Theta)
        mArray[i, j] = np.array([mx, my, mz])
        
        # Create cone and cylinder for arrow
        bpy.ops.mesh.primitive_cone_add(vertices=100, location=(x, y, 2))
        theCone = bpy.data.objects.get('Cone')  # We rename the objects so that we can select them, then join them together into one object
        theCone.name = 'NewCone'
        bpy.ops.mesh.primitive_cylinder_add(vertices=100, location=(x, y,  0), radius=0.5)
        theCylinder = bpy.data.objects.get('Cylinder')
        theCylinder.name = 'NewCylinder'
    
        # Select cone and cylinder, and join them together into a single mesh
        bpy.ops.object.select_all(action='DESELECT') # Deselect all objects
        bpy.context.scene.objects['NewCone'].select_set(True)
        bpy.context.scene.objects['NewCylinder'].select_set(True)
        bpy.ops.object.join()
        bpy.context.selected_objects[0].name = str(i) + '_' + str(j)  # Assign unique name to arrow
        
        # Rotate arrow to its given orientation (all arrows start pointing along z)
        bpy.ops.transform.rotate(value=Theta, orient_axis='Y')
        bpy.ops.transform.rotate(value=Phi, orient_axis='Z')
        
        # Obtain RGB values from matplotlib colormap
        r, g, b, alphaValue = cmap(norm(mz))
        
        # Resize the arrow
        bpy.context.active_object.scale = (0.5, 0.5, 0.5)
        
        # Create a new unique material to colour this arrow
        newMat = bpy.data.materials.new(name=f'{i}_{j}')
        newMat.use_nodes = True
        bpy.context.active_object.data.materials.append(newMat)
        bpy.data.materials[f'{i}_{j}'].node_tree.nodes[0].inputs['Base Color'].default_value = [r, g, b, alphaValue]
        bpy.data.materials[f'{i}_{j}'].node_tree.nodes[0].inputs['Alpha'].default_value = alphaValue
