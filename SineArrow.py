# For drawing a 3D sine arrow
# For some reason, this leaves some extra points not on the sine curve which need to be deleted manually

from bpy import ops, context, data
import numpy as np

x = np.linspace(0, 6.5 * np.pi, 100)
z = np.sin(x)

ops.curve.primitive_bezier_curve_add(enter_editmode=True)
ops.curve.subdivide(number_cuts=len(x))

# Cache a reference to the curve
curve = context.active_object

# Locate the array of bezier points
bez_points = curve.data.splines[0].bezier_points

for i in range(len(x)):
    
    xValue = x[i]
    zValue = z[i]
    
    if x[i] < 6 * np.pi:
    
        bez_points[i].co.x = xValue
        bez_points[i].co.z = zValue
        bez_points[i].co.y = 0
         
        # The handles of the Bezier curves are just small distances away from the points along the tangents
        bez_points[i].handle_left.x = xValue - 0.0001
        bez_points[i].handle_left.z = zValue - 0.0001*np.cos(xValue)
        bez_points[i].handle_left.y = 0
        
        # Solves bug, from https://developer.blender.org/T40978
        bez_points[i].select_left_handle = False
        bez_points[i].select_right_handle = True
        
        bez_points[i].handle_right.x = xValue + 0.0001
        bez_points[i].handle_right.z = zValue + 0.0001*np.cos(xValue)
        bez_points[i].handle_right.y = 0
    
    else:
        
        bez_points[i].co.x = xValue
        bez_points[i].co.z = 0
        bez_points[i].co.y = 0
        
        bez_points[i].handle_left.x = xValue - 0.0001
        bez_points[i].handle_left.z = 0
        bez_points[i].handle_left.y = 0
        
        # Solves bug, from https://developer.blender.org/T40978
        bez_points[i].select_left_handle = False
        bez_points[i].select_right_handle = True
        
        bez_points[i].handle_right.x = xValue + 0.0001
        bez_points[i].handle_right.z = 0
        bez_points[i].handle_right.y = 0
