import bpy
import numpy as np

skCol = bpy.data.collections.new("Skyrmion")
bpy.context.scene.collection.children.link(skCol)
sphereCol = bpy.data.collections.new("Sphere")
bpy.context.scene.collection.children.link(sphereCol)

def drawSphere(R, h, m=1, eta=np.pi/2, N=750):

    a = 4 * np.pi * R * R / (N)
    d = np.sqrt(a)
    M_theta = int(np.round(np.pi / d))
    d_theta = np.pi / M_theta
    d_phi = a / d_theta

    for object in bpy.context.scene.collection.children['Sphere'].objects:
        bpy.data.objects.remove(object)

    for i in range(M_theta):

        print(i, M_theta)

        theta = np.pi * (i + 0.5) / M_theta
        M_phi = int(np.round(2 * np.pi * np.sin(theta) / d_phi))

        for j in range(M_phi):

            phi = 2 * np.pi * j / M_phi
            Phi = m * phi + eta
            Theta = theta

            bpy.ops.mesh.primitive_cone_add(location=(R*np.cos(phi)*np.sin(theta), R*np.sin(phi)*np.sin(theta), R + h + R*np.cos(theta)))

            bpy.ops.transform.rotate(value=theta, orient_axis='Y')
            bpy.ops.transform.rotate(value=Phi, orient_axis='Z')

            cone = bpy.context.active_object
            # bpy.ops.collection.objects_remove_all()
            bpy.data.collections['Sphere'].objects.link(cone)

            # Remove from other collections that are not Sphere
            # try:
            #     bpy.data.collections['Collection'].objects.unlink(cone)
            # except RuntimeError:
            #     pass

            try:
                bpy.data.scenes['Scene'].collection.objects.unlink(cone)
            except RuntimeError:
                pass

            bpy.ops.transform.resize(value=(0.1*R, 0.1*R, 0.1*R))
            bpy.ops.object.shade_smooth()

            normalisedTheta = (np.cos(theta) + 1) / 2
            theMaterial = createMaterial("theta" + str(Theta) + "phi" + str(Phi), normalisedTheta)
            bpy.context.active_object.data.materials.append(theMaterial)


def middleSphere(R, h):

    theName = "SphereMaterial"

    mat = bpy.data.materials.new(name=theName)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Shader already has Principled BSDF and MaterialOutput nodes
    psNode = nodes.get('Principled BSDF')
    psNode.inputs['Metallic'].default_value = 0


    # Add ramp node and colours
    rampNode = nodes.new("ShaderNodeValToRGB")
    rampNode.location.x -= 400  # Easier to see in shader editor when they're not stacked on top of each other

    # Add middle colour value
    rampNode.color_ramp.elements.new(position=0.5)
    rampNode.color_ramp.elements[0].color = (0, 0, 1, 1)
    rampNode.color_ramp.elements[1].color = (1, 1, 1, 1)
    rampNode.color_ramp.elements[2].color = (1, 0, 0, 1)

    # Add gradient node and colours
    gradientNode = nodes.new("ShaderNodeTexGradient")
    gradientNode.location.x -= 600

    # Link the nodes together
    links.new(gradientNode.outputs["Fac"], rampNode.inputs["Fac"])
    links.new(rampNode.outputs["Color"], psNode.inputs["Base Color"])

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9*R, enter_editmode=False, align='WORLD', location=(0, 0, h+R), rotation=(0, -np.pi/2, 0))
    bpy.ops.object.shade_smooth()

    bpy.context.active_object.data.materials.append(mat)


def skyrmionFromSphere(R, h, x, y, m=1, eta=np.pi/2):

    # Remove already existing skyrmion cones
    for object in bpy.context.scene.collection.children['Skyrmion'].objects:
        bpy.data.objects.remove(object)

    for i in range(len(x)):
        print(i)

        for j in range(len(y)):

            # X, Y in the plane
            X =  x[i]
            Y = y[j]

            if np.sqrt(X**2 + Y**2) < np.max(x):

                # Spherical polars in the plane
                phi = np.arctan2(Y, X)
                r = np.sqrt(X**2 + Y**2)

                # Angle between corresponding point on sphere and vertical
                alpha = np.arctan(r/(h+2*R))

                theta = np.pi - 2*alpha

                Phi = m * phi + eta
                Theta = theta


                bpy.ops.mesh.primitive_cone_add(location=(X, Y, 0))

                bpy.ops.transform.rotate(value=theta, orient_axis='Y')
                bpy.ops.transform.rotate(value=Phi, orient_axis='Z')

                cone = bpy.context.active_object
                # bpy.ops.collection.objects_remove_all()
                bpy.data.collections['Skyrmion'].objects.link(cone)

                # try:
                #     bpy.data.collections['Collection'].objects.unlink(cone)
                # except RuntimeError:
                    # pass

                try:
                    bpy.data.scenes['Scene'].collection.objects.unlink(cone)
                except RuntimeError:
                    pass


                bpy.ops.transform.resize(value=(0.25*R, 0.25*R, 0.25*R))
                bpy.ops.object.shade_smooth()

                normalisedTheta = (np.cos(theta) + 1) / 2
                theMaterial = createMaterial("theta" + str(Theta) + "phi" + str(Phi), normalisedTheta)
                bpy.context.active_object.data.materials.append(theMaterial)


def createMaterial(theName, theValue):

    mat = bpy.data.materials.new(name=theName)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Shader already has Principled BSDF and MaterialOutput nodes
    psNode = nodes.get('Principled BSDF')
    psNode.inputs['Metallic'].default_value = 0


    # Add ramp node and colours
    rampNode = nodes.new("ShaderNodeValToRGB")
    rampNode.location.x -= 400  # Easier to see in shader editor when they're not stacked on top of each other

    # Add middle colour value
    rampNode.color_ramp.elements.new(position=0.5)
    rampNode.color_ramp.elements[0].color = (0, 0, 1, 1)
    rampNode.color_ramp.elements[1].color = (1, 1, 1, 1)
    rampNode.color_ramp.elements[2].color = (1, 0, 0, 1)

    valueNode = nodes.new("ShaderNodeValue")
    valueNode.location.x -= 600

    # Set value node to our required value depending on e.g. angle
    valueNode.outputs["Value"].default_value = theValue

    # Link the nodes together
    links.new(valueNode.outputs["Value"], rampNode.inputs["Fac"])
    links.new(rampNode.outputs["Color"], psNode.inputs["Base Color"])

    return mat


# Delete the initial cube
bpy.ops.object.select_all(action='DESELECT')

try:
    bpy.data.objects['Cube'].select_set(True)
    bpy.ops.object.delete()
except KeyError:
    pass


R = 3
h = 5
L = 10
numPoints = 25

drawSphere(R, h)
middleSphere(R, h)

x = np.linspace(-L, L, numPoints)
y = np.linspace(-L, L, numPoints)
skyrmionFromSphere(1, 0.5, x, y)

#bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath + "built")
