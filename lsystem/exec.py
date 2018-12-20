
import lsystem.lsystem
import lsystem.turtle

import math
import time
import random
import copy

import bpy
import bpy_extras.mesh_utils
import mathutils


# todo: allow "animation" - create iterations of the same seed in the same place but use hide property to show only one at a time

def execute(context,
            axiom,
            rules,
            instances=1,
            seed=0,
            min_iterations=1,
            iterations=1,
            angle=math.radians(25),
            length=1.0,
            radius=0.1,
            expansion=1.1,
            shrinkage=0.9,
            fat=1.2,
            slinkage=0.8,
            animate=False,
            normal=(0.0, 0.0, 1.0)):
    turtle = lsystem.turtle.Turtle(seed)
    turtle.set_angle(angle)
    turtle.set_length(length)
    turtle.set_radius(radius)
    turtle.set_expansion(expansion)
    turtle.set_shrinkage(shrinkage)
    turtle.set_fat(fat)
    turtle.set_slinkage(slinkage)
    turtle.set_direction(mathutils.Vector((normal[0], normal[1], normal[2])))

    lsys = lsystem.lsystem.LSystem(axiom, rules)
    return exec_turtle(context, lsys, instances, min_iterations, iterations, animate, turtle)


def exec_turtle(context, lsys, instances, min_iterations, max_iterations, animate, turtle):
    # Need to call scene.update for ray_cast method.
    # See http://blender.stackexchange.com/questions/40429/error-object-has-no-mesh-data-to-be-used-for-ray-casting
    bpy.context.scene.update()

    rmax_iter = max_iterations+1
    if max_iterations <= min_iterations:
        rmax_iter = min_iterations+1

    inst_list = []
    seed = turtle.seed
    for instance in range(0, instances):
        iter_list = []
        for iterations in range(min_iterations, rmax_iter):
            new_turtle = copy.deepcopy(turtle)
            new_turtle.seed = seed
            object_base_pairs = run_once(context, new_turtle, instance, lsys, iterations)
            iter_list.append(object_base_pairs)
        seed += 1
        inst_list.append(iter_list)
    selected = bpy.context.selected_objects
    print("selected: " + str(selected))
    if len(selected) == 0:
        grid(inst_list, not animate)
    else:
       add_to_selected_faces(inst_list, selected)

    for ob in context.scene.objects:
        ob.select = False

    if animate:
        animate_inst_list(inst_list)

    objects = []
    for iter_list in inst_list:
        for object_base_pairs in iter_list:
            for obj_base_pair in object_base_pairs:
                base = obj_base_pair[1]
                base.select = True
                objects.append(obj_base_pair[0])
            context.scene.objects.active = object_base_pairs[-1][0]
    return objects


def animate_inst_list(inst_list):
    for iter_list in inst_list:
        animate_iter_list(iter_list)


def animate_iter_list(iter_list):
    frame_delta = 5
    frame = 0
    for object_base_pair_list in iter_list:
        for object_base_pair in object_base_pair_list:
            object = object_base_pair[0]
            object.hide = True
            object.keyframe_insert(data_path="hide", index=-1, frame=0)
            object.hide = False
            object.keyframe_insert(data_path="hide", index=-1, frame=frame)
            object.hide = True
            object.keyframe_insert(data_path="hide", index=-1, frame=frame+frame_delta)
        frame += frame_delta

# def add_lsystem_to_object(ob, context, lsys, turtle, instances, min_iterations, max_iterations):
#     positions = []
#     for i in range(0, instances):
#         x = random.uniform(0, ob.dimensions.x) - ob.dimensions.x * 0.5
#         y = random.uniform(0, ob.dimensions.y) - ob.dimensions.y * 0.5
#         start = mathutils.Vector((x, y, -(ob.dimensions.z + 1.0)))
#         direction = mathutils.Vector((0, 0, 1))
#         res, location, normal, index = ob.ray_cast(start, direction)
#         if index == -1:
#             print("dimensions = " + str(ob.dimensions))
#             print("scale = " + str(ob.scale))
#             print("start " + str(start))
#             print("end " + str(direction))
#             print("res: " + str(res) + ", location: " + str(location) + ", normal = " + str(
#                     normal) + ", index = " + str(index))
#             print("no intersection found")
#             continue
#         positions.append((i, location + ob.location))
#
#     obj_base_pairs = []
#     for i, position in positions:
#         random.seed()
#         new_turtle = copy.deepcopy(turtle)
#         new_turtle.seed = random.randint(0,1000)
#         iterations = random.randint(min_iterations, max_iterations)
#         new_obj_base_pairs = run_once(context,
#                                       new_turtle,
#                                       i,
#                                       lsys,
#                                       iterations,
#                                       position,
#                                       None)
#         obj_base_pairs.extend(new_obj_base_pairs)
#     return obj_base_pairs


