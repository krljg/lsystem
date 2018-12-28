import mathutils
from . import pen
from math import radians
from math import pi
import random
import bpy
import bmesh


class BlObject:
    def __init__(self, radius):
        self.stack = []
        self.radius = radius
        self.pen = pen.CylPen(4)
        self.materials = []
        self.bmesh = bmesh.new()
        self.mesh = bpy.data.meshes.new('lsystem')
        self.object = bpy.data.objects.new(self.mesh.name, self.mesh)

    def set_pen(self, name, transform):
        self.end_mesh_part()

        if name == "pol":
            self.pen = pen.PolPen()
        elif name == "edge":
            self.pen = pen.EdgePen(False, False)
        elif name == "skin":
            self.pen = pen.EdgePen(True, False)
        elif name == "subsurf":
            self.pen = pen.EdgePen(True, True)
        elif name == "curve":
            self.pen = pen.CurvePen()
        elif name == "line":
            # self.pen = pen.LinePen()
            self.pen = pen.BLinePen()
        elif name == "triangle":
            self.pen = pen.CylPen(3)
        elif name == "quad":
            self.pen = pen.BCylPen(4)
        elif name.startswith("cyl"):
            try:
                vertices = int(name[3:])
                self.pen = pen.CylPen(vertices)
            except Exception:
                print("Invalid cyl '"+name+"'")
        else:
            print("No pen with name '"+name+"' found")
            return
        self.start_new_mesh_part(transform)

    def set_material(self, name):
        if name not in self.materials:
            self.materials.append(name)
            mat = bpy.data.materials.get(name)
            self.mesh.materials.append(mat)
        index = self.materials.index(name)
        self.pen.set_material(index)

    def scale_radius(self, scale):
        self.pen.set_radius(self.pen.get_radius() * scale)

    def set_radius(self, radius):
        self.pen.set_radius(radius)

    def get_radius(self):
        return self.pen.get_radius()

    def push(self, transform):
        t = (transform, self.pen)
        self.pen.start_branch()
        self.stack.append(t)

    def pop(self):
        if not self.stack:
            return None
        transform, pen = self.stack.pop()
        if self.pen is not pen:
            self.end_mesh_part()
        self.pen = pen
        mesh = self.pen.end_branch()
        if mesh is not None:
            self.bmesh.from_mesh(mesh)
        return transform

    def is_new_mesh_part(self):
        return self.last_indices is None

    def start_new_mesh_part(self, transform):
        self.end_mesh_part()
        self.pen.set_radius(self.radius)
        self.pen.start(transform)

    def end_mesh_part(self):
        new_mesh = self.pen.end() # pen.end() will return a mesh if it's really the end and not just a branch closing
        if new_mesh is not None:
            self.bmesh.from_mesh(new_mesh)

    def get_last_indices(self):
        return self.last_indices

    def set_last_indices(self, indices):
        self.last_indices = indices

    def finish(self, context):
        new_mesh = self.pen.end()
        if new_mesh is not None:
            self.bmesh.from_mesh(new_mesh)

        # me = bpy.data.meshes.new("lsystem")
        self.bmesh.to_mesh(self.mesh)
        base = context.scene.objects.link(self.object)
        return self.object, base

    def move_and_draw(self, transform):
        self.pen.move_and_draw(transform)

    def move(self, transform):
        self.pen.move(transform)


