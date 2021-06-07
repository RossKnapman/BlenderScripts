############################################################
# Script to generate skyrmion tube to demonstrate hopfions #
############################################################


import bpy
import numpy as np
import matplotlib.cm


def transform_to_origin(x, y, L):

    """
    For a given skyrmion slice of the doughnut, we would like to transform to the origin, which makes it simpler to create the skyrmion texture.

    We first translate the coordinates to the origin, then rotate them into the x-z plane.

    As z is invariant under this transformation, we don't need to take it as a parameter.

    Args:
        x: Global x-position
        y: Global y-position
        z: Global z-position
        L: Skyrmion tube ("doughnut") radius

    Returns:
        x, y in the transformed system

    """

    # The angle around the "doughnut" when viewed from above, i.e. to the global x-axis
    psi = np.arctan2(y, x)

    # We translate the skyrmion from the ring to the origin (xPrime, yPrime), then rotate it so that the texture lies in the x-z plane (xDoublePrime)
    xPrime = x - L * np.cos(psi)
    yPrime = y - L * np.sin(psi)
    xDoublePrime = xPrime * np.cos(psi) + yPrime * np.sin(psi)

    return xDoublePrime, yPrime


def get_helicity(x, y, eta, hopf_index):
    
    """
    Get the helicity of the spins at a given point in space.
    
    Args:
        x, y: Position in global coordinates
        eta: Helicity at phi = 0
        hopf_index: Self-explanatory
        
    Returns:
        The helicity
        
    """
    
    psi = np.arctan2(y, x)
    
    return eta + hopf_index * psi


L = 20           # Skyrmion tube major radius (of "doughnut hole")
R = 5            # Skyrmion tube minor radius
w = 2            # Skyrmion domain wall width
m = 1            # Vorticity
eta = np.pi / 2  # Helicity at psi = 0
hopf_index = 1


# Set the color map and normalisation
cmap = matplotlib.cm.get_cmap('hsv')
norm = matplotlib.colors.Normalize(vmin=-np.pi, vmax=np.pi)

# Clear objects from previous runs
for obj in bpy.data.objects:
   bpy.data.objects.remove(obj)

# Clear materials from pervious runs
for mat in bpy.data.materials:
   bpy.data.materials.remove(mat)
   

sideLength = 50            # x- and y-extent of the system
height = 10                # z-extent of the system
distanceBetweenPoints = 2  # Distance between cones (higher means fewer cones but faster run)

X = np.linspace(-sideLength, sideLength, int(sideLength / distanceBetweenPoints), dtype=np.float64)
Y = np.linspace(-sideLength, sideLength, int(sideLength / distanceBetweenPoints), dtype=np.float64)
Z = np.linspace(-height, height, int(height / distanceBetweenPoints), dtype=np.float64)

x, y, z = np.meshgrid(X, Y, Z)

# Transform the coordinate system of the skyrmion on the ring to the origin
xTransformed, yTransformed = transform_to_origin(x, y, L)

# Radius from the centre of the skyrmion texture now at the origin
rho = np.sqrt(xTransformed**2 + z**2)

# Polar angle in the skyrmion texture
phi = np.arctan2(z, xTransformed)

# The angle around the "doughnut" when viewed from above, i.e. to the global x-axis
psi = np.arctan2(y, x)

# The helicity of the spins in the skyrmion (will just be eta around the ring if hopf_index = 0)
helicity = get_helicity(x, y, eta, hopf_index)

# Spin angle in x-z plane
Phi = m * phi + helicity

# Spin angle to y-axis
Theta = 2 * np.arctan2(np.sinh(R/w), np.sinh(rho/w))

# The magnetization components in the transformed system
mxRotated = np.cos(Phi) * np.sin(Theta)
myRotated = np.cos(Theta)
mz = np.sin(Phi) * np.sin(Theta)  # (mz is unaffected by the transformation)

# Transform back from the origin to its original position on the "doughnut"
mx = mxRotated * np.cos(psi) - myRotated * np.sin(psi)
my = mxRotated * np.sin(psi) + myRotated * np.cos(psi)

# Like Phi and Theta, but now in global coordinates
chi = np.arctan2(my, mx)
alpha = np.arccos(mz)

# For evaluating the Hopf index at the end as a sanity check
mArray = np.zeros((len(X), len(Y), len(Z), 3), dtype=np.float64)
mArray[:, :, :, 0] = mx
mArray[:, :, :, 1] = my
mArray[:, :, :, 2] = mz


for i in range(len(X)):
    print(i, len(X), end='\r')
    for j in range(len(Y)):
        for k in range(len(Z)):
            
            if rho[i, j, k] < 2*R:  # Get tube, rather than magnetization everywhere
                
                if not (x[i, j, k] > 1 and y[i, j, k] > 1):  # Cut out a quadrant for visibility of the skyrmion texture
                
                    # Create a cone at position x, y, z, which initially points along +z
                    bpy.ops.mesh.primitive_cone_add(vertices=100, location=(x[i, j, k], y[i, j, k], z[i, j, k]))

                    # Name the cone so that we can easily select it
                    theCone = bpy.data.objects.get('Cone')
                    theCone.name = f'Cone({i},{j},{k})'
                    theCone.rotation_mode = 'AXIS_ANGLE'
                    
                    # Create a material with the same name as the cone, and attach it to the cone
                    newMat = bpy.data.materials.new(name=f'Cone({i},{j},{k})')
                    newMat.use_nodes = True
                    theCone.data.materials.append(newMat)                    

                    # Perform the rotation of the cone
                    bpy.ops.transform.rotate(value=alpha[i, j, k], orient_axis='Y')
                    bpy.ops.transform.rotate(value=chi[i, j, k], orient_axis='Z')

                    # Make helicity be between -pi and pi for colouring
                    while helicity[i, j, k] > np.pi:
                        helicity[i, j, k] -= 2 * np.pi
                        
                    while helicity[i, j, k] < -np.pi:
                        helicity[i, j, k] += 2 * np.pi
                    
                    # Get the RGBA value from the matplotlib colour map
                    r, g, b, alphaValue = cmap(norm(helicity[i, j, k]))
                    
                    # Set the colour of the cone
                    bpy.data.materials[f'Cone({i},{j},{k})'].node_tree.nodes[0].inputs['Base Color'].default_value = [r, g, b, alphaValue]
                    bpy.data.materials[f'Cone({i},{j},{k})'].node_tree.nodes[0].inputs['Alpha'].default_value = alphaValue


# Calculate Hopf index as a sanity check (does not work if a segment has been cut out)
mReduced = mArray[:-1, :-1, :-1]
mdx = np.diff(mArray, axis=0)[:, :-1, :-1]
mdy = np.diff(mArray, axis=1)[:-1, :, :-1]
mdz = np.diff(mArray, axis=2)[:-1, :-1, :]

oneLineHopfIdx = -np.sum(np.einsum('ijkl,ijkl->ijk', mReduced, np.einsum('ijk,ijkl->ijkl', np.cumsum(np.einsum('ijkl,ijkl->ijk', mReduced, np.cross(mdx, mdy)), axis=1), np.cross(mdz, mdy)) + np.einsum('ijk,ijkl->ijkl', np.cumsum(np.einsum('ijkl,ijkl->ijk', mReduced, np.cross(mdy, mdz)), axis=1), np.cross(mdx, mdy))))/(4*np.pi)**2

print(oneLineHopfIdx)
