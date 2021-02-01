import bpy
import numpy as np
import matplotlib.cm

cmap = matplotlib.cm.get_cmap('RdBu_r')
norm = matplotlib.colors.Normalize(vmin=-1, vmax=1)


w = 2
R = 5
L = 20
m = 1
eta = np.pi/2


def clear():
    # Clear objects from previous runs
    for obj in bpy.data.objects:
        if "Cone" in obj.name or "BezierCurve" in obj.name:
            bpy.data.objects.remove(obj)

    # Clear materials from pervious runs
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)


def getXYZ(psi, alpha, chi):
    
    A = np.cos(psi) * np.sin(alpha) * np.cos(chi) + np.sin(psi) * np.sin(alpha) * np.sin(chi)
    B = -np.sin(psi) * np.sin(alpha) * np.cos(chi) + np.cos(psi) * np.sin(alpha) * np.sin(chi)
    
    Phi = np.arctan2(np.cos(alpha), A)
    Theta = np.arccos(B)
    
    phi = (Phi - eta) / m
    
    r = w * np.arcsinh(np.sinh(R/w) / np.tan(Theta/2))
    
    xPrime = r * np.cos(phi)
    z = r * np.sin(phi)
    
    x = (L + xPrime) * np.cos(psi)
    y = (L + xPrime) * np.sin(psi)
    
    return x, y, z


def getMaterial(chi, alpha):
    
    theMaterial = bpy.data.materials.new(name=f'{alpha},{chi}')
    theMaterial.use_nodes = True

    mx = np.sin(alpha) * np.cos(chi)
    r, g, b, alphaValue = cmap(norm(mx))

    theMaterial.node_tree.nodes[0].inputs['Base Color'].default_value = [r, g, b, alphaValue]
    
    return theMaterial


def drawCones(chi, alpha, theMaterial):
    
    psiValues = np.linspace(0, 2*np.pi, 20)
    
    bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True)
    bpy.ops.curve.subdivide(number_cuts=len(psiValues))

    # Cache a reference to the curve.
    curve = bpy.context.active_object

    # Locate the array of bezier points.
    bez_points = curve.data.splines[0].bezier_points
    
    for i in range(len(psiValues)):
        
#        print(i, len(psiValues), end='\r')
        
        psi = psiValues[i]

        x, y, z = getXYZ(psi, alpha, chi)
        
        bpy.ops.mesh.primitive_cone_add(location=(x, y, z))
                        
        theCone = bpy.data.objects.get('Cone')
        theCone.name = f'Cone({psiValues[i]})'
        theCone.data.materials.append(theMaterial)

        bpy.ops.transform.rotate(value=alpha, orient_axis='Y')
        bpy.ops.transform.rotate(value=chi, orient_axis='Z')
    


def drawTube(chi, alpha, theMaterial):
    
    """ The chi is the global azimuthal angles; the alpha is the global angles from the z-axis. """
    
    psiValues = np.linspace(0, 2*np.pi, 100)
    
    bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True)
    
    bpy.ops.curve.subdivide(number_cuts=len(psiValues))

    # Cache a reference to the curve.
    curve = bpy.context.active_object

    # Locate the array of bezier points.
    bez_points = curve.data.splines[0].bezier_points

    for i in range(len(psiValues)):
        
#        print(i, len(psiValues), end='\r')
        
        psi = psiValues[i]

        x, y, z = getXYZ(psi, alpha, chi)
        
        bez_points[i].co.x = x
        bez_points[i].co.y = y
        bez_points[i].co.z = z
        
        xL, yL, zL = getXYZ(psi-0.01, alpha, chi)
        
        bez_points[i].handle_left.x = xL
        bez_points[i].handle_left.y = yL
        bez_points[i].handle_left.z = zL
        
        # Solves bug, from https://developer.blender.org/T40978
        bez_points[i].select_left_handle = False
        bez_points[i].select_right_handle = True
        
        xR, yR, zR = getXYZ(psi+0.01, alpha, chi)
        
        bez_points[i].handle_right.x = xR
        bez_points[i].handle_right.y = yR
        bez_points[i].handle_right.z = zR
                
    bpy.context.object.data.bevel_object = bpy.data.objects["BezierCircle"]
        

if __name__ == "__main__":
    
    clear()
    
    chi = np.pi/2
    alpha = np.pi
    
    theMaterial = getMaterial(chi, alpha)
    drawCones(chi, alpha, theMaterial)
    drawTube(chi, alpha, theMaterial)
    
    chi = 0
    alpha = np.pi / 4
    
    theMaterial = getMaterial(chi, alpha)
    drawCones(chi, alpha, theMaterial)
    drawTube(chi, alpha, theMaterial)