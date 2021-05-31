############################################################
# Script to generate skyrmion tube to demonstrate hopfions #
############################################################


import bpy
import numpy as np
import matplotlib.cm

cmap = matplotlib.cm.get_cmap('RdBu_r')
norm = matplotlib.colors.Normalize(vmin=-1, vmax=1)


# Clear objects from previous runs
for obj in bpy.data.objects:
   bpy.data.objects.remove(obj)

# Clear materials from pervious runs
for mat in bpy.data.materials:
   bpy.data.materials.remove(mat)

X = np.linspace(-50, 50, 50, dtype=np.float64)
Y = np.linspace(-50, 50, 50, dtype=np.float64)
Z = np.linspace(-10, 10, 10, dtype=np.float64)

mArray = np.zeros((len(X), len(Y), len(Z), 3), dtype=np.float64)

w = 2
R = 5
L = 20
m = 1
eta = np.pi/2

for i in range(len(X)):
    print(i, len(X), end='\r')
    for j in range(len(Y)):
        for k in range(len(Z)):
            
            x = X[i]
            y = Y[j]
            z = Z[k]
            
            psi = np.arctan2(y, x)
            
            # Translation from the ring to the origin
            xPrime = x - L * np.cos(psi)
            yPrime = y - L * np.sin(psi)
            
            # At origin, rotate around z to get the texture in the x-y plane
            xDoublePrime = xPrime * np.cos(psi) + yPrime * np.sin(psi)
            
            rho = np.sqrt(xDoublePrime**2 + z**2)
            
            if rho < 2*R:
        
                phi = np.arctan2(z, xDoublePrime)
                Phi = m*phi + eta + psi
                Theta = 2 * np.arctan2(np.sinh(R/w), np.sinh(rho/w))
                
                mxRotated = np.cos(Phi) * np.sin(Theta)
                myRotated = np.cos(Theta)
                mz = np.sin(Phi) * np.sin(Theta)
                
                mx = mxRotated * np.cos(psi) - myRotated * np.sin(psi)
                my = mxRotated * np.sin(psi) + myRotated * np.cos(psi)
                
                mArray[i, j, k] = np.array([mx, my, mz])
                
                bpy.ops.mesh.primitive_cone_add(vertices=100, location=(x, y, z))
            
                # We rename the objects so that we can select them, then join them together into one object
                theCone = bpy.data.objects.get('Cone')
                theCone.name = f'Cone({i},{j},{k})'
                theCone.rotation_mode = 'AXIS_ANGLE'
                
                newMat = bpy.data.materials.new(name=f'Cone({i},{j},{k})')
                newMat.use_nodes = True
                theCone.data.materials.append(newMat)
                
                chi = np.arctan2(my, mx)
                alpha = np.arccos(mz)
            
                bpy.ops.transform.rotate(value=alpha, orient_axis='Y')
                bpy.ops.transform.rotate(value=chi, orient_axis='Z')

                r, g, b, alphaValue = cmap(norm(mx))
                
                if x > 0:
                    alphaValue = 0.05
                
                bpy.data.materials[f'Cone({i},{j},{k})'].node_tree.nodes[0].inputs['Base Color'].default_value = [r, g, b, alphaValue]
                bpy.data.materials[f'Cone({i},{j},{k})'].node_tree.nodes[0].inputs['Alpha'].default_value = alphaValue


bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)


# Calculate Hopf index as a sanity check
mReduced = mArray[:-1, :-1, :-1]
mdx = np.diff(mArray, axis=0)[:, :-1, :-1]
mdy = np.diff(mArray, axis=1)[:-1, :, :-1]
mdz = np.diff(mArray, axis=2)[:-1, :-1, :]

oneLineHopfIdx = -np.sum(np.einsum('ijkl,ijkl->ijk', mReduced, np.einsum('ijk,ijkl->ijkl', np.cumsum(np.einsum('ijkl,ijkl->ijk', mReduced, np.cross(mdx, mdy)), axis=1), np.cross(mdz, mdy)) + np.einsum('ijk,ijkl->ijkl', np.cumsum(np.einsum('ijkl,ijkl->ijk', mReduced, np.cross(mdy, mdz)), axis=1), np.cross(mdx, mdy))))/(4*np.pi)**2

print(oneLineHopfIdx)
