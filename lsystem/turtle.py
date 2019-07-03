import mathutils
from . import pen
from . import util
from math import radians
from math import pi
from math import acos
import random
import bpy
import bmesh


class BlObject:
    def __init__(self, radius, name="lsystem"):
        self.stack = []
        self.radius = radius
        self.pen = pen.CylPen(4)
        self.materials = []
        self.bmesh = bmesh.new()
        self.mesh = bpy.data.meshes.new(name)
        self.object = bpy.data.objects.new(self.mesh.name, self.mesh)

    def set_pen(self, name, transform):
        self.end_mesh_part()

        if name == "surface":
            self.pen = pen.SurfacePen()
        elif name == "pol":
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
        elif name == "vert":
            self.pen = pen.VertexPen()
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
        new_mesh = self.pen.end()  # pen.end() will return a mesh if it's really the end and not just a branch closing
        if new_mesh is not None:
            self.bmesh.from_mesh(new_mesh)

    def get_last_indices(self):
        return self.last_indices

    def set_last_indices(self, indices):
        self.last_indices = indices

    def finish(self, context):
        print("turtle.finish")
        print(str(self.pen))
        new_mesh = self.pen.end()
        print(str(new_mesh))
        if new_mesh is not None:
            self.bmesh.from_mesh(new_mesh)

        # me = bpy.data.meshes.new("lsystem")
        self.bmesh.to_mesh(self.mesh)
        base = util.link(context, self.object)

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
        self.length = 1.0
        self.expansion = 1.1
        self.shrinkage = 0.9
        self.fat = 1.2
        self.slinkage = 0.8
        self.transform = mathutils.Matrix.Identity(4)
        self.direction = (0.0, 0.0, 1.0)
        self.object_stack = []
        self.seed = seed
        self.tropism_vector = (0.0, 0.0, 0.0)
        self.tropism_force = 0

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
        self.set_interpretation('p', set_pen)
        self.set_interpretation('m', set_material)
        self.set_interpretation(':', start_face)
        self.set_interpretation(';', end_face)

    def set_radius(self, radius):
        self.radius = radius

    def set_angle(self, angle):
        self.angle = angle

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
        up = mathutils.Vector((0.0, 0.0, 1.0))
        old_direction = util.matmul(self.transform, up)
        quat = old_direction.rotation_difference(direction)
        rot_matrix = quat.to_matrix().to_4x4()
        self.transform = util.matmul(self.transform, rot_matrix)

    def rotate(self, angle, vector):
        self.transform = util.matmul(self.transform, mathutils.Matrix.Rotation(angle, 4, vector))

    def rotate_y(self, angle):
        self.rotate(angle, mathutils.Vector((0.0, 1.0, 0.0)))

    def rotate_x(self, angle):
        self.rotate(angle, mathutils.Vector((1.0, 0.0, 0.0)))

    def rotate_z(self, angle):
        self.rotate(angle, mathutils.Vector((0.0, 0.0, 1.0)))

    def rotate_upright(self):
        loc, rot, sca = self.transform.decompose()

        # rot_mat = rot.to_matrix()
        # y = rot_mat[2][2]
        # x = rot_mat[2][1]
        # print("x {} y {}".format(x,y))
        # roll_angle = atan2(y,x)
        # print("roll {}".format(roll_angle))
        # self.rotate_z(-roll_angle)

        up = mathutils.Vector((0.0, 0.0, 1.0))
        # up = mathutils.Vector((0.0, 1.0, 0.0))
        direction = util.matmul(rot, mathutils.Vector((0.0, 0.0, 1.0)))
        old_left = util.matmul(rot, mathutils.Vector((-1.0, 0.0, 0.0)))
        new_left = direction.cross(up)
        new_left.normalize()

        # q = old_left.rotation_difference(new_left)
        # angle = q.angle
        # self.rotate_z(angle)

        scalar = util.matmul(old_left, new_left)
        print("direction {} old_left {} new_left {} scalar {}".format(direction, old_left, new_left, scalar))
        if scalar >= 1.0:
            return  # lines are parallel
        # if 0.000001 > scalar > -0.000001:
        #     return
        # if scalar < -1.0:
        #     return

        angle = acos(scalar)  # angle is between 0 and pi
        new_rot = util.matmul(rot.to_matrix(), mathutils.Matrix.Rotation(angle, 3, mathutils.Vector(0.0, 0.0, 1.0)))
        test_up = util.matmul(new_rot, mathutils.Vector((0.0, 1.0, 0.0)))
        new_up = direction.cross(new_left)
        print("angle {}".format(angle))

        if util.matmul(test_up, new_up) < 0:
            angle = -angle
        print("test up {} new_up {} angle {}".format(test_up, new_up, angle))
        self.rotate_z(angle)

    def scale_radius(self, scale, bl_obj):
        bl_obj.set_radius(bl_obj.get_radius()*scale)

    def set_current_radius(self, radius, bl_obj):
        bl_obj.set_radius(radius)

    def set_tropism(self, tropism_vector, tropism_force):
        self.tropism_vector = tropism_vector
        self.tropism_force = tropism_force

    def scale(self, scaling, bl_obj):
        self.transform = self.transform * mathutils.Matrix.Scale(scaling, 4)
        self.scale_radius(scaling, bl_obj)

    def forward(self, length):
        vec = (0.0, 0.0, length)
        self.transform = util.matmul(self.transform, mathutils.Matrix.Translation(vec))
        if self.tropism_force > 0.0:
            loc, rot, sca = self.transform.decompose()
            heading = util.matmul(rot, mathutils.Vector((0.0, 0.0, 1.0)))
            tvec = heading.cross(self.tropism_vector)
            tforce = util.matmul(tvec.length, self.tropism_force)
            # print("heading {} tropism {} force {} tvec {}".format(heading, self.tropism_vector, self.tropism_force, tvec))
            self.rotate(tforce, tvec)

    def copy_object(self, object_name, bl_obj, obj_base_pairs):
        if object_name not in bpy.data.objects:
            print("Invalid object name '"+object_name+"'")
            return
        obj = bpy.data.objects[object_name]
        copy = obj.copy()
        copy.locaton = util.matmul(self.transform, mathutils.Vector(0.0, 0.0, 0.0))
        copy.rotation_euler = self.transform.to_euler()
        # todo: scaling?
        base = bpy.context.scene.objects.link(copy)
        copy.parent = bl_obj.object
        obj_base_pairs.append((copy, base))

    def set_interpretation(self, symbol, function):
        self.sym_func_map[symbol] = function

    def interpret(self, input, context):
        # print("seed: {}".format(self.seed))
        random.seed(self.seed)
        obj_base_pairs = []
        bl_obj = BlObject(self.radius)
        bl_obj.start_new_mesh_part(self.transform)
        self.object_stack.append(bl_obj)

        pos = 0
        tot_len = len(input)
        while pos < tot_len:
            parameters = []
            c = input[pos]
            # print("c["+str(i)+"] = "+c)
            if pos+2 < tot_len and input[pos+1] == '(':
                parameters, pos = self.scan_parameters(input, pos)
            else:
                pos += 1

            self.exec_sym(obj_base_pairs, context, c, parameters)

        obj, base = bl_obj.finish(context)
        obj_base_pairs.insert(0, (obj, base))
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
        parameters = val_str.split(",")
        return parameters, end+1

    def exec_sym(self, obj_base_pairs, context, sym, parameters):
        bl_obj = self.object_stack[-1]
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
            bl_obj = BlObject(self.radius)
            self.object_stack.append(bl_obj)
            # bl_obj = BlObject(self.radius)
            bl_obj.start_new_mesh_part(self.transform)
        elif sym == '}':
            obj, base = bl_obj.finish(context)
            obj_base_pairs.append((obj, base))
            self.object_stack.pop()
            bl_obj = self.object_stack[-1]
            t = bl_obj.pop()
            if t is not None:
                self.transform = t
            obj.parent = bl_obj.object

        elif sym in self.sym_func_map:
            func = self.sym_func_map[sym]
            func(self, parameters, bl_obj, obj_base_pairs)


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


