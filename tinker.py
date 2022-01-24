import bpy
import numpy as np
import math as m
import random
import time
import os
import sys
import importlib
import addon_utils

def add_path_for_modules():
    dir = os.path.dirname(bpy.data.filepath)
    print(f"Adding {dir}")
    if not dir in sys.path:
        sys.path.append(dir)


def super_market_lights():
    for x in range(0, 4, 2):
        for y in np.arange(0, 5, 1.5):
            light.Light(type='SPOT', location=(x, y, 2))


add_path_for_modules()
import utils
import generation
from utils import *
from generation import Render, RenderPreloadingAssets
import camera
import light

importlib.reload(utils)
importlib.reload(generation)
importlib.reload(camera)
importlib.reload(light)

addon_utils.enable("io_import_images_as_planes")

# Have to enable the module for importing images as planes
# https://blender.stackexchange.com/questions/121980/how-to-load-import-a-png-image-as-plane-via-blenders-python-api
# bpy.ops.wm.addon_enable(module='io_import_images_as_planes')

EPOCHS = 5
dataset_path = "/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/dataset/"
cart_path = dataset_path + "cart"
human_path = dataset_path + "human"
background_path = dataset_path + "bg"

classes = {"cart": 0, "human": 1}

axis = bpy.data.objects['Main Axis']
axis.rotation_euler = (0, 0, 0)
axis.location = (0, 0, 0)


camera = camera.Camera(location=(0, 6, 0.3), location_range=((-0.5,0.5), (4, 6), (0.3, 0.8)), rotation=(90, 0, 180))

render_img_saving_path = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/generated'

floor = generation.Floor(random=True, size=30, location=(0, 0, 0))
# floor.add_simple_floor()

# light = light.Light(type='SPOT', location=(1,1,2), location_range=((-4, 4), (-4, 4), (1.2, 3)))
# light.randomize_location()

super_market_lights()

# from timeit import Timer

wanted_objects = ["cart", "human"]
# wanted_objects = ["cart_simple"]

# render = generation.RenderPreloadingAssets(
#     dataset_path, render_img_saving_path, camera=camera, wanted_objects=wanted_objects)

background = generation.Background(dataset_path, wanted_classes=["bg"],
                                   location=(0, 0, 0.5), rotation=(m.radians(90), 0, m.radians(180)),
                                   scale=5)

# # t = Timer(lambda: render.generate_scene(1))
# # # print(t.timeit(number=20))  # 22.929327520003426
# # print(t.timeit(number=5))
# for i in range(EPOCHS):
#     # floor.add_simple_floor()
#     background.add_img_background()
#     render.generate_scene(i)
#     camera.randomize_location()
#     camera.randomize_rotation()
#     # floor.delete_existing_floor()
#     background.remove_img_background()
# render.delete_all_images()
# camera.delete_camera()

######################

# background.add_img_background()
# floor.add_simple_floor()
# background.remove_img_background()

render = Render(dataset_path, render_img_saving_path, wanted_objects=wanted_objects, camera=camera)
# # t = Timer(lambda: render.generate_scene(1))
# # print(t.timeit(number=20)) # 22.532155615001102
# # print(t.timeit(number=5))
for i in range(EPOCHS):
    floor.add_simple_floor()
    background.add_img_background()
    render.generate_scene(i)
    camera.randomize_location()
    camera.randomize_rotation()
    floor.delete_existing_floor()
    background.remove_img_background()
camera.delete_camera()

"""
To get size of an image
bpy.data.images['1.png'].size
"""