# A turtle has three attributes: location, orientation, a pen
class Turtle:
    def __init__(self, seed):
        self.radius = 0.1
        self.angle = radians(25.7)
        self.base_angle = self.angle
        self.length = 1.0
        self.expansion = 1.1
        self.shrinkage = 0.9
        self.fat = 1.2
        self.slinkage = 0.8
        self.transform = mathutils.Matrix.Identity(4)
        self.direction = (0.0, 0.0, 1.0)
        self.object_stack = []
        self.seed = seed

        self.sym_func_map = {}
        self.set_interpretation('+', rot_y)
        self.set_interpretation('-', rot_y_neg)
        self.set_interpretation('/', rot_x)
        self.set_interpretation('\\', rot_x_neg)
        self.set_interpretation('<', rot_z)
        self.set_interpretation('>', rot_z_neg)
        self.set_interpretation('$', rotate_upright)
        self.set_interpretation('&', random_angle)
        self.set_interpretation('#', fatten)
        self.set_interpretation('%', slink)
        self.set_interpretation('¤', set_current_radius)
        self.set_interpretation('~', copy_object)
        self.set_interpretation('s', scale)

    def set_radius(self, radius):
        self.radius = radius

    def set_angle(self, angle):
        self.angle = angle
        self.base_angle = angle

    def set_length(self, length):
        self.length = length

    def set_expansion(self, expansion):
        self.expansion = expansion

    def set_shrinkage(self, shrinkage):
        self.shrinkage = shrinkage

    def set_fat(self, fat):
        self.fat = fat

    def set_slinkage(self, slinkage):
        self.slinkage = slinkage

    def set_direction(self, direction):
        self.direction = direction
        quat = direction.rotation_difference(mathutils.Vector((0.0, 0.0, 1.0)))
        rot_matrix = quat.to_matrix().to_4x4()
        self.transform = self.transform * rot_matrix

    def rotate(self, angle, vector):
        self.transform = self.transform * mathutils.Matrix.Rotation(angle, 4, vector)
        self.angle = self.base_angle

    def rotate_y(self, angle):
        self.rotate(angle, mathutils.Vector((0.0, 1.0, 0.0)))

    def rotate_x(self, angle):
        self.rotate(angle, mathutils.Vector((1.0, 0.0, 0.0)))

    def rotate_z(self, angle):
        self.rotate(angle, mathutils.Vector((0.0, 0.0, 1.0)))

    def rotate_upright(self):
        loc, rot, sca = self.transform.decompose()
        sm = mathutils.Matrix()
        sm[0][0] = sca[0]
        sm[1][1] = sca[1]
        sm[2][2] = sca[2]
        sm[3][3] = 1.0
        self.transform = mathutils.Matrix.Translation(loc) * sm

    def scale_radius(self, scale, bl_obj):
        bl_obj.set_radius(bl_obj.get_radius()*scale)

    def set_current_radius(self, radius, bl_obj):
        bl_obj.set_radius(radius)

    def scale(self, scaling, bl_obj):
        self.transform = self.transform * mathutils.Matrix.Scale(scaling, 4)
        self.scale_radius(scaling, bl_obj)

    def forward(self, length):
        vec = (0.0, 0.0, length)
        self.transform = self.transform * mathutils.Matrix.Translation(vec)

    def copy_object(self, object_name):
        if object_name not in bpy.data.objects:
            print("Invalid object name '"+object_name+"'")
            return
        obj = bpy.data.objects[object_name]
        copy = obj.copy()
        copy.location = self.transform * mathutils.Vector((0.0, 0.0, 0.0))
        copy.rotation_euler = self.transform.to_euler()
        # todo: scaling?
        bpy.context.scene.objects.link(copy)

    def set_interpretation(self, symbol, function):
        self.sym_func_map[symbol] = function

