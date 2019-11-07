
import lsystem.lsystem
import lsystem.turtle
import lsystem.util

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
        self.constants = {}
        self.replacements = None
        self.interpretations = {}

        self.tropism_vector = (0,0,0)
        self.tropism_force = 0

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

    def define(self, constant, value):
        self.constants[constant] = value

    def replace(self, pattern, result, condition=None):
        new_rule = lsystem.lsystem.ProductionRule(pattern, result, condition)
        if self.replacements is None:
            self.replacements = []
        self.replacements.append(new_rule)

    def set_tropism(self, vector, force):
        self.tropism_vector = vector
        self.tropism_vector.normalize()
        self.tropism_force = force

    def set_interpretation(self, symbol, function):
        self.interpretations[symbol] = function

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
            self.angle = math.radians(angle)
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

        axiom = self.axiom.copy_replace(self.constants)
        rules = []
        for rule in self.rules:
            rules.append(rule.copy_replace(self.constants))

        self.objects = execute(context,
                               axiom,
                               rules,
                               self.replacements,
                               instances=self.instances,
                               seed=self.seed,
                               min_iterations=self.min_iterations,
                               max_iterations=self.max_iterations,
                               angle=self.angle,
                               length=self.length,
                               radius=self.radius,
                               expansion=self.expansion,
                               shrinkage=self.shrinkage,
                               fat=self.fat,
                               slinkage=self.slinkage,
                               animate=self.animate,
                               frame_delta=self.frame_delta,
                               normal=(0.0, 0.0, 1.0),
                               tropism_vector=self.tropism_vector,
                               tropism_force=self.tropism_force,
                               interpretations=self.interpretations)

    def select(self):
        if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
            # This doesn't work for objects that aren't visible in the current keyframe
            for ob in bpy.context.selected_objects:
                ob.select_set(False)
            for ob in self.objects:
                ob.select_set(True)
        else:
            # deselect currently selected objects
            for ob in bpy.context.selected_objects:
                ob.select = False

            # select objects belonging to this LSystem
            for ob in self.objects:
                ob.select = True

    def delete(self):
        old_selected = self.get_selection()

        if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
            for obj in self.objects:
                try:
                    bpy.data.objects.remove(obj, do_unlink=True)
                except ReferenceError:
                    # object already deleted, ignore
                    pass
        else:
            self.select()
            try:
                bpy.ops.object.delete()
            except ReferenceError:
                # lsystem objects already deleted, ignore
                pass

        if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
            for ob in old_selected:
                if ob not in self.objects:
                    ob.select_set(True)
        else:
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


class PosInfo:
    def __init__(self, position, normal, obj, seed, iterations):
        self.position = position
        self.normal = normal
        self.obj = obj
        self.seed = seed
        self.iterations = iterations


def execute(context,
            axiom,
            rules,
            replacements,
            instances=1,
            seed=0,
            min_iterations=1,
            max_iterations=1,
            angle=math.radians(25),
            length=1.0,
            radius=0.1,
            expansion=1.1,
            shrinkage=0.9,
            fat=1.2,
            slinkage=0.8,
            animate=False,
            frame_delta=5,
            normal=(0.0, 0.0, 1.0),
            tropism_vector=(0.0, 0.0, -1.0),
            tropism_force=0.0,
            interpretations=None):
    turtle = lsystem.turtle.Turtle(seed)
    turtle.set_angle(angle)
    turtle.set_length(length)
    turtle.set_radius(radius)
    turtle.set_expansion(expansion)
    turtle.set_shrinkage(shrinkage)
    turtle.set_fat(fat)
    turtle.set_slinkage(slinkage)
    turtle.set_direction(mathutils.Vector((normal[0], normal[1], normal[2])))
    turtle.set_tropism(tropism_vector, tropism_force)
    if interpretations is not None:
        for key in interpretations:
            turtle.set_interpretation(key, interpretations[key])

    lsys = lsystem.lsystem.LSystem(axiom, rules, replacements)
    return exec_turtle(context, lsys, instances, min_iterations, max_iterations, animate, turtle, frame_delta)


