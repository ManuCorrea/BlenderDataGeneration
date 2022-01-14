import random
import bpy
import mathutils
from utils import *


class DataHandler:
    def __init__(self, path_of_classes_folders=None, wanted_classes=None):

        self.classes = {}
        self.objects_paths = {}  # Dict keys:class_name = path
        self.objects = {}  # Dict keys:class_name = [objects_name]
        self.active_objects = None
        # Intended for future features use
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
        classes_location = os.path.join(path_of_classes_folders, "classes.txt")

        if os.path.isfile(classes_location):
            self.read_classes_file(classes_location)
        else:
            self.generate_classes_file(classes_location)

    def sample(self):
        self.active_objects = []
        for obj in self.objects.keys():
            self.active_objects.append(
                get_list_random_images(self.objects[obj]))
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
            classes_txt.write(class_)
            self.classes[class_] = idx
            idx += 1

    def get_data_path_of_classes_folders(self, classes, path_of_classes_folders):
        for class_ in classes:
            object_path = os.path.join(path_of_classes_folders, class_)
            self.objects_paths[class_] = object_path
            print(f"iter {class_} y su obj path = {object_path}")


# TODO: Class for floor

# TODO: Class for background


class Render:
    def __init__(self, object_list, data_paths, output_path, classes):
        self.path, self.objects = data_paths, object_list
        self.classes = classes
        self.scene = bpy.data.scenes['Scene']
        self.render_img_saving_path = output_path
        self.labels_filepath = os.path.join(output_path, "labels")

    def generate_scene(self, idx):
        add_simple_floor(
            rgba=(random.random(), random.random(), random.random(), 1))

        sampled_objects = get_list_random_images(self.objects)
        added_carts_names = add_images_planes(sampled_objects, self.path)
        print(f"\n\n\nadded_carts_names------ {added_carts_names}\n\n\n")

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

        print(f"added_carts_names------ {added_carts_names}")

        # TODO handle classes in non-hardcored way
        text_coordinates = get_all_coordinates(
            added_carts_names, self.classes["cart"], self.scene)

        splitted_coordinates = text_coordinates.split(
            '\n')[:-1]  # Delete last '\n' in coordinates
        # Write the coordinates to the text file and output the render_counter.txt file
        text_file.write('\n'.join(splitted_coordinates))
        text_file.close()  # Close the .txt file corresponding to the label

        # print(f"Before delete_image_planes --------- {bpy.data.objects.keys()}")
        # print(added_carts_names)
        delete_images_planes(added_carts_names)
        # print(f"Before calling --------- {bpy.data.objects.keys()}")
        delete_existing_floor()
        # print(f" --------- {bpy.data.objects.keys()}")


class RenderPreloadingAssets:
    def __init__(self, object_list, data_paths, output_path, classes):
        self.objects = add_all_images_unrendered(object_list, data_paths)
        print(f"\n\n\n\n\n self.objects {self.objects} \n\n\n\n")
        self.classes = classes
        self.scene = bpy.data.scenes['Scene']
        self.render_img_saving_path = output_path
        self.labels_filepath = os.path.join(output_path, "labels")

    def move_selected_objects(self):
        for name in self.selected_objects:
            bpy.data.objects[name].location = mathutils.Vector(
                get_random_xyz())

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
        # it will use sample() and will be a dict instead of a list
        self.selected_objects = get_list_random_images(self.objects)
        # make them render
        self.hide_render_of_objects(self.selected_objects, False)
        # move them
        self.move_selected_objects()
        # TODO handle camera
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

        # TODO handle classes in non-hardcored way
        text_coordinates = get_all_coordinates(
            self.selected_objects, self.classes["cart"], self.scene)

        splitted_coordinates = text_coordinates.split(
            '\n')[:-1]  # Delete last '\n' in coordinates
        # Write the coordinates to the text file and output the render_counter.txt file
        text_file.write('\n'.join(splitted_coordinates))
        text_file.close()  # Close the .txt file corresponding to the label

        # make the picked unrender
        self.hide_render_of_objects(self.selected_objects, True)

        # world config
        delete_existing_floor()
