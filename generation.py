import random
from typing import NamedTuple
import bpy
import mathutils
from utils import *

# TODO get position+- as per class parameter
# TODO get scaling+- as per class parameter

"""
Parameters class will be associated with each type of object.
So we will have to define optionally a parameters object for each object class
"""
class Parameters:
    def __init__(self, location=None, location_range=((-1, 1), (-1, 1), (-1, 1)), random_location=False,
                 rotation=None, rotation_range=((-1, 1), (-1, 1), (-1, 1)), random_rotation=False,
                 scaling=None, scaling_range=(0.9, 1.1), random_scaling=False,
                 object_to_floor=True, n_objects=None, n_objects_fixed=False):
        self.location = location
        self.location_x_range = location_range[0]
        self.location_y_range = location_range[1]
        self.location_z_range = location_range[2]

        self.rotation = rotation
        self.rotation_x_range = rotation_range[0]
        self.rotation_y_range = rotation_range[1]
        self.rotation_z_range = rotation_range[2]

        self.scaling = scaling
        self.scaling_range = scaling_range

        self.random_location = random_location
        self.random_rotation = random_rotation
        self.random_scaling = random_scaling

    ####### Get functions #######
    def get_location(self):
        return self.location

    def get_scaling(self):
        return (self.scaling, self.scaling, self.scaling)

    def get_rotation(self):
        return self.location

    ####### Random related functions #######
    def get_random_location(self):
        return mathutils.Vector(
            get_random_xyz(self.location_x_range, self.location_y_range, self.location_z_range))

    def get_random_scaling(self):
        random_scale = random.uniform(
            self.scaling_range[0], self.scaling_range[1])
        return (random_scale, random_scale, random_scale)

    def get_random_rotation(self):
        return mathutils.Vector(
            get_random_xyz(self.rotation_x_range, self.rotation_y_range, self.rotation_z_range))