def exec_turtle(context, lsys, instances, min_iterations, max_iterations, animate, turtle, frame_delta=5):
    # Need to call scene.update for ray_cast method.
    # See http://blender.stackexchange.com/questions/40429/error-object-has-no-mesh-data-to-be-used-for-ray-casting
    if hasattr(bpy.app, "version") and bpy.app.version < (2, 80):
        bpy.context.scene.update()

    rmax_iter = max_iterations+1
    if max_iterations <= min_iterations:
        rmax_iter = min_iterations+1

    pos_info_list = get_pos_info(instances, min_iterations, rmax_iter, turtle.seed, animate)

    inst_list = []
    seed = turtle.seed

    pos_info_index = 0
    for instance in range(0, instances):
        iter_list = []
        for iterations in range(min_iterations, rmax_iter):
            new_turtle = copy.deepcopy(turtle)
            new_turtle.seed = seed
            pos_info = None
            if pos_info_list:
                pos_info = pos_info_list[pos_info_index]
            if pos_info:
                new_turtle.set_direction(pos_info.normal)
                new_turtle.seed = pos_info.seed
            object_base_pairs = run_once(context, new_turtle, instance, lsys, iterations)
            if pos_info:
                obj = object_base_pairs[0][0]
                obj.location = pos_info.position
                obj.parent = pos_info.obj
            iter_list.append(object_base_pairs)
            pos_info_index += 1
        seed += 1
        inst_list.append(iter_list)

    if not pos_info_list:
        grid(inst_list, not animate)

    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        for ob in context.scene.objects:
            ob.select_set(False)
    else:
        for ob in context.scene.objects:
            ob.select = False

    if animate:
        animate_inst_list(inst_list, frame_delta)

    objects = []
    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        for iter_list in inst_list:
            for object_base_pairs in iter_list:
                for obj_base_pair in object_base_pairs:
                    obj = obj_base_pair[0]
                    obj.select_set(True)
                    objects.append(obj)
        context.view_layer.objects.active = objects[-1]
    else:
        for iter_list in inst_list:
            for object_base_pairs in iter_list:
                for obj_base_pair in object_base_pairs:
                    base = obj_base_pair[1]
                    base.select = True  # no bases in 2.80
                    objects.append(obj_base_pair[0])
                context.scene.objects.active = object_base_pairs[-1][0]  # this won't work in 2.80
    return objects


def get_pos_info(instances, min_iterations, max_iterations, seed, animate):
    selected = bpy.context.selected_objects
    print("selected: " + str(selected))
    if not selected:
        return None

    faces = get_selected_faces(selected)

    pos_info_list = []
    current_seed = seed
    if animate:
        for instances in range(0, instances):
            face, ob = random.choice(faces)
            new_positions = bpy_extras.mesh_utils.triangle_random_points(1, [face])
            pos = new_positions[0]
            for iter in range(min_iterations, max_iterations):
                pos_info = PosInfo(pos, face.normal, ob, current_seed, iter)
                pos_info_list.append(pos_info)
            current_seed += 1
    else:
        for instances in range(0, instances):
            for iter in range(min_iterations, max_iterations):
                face, ob = random.choice(faces)
                if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
                    new_positions = bpy_extras.mesh_utils.triangle_random_points(1, [face])
                else:
                    new_positions = bpy_extras.mesh_utils.face_random_points(1, [face])
                pos_info = PosInfo(new_positions[0], face.normal, ob, current_seed, iter)
                pos_info_list.append(pos_info)
            current_seed += 1
    return pos_info_list


def animate_inst_list(inst_list, frame_delta=5):
    for iter_list in inst_list:
        animate_iter_list(iter_list, frame_delta)


def animate_iter_list(iter_list, frame_delta=5):
    frame = 0
    for object_base_pair_list in iter_list:
        for object_base_pair in object_base_pair_list:
            obj = object_base_pair[0]
            lsystem.util.hide_render(obj, True, 0)
            lsystem.util.hide_render(obj, False, frame)
            lsystem.util.hide_render(obj, True, frame+frame_delta)
        frame += frame_delta

    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        bpy.data.scenes["Scene"].frame_end = frame


def get_selected_faces(objects):
    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        polygons = []
        for ob in objects:
            me = ob.data
            # me.update(calc_loop_triangles=True)
            me.calc_loop_triangles()
            selected_tris = [(t, ob) for t in me.loop_triangles] # just get all faces for now
            polygons.extend(selected_tris)
        return polygons

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
    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        cursor_loc = bpy.context.scene.cursor.location
    else:
        cursor_loc = bpy.context.scene.cursor_location
    y = 0
    for iter_list in inst_list:
        x = 0
        max_ydim = 0
        for obj_base_pairs in iter_list:
            obj = obj_base_pairs[0][0]
            dx = get_max_x(obj_base_pairs)
            dy = get_max_y(obj_base_pairs)
            obj.location = (cursor_loc.x+x, cursor_loc.y+y, cursor_loc.z)
            if move_x:
                x += dx
            if obj.dimensions.y > max_ydim:
                max_ydim += dy
        y += max_ydim


def get_max_x(obj_base_pairs):
    x = 1.0
    for obj, base in obj_base_pairs:
        cx = obj.location.x + obj.dimensions.x
        if cx > x:
            x = cx
    return x


def get_max_y(obj_base_pairs):
    y = 1.0
    for obj, base in obj_base_pairs:
        cy = obj.location.y + obj.dimensions.y
        if cy > y:
            y = cy
    return y


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


def print_time(start_time, message):
    elapsed = time.time() - start_time
    print("%.5fs: %s" % (elapsed, message))
