import bpy
import os
import shutil
import math
import mathutils


def convert_to_msh(directory, obj_name, msh_name):
    os.chdir(directory)
    
    os.system('docker cp {} ipc_mesh:/app/convert/mesh.obj'.format(obj_name))
    os.system('docker start -a ipc_mesh')
    os.system('docker cp ipc_mesh:/app/convert/mesh.msh {}'.format(msh_name))
    os.chdir('..')


def lookup_material(name):
    materials = {
                'default': ('1000', '1e5', '0.4'),
                'aluminium': ('2700', '7e10', '0.35'),
                'copper': ('8950', '1e11', '0.34'),
                'gold': ('19320', '8e10', '0.44'),
                'iron': ('7870', '2e11', '0.29'),
                'lead': ('11350', '2e10', '0.44'),
                'abs': ('1020', '2e09', '0.46'),
                'glass': ('2500', '7e10', '0.25'),
                'nylon': ('1150', '3e9', '0.39'),
                'wood': ('700', '1e10', '0.43'),
                'rubber': ('2300', '1e6', '0.47'),
                'hardrubber': ('1000', '5e6', '0.47'),
                'cork': ('240', '3e7', '0.26'),
                'hydrogel': ('1000', '1e5', '0.45')
                }

    mat = materials['default']
    if name and name in materials:
        mat = materials[name]
    return 'material {} {} {} '.format(mat[0], mat[1], mat[2])


def get_material(object, is_static):
    material = ''
    if not is_static:
        parts = object.name.split('_')
        material = lookup_material('default')
        if len(parts) >= 2:
            material = lookup_material(parts[1])
    return material


def deselect_all():
    for ob in bpy.context.selected_objects:
        ob.select_set(False)


def select_single_object(object):
    deselect_all()
    object.select_set(True)
    for obj in bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = obj


def select_multiple_objects(objects):
    deselect_all()
    for object in objects:
        object.select_set(True)
    for obj in bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = obj



class PhysicsObject:
    
    def __init__(self, object):
        self.object = object
        self.is_static = object.name.startswith('static_')
        self.is_dynamic = not self.is_static
        self.obj_name = object.name + '.obj'
        self.msh_name = object.name + '.msh'
        self.result_name = self.msh_name if self.is_dynamic else self.obj_name
        self.material = get_material(object, self.is_static)
        
    def export_and_convert(self, directory):
        select_single_object(self.object)
        bpy.context.scene.frame_set(0)
    
        original_location = (self.object.location.x, self.object.location.y, self.object.location.z)
        original_rotation = (self.object.rotation_euler.x, self.object.rotation_euler.y, self.object.rotation_euler.z)
        
        self.object.location = (0, 0, 0)
        self.object.rotation_euler = (0, 0, 0)
        
        bpy.ops.export_scene.obj(filepath=os.path.join(directory, self.obj_name), use_selection=True, use_triangles=True, use_materials=False)
        
        self.object.location = original_location
        self.object.rotation_euler = original_rotation
        
        if self.is_dynamic:
            convert_to_msh(directory, self.obj_name, self.msh_name)
        
    def get_shape_string(self):
        converted_euler = self.object.rotation_euler.to_quaternion().to_euler('YXZ')
        x = math.degrees(converted_euler.x)
        y = math.degrees(converted_euler.y)
        z = math.degrees(converted_euler.z)
        
        transform = '{} {} {} {} {} {} {} 1 1 1 '.format(self.result_name, self.object.location.x, self.object.location.z, -self.object.location.y, x, z, -y)
        
        return transform + self.material