class DataHandler:
    # TODO implement classes properties
    def __init__(self, path_of_classes_folders=None, wanted_classes=None, classes_properties=None, classes_txt=True):
        self.classes = {}
        self.objects_paths = {}  # Dict keys:class_name = path
        self.objects = {}  # Dict keys:class_name = [objects_name]
        # IMPROVE active objects saves names with extension so
        # they must be process before interacting with them by
        # bpy.data.objects
        self.active_objects = None
        # Intended for future features use
        # TODO for each of the folders check what kind of objects they have
        self.type = None  # Dict keys:class_name = type(3D object/image)

        if path_of_classes_folders != None:
            # then we read the directories inside the given path
            if wanted_classes != None:
                # then we don't want to read all folders inside
                self.get_data_path_of_classes_folders(
                    wanted_classes, path_of_classes_folders)
            else:
                directories = get_directories_from_path(
                    path_of_classes_folders)
                self.get_data_path_of_classes_folders(
                    directories, path_of_classes_folders)
        print(f"El dicc de objects_paths {self.objects_paths}")
        # get self.objects
        for class_ in self.objects_paths.keys():
            print(
                f'\nclass_: {class_} | las keys {self.objects_paths.keys()} | self.objects {self.objects}\n')
            self.objects[class_] = get_files_from_path(
                self.objects_paths[class_])

        # get self.classes
        if classes_txt:
            classes_location = os.path.join(
                path_of_classes_folders, "classes.txt")
            classes_txt_exist = os.path.isfile(classes_location)
            print(
                f"\nChecking if {classes_location} exist -> {classes_txt_exist}\n")
            if classes_txt_exist:
                self.read_classes_file(classes_location)
            else:
                self.generate_classes_file(classes_location)

    # TODO n_max_objects_per_class make it parametrizable from __init__
    def sample(self, n_max_objects_per_class=5):
        self.active_objects = {}
        for obj in self.objects.keys():
            self.active_objects[obj] = get_list_random_images(
                self.objects[obj], n_max_objects=n_max_objects_per_class)
        return self.active_objects

    def read_classes_file(self, path):
        idx = 0
        with open(path, 'r') as classes_file:
            classes = classes_file.read().split('\n')
            for class_ in classes:
                self.classes[class_] = idx
                idx += 1

    def generate_classes_file(self, classes_location):
        idx = 0
        classes_txt = open(classes_location, 'w')
        for class_ in self.objects_paths.keys():
            classes_txt.write(f"{class_}\n")
            self.classes[class_] = idx
            idx += 1
        classes_txt.close()

    def get_data_path_of_classes_folders(self, classes, path_of_classes_folders):
        for class_ in classes:
            object_path = os.path.join(path_of_classes_folders, class_)
            self.objects_paths[class_] = object_path
            print(f"iter {class_} y su obj path = {object_path}")

    # FIXME make location as general parameter, not as function arg
    # FIXME make rotation as general parameter, not as function arg
    # change made for temporal background class
    def add_images_planes(self, location=None, rotation=None, scale=None):
        for obj in self.active_objects.keys():
            objects_list = self.active_objects[obj]
            path = self.objects_paths[obj]
            for object_to_add in objects_list:
                name = os.path.basename(object_to_add)
                bpy.ops.import_image.to_plane(shader='PRINCIPLED', #shader='SHADELESS',
                                              files=[{'name': name}],
                                              directory=path)
                name = os.path.splitext(name)[0]

                # make object by default stand on the floor
                # on images Y dimension/2
                z_pos = bpy.data.objects[name].dimensions[1]/2
                if location is None:
                    bpy.data.objects[name].location = mathutils.Vector(
                        get_random_xyz(z_range=(z_pos, z_pos)))
                else:
                    bpy.data.objects[name].location = mathutils.Vector(
                        location)
                if rotation is not None:
                    bpy.data.objects[name].rotation_euler = mathutils.Vector(
                        rotation)
                if scale is not None:
                    bpy.data.objects[name].scale *= scale

    def delete_images_planes(self):
        for obj in self.active_objects.keys():
            names_list = self.active_objects[obj]
            if len(names_list) == 0:
                return
            repeated = False
            if len(names_list) != len(set(names_list)):
                repeated = True
            for name in names_list:
                name = name.split('.')[0]
                # print(f"Selecting {name} in {bpy.data.objects.keys()}")
                if name in bpy.data.objects.keys():
                    bpy.data.objects[name].select_set(True)
                # FIXME this approach does not work with DataHandler class
                if repeated:
                    for key in bpy.data.objects.keys():
                        if key.startswith(name):
                            bpy.data.objects[key].select_set(True)
        bpy.ops.object.delete()

    def add_all_images_unrendered(self):
        for obj in self.objects.keys():
            objects_list = self.objects[obj]
            path = self.objects_paths[obj]
            for object_to_add in objects_list:
                name = os.path.basename(object_to_add)
                bpy.ops.import_image.to_plane(shader='SHADELESS',
                                              files=[{'name': name}],
                                              directory=path)
                name = os.path.splitext(name)[0]
                bpy.data.objects[name].location = mathutils.Vector(
                    get_random_xyz())

    def get_all_coordinates(self, scene):
        '''
        This function takes no input and outputs the complete string with the coordinates
        of all the objects in view in the current image
        '''
        main_text_coordinates = ''  # Initialize the variable where we'll store the coordinates

        for obj in self.active_objects.keys():
            objects_list = self.active_objects[obj]
            # Loop through all of the objects
            for i, objct in enumerate(objects_list):
                # print("     On object:", objct)
                # Get current object's coordinates
                objct = objct.split('.')[0]
                b_box = find_img_bounding_box(bpy.data.objects[objct], scene)
                if b_box:  # If find_bounding_box() doesn't return None
                    # print("         Initial coordinates:", b_box)
                    text_coordinates = format_coordinates(
                        b_box, self.classes[obj])  # Reformat coordinates to YOLOv3 format
                    # print("         YOLO-friendly coordinates:", text_coordinates)
                    # Update main_text_coordinates variables whith each
                    main_text_coordinates = main_text_coordinates + text_coordinates
                    # line corresponding to each class in the frame of the current image
                else:
                    # print("         Object not visible")
                    pass
        return main_text_coordinates


class Floor:
    def __init__(self, size=50, location=(0, 0, 0), rgba=(0, 0, 0, 1), random=False):
        self.size = size
        self.location = location
        self.rgba = rgba
        self.random = random

    def add_simple_floor(self):
        set_before_adding = set(bpy.data.objects.keys())
        # This adds a plane
        bpy.ops.mesh.primitive_plane_add(
            size=self.size, enter_editmode=False, align='WORLD', location=self.location, scale=(1, 1, 1))

        set_after_adding = set(bpy.data.objects.keys())
        # Finding the name of the added plane
        self.plane_name = set_after_adding.difference(set_before_adding).pop()
        # material = bpy.data.materials["Material"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (
        #     0.8, 0.269606, 0, 1)

        # https://blender.stackexchange.com/questions/56751/add-material-and-apply-diffuse-color-via-python
        mat = bpy.data.materials.new(name="MaterialName")
        bpy.data.objects[self.plane_name].data.materials.append(
            mat)  # add the material to the object
        if self.random:
            bpy.context.object.active_material.diffuse_color = (
                random.random(), random.random(), random.random(), 1)
        else:
            bpy.context.object.active_material.diffuse_color = self.rgba

    def delete_existing_floor(self):
        bpy.data.objects[self.plane_name].select_set(True)
        bpy.ops.object.delete()


