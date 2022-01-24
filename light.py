import random
from typing import NamedTuple
import bpy
import mathutils
from utils import *

# TODO add Spot Size option for SPOT light
# TODO add Spread option for AREA light
class Light:
    def __init__(self, type="POINT", random_type=False, random_types=['POINT', 'SUN', 'SPOT', 'AREA'],
                 location=(0, 0, 0), rotation=(0, 0, 0), location_range=((-1, 1), (-1, 1), (-1, 1)),
                 rotation_range=((-5, 5), (-5, 5), (-5, 5)), color=(1, 1, 1), energy=40, energy_range=(0, 100)):
        """
        Initialization of Light
        Args:
            type (str, optional): Light's type. Defaults to "POINT".
            random_type (bool, optional): Option to initialize with random type. Defaults to False.
            random_types (list, optional): List of types available for random choosing. Defaults to ['POINT', 'SUN', 'SPOT', 'AREA'].
            location (tuple, optional): Light's location. Defaults to (0, 0, 0).
            rotation (tuple, optional): Light's rotation (in degrees). Defaults to (0, 0, 0).
            location_range (tuple, optional): Light's location ranges when calling randomize_location(). Defaults to ((-1, 1), (-1, 1), (-1, 1)).
            rotation_range (tuple, optional): Light's location ranges when calling randomize_rotation(). Defaults to ((-5, 5), (-5, 5), (-5, 5)).
            color (tuple, optional): Light's color. Defaults to (1, 1, 1).
            energy (int, optional): Light's energy. Defaults to 40.
        """
        if type not in ['POINT', 'SUN', 'SPOT', 'AREA']:
            # TODO raise warning
            print(
                f"{type} is not a valid Light type, pick one from: ['POINT', 'SUN', 'SPOT', 'AREA']")
        type = random.choice(random_types) if random_type else type
        bpy.ops.object.light_add(type=type, align='WORLD',
                                 location=location, rotation=rotation,
                                 scale=(1, 1, 1))

        self.name = bpy.context.active_object.name
        self.light = bpy.data.objects[self.name]
        self.light.data.color = color
        self.light.data.energy = energy

        self.random_types = random_types

        self.location_x_range = location_range[0]
        self.location_y_range = location_range[1]
        self.location_z_range = location_range[2]

        self.rotation_x_range = rotation_range[0]
        self.rotation_y_range = rotation_range[1]
        self.rotation_z_range = rotation_range[2]

        self.energy_range = energy_range

    def randomize_location(self):
        """
        Randomizes the location of the light with the given ranges in initialization
        """
        self.light.location = mathutils.Vector(
            get_random_xyz(self.location_x_range, self.location_y_range, self.location_z_range))

    def randomize_rotation(self):
        """
        Randomizes the rotation of the light with the given ranges in initialization
        """
        self.light.rotation_euler = mathutils.Vector(
            get_random_xyz_rotation(self.rotation_x_range, self.rotation_y_range, self.rotation_z_range))

    def randomize_energy(self):
        self.light.data.energy = random.uniform(
            self.energy_range[0], self.energy_range[1])

    def change_type(self, type):
        if type in ['POINT', 'SUN', 'SPOT', 'AREA']:
            self.light.data.type = type
        else:
            # TODO raise warning
            print(
                f"{type} is not a valid Light type, pick one from: ['POINT', 'SUN', 'SPOT', 'AREA']")

    def delete_light(self):
        """
        Deletes the light in Blender
        """
        bpy.data.objects[self.name].select_set(True)
        bpy.ops.object.delete()
