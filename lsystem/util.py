
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
