import random
import bpy
import mathutils
from utils import *

# TODO handle multiple data_paths/classes/etc


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
