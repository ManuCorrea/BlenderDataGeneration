from numpy.core import numeric
import bpy
import numpy as np
import math as m
import random
import time
import os
import mathutils
import addon_utils

addon_utils.enable("io_import_images_as_planes")

# Have to enable the module for importing images as planes
# https://blender.stackexchange.com/questions/121980/how-to-load-import-a-png-image-as-plane-via-blenders-python-api
# bpy.ops.wm.addon_enable(module='io_import_images_as_planes')

"""
TODO:
* define 3 lines stages
* move images once imported for saving reading disk
* make them look to camera
* position them in line
* scaled images
* add classes to the YOLO file

* Scale humans a bit bigger
    * Scale them around 1.2
* Add +- scaling setting
* Find dimensions or way to make image "stand" on the floor
    * Location of images is the middle point of it. So knowing the dimension/2 and make that move from the floor up
* Add background random way
* Lines testing and stuff
* Add some 3D object
* Move lights around the scene
* Refactor code

TODO design:
* Make general structure to define paths, type of objects/class, properties(eg: scaling), number of objects, +-positions...

FIXME
* Images that are added with sufix
* Non deleted objects -> sol: delete keys that contains object
* When floor is added and no objects are managed in delete_images_planes([]) (with empty list)
  the floor is deleted on delete_images_planes (since the plane must be selected and gets
  deleted by bpy.ops.object.delete())
"""
EPOCHS = 10
dataset_path = "/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/dataset/"
cart_path = dataset_path + "cart"
human_path = dataset_path + "human"
background_path = dataset_path + "bg"

classes = {"cart": 0, "human": 1}


camera = bpy.data.objects['Camera']
axis = bpy.data.objects['Main Axis']
axis.rotation_euler = (0, 0, 0)
axis.location = (0, 0, 0)
camera.location = (0, 6, 0)
camera.rotation_euler = (m.radians(90), 0, m.radians(180))


def get_list_random_images(imgs_list, n_max_objects=5):
    i = random.randrange(n_max_objects + 1)
    objects = list()
    while i > 0:
        objects.append(random.choice(imgs_list))
        i -= 1
    return objects


def get_files_from_path(path):
    (_, _, filenames) = next(os.walk(path))
    return filenames


def get_random_xyz(x_range=(-2, 2), y_range=(0, 2), z_range=(0, 0)):
    x = random.uniform(x_range[0], x_range[1])
    y = random.uniform(y_range[0], y_range[1])
    z = random.uniform(z_range[0], z_range[1])
    return x, y, z


scene = bpy.data.scenes['Scene']


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

    # Take picture of current visible scene
    bpy.ops.render.render(write_still=True)


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



class RenderPreloadingAssets:
    def __init__(self, object_list, path):
        self.objects = add_all_images_unrendered(object_list, path)

    def move_selected_objects(self):
        for name in self.selected_objects:
            bpy.data.objects[name].location = mathutils.Vector(get_random_xyz())

    def hide_render_of_objects(self, object_list, render_object):
        for obj in object_list:
            bpy.data.objects[obj].hide_render = render_object


    def delete_all_images(self):
        for name in self.objects:
            if name in bpy.data.objects.keys():
                bpy.data.objects[name].select_set(True)
        bpy.ops.object.delete()

    def generate_scene(self, idx):
        add_simple_floor(rgba=(random.random(), random.random(),
                               random.random(), 1))
        # over the existing objects pick some
        self.selected_objects = get_list_random_images(self.objects)
        # make them render
        self.hide_render_of_objects(self.selected_objects, False)
        # move them
        self.move_selected_objects()
        # TODO handle camera
        # render
        render_img_saving_path = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/generated'
        export_render(scene, 500, 500, 100, 30, render_img_saving_path, f'{idx}.png')

        # Here we add the bbox
        labels_filepath = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/labels'
        # Output Labels
        text_file_name = labels_filepath + '/' + \
            str(idx) + \
            '.txt'  # Create label file name
        # Open .txt file of the label
        text_file = open(text_file_name, 'w+')
        # Get formatted coordinates of the bounding boxes of all the objects in the scene
        # Display demo information - Label construction

        text_coordinates = get_all_coordinates(self.selected_objects, classes["cart"])

        splitted_coordinates = text_coordinates.split(
            '\n')[:-1]  # Delete last '\n' in coordinates
        # Write the coordinates to the text file and output the render_counter.txt file
        text_file.write('\n'.join(splitted_coordinates))
        text_file.close()  # Close the .txt file corresponding to the label

        # make the picked unrender
        self.hide_render_of_objects(self.selected_objects, True)

        # world config
        delete_existing_floor()


def add_all_images_unrendered(objects_list, path):
    objects_list = add_images_planes(objects_list, path)
    for obj in objects_list:
        bpy.data.objects[obj].hide_render = True
    return objects_list


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

# This may be improved
def delete_images_planes(names_list):
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


