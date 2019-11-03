import mathutils
import bmesh
import lsystem.exec
import lsystem.util


def sphere(turtle, parameters, bl_obj, obj_base_pairs, context):
    mesh = bpy.data.meshes.new("sphere")
    obj = bpy.data.objects.new("sphere", mesh)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=bl_obj.radius*5)
    bm.to_mesh(mesh)
    bm.free()
    obj.location = lsystem.util.matmul(turtle.transform, mathutils.Vector((0.0, 0.0, 0.0)))
    obj.rotation_euler = turtle.transform.to_euler()
    base = lsystem.util.link(context, obj)
    obj.parent = bl_obj.object
    obj_base_pairs.append((obj, base))


exec = lsystem.exec.Exec()
exec.set_axiom("p(subsurf)X")
exec.add_rule("X", "/(rand(0,359))[+FX][-FX]")
exec.add_rule("X", "FX")
exec.set_interpretation("X", sphere)
exec.exec(min_iterations=6)