def rot_y(turtle, parameters, bl_obj, obj_base_pairs):
    val = to_float_array(parameters, None)
    if val is None:
        val = turtle.angle
    else:
        val = radians(val)

    turtle.rotate_y(val)


def rot_y_neg(turtle, parameters, bl_obj, obj_base_pairs):
    val = to_float_array(parameters, None)
    if val is None:
        val = -turtle.angle
    else:
        val = radians(-val)

    turtle.rotate_y(val)


def rot_x(turtle, parameters, bl_obj, obj_base_pairs):
    val = to_float_array(parameters, None)
    if val is None:
        val = turtle.angle
    else:
        val = radians(val)

    turtle.rotate_x(val)


def rot_x_neg(turtle, parameters, bl_obj, obj_base_pairs):
    val = to_float_array(parameters, None)
    if val is None:
        val = -turtle.angle
    else:
        val = radians(-val)

    turtle.rotate_x(val)


def rot_z(turtle, parameters, bl_obj, obj_base_pairs):
    val = to_float_array(parameters, None)
    if val is None:
        val = turtle.angle
    else:
        val = radians(val)

    turtle.rotate_z(val)


def rot_z_neg(turtle, parameters, bl_obj, obj_base_pairs):
    val = to_float_array(parameters, None)
    if val is None:
        val = -turtle.angle
    else:
        val = radians(-val)

    turtle.rotate_z(val)


def rotate_upright(turtle, parameters, bl_obj, obj_base_pairs):
    turtle.rotate_upright()


def random_angle(turtle, parameters, bl_obj, obj_base_pairs):
    turtle.angle = random.random() * 2 * pi


def fatten(turtle, parameters, bl_obj, obj_base_pairs):
    val = to_float_array(parameters, turtle.fat)
    turtle.scale_radius(val, bl_obj)


def slink(turtle, parameters, bl_obj, obj_base_pairs):
    val = to_float_array(parameters, turtle.slinkage)
    turtle.scale_radius(val, bl_obj)


def set_current_radius(turtle, parameters, bl_obj, obj_base_pairs):
    val = to_float_array(parameters, 1.0)
    turtle.set_current_radius(val, bl_obj)


def scale(turtle, parameters, bl_obj, obj_base_pairs):
    val = to_float_array(parameters, turtle.scale)
    turtle.scale(val, bl_obj)


def copy_object(turtle, parameters, bl_obj, obj_base_pairs):
    if len(parameters) == 0:
        print("~ operator has no value")
        return
    turtle.copy_object(parameters[0], bl_obj, obj_base_pairs)


def set_pen(turtle, parameters, bl_obj, obj_base_pairs):
    if parameters:
        bl_obj.set_pen(parameters[0], turtle.transform)


def set_material(turtle, parameters, bl_obj, obj_base_pairs):
    if parameters:
        bl_obj.set_material(parameters[0])


def start_face(turtle, parameters, bl_obj, obj_base_pairs):
    bl_obj.pen.start_face()


def end_face(turtle, parameters, bl_obj, obj_base_pairs):
    bl_obj.pen.end_face()
