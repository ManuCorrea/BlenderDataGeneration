import bpy
import mathutils
import random
import os
import sys
import numpy as np
import math as m

# TODO add option to choose exact number
def get_list_random_images(imgs_list, n_max_objects=5, n_exact_number=None):
    objects = list()
    if n_exact_number is None:
        i = random.randrange(n_max_objects + 1)
        while i > 0:
            objects.append(random.choice(imgs_list))
            i -= 1
    else:
        for i in range(n_exact_number):
            objects.append(random.choice(imgs_list))
    return objects


def get_files_from_path(path):
    (_, _, filenames) = next(os.walk(path))
    return filenames


def get_directories_from_path(path):
    (_, directories, _) = next(os.walk(path))
    return directories


def get_random_xyz(x_range=(-2, 2), y_range=(0, 2), z_range=(0, 0)):
    """Returns random XYZ in ranges given

    Args:
        x_range (tuple, optional): -+ range. Defaults to (-2, 2).
        y_range (tuple, optional): -+ range. Defaults to (0, 2).
        z_range (tuple, optional): -+ range. Defaults to (0, 0).

    Returns:
        XYZ tuple: XYZ random components
    """
    x = random.uniform(x_range[0], x_range[1])
    y = random.uniform(y_range[0], y_range[1])
    z = random.uniform(z_range[0], z_range[1])
    return x, y, z


def get_random_xyz_rotation(x_range=(-1, 1), y_range=(-1, 1), z_range=(-1, 1), degrees=True):
    """Returns random XYZ in ranges given

    Args:
        x_range (tuple, optional): -+ range. Defaults to (-2, 2).
        y_range (tuple, optional): -+ range. Defaults to (0, 2).
        z_range (tuple, optional): -+ range. Defaults to (0, 0).
        degrees (bool, optional): if the given range is in degrees
    
    Returns:
        XYZ tuple: XYZ random compoents in radians
    """
    if degrees:
        x = random.uniform(m.radians(x_range[0]), m.radians(x_range[1]))
        y = random.uniform(m.radians(y_range[0]), m.radians(y_range[1]))
        z = random.uniform(m.radians(z_range[0]), m.radians(z_range[1]))
    else:
        x = random.uniform(x_range[0], x_range[1])
        y = random.uniform(y_range[0], y_range[1])
        z = random.uniform(z_range[0], z_range[1])
    return x, y, z


"""
################## Media ########################
"""


def add_images_planes(objects_list, path):
    added = []
    for object_to_add in objects_list:

        name = os.path.basename(object_to_add)

        a = bpy.ops.import_image.to_plane(shader='SHADELESS',
                                          files=[{'name': name}],
                                          directory=path)
        print(f"Intentando añadir {object_to_add} {a}")
        name = os.path.splitext(name)[0]
        added.append(name)
        bpy.data.objects[name].location = mathutils.Vector(get_random_xyz())
    return added


def add_all_images_unrendered(objects_list, path):
    objects_list = add_images_planes(objects_list, path)
    for obj in objects_list:
        bpy.data.objects[obj].hide_render = True
    return objects_list

# This may be improved


def delete_images_planes(names_list):
    if len(names_list) == 0:
        return
    repeated = False

    if len(names_list) != len(set(names_list)):
        repeated = True
    for name in names_list:
        print(f"Selecting {name} in {bpy.data.objects.keys()}")
        if name in bpy.data.objects.keys():
            bpy.data.objects[name].select_set(True)
        if repeated:
            for key in bpy.data.objects.keys():
                if key.startswith(name):
                    bpy.data.objects[key].select_set(True)
            print(
                f"\n\n\n!!!!Pues eso repetido {name} hay {names_list.count(name)}\n\n\n")
    bpy.ops.object.delete()


"""
################## Floor & Background ########################
"""


def add_simple_floor(size=50, location=(0, 0, -0.5), rgba=(0, 0, 0, 1)):
    print("Adding floor")
    # This adds a plane
    bpy.ops.mesh.primitive_plane_add(
        size=size, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))

    # material = bpy.data.materials["Material"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (
    #     0.8, 0.269606, 0, 1)

    # https://blender.stackexchange.com/questions/56751/add-material-and-apply-diffuse-color-via-python
    mat = bpy.data.materials.new(name="MaterialName")
    bpy.data.objects['Plane'].data.materials.append(
        mat)  # add the material to the object
    bpy.context.object.active_material.diffuse_color = rgba  # change color


def delete_existing_floor():
    bpy.data.objects["Plane"].select_set(True)
    bpy.ops.object.delete()


# def add_background(object_to_add, path):
#     name = os.path.basename(object_to_add)

#     bpy.ops.import_image.to_plane(files=[{"name": name}], directory=path,
#                                   align_axis='CAM', prev_align_axis='CAM_AX',
#                                   size_mode='CAMERA', fill_mode='FILL', shader='SHADELESS')


# def delete_existing_background():
#     pass

"""
################## Bounding Boxes ########################
"""


