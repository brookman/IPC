import bpy
import os
import math

from blender_utils import *
from ipc_docker import IpcDocker
from materials import *

class PhysicsObject:

    def __init__(self, blender_mesh):
        self.blender_mesh = blender_mesh
        self.material = ''
        if self.blender_mesh.is_dynamic():
            self.material = get_material(blender_mesh.obj)

    def export_and_convert(self, directory, ipc):
        obj_path = os.path.join(directory, self.blender_mesh.obj_name)
        export_single_obj(self.blender_mesh, obj_path)

        self.result_name = self.blender_mesh.obj_name
        if self.blender_mesh.is_dynamic():
            msh_path = os.path.join(directory, self.blender_mesh.msh_name)
            ipc.convert_to_msh(obj_path, msh_path)
            self.result_name = self.blender_mesh.msh_name
             

    def get_shape_string(self):
        converted_euler = self.blender_mesh.obj.rotation_euler.to_quaternion().to_euler('YXZ')
        x = math.degrees(converted_euler.x)
        y = math.degrees(converted_euler.y)
        z = math.degrees(converted_euler.z)

        output = '{} {} {} {} {} {} {} 1 1 1 '.format(self.result_name, self.blender_mesh.obj.location.x, self.blender_mesh.obj.location.z, -self.blender_mesh.obj.location.y, x, z, -y)

        return output + self.material


class AnimatedObjects:

    def __init__(self, objects):
        self.objects = objects
        self.obj_name = 'animated_objects.obj'

    def export_and_convert(self, directory):
        animation_dir = os.path.join(directory, 'animations')
        os.mkdir(animation_dir)

        for f in range(0, 202):
            ani_file = os.path.join(animation_dir, str(f) + '.obj')
            export_multiple_objs(self.objects, ani_file, f)

    def get_shape_string(self):
        return 'animations/1.obj 0 0 0 0 0 0 1 1 1 meshSeq animations'


class Simulation:

    def __init__(self, ipc):
        self.ipc = ipc
        self.physics_objects = get_physics_objects()
        self.animation_objects = get_animation_objects()
    
    def prepare(self, input_directory):
        for physics_object in self.physics_objects:
            physics_object.export_and_convert(input_directory, self.ipc)
        if self.animation_objects is not None:
            self.animation_objects.export_and_convert(input_directory)
        
        self.write_scene_file(input_directory)

    def get_physics_objects():
        return [PhysicsObject(obj) for obj in get_blender_meshes() if not obj.is_sequence() and not obj.is_ignored() and not obj.is_animation()]


    def get_animation_objects():
        array = [obj for obj in get_blender_meshes() if obj.is_animation()]
        if len(array) <= 0:
            return None
        return AnimatedObjects(array)

    def write_scene_file(self, input_directory):
        scene_file = open(os.path.join(input_directory, 'scene.txt'), 'w')
        n = len(self.physics_objects)
        if self.animation_objects is not None:
            n = n + 1
        scene_file.write('shapes input ' + str(n) + '\n')
        for physics_object in self.physics_objects:
            scene_file.write(physics_object.get_shape_string() + '\n')
        if self.animation_objects is not None:
            scene_file.write(self.animation_objects.get_shape_string() + '\n')
        scene_file.write('\n')
        scene_file.write('selfFric 0.1\n')
        scene_file.write('\n')
        scene_file.write('ground 0.1 0\n')
        scene_file.write('\n')
        scene_file.write('time 5 0.025\n')
        scene_file.write('\n')
        if self.animation_objects is not None:
            scene_file.write('script meshSeqFromFile /app/run/input/animations\n')
        scene_file.close()

    def run(self, input_directory, output_parent_directory, output_directory):
        self.ipc.run_simulation(input_directory, output_parent_directory)
        self.rename_output_files(output_directory)

    def rename_output_files(self, path):
        for filename in os.listdir(path):
            if filename.endswith('.obj') and filename[0].isdigit():
                os.rename(os.path.join(path, filename), os.path.join(path, 'seq_' + filename))