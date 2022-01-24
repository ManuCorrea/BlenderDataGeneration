import random
from typing import NamedTuple
import bpy
import mathutils
from utils import *


class Camera:
    def __init__(self, location=(0, 0, 0), rotation=(0, 0, 0), location_range=((-1, 1), (-1, 1), (-1, 1)), rotation_range=((80, 100), (-5, 5), (175, 185))):
        """Initialization of Camera

        Args:
            location (tuple, optional): Camera's location. Defaults to (0, 0, 0).
            rotation (tuple, optional): Camera's rotation (in degrees). Defaults to (0, 0, 0).
            location_range (tuple, optional): Camera's location ranges when calling randomize_location(). Defaults to ((-1, 1), (-1, 1), (-1, 1)).
            rotation_range (tuple, optional): Camera's location ranges when calling randomize_rotation(). Defaults to ((80, 100), (-5, 5), (175, 185)).
        """
        bpy.ops.object.camera_add(enter_editmode=False, align='VIEW',
                                  location=location, rotation=rotation, scale=(1, 1, 1))
        self.name = bpy.context.active_object.name
        self.camera = bpy.data.objects[self.name]

        self.camera.location = location
        self.camera.rotation_euler = tuple(m.radians(i) for i in rotation)

        self.location_x_range = location_range[0]
        self.location_y_range = location_range[1]
        self.location_z_range = location_range[2]

        self.rotation_x_range = rotation_range[0]
        self.rotation_y_range = rotation_range[1]
        self.rotation_z_range = rotation_range[2]

    def randomize_location(self):
        """
        Randomizes the location of the camera with the given ranges in initialization
        """
        self.camera.location = mathutils.Vector(
            get_random_xyz(self.location_x_range, self.location_y_range, self.location_z_range))

    def randomize_rotation(self):
        """
        Randomizes the rotation of the camera with the given ranges in initialization
        """
        self.camera.rotation_euler = mathutils.Vector(
            get_random_xyz_rotation(self.rotation_x_range, self.rotation_y_range, self.rotation_z_range))

    def delete_camera(self):
        """
        Deletes the camera in Blender
        """
        bpy.data.objects[self.name].select_set(True)
        bpy.ops.object.delete()
