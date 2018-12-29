
import lsystem.lsystem
import lsystem.turtle

import math
import time
import random
import copy

import bpy
import bpy_extras.mesh_utils
import mathutils


class Exec:
    def __init__(self):
        self.objects = []
        # self.object_base_pairs = []
        self.axiom = lsystem.lsystem.ProductionRule("", "")
        self.rules = []

        self.instances = 1
        self.seed = 0
        self.min_iterations = 1
        self.max_iterations = 1
        self.angle = math.radians(25)
        self.length = 1.0
        self.radius = 0.1
        self.expansion = 1.1
        self.shrinkage = 0.9
        self.fat = 1.2
        self.slinkage = 0.8
        self.animate = False
        self.frame_delta = 5

    def set_axiom(self, axiom_str):
        self.axiom = lsystem.lsystem.ProductionRule("", axiom_str)

    def set_rule(self, pattern, result, condition=None, index=None):
        if index is None:
            self.add_rule(pattern, result, condition)
        new_rule = lsystem.lsystem.ProductionRule(pattern, result, condition)
        self.rules[index] = new_rule

    def add_rule(self, pattern, result, condition=None):
        new_rule = lsystem.lsystem.ProductionRule(pattern, result, condition)
        self.rules.append(new_rule)

    def exec(self,
             context=None,
             instances=None,
             seed=None,
             min_iterations=None,
             max_iterations=None,
             angle=None,
             length=None,
             radius=None,
             expansion=None,
             shrinkage=None,
             fat=None,
             slinkage=None,
             animate=None,
             frame_delta=None):
        if context is None:
            context = bpy.context
        if instances is not None:
            self.instances = instances
        if seed is not None:
            self.seed = seed
        if min_iterations is not None:
            self.min_iterations = min_iterations
        if max_iterations is not None:
            self.max_iterations = max_iterations
        if angle is not None:
            self.angle = angle
        if length is not None:
            self.length = length
        if radius is not None:
            self.radius = radius
        if expansion is not None:
            self.expansion = expansion
        if shrinkage is not None:
            self.shrinkage = shrinkage
        if fat is not None:
            self.fat = fat
        if slinkage is not None:
            self.slinkage = slinkage
        if animate is not None:
            self.animate = animate
        if frame_delta is not None:
            self.frame_delta = frame_delta

        self.delete()

        self.objects = execute(context,
                self.axiom,
                self.rules,
                self.instances,
                self.seed,
                self.min_iterations,
                self.max_iterations,
                self.angle,
                self.length,
                self.radius,
                self.expansion,
                self.shrinkage,
                self.fat,
                self.slinkage,
                self.animate,
                self.frame_delta,
                (0.0, 0.0, 1.0))

    def select(self):
        #deselect currently selected objects
        for ob in bpy.context.selected_objects:
            ob.select = False

        #select objects belonging to this LSystem
        for ob in self.objects:
            ob.select = True

        # for obj_base_pair in self.object_base_pairs:
        #     base = obj_base_pair[1]
        #     base.select = True
        # if self.object_base_pairs:
        #     bpy.context.scene.objects.active = self.object_base_pairs[-1][0]

    def delete(self):
        old_selected = self.get_selection()

        self.select()
        bpy.ops.object.delete()

        for ob in old_selected:
            ob.select = True

    def get_selection(self):
        selected = []
        for ob in bpy.context.selected_objects:
            selected.append(ob)
        return selected

    def __str__(self):
        str = "{}\n".format(self.axiom)
        for rule in self.rules:
            str += "{}\n".format(rule)
        return str


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
            frame_delta=5,
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
    return exec_turtle(context, lsys, instances, min_iterations, iterations, animate, turtle, frame_delta)


def exec_turtle(context, lsys, instances, min_iterations, max_iterations, animate, turtle, frame_delta=5):
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
        animate_inst_list(inst_list, frame_delta)

    objects = []
    for iter_list in inst_list:
        for object_base_pairs in iter_list:
            for obj_base_pair in object_base_pairs:
                base = obj_base_pair[1]
                base.select = True
                objects.append(obj_base_pair[0])
            context.scene.objects.active = object_base_pairs[-1][0]
    return objects


def animate_inst_list(inst_list, frame_delta=5):
    for iter_list in inst_list:
        animate_iter_list(iter_list, frame_delta)


def animate_iter_list(iter_list, frame_delta=5):
    frame = 0
    for object_base_pair_list in iter_list:
        for object_base_pair in object_base_pair_list:
            object = object_base_pair[0]
            object.hide = True
            object.keyframe_insert(data_path="hide", index=-1, frame=0)
            object.hide_render = True
            object.keyframe_insert(data_path="hide_render", index=-1, frame=0)
            object.hide = False
            object.keyframe_insert(data_path="hide", index=-1, frame=frame)
            object.hide_render = False
            object.keyframe_insert(data_path="hide_render", index=-1, frame=frame)
            object.hide = True
            object.keyframe_insert(data_path="hide", index=-1, frame=frame+frame_delta)
            object.hide_render = True
            object.keyframe_insert(data_path="hide_render", index=-1, frame=frame + frame_delta)
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
            obj = obj_base_pairs[0][0]
            obj.location = new_positions[0]
            obj.parent = ob


def grid(inst_list, move_x=True):
    cursor_loc = bpy.context.scene.cursor_location
    y = 0
    for iter_list in inst_list:
        x = 0
        max_ydim = 0
        for obj_base_pairs in iter_list:
            obj = obj_base_pairs[0][0]
            obj.location = (cursor_loc.x+x, cursor_loc.y+y, cursor_loc.z)
            if move_x:
                x += obj.dimensions.x
            if obj.dimensions.y > max_ydim:
                max_ydim = obj.dimensions.y
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