# +,- rotate around the right axis (y-axis)
# /,\ rotate around the up axis (x-axis)
# <,> rotate around the forward axis (z-axis)
# [,] push or pop state
# &   rotate random amount
# !,@ expand or shrink the size of a forward step (a branch segment or leaf)
# #,% fatten or slink the radius of a branch
# ¤   set radius
# F   produce an edge ( a branch segment)
# {,} Start and end a blender object
# ~   Duplicate an existing blender object and add
# p   change pens
# m   set material
# s   scale
# $   rotate the turtle to vertical

    def interpret(self, input, context):
        # print("seed: {}".format(self.seed))
        random.seed(self.seed)
        obj_base_pairs = []
        bl_obj = BlObject(self.radius)
        bl_obj.start_new_mesh_part(self.transform)

        pos = 0
        tot_len = len(input)
        parameters = []
        while pos < tot_len:
            c = input[pos]
            # print("c["+str(i)+"] = "+c)
            if pos+2 < tot_len and input[pos+1] == '(':
                parameters, pos = self.scan_parameters(input, pos)
            else:
                pos += 1

            self.exec_sym(bl_obj, obj_base_pairs, context, c, parameters)

        obj, base = bl_obj.finish(context)
        obj_base_pairs.append((obj, base))
        return obj_base_pairs

    @staticmethod
    def scan_parameters(string, pos):
        start = pos + 2
        end = start
        tot_len = len(string)
        while end < tot_len:
            if string[end] == ')':
                break
            end += 1
        val_str = string[start:end]
        pos = end + 1
        parameters = val_str.split(",")
        return parameters, pos

    def exec_sym(self, bl_obj, obj_base_pairs, context, sym, parameters):
        if sym == '[':
            bl_obj.push(self.transform)
        elif sym == ']':
            t = bl_obj.pop()
            if t is not None:
                self.transform = t
        elif sym == 'F':
            val = to_float_array(parameters, self.length)
            self.forward(val)
            bl_obj.move_and_draw(self.transform)
        elif sym == 'f':
            val = to_float_array(parameters, self.length)
            self.forward(val)
            bl_obj.move(self.transform)
        elif sym == '{':
            bl_obj.push(self.transform)
            self.object_stack.append(bl_obj)
            bl_obj = BlObject(self.radius)
            bl_obj.start_new_mesh_part(self.transform)
            pass
        elif sym == '}':
            obj, base = bl_obj.finish(context)
            obj_base_pairs.append((obj, base))
            bl_obj = self.object_stack.pop()
            t = bl_obj.pop()
            if t is not None:
                self.transform = t
            pass
        elif sym == 'p':
            if parameters:
                bl_obj.set_pen(parameters[0], self.transform)
        elif sym == 'm':
            if parameters:
                bl_obj.set_material(parameters[0])
        elif sym in self.sym_func_map:
            func = self.sym_func_map[sym]
            func(self, parameters, bl_obj)


def to_float(string, default):
    try:
        return float(string)
    except:
        # Not a float, fallback to default
        return default


def to_float_array(array, default):
    if len(array) > 0:
        return to_float(array[0], default)
    return default


def rot_y(turtle, parameters, bl_obj):
    val = to_float_array(parameters, None)
    if val is None:
        val = turtle.angle
    else:
        val = radians(val)

    turtle.rotate_y(val)


def rot_y_neg(turtle, parameters, bl_obj):
    val = to_float_array(parameters, None)
    if val is None:
        val = -turtle.angle
    else:
        val = radians(-val)

    turtle.rotate_y(val)


def rot_x(turtle, parameters, bl_obj):
    val = to_float_array(parameters, None)
    if val is None:
        val = turtle.angle
    else:
        val = radians(val)

    turtle.rotate_x(val)


def rot_x_neg(turtle, parameters, bl_obj):
    val = to_float_array(parameters, None)
    if val is None:
        val = -turtle.angle
    else:
        val = radians(-val)

    turtle.rotate_x(val)


def rot_z(turtle, parameters, bl_obj):
    val = to_float_array(parameters, None)
    if val is None:
        val = turtle.angle
    else:
        val = radians(val)

    turtle.rotate_z(val)


def rot_z_neg(turtle, parameters, bl_obj):
    val = to_float_array(parameters, None)
    if val is None:
        val = -turtle.angle
    else:
        val = radians(-val)

    turtle.rotate_z(val)


def rotate_upright(turtle, parameters, bl_obj):
    turtle.rotate_upright()


def random_angle(turtle, parameters, bl_obj):
    turtle.angle = random.random() * 2 * pi


def fatten(turtle, parameters, bl_obj):
    val = to_float_array(parameters, turtle.fat)
    turtle.scale_radius(val, bl_obj)


def slink(turtle, parameters, bl_obj):
    val = to_float_array(parameters, turtle.slinkage)
    turtle.scale_radius(val, bl_obj)


def set_current_radius(turtle, parameters, bl_obj):
    val = to_float_array(parameters, 1.0)
    turtle.set_current_radius(val, bl_obj)


def scale(turtle, parameters, bl_obj):
    val = to_float_array(parameters, turtle.scale)
    turtle.scale(val)


def copy_object(turtle, parameters, bl_obj):
    if len(parameters) == 0:
        print("~ operator has no value")
        return
    turtle.copy_object(parameters[0])
