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
