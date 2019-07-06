
import bpy
import operator


def matmul(a, b):
    """Perform matrix multiplication in a blender 2.7 and 2.8 safe way"""
    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        return operator.matmul(a, b) # the same as writing a @ b
    else:
        return a * b


def link(context, object):
    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        return context.scene.collection.objects.link(object)
    else:
        return context.scene.objects.link(object)


def to_mesh(obj, context=None):
    print("util.to_mesh()\n{}\n{}".format(obj, obj.modifiers))
    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        print("version >= 2.80")
        if not context:
            context = bpy.context
        depsgraph = context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        #new_mesh = obj_eval.to_mesh()
        new_mesh = bpy.data.meshes.new_from_object(obj_eval)
        return new_mesh
    else:
        new_mesh = obj.to_mesh(scene=bpy.context.scene, apply_modifiers=True, settings='PREVIEW')
        bpy.data.objects.remove(obj)
        return new_mesh