def get_all_coordinates(objects, class_type, scene):
    '''
    This function takes no input and outputs the complete string with the coordinates
    of all the objects in view in the current image
    '''
    main_text_coordinates = ''  # Initialize the variable where we'll store the coordinates
    # Loop through all of the objects
    for i, objct in enumerate(objects):
        # print("     On object:", objct)
        # Get current object's coordinates
        b_box = find_img_bounding_box(bpy.data.objects[objct], scene)
        if b_box:  # If find_bounding_box() doesn't return None
            # print("         Initial coordinates:", b_box)
            text_coordinates = format_coordinates(
                b_box, class_type)  # Reformat coordinates to YOLOv3 format
            # print("         YOLO-friendly coordinates:", text_coordinates)
            # Update main_text_coordinates variables whith each
            main_text_coordinates = main_text_coordinates + text_coordinates
            # line corresponding to each class in the frame of the current image
        else:
            # print("         Object not visible")
            pass
    return main_text_coordinates


def format_coordinates(coordinates, classe):
    '''
    This function takes as inputs the coordinates created by the find_bounding box() function, the current class,
    the image width and the image height and outputs the coordinates of the bounding box of the current class
    '''
    # If the current class is in view of the camera
    if coordinates:
        # Change coordinates reference frame
        x1 = (coordinates[0][0])
        x2 = (coordinates[1][0])
        y1 = (1 - coordinates[1][1])
        y2 = (1 - coordinates[0][1])

        # Get final bounding box information
        width = (x2-x1)  # Calculate the absolute width of the bounding box
        # Calculate the absolute height of the bounding box
        height = (y2-y1)
        # Calculate the absolute center of the bounding box
        cx = x1 + (width/2)
        cy = y1 + (height/2)

        # Formulate line corresponding to the bounding box of one class
        txt_coordinates = f"{classe} {cx} {cy} {width} {height} \n"
        return txt_coordinates
    # If the current class isn't in view of the camera, then pass
    else:
        pass


def find_img_bounding_box(obj, scene):
    camera = bpy.data.objects['Camera']
    """ Get the inverse transformation matrix. """
    matrix = camera.matrix_world.normalized().inverted()
    """ Create a new mesh data block, using the inverse transform matrix to undo any transformations. """
    mesh = obj.to_mesh(preserve_all_data_layers=True)
    mesh.transform(obj.matrix_world)
    mesh.transform(matrix)

    """ Get the world coordinates for the camera frame bounding box, before any transformations. """
    # view_frame() Return 4 points for the cameras frame (before object transformation)
    frame = [-v for v in camera.data.view_frame(scene=scene)[:3]]

    lx = []
    ly = []

    for v in mesh.vertices:
        # returns a vector
        # https://blender.stackexchange.com/questions/1311/how-can-i-get-vertex-positions-from-a-mesh
        # for each vertex it gets its local x/y/z coordinate
        co_local = v.co
        z = -co_local.z

        if z <= 0.0:
            """ Vertex is behind the camera; ignore it. """
            continue
        else:
            """ Perspective division """
            frame = [(v / (v.z / z)) for v in frame]

        # take the points of the frame
        min_x, max_x = frame[1].x, frame[2].x
        min_y, max_y = frame[0].y, frame[1].y

        x = (co_local.x - min_x) / (max_x - min_x)
        y = (co_local.y - min_y) / (max_y - min_y)

        lx.append(x)
        ly.append(y)

    """ Image is not in view if all the mesh verts were ignored """
    if not lx or not ly:
        return None

    min_x = np.clip(min(lx), 0.0, 1.0)
    min_y = np.clip(min(ly), 0.0, 1.0)
    max_x = np.clip(max(lx), 0.0, 1.0)
    max_y = np.clip(max(ly), 0.0, 1.0)

    """ Image is not in view if both bounding points exist on the same side """
    if min_x == max_x or min_y == max_y:
        return None

    """ Figure out the rendered image size """
    render = scene.render
    fac = render.resolution_percentage * 0.01
    dim_x = render.resolution_x * fac
    dim_y = render.resolution_y * fac

    # Verify there's no coordinates equal to zero
    coord_list = [min_x, min_y, max_x, max_y]
    if min(coord_list) == 0.0:
        indexmin = coord_list.index(min(coord_list))
        coord_list[indexmin] = coord_list[indexmin] + 0.0000001

    return (min_x, min_y), (max_x, max_y)


"""
################## Rendering ########################
"""


def render_blender(self, count_f_name):
    # Define random parameters
    random.seed(random.randint(1, 1000))
    self.xpix = random.randint(500, 1000)
    self.ypix = random.randint(500, 1000)
    self.percentage = random.randint(90, 100)
    self.samples = random.randint(25, 50)
    # Render images
    image_name = str(count_f_name) + '.png'
    self.export_render(self.xpix, self.ypix, self.percentage,
                       self.samples, self.images_filepath, image_name)


def export_render(scene, res_x, res_y, res_per, samples, file_path, file_name):
    # Set all scene parameters
    bpy.context.scene.cycles.samples = samples
    scene.render.resolution_y = res_y
    scene.render.resolution_x = res_x
    scene.render.resolution_percentage = res_per
    scene.render.filepath = file_path + '/' + file_name

    # TODO handle options for masks
    # scene.view_layers["View Layer"].use_pass_object_index = True

    # Take picture of current visible scene
    bpy.ops.render.render(write_still=True)


"""
################## Misc ########################
"""