def get_all_coordinates(objects, class_type):
    '''
    This function takes no input and outputs the complete string with the coordinates
    of all the objects in view in the current image
    '''
    main_text_coordinates = ''  # Initialize the variable where we'll store the coordinates
    # Loop through all of the objects
    for i, objct in enumerate(objects):
        # print("     On object:", objct)
        # Get current object's coordinates
        b_box = find_img_bounding_box(bpy.data.objects[objct])
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


def find_img_bounding_box(obj):
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


cart_images = get_files_from_path(cart_path)
human_images = get_files_from_path(human_path)

print("################################")
print(f"Cart path: {cart_path}")
print(f"Human path: {human_images}")
print("################################")

# import sys
# sampled_carts = get_list_random_images(cart_images)
# add_all_images_unrendered(cart_images, cart_path)

# for i in range(EPOCHS):
#     add_simple_floor(rgba=(random.random(), random.random(),
#                            random.random(), 1))
#     sampled_carts = get_list_random_images(cart_images)
#     sampled_humans = get_list_random_images(human_images)

#     # print("!!!!!!!!!!!!!!!!!SAMPLED!!!!!!!!!!!!!!!!!")
#     # print(sampled_carts)
#     # print(sampled_humans)
#     # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

#     added_carts_names = add_images_planes(sampled_carts, cart_path)
#     added_humans_names = add_images_planes(sampled_humans, human_path)

#     render_img_saving_path = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/generated'
#     export_render(scene, 500, 500, 100, 30, render_img_saving_path, f'{i}.png')

#     # Here we add the bbox
#     labels_filepath = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/labels'
#     # Output Labels
#     text_file_name = labels_filepath + '/' + \
#         str(i) + \
#         '.txt'  # Create label file name
#     # Open .txt file of the label
#     text_file = open(text_file_name, 'w+')
#     # Get formatted coordinates of the bounding boxes of all the objects in the scene
#     # Display demo information - Label construction
#     print("---> Label Construction")
#     text_coordinates = get_all_coordinates(added_carts_names, classes["cart"])
#     text_coordinates_humans = get_all_coordinates(
#         added_humans_names, classes["human"])

#     text_coordinates = text_coordinates + text_coordinates_humans

#     splitted_coordinates = text_coordinates.split(
#         '\n')[:-1]  # Delete last '\n' in coordinates
#     # Write the coordinates to the text file and output the render_counter.txt file
#     text_file.write('\n'.join(splitted_coordinates))
#     text_file.close()  # Close the .txt file corresponding to the label

#     # print("!!!!!!!!!!!!!!!!!ADDED!!!!!!!!!!!!!!!!!")
#     # print(added_carts_names)
#     # print(added_humans_names)
#     # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

#     delete_images_planes(added_carts_names)
#     delete_images_planes(added_humans_names)
#     delete_existing_floor()


from timeit import Timer

render = RenderPreloadingAssets(cart_images, cart_path)

t = Timer(lambda: render.generate_scene(1))
print(t.timeit(number=20))  # 22.929327520003426
# # for i in range(EPOCHS):
    
    
# render.delete_all_images()


def generate_scene(i):
    add_simple_floor(rgba=(random.random(), random.random(),
                           random.random(), 1))

    print(f" --------- {bpy.data.objects.keys()}")
    sampled_carts = get_list_random_images(cart_images)
    added_carts_names = add_images_planes(sampled_carts, cart_path)

    render_img_saving_path = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/generated'
    export_render(scene, 500, 500, 100, 30, render_img_saving_path, f'{i}.png')

    # Here we add the bbox
    labels_filepath = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/labels'
    # Output Labels
    text_file_name = labels_filepath + '/' + \
        str(i) + \
        '.txt'  # Create label file name
    # Open .txt file of the label
    text_file = open(text_file_name, 'w+')
    # Get formatted coordinates of the bounding boxes of all the objects in the scene
    # Display demo information - Label construction

    text_coordinates = get_all_coordinates(added_carts_names, classes["cart"])

    splitted_coordinates = text_coordinates.split(
        '\n')[:-1]  # Delete last '\n' in coordinates
    # Write the coordinates to the text file and output the render_counter.txt file
    text_file.write('\n'.join(splitted_coordinates))
    text_file.close()  # Close the .txt file corresponding to the label


    print(f"Before delete_image_planes --------- {bpy.data.objects.keys()}")
    print(added_carts_names)
    delete_images_planes(added_carts_names)
    print(f"Before calling --------- {bpy.data.objects.keys()}")
    delete_existing_floor()
    print(f" --------- {bpy.data.objects.keys()}")


# t = Timer(lambda: generate_scene(1))
# print(t.timeit(number=20)) # 22.532155615001102

"""
To get size of an image
bpy.data.images['1.png'].size

Data for images
Location X (to camera) Y (sides) Z 0+-?
Rotation 90 0 180
"""
