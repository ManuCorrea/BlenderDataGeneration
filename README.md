# Blender Data Generation
The main objective of this project is to provide an abstraction layer over Blender API in order to have a set of tools for an easy generation of labeled synthetic data.

## Using it
In this repository an example for a basic generation is provided in "tinker.py". The blender project "YOLO_data_generator.blend" includes in the scripting section the script already opened.

You have to provide absolute path for: 
* "dataset_path": where the dataset is located
* "render_img_saving_path": where we save our results

With EPOCHS we specify the number of images we want to generate

## Roadmap
### TODO:
* Render labeled image masks
* Option to make images look at the camera
* Option/params to scale images/+- scaling randomly (Class already done, needs to integrate)
* Make images "stand" on the floor as a parameter (Done by default)
* Add background simple
* Add 3D objects and handle them with DataHandler
* Scene rendering class
* Enable GPU by code
* Refactor code

### FIX:
* Sometimes image planes are not deleted properly (probably related with class DataHandler with delete_images_planes())

## Acknowledgments
* [Federico Arenas López](https://github.com/federicoarenasl/Data-Generation-with-Blender): For providing a good base project and functions for defining bounding boxes and rendering.
