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

add_path_for_modules()
import utils
import generation
from utils import *
from generation import Render, RenderPreloadingAssets
import camera
import light

# Necesary for development so when modules are changed are reloaded in Blender
importlib.reload(utils)
importlib.reload(generation)
importlib.reload(camera)
importlib.reload(light)

# Have to enable the module for importing images as planes
addon_utils.enable("io_import_images_as_planes")

##### CONFIGURATION #####
EPOCHS = 10
dataset_path = "/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/dataset/"
render_img_saving_path = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/generated'
##### END CONFIGURATION #####

# camera
camera = camera.Camera(location=(0, 6, 0.3), location_range=((-0.5,0.5), (4, 6), (0.3, 0.8)), rotation=(90, 0, 180))

# floor and background object
floor = generation.Floor(random=True, size=30, location=(0, 0, 0))

background = generation.Background(dataset_path, wanted_classes=["bg"],
                                   location=(0, 0, 0.5), rotation=(m.radians(90), 0, m.radians(180)),
                                   scale=5)

# Lights objects
light1 = light.Light(location=(1,1,2), location_range=((-2, 2), (0, 2), (1.2, 3)),
                     energy_range=(60, 200))

light2 = light.Light(location=(1, 1, 2), location_range=(
    (-3, 3), (0, 3), (1.2, 2)),
    energy_range=(60,120))

# we specify which folders are out img data classes
wanted_objects = ["cart", "human"]
render = Render(dataset_path, render_img_saving_path,
                wanted_objects=wanted_objects, camera=camera)

for i in range(EPOCHS):
    # floor and background
    floor.add_simple_floor()
    background.add_img_background()
    # lights
    light1.randomize_location()
    light1.randomize_energy()
    light2.randomize_location()
    light2.randomize_energy()
    # generate scene
    render.generate_scene(i)
    # camera
    camera.randomize_location()
    camera.randomize_rotation()
    # delete floor and background
    floor.delete_existing_floor()
    background.remove_img_background()
camera.delete_camera()
light1.delete_light()
light2.delete_light()
