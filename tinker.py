import bpy
import numpy as np
import math as m
import random
import time
import os
import sys
import importlib
import mathutils
import addon_utils

def add_path_for_modules():
    dir = os.path.dirname(bpy.data.filepath)
    print(f"Adding {dir}")
    if not dir in sys.path:
        sys.path.append(dir)


add_path_for_modules()
import utils
import generation
from utils import *
from generation import Render, RenderPreloadingAssets

importlib.reload(utils)
importlib.reload(generation)

addon_utils.enable("io_import_images_as_planes")

# Have to enable the module for importing images as planes
# https://blender.stackexchange.com/questions/121980/how-to-load-import-a-png-image-as-plane-via-blenders-python-api
# bpy.ops.wm.addon_enable(module='io_import_images_as_planes')

# FIXME When floor is added and no objects are managed in delete_images_planes([])
# (with empty list)the floor is deleted on delete_images_planes(since the plane must
# be selected and gets deleted by bpy.ops.object.delete())
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


cart_images = get_files_from_path(cart_path)
print(cart_images)
human_images = get_files_from_path(human_path)

labels_filepath = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/labels'
render_img_saving_path = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/generated'

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

# render = RenderPreloadingAssets(
#     cart_images, cart_path, render_img_saving_path, classes)

# t = Timer(lambda: render.generate_scene(1))
# # print(t.timeit(number=20))  # 22.929327520003426
# print(t.timeit(number=5))
# # for i in range(EPOCHS):
       
# render.delete_all_images()

render = Render(cart_images, cart_path, render_img_saving_path, classes)
t = Timer(lambda: render.generate_scene(1))
# print(t.timeit(number=20)) # 22.532155615001102
print(t.timeit(number=5))

"""
To get size of an image
bpy.data.images['1.png'].size

Data for images
Location X (to camera) Y (sides) Z 0+-?
Rotation 90 0 180
"""