class Background:
    def __init__(self, path_of_classes_folders=None, wanted_classes=None, size=50, location=(0, 0, 0), rotation=(0, 0, 0), scale=1, rgba=(0, 0, 0, 1), random=False):
        self.size = size
        self.location = location
        self.rotation = rotation
        self.scale = scale
        # TODO make also simple_background, maybe make parent class for Floor and Background classes
        self.rgba = rgba
        self.random = random
        self.data_handler = DataHandler(
            path_of_classes_folders, wanted_classes, classes_txt=False)

    def sample(self):
        self.data_handler.active_objects = {}
        for obj in self.data_handler.objects.keys():
            self.data_handler.active_objects[obj] = get_list_random_images(
                self.data_handler.objects[obj], n_exact_number=1)
        return self.data_handler.active_objects

    def add_img_background(self):
        # self.data_handler.sample(1)
        self.sample()
        print(
            f"Active objects en background: {self.data_handler.active_objects}")
        self.data_handler.add_images_planes(
            location=self.location, rotation=self.rotation, scale=self.scale)

    def remove_img_background(self):
        self.data_handler.delete_images_planes()


# TODO finish function so we delete all resources
class Render:
    def __init__(self, data_path, output_path, camera, wanted_objects=None):
        self.scene = bpy.data.scenes['Scene']
        self.scene.camera = camera.camera
        self.render_img_saving_path = output_path
        self.labels_filepath = os.path.join(output_path, "labels")
        self.data_handler = DataHandler(data_path, wanted_objects)

    def generate_scene(self, idx):
        self.data_handler.sample()
        self.data_handler.add_images_planes()

        print("\n\n\n\n\nEXPORTING Y TAL\n\n\n\n\n")
        # export_render(self.scene, 500, 500, 100, 60,
        #               self.render_img_saving_path, f'{idx}.png')

        export_render(self.scene, 1920, 1080, 100, 60,
                      self.render_img_saving_path, f'{idx}.png')
        # export_render(self.scene, 1280, 720, 100, 50,
        #               self.render_img_saving_path, f'{idx}.png')

        # Here we add the bbox
        # Output Labels
        # Create label file name
        text_file_name = f"{self.labels_filepath}/{idx}.txt"
        # Open .txt file of the label
        text_file = open(text_file_name, 'w+')
        # Get formatted coordinates of the bounding boxes of all the objects in the scene
        text_coordinates = self.data_handler.get_all_coordinates(self.scene)
        splitted_coordinates = text_coordinates.split(
            '\n')[:-1]  # Delete last '\n' in coordinates
        # Write the coordinates to the text file and output the render_counter.txt file
        text_file.write('\n'.join(splitted_coordinates))
        text_file.close()  # Close the .txt file corresponding to the label

        # print(f"Before delete_image_planes --------- {bpy.data.objects.keys()}")
        self.data_handler.delete_images_planes()


# TODO/FIXME orientation of the added assets
class RenderPreloadingAssets:
    def __init__(self, data_path, output_path, camera, wanted_objects=None):
        self.data_handler = DataHandler(data_path, wanted_objects)
        self.data_handler.add_all_images_unrendered()
        self.scene = bpy.data.scenes['Scene']
        self.scene.camera = camera.camera
        self.render_img_saving_path = output_path
        self.labels_filepath = os.path.join(output_path, "labels")

    def move_selected_objects(self):
        for obj in self.data_handler.active_objects.keys():
            selected_objects = self.data_handler.active_objects[obj]
            for name in selected_objects:
                name = name.split('.')[0]
                bpy.data.objects[name].location = mathutils.Vector(
                    get_random_xyz())

    def hide_render_of_objects(self, render_object):
        for class_ in self.data_handler.active_objects.keys():
            # Active objects
            object_list = self.data_handler.active_objects[class_]
            for obj in object_list:
                name = obj.split('.')[0]
                bpy.data.objects[name].hide_render = render_object

    def delete_all_images(self):
        for class_ in self.data_handler.objects.keys():
            objects_list = self.data_handler.objects[class_]
            for object_to_delete in objects_list:
                name_ = object_to_delete.split('.')[0]
                if name_ in bpy.data.objects.keys():
                    bpy.data.objects[name_].select_set(True)
        bpy.ops.object.delete()

    def generate_scene(self, idx):
        self.data_handler.sample()
        self.hide_render_of_objects(False)
        # move them
        self.move_selected_objects()

        # render
        export_render(self.scene, 500, 500, 100, 30,
                      self.render_img_saving_path, f'{idx}.png')

        # Here we add the bbox
        # Output Labels
        # Create label file name
        text_file_name = f"{self.labels_filepath}/{idx}.txt"
        # Open .txt file of the label
        text_file = open(text_file_name, 'w+')
        # Get formatted coordinates of the bounding boxes of all the objects in the scene
        # Display demo information - Label construction
        text_coordinates = self.data_handler.get_all_coordinates(self.scene)

        splitted_coordinates = text_coordinates.split(
            '\n')[:-1]  # Delete last '\n' in coordinates
        # Write the coordinates to the text file and output the render_counter.txt file
        text_file.write('\n'.join(splitted_coordinates))
        text_file.close()  # Close the .txt file corresponding to the label

        # make the picked unrender
        self.hide_render_of_objects(True)
