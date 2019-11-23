import lsystem.exec
import mathutils


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


def leaf(turtle, parameters, bl_obj, obj_base_pairs, context):
    # Expect one parameter
    lex = lsystem.exec.Exec()
    lex.set_axiom("p(line)X")
    lex.add_rule("X", "FX")
    lex.min_iterations = int(float(parameters[0]))
    lex.exec(context=context)
    for obj in lex.objects:
        obj.location = lsystem.util.matmul(turtle.transform, mathutils.Vector((0.0, 0.0, 0.0)))
        obj.rotation_euler = turtle.transform.to_euler()
        obj.parent = bl_obj.object
        obj_base_pairs.append((obj, None))  # blender 2.80 specific


def flower(turtle, parameters, bl_obj, obj_base_pairs, context):
    pass


ex = lsystem.exec.Exec()
ex.set_axiom("p(subsurf)a(1)")
ex.add_rule("a(t)", "F(1)[&(30)L(0)]/(137.5)a(add(t,1))", "lt(t,7)")
ex.add_rule("a(t)", "F(20)A", "eq(t,7)")
ex.add_rule("A", "K(0)")
ex.add_rule("L(t)", "L(add(t,1))", "lt(t,9)")  # todo: create Leaf
ex.add_rule("K(t)", "K(add(t,1))", "lt(t,5)")  # todo: create flower
ex.add_rule("F(l)", "F(add(l,0.2))", "lt(l,2)")
ex.set_interpretation("L", leaf)
ex.set_interpretation("K", flower)
ex.exec(min_iterations=7)
