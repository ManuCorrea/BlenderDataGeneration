import bpy
import numpy as np
import math as m
import random
import time
import os
import sys

import mathutils
import addon_utils
import importlib


def add_path_for_modules():
    dir = os.path.dirname(bpy.data.filepath)
    print(f"Adding {dir}")
    if not dir in sys.path:
        sys.path.append(dir)


add_path_for_modules()

import utils
import generation
from utils import *
from generation import Render, RenderPreloadingAssets, DataHandler

importlib.reload(utils)
importlib.reload(generation)

addon_utils.enable("io_import_images_as_planes")

data_dir = '/home/yo/Desktop/Desarrollo/blender/Data-Generation-with-Blender/Resources/dataset'
data = generation.DataHandler(data_dir, ['human', 'cart'])


print(f"\ndata.classes -> {data.classes}")
print("----------------")

print(f"\ndata.objects_paths -> {data.objects_paths}")
print("----------------")

print(f"\ndata.objects -> {data.objects}")
print("----------------")

print(f"\ndata.active_objects -> {data.active_objects}")
print("----------------")

data.sample()

print(f"\ndata.active_objects -> {data.active_objects}")
print("----------------")

print(f"\ndata.classes -> {data.classes}")
print("----------------")

