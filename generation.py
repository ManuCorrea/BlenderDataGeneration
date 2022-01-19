import random
import bpy
import mathutils
from utils import *


class DataHandler:
    def __init__(self, path_of_classes_folders=None, wanted_classes=None):

        self.classes = {}
        self.objects_paths = {}  # Dict keys:class_name = path
        self.objects = {}  # Dict keys:class_name = [objects_name]
        # IMPROVE active objects saves names with extension so
        # they must be process before interacting with them by
        # bpy.data.objects
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
                print("TAKING ALL DIRECTORIES")
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
        classes_txt_exist = os.path.isfile(classes_location)
        print(
            f"\nChecking if {classes_location} exist -> {classes_txt_exist}\n")
        if classes_txt_exist:
            self.read_classes_file(classes_location)
        else:
            self.generate_classes_file(classes_location)

    def sample(self):
        self.active_objects = {}
        for obj in self.objects.keys():
            self.active_objects[obj] = get_list_random_images(
                self.objects[obj])
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

    def add_images_planes(self):
        for obj in self.active_objects.keys():
            objects_list = self.active_objects[obj]
            path = self.objects_paths[obj]
            for object_to_add in objects_list:
                name = os.path.basename(object_to_add)
                bpy.ops.import_image.to_plane(shader='SHADELESS',
                                              files=[{'name': name}],
                                              directory=path)
                name = os.path.splitext(name)[0]
                bpy.data.objects[name].location = mathutils.Vector(
                    get_random_xyz())

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
                print(f"Selecting {name} in {bpy.data.objects.keys()}")
                if name in bpy.data.objects.keys():
                    bpy.data.objects[name].select_set(True)
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

# TODO: Class for floor

# TODO: Class for background


class Render:
    def __init__(self, data_path, output_path, wanted_objects=None):
        self.scene = bpy.data.scenes['Scene']
        self.render_img_saving_path = output_path
        self.labels_filepath = os.path.join(output_path, "labels")
        self.data_handler = DataHandler(data_path, wanted_objects)

    def generate_scene(self, idx):
        add_simple_floor(
            rgba=(random.random(), random.random(), random.random(), 1))

        self.data_handler.sample()
        # sampled_objects = get_list_random_images(self.objects)

        # TODO add_images_planes change for DataHandler
        # added_carts_names = add_images_planes(
        #     self.data_handler.active_objects, self.path)
        # print(f"\n\n\nadded_carts_names------ {added_carts_names}\n\n\n")
        self.data_handler.add_images_planes()

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
        text_coordinates = self.data_handler.get_all_coordinates(self.scene)

        splitted_coordinates = text_coordinates.split(
            '\n')[:-1]  # Delete last '\n' in coordinates
        # Write the coordinates to the text file and output the render_counter.txt file
        text_file.write('\n'.join(splitted_coordinates))
        text_file.close()  # Close the .txt file corresponding to the label

        # print(f"Before delete_image_planes --------- {bpy.data.objects.keys()}")
        # print(added_carts_names)
        # delete_images_planes(added_carts_names)
        self.data_handler.delete_images_planes()
        # print(f"Before calling --------- {bpy.data.objects.keys()}")
        delete_existing_floor()
        # print(f" --------- {bpy.data.objects.keys()}")


class RenderPreloadingAssets:
    def __init__(self, data_path, output_path, wanted_objects=None):
        self.data_handler = DataHandler(data_path, wanted_objects)
        
        self.data_handler.add_all_images_unrendered()
        self.scene = bpy.data.scenes['Scene']
        self.render_img_saving_path = output_path
        self.labels_filepath = os.path.join(output_path, "labels")

    def move_selected_objects(self):
        for obj in self.data_handler.active_objects.keys():
            selected_objects = self.data_handler.active_objects[obj]
            for name in selected_objects:
                name = name.split('.')[0]
                bpy.data.objects[name].location = mathutils.Vector(
                    get_random_xyz())

    # TODO handle this function
    def hide_render_of_objects(self, render_object):
        for class_ in self.data_handler.active_objects.keys():
            object_list = self.data_handler.active_objects[class_] # Active objects
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
        add_simple_floor(rgba=(random.random(), random.random(),
                               random.random(), 1))
        # over the existing objects pick some
        # it will use sample() and will be a dict instead of a list

        self.data_handler.sample()

        # self.selected_objects = get_list_random_images(self.objects)

        # make them render
        # self.hide_render_of_objects(self.selected_objects, False)
        self.hide_render_of_objects(False)
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
        text_coordinates = self.data_handler.get_all_coordinates(self.scene)

        splitted_coordinates = text_coordinates.split(
            '\n')[:-1]  # Delete last '\n' in coordinates
        # Write the coordinates to the text file and output the render_counter.txt file
        text_file.write('\n'.join(splitted_coordinates))
        text_file.close()  # Close the .txt file corresponding to the label

        # make the picked unrender
        self.hide_render_of_objects(True)

        # world config
        delete_existing_floor()
