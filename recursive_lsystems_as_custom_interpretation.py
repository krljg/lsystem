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

    # Deselect everything because otherwise the new lsystem will try randomly place the new lsystem on the old lsystem
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    lex = lsystem.exec.Exec()
    lex.set_axiom("p(line)X")
    lex.add_rule("X", "FX") #todo: make it more leaf shaped
    lex.min_iterations = int(float(parameters[0]))
    lex.exec(context=context)
    # Go through all the objects in the child lsystem and set position, rotation, and parent
    for obj in lex.objects:
        obj.location = lsystem.util.matmul(turtle.transform, mathutils.Vector((0.0, 0.0, 0.0)))
        obj.rotation_euler = turtle.transform.to_euler()
        obj.parent = bl_obj.object
        obj_base_pairs.append((obj, None))  # blender 2.80 specific


def flower(turtle, parameters, bl_obj, obj_base_pairs, context):
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    lex = lsystem.exec.Exec()  # Problem with original lsystem being selected
    # todo: make the flower unfold
    # todo: expand the size of the leafs
    lex.define("a0", "45")
    lex.define("a1", "12.5")
    lex.set_axiom("p(line)LLLLLLLL")
    lex.add_rule("L", "/(a0)f(0)[^(60)¤(0.4)F^(-a1)¤(0.75)F^(-a1)¤(0.5)F^(-a1)¤(0.35)F^(-a1)¤(0.05)F]")
    lex.min_iterations = int(float(parameters[0]))
    lex.exec(context=context)
    for obj in lex.objects:
        obj.location = lsystem.util.matmul(turtle.transform, mathutils.Vector((0.0, 0.0, 0.0)))
        obj.rotation_euler = turtle.transform.to_euler()
        obj.parent = bl_obj.object
        obj_base_pairs.append((obj, None))  # blender 2.80 specific


# See figure 3.2 in abop, page 69.
ex = lsystem.exec.Exec()
ex.set_axiom("p(subsurf)a(1)")
ex.add_rule("a(t)", "F(1)[&(30)L(0)]/(137.5)a(add(t,1))", "lt(t,7)")
ex.add_rule("a(t)", "F(20)A", "eq(t,7)")
ex.add_rule("A", "K(0)")
ex.add_rule("L(t)", "L(add(t,1))", "lt(t,9)")  # create Leaf
ex.add_rule("K(t)", "K(add(t,1))", "lt(t,5)")  # create flower
ex.add_rule("F(l)", "F(add(l,0.2))", "lt(l,2)")
ex.set_interpretation("L", leaf)
ex.set_interpretation("K", flower)
ex.exec(min_iterations=11)