class AnimatedObjects:
    
    def __init__(self, objects):
        self.objects = objects
        self.obj_name = 'animated_objects.obj'
        
    def export_and_convert(self, directory):
        bpy.context.scene.frame_set(0)
        select_multiple_objects(self.objects)
        
        bpy.ops.export_scene.obj(filepath=os.path.join(directory, self.obj_name), use_selection=True, use_triangles=True, use_materials=False)
        
        animation_dir = os.path.join(directory, 'animations')
        os.mkdir(animation_dir)
        
        for f in range(0, 202):
            bpy.context.scene.frame_set(f)
            select_multiple_objects(self.objects)
            ani_file = os.path.join(animation_dir, str(f) + '.obj')
            bpy.ops.export_scene.obj(filepath=ani_file, use_selection=True, use_triangles=True, use_materials=False)
        
    def get_shape_string(self):        
        return 'animated_objects.obj 0 0 0 0 0 0 1 1 1 meshSeq animations'



def run_simulation():
    #os.system('docker exec ipc_run /bin/bash -c "rm -rf /app/run && mkdir -p /app/run/output"')
    os.system('docker cp input ipc_run:/app/run')
    os.system('docker start -a ipc_run')
    os.system('docker cp ipc_run:/app/run/output/ .')


def is_physics_object(object):
    return not object.hide_get() and object.type == 'MESH' and not object.name.endswith('_sequence') and not object.name.startswith('ignore_') and not object.name.startswith('ani_')


def is_animation_object(object):
    return not object.hide_get() and object.type == 'MESH' and object.name.startswith('ani_')


def create_physics_objects():
    return [PhysicsObject(object) for object in bpy.data.objects if is_physics_object(object)]

def create_animation_objects():
    list = [object for object in bpy.data.objects if is_animation_object(object)]
    if len(list) > 0:
        return AnimatedObjects(list)
    return None


def write_scene_file(path, physics_objects, animation_objects):
    scene_file = open(path, 'w')
    n = len(physics_objects)
    if animation_objects is not None:
        n = n + 1
    scene_file.write('shapes input ' + str(n) + '\n')
    for physics_object in physics_objects:
        scene_file.write(physics_object.get_shape_string() + '\n')
    if animation_objects is not None:
        scene_file.write(animation_objects.get_shape_string() + '\n')
    scene_file.write('\n')
    scene_file.write('selfFric 0.1\n')
    scene_file.write('\n')
    scene_file.write('ground 0.1 0\n')
    scene_file.write('\n')
    scene_file.write('time 5 0.025\n')
    scene_file.write('\n')
    if animation_objects is not None:
        scene_file.write('script meshSeqFromFile /app/run/input/animations\n')
    scene_file.close()
    

def rename_output_files(path):
    for filename in os.listdir(path):
        if filename.endswith('.obj') and filename[0].isdigit():
            os.rename(os.path.join(output_directory, filename), os.path.join(output_directory, 'seq_' + filename))


os.system('docker rm ipc_mesh')
os.system('docker rm ipc_run')
os.system('docker run --name ipc_mesh -d ipc /bin/bash -c "mkdir -p /app/convert && cd /app/convert && /app/src/Projects/MeshProcessing/meshprocessing 0 /app/convert/mesh.obj 3 5e-1 0"')
os.system('docker run --name ipc_run -d ipc /bin/bash -c "mkdir -p /app/run/input && cd /app/run/input && /app/build/IPC_bin 100 /app/run/input/scene.txt -o /app/run/output"')

blend_file_path = bpy.data.filepath
input_directory = os.path.join(os.path.dirname(blend_file_path), 'input')
output_directory = os.path.join(os.path.dirname(blend_file_path), 'output')
scene_file = os.path.join(input_directory, 'scene.txt')
 
if os.path.exists(input_directory):
    shutil.rmtree(input_directory)
if os.path.exists(output_directory):
    shutil.rmtree(output_directory)

os.mkdir(input_directory)


physics_objects = create_physics_objects()
for physics_object in physics_objects:
    physics_object.export_and_convert(input_directory)
    
animation_objects = create_animation_objects()
if animation_objects is not None:
    animation_objects.export_and_convert(input_directory)


write_scene_file(scene_file, physics_objects, animation_objects)
run_simulation()
rename_output_files(output_directory)