# def add_lsystems_to_selected_faces(selected, context, instances, min_iterations, max_iterations, turtle, lsys):
#     random.seed(turtle.seed)
#     tessfaces = []
#     for ob in selected:
#         me = ob.data
#         me.calc_tessface()
#         tessfaces_select = [(f, ob) for f in me.tessfaces if f.select]
#         tessfaces.extend(tessfaces_select)
#
#     # todo: handle tessfaces empty
#
#     positions = []
#     for i in range(0, instances):
#         face, ob = random.choice(tessfaces)
#         new_positions = bpy_extras.mesh_utils.face_random_points(1, [face])
#         position = new_positions[0]
#         seed = random.randint(0, 1000)
#         if min_iterations >= max_iterations:
#             iterations = min_iterations
#         else:
#             iterations = random.randint(min_iterations, max_iterations)
#         positions.append((i, position, face.normal, seed, iterations, ob))
#
#     obj_base_pairs = []
#     for i, position, normal, seed, iterations, parent in positions:
#         new_obj_base_pairs = run_once(context, turtle, i, lsys, iterations, position, parent)
#
#         obj_base_pairs.extend(new_obj_base_pairs)
#     return obj_base_pairs


# def add_lsystems_grid(context, lsys, turtle, instances, min_iterations, max_iterations):
#     start_iter = min_iterations
#     end_iter = max_iterations + 1
#     if start_iter >= end_iter:
#         end_iter = start_iter + 1
#     object_base_pairs = []
#     i = 0
#     y = 0
#     first_row = True
#     while i < instances:
#         new_turtle = copy.deepcopy(turtle)
#         new_turtle.seed = turtle.seed + i
#         max_ydim = 0
#         x = 0
#         row = []
#         for iter in range(start_iter, end_iter):
#             new_obj_base_list = run_once(context,
#                                          new_turtle,
#                                          i,
#                                          lsys,
#                                          iter,
#                                          mathutils.Vector((0.0, 0.0, 0.0)),
#                                          None)
#             object = new_obj_base_list[0][0]  # todo: handle multiple objects
#             if iter == start_iter:
#                 object.location.x = 0
#             else:
#                 object.location.x = x + object.dimensions.x * 0.75
#             x = object.location.x + (object.dimensions.x * 0.75)
#             if object.dimensions.y > max_ydim:
#                 max_ydim = object.dimensions.y
#             row.append(object)
#             object_base_pairs.extend(new_obj_base_list)
#             i += 1
#             if i >= instances:
#                 break
#         if first_row:
#             y += max_ydim * 1.5
#             first_row = False
#         else:
#             y += max_ydim * 0.75
#             for object in row:
#                 object.location.y = y
#             y += max_ydim * 0.75
#
#     return object_base_pairs


def get_selected_faces(objects):
    tessfaces = []
    for ob in objects:
        me = ob.data
        me.calc_tessface()
        tessfaces_select = [(f, ob) for f in me.tessfaces if f.select]
        tessfaces.extend(tessfaces_select)
    return tessfaces


def add_to_selected_faces(inst_list, objects):
    faces = get_selected_faces(objects)

    for iter_list in inst_list:
        for obj_base_pairs in iter_list:
            face, ob = random.choice(faces)
            new_positions = bpy_extras.mesh_utils.face_random_points(1, [face])
            object = obj_base_pairs[0][0]
            object.location = new_positions[0]
            object.parent = ob


def grid(inst_list, move_x=True):
    y = 0
    for iter_list in inst_list:
        x = 0
        max_ydim = 0
        for obj_base_pairs in iter_list:
            object = obj_base_pairs[0][0]
            object.location.x = x
            object.location.y = y
            if move_x:
                x += object.dimensions.x
            if object.dimensions.y > max_ydim:
                max_ydim = object.dimensions.y
        y += max_ydim


def run_once(context, turtle, instance, lsys, iterations):
    start_time = time.time()
    print_time(start_time, "lsystem: execute" +
               "\n  seed = " + str(turtle.seed) +
               "\n  iterations = " + str(iterations))
    result = lsys.iterate(instance, iterations)
    print_time(start_time, "turtle interpreting")
    object_base_pairs = turtle.interpret(result, context)
    print_time(start_time, "turtle finished")

    return object_base_pairs


# def run_once(context, turtle, instance, lsys, iterations, position, parent):
#     start_time = time.time()
#     print_time(start_time, "lsystem: execute\n  position = " + str(position) +
#                "\n  seed = " + str(turtle.seed) +
#                "\n  iterations = " + str(iterations))
#     result = lsys.iterate(instance, iterations)
#     print_time(start_time, "turtle interpreting")
#     object_base_pairs = turtle.interpret(result, context)
#     print_time(start_time, "turtle finished")
#
#     if position is not None:
#         for pair in object_base_pairs:
#             object = pair[0]
#             object.location = position
#             if parent is not None:
#                 object.parent = parent
#
#     return object_base_pairs


def print_time(start_time, message):
    elapsed = time.time() - start_time
    print("%.5fs: %s" % (elapsed, message))
