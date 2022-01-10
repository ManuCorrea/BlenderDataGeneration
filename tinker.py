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


def get_random_xyz(x_range=(0, 3), y_range=(-1, 1), z_range=(0, 0)):
    x = random.uniform(x_range[0], x_range[1])
    y = random.uniform(y_range[0], y_range[1])
    z = random.uniform(z_range[0], z_range[1])
    return x, y, z


scene = bpy.data.scenes['Scene']

# TODO if used attribute properly


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


"""
TODO:
* define 3 lines stages
* move images
* make them look to camera
* position them in line
* scaled images

* Scale humans a bit bigger 30 min
* Add background random way 30 min
* Bounding boxes 3h
* Lines testing and stuff 1h
* Add some 3D object

FIXME
* Images that are added with sufix
* Non deleted objects -> sol: delete keys that contains object
"""
dataset_path = "/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/dataset/"
cart_path = dataset_path + "cart"
human_path = dataset_path + "human"
cart_images = get_files_from_path(cart_path)
human_images = get_files_from_path(human_path)

print("################################")
print(cart_path)
print(human_path)

print(cart_images)
print(human_images)
print("################################")

# file = os.path.abspath('/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/dataset/cart/0.png')

# print(f"Correcto files {os.path.basename(file)} dirname {os.path.dirname(file)}")


# bpy.ops.import_image.to_plane(shader='SHADELESS',
#     files=[{'name': os.path.basename(file)}],
#     directory=os.path.dirname(file))


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


def delete_images_planes(names_list):
    for name in names_list:
        print(f"Deleting {name}")
        if name in bpy.data.objects.keys():
            bpy.data.objects[name].select_set(True)
    bpy.ops.object.delete()


for i in range(5):
    sampled_carts = get_list_random_images(cart_images)
    sampled_humans = get_list_random_images(human_images)

    print("!!!!!!!!!!!!!!!!!SAMPLED!!!!!!!!!!!!!!!!!")
    print(sampled_carts)
    print(sampled_humans)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    added_carts_names = add_images_planes(sampled_carts, cart_path)
    added_humans_names = add_images_planes(sampled_humans, human_path)

    render_img_saving_path = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources'
    export_render(scene, 500, 500, 100, 30, render_img_saving_path, f'{i}.png')

    print("!!!!!!!!!!!!!!!!!ADDED!!!!!!!!!!!!!!!!!")
    print(added_carts_names)
    print(added_humans_names)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    delete_images_planes(added_carts_names)
    delete_images_planes(added_humans_names)

"""
For delecting objects you select the object and then call bpy.ops.object.delete()
Ej:
bpy.data.objects['1.001'].select_set(True)
bpy.ops.object.delete()

To get size of an image
bpy.data.images['1.png'].size

Data for camera
Location 3 0 0
Rotation 90 0 90

Data for images
Location X (to camera) Y (sides) Z 0+-?
Rotation 90 0 180

"""
