import bpy
import os


def deselect_all():
    for ob in bpy.context.selected_objects:
        ob.select_set(False)


def select_single_object(blender_mesh):
    deselect_all()
    blender_mesh.obj.select_set(True)
    for obj in bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = blender_mesh.obj


def select_multiple_objects(blender_meshes):
    deselect_all()
    for blender_mesh in blender_meshes:
        blender_mesh.obj.select_set(True)
    for obj in bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = obj


def get_visible_mesh_objects():
    return [obj for obj in bpy.data.objects if not obj.hide_get() and obj.type == 'MESH']


class BlenderMesh:

    def __init__(self, obj):
        self.obj = obj
        self.obj_name = obj.name + '.obj'
        self.msh_name = obj.name + '.msh'

    def is_sequence(self):
        return self.obj.name.endswith('_sequence')

    def is_ignored(self):
        return self.obj.name.startswith('ignore_')

    def is_static(self):
        return self.obj.name.startswith('static_')

    def is_animation(self):
        return self.obj.name.startswith('ani_')

    def is_dynamic(self):
        return not self.is_sequence() and not self.is_ignored() and not self.is_static() and not self.is_animation()


def get_blender_meshes():
    return [BlenderMesh(obj) for obj in get_visible_mesh_objects()]


def export_obj(blender_mesh, path, frame, keep_transform):
    bpy.context.scene.frame_set(frame)

    if keep_transform:
        original_location = (blender_mesh.obj.location.x,
                             blender_mesh.obj.location.y, blender_mesh.obj.location.z)
        original_rotation = (blender_mesh.obj.rotation_euler.x,
                             blender_mesh.obj.rotation_euler.y, blender_mesh.obj.rotation_euler.z)
        blender_mesh.obj.location = (0, 0, 0)
        blender_mesh.obj.rotation_euler = (0, 0, 0)

    bpy.ops.export_scene.obj(
        filepath=path, use_selection=True, use_triangles=True, use_materials=False)

    if keep_transform:
        blender_mesh.obj.location = original_location
        blender_mesh.obj.rotation_euler = original_rotation


def export_single_obj(blender_mesh, path):
    select_single_object(blender_mesh)
    export_obj(blender_mesh, path, 0, True)


def export_multiple_objs(blender_meshes, path, frame):
    select_multiple_objects(blender_meshes)
    export_obj(None, path, frame, False)
