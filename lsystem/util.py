
import bpy
import operator


def matmul(a, b):
    """Perform matrix multiplication in a blender 2.7 and 2.8 safe way"""
    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        return operator.matmul(a, b)  # the same as writing a @ b
    else:
        return a * b


def link(context, obj):
    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        return context.scene.collection.objects.link(obj)
    else:
        return context.scene.objects.link(obj)


def to_mesh(obj, context=None):
    print("util.to_mesh()\n{}\n{}".format(obj, obj.modifiers))
    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        print("version >= 2.80")
        if not context:
            context = bpy.context
        context.scene.collection.objects.link(obj)
        depsgraph = context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        #new_mesh = obj_eval.to_mesh()
        new_mesh = bpy.data.meshes.new_from_object(obj_eval, preserve_all_data_layers=True, depsgraph=depsgraph)
        context.scene.collection.objects.unlink(obj)
        return new_mesh
    else:
        new_mesh = obj.to_mesh(scene=bpy.context.scene, apply_modifiers=True, settings='PREVIEW')
        bpy.data.objects.remove(obj)
        return new_mesh


def print_verts(mesh):
    for v in mesh.vertices:
        print(v.co)


def hide_render(obj, hide, frame):
    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        obj.hide_viewport = hide
        res = obj.keyframe_insert(data_path="hide_viewport", index=-1, frame=frame)
        if not res:
            print("Failed to insert keyframe")
    else:
        obj.hide = hide
        obj.keyframe_insert(data_path="hide", index=-1, frame=frame)
    obj.hide_render = hide
    obj.keyframe_insert(data_path="hide_render", index=-1, frame=frame)
