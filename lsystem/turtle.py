import mathutils
from . import pen
from math import radians
from math import pi
import random
import bpy


class BlObject:
    def __init__(self, radius):
        self.vertices = []
        self.tmp_vertices = []
        self.edges = []
        self.quads = []
        self.last_indices = None
        self.radius = radius
        self.pen = pen.CylPen(4)
        self.material = None

    def set_pen(self, name, transform):
        if name == "line":
            self.pen = pen.LinePen()
        elif name == "triangle":
            self.pen = pen.CylPen(3)
        elif name == "quad":
            self.pen = pen.CylPen(4)
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
        self.material = name

    def scale_radius(self, scale):
        self.radius *= scale

    def set_radius(self, radius):
        self.radius = radius

    def get_radius(self):
        return self.radius

    def is_new_mesh_part(self):
        return self.last_indices is None

    def start_new_mesh_part(self, transform):
        vertices = self.pen.create_vertices(self.radius)
        self.tmp_vertices = []
        for v in vertices:
            new_v = transform * v
            self.tmp_vertices.append(new_v)

        self.last_indices = None

    def get_last_indices(self):
        return self.last_indices

    def set_last_indices(self, indices):
        self.last_indices = indices

    def new_vertices(self, transform):
        if self.is_new_mesh_part():
            start = len(self.vertices)
            stop = start + len(self.tmp_vertices)
            self.last_indices = list(range(start, stop))
            self.vertices.extend(self.tmp_vertices)

        new_vertices = self.pen.create_vertices(self.radius)
        transformed_vertices = []
        for v in new_vertices:
            v = transform * v
            transformed_vertices.append(v)

        new_indices = list(range(len(self.vertices), len(self.vertices) + len(transformed_vertices)))
        self.vertices.extend(transformed_vertices)

        new_quads = self.pen.connect(self.last_indices, new_indices)
        self.quads.extend(new_quads)
        self.last_indices = new_indices

    def finish(self, context):
        return self.new_object(self.vertices, self.edges, self.quads, context)

    def new_object(self, vertices, edges, quads, context):
        mesh = bpy.data.meshes.new('lsystem')
        mesh.from_pydata(vertices, edges, quads)
        mesh.update()
        obj, base = self.add_obj(mesh, context)
        return obj, base

    def add_obj(self, obdata, context):
        scene = context.scene
        obj_new = bpy.data.objects.new(obdata.name, obdata)
        if self.material is not None:
            mat = bpy.data.materials.get(self.material)
            if mat is not None:
                if obj_new.data.materials:
                    obj_new.data.materials[0] = mat
                else:
                    obj_new.data.materials.append(mat)
        base = scene.objects.link(obj_new)
        return obj_new, base


# A turtle has three attributes: location, orientation, a pen
class Turtle():
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
        # self.last_indices = None
        self.stack = []
        self.object_stack = []
        random.seed(seed)

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

    def push(self, bl_obj):
        t = (self.transform, bl_obj.get_last_indices(), bl_obj.get_radius())
        self.stack.append(t)

    def pop(self, bl_obj):
        t = self.stack.pop()
        (self.transform, last_indices, radius) = t
        bl_obj.set_last_indices(last_indices)
        bl_obj.set_radius(radius)

    def scale_radius(self, scale, bl_obj):
        bl_obj.set_radius(bl_obj.get_radius()*scale)

    def scale(self, scaling):
        self.transform = self.transform * mathutils.Matrix.Scale(scaling, 4)

    def forward(self, length):
        self.transform = self.transform * mathutils.Matrix.Translation((0.0, 0.0, length))

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

# +,- rotate around the right axis (y-axis)
# /,\ rotate around the up axis (x-axis)
# <,> rotate around the forward axis (z-axis)
# [,] push or pop state
# &   rotate random amount
# !,@ expand or shrink the size of a forward step (a branch segment or leaf)
# #,% fatten or slink the radius of a branch
# F produce an edge ( a branch segment)
# {,} Start and end a blender object
# ~ Duplicate an existing blender object and add
# p change pens
# s scale
# $ rotate the turtle to vertical
# todo: parametric rotations, random values, etc
# todo: change material

    def interpret(self, input, context):
        obj_base_pairs = []
        bl_obj = BlObject(self.radius)
        bl_obj.start_new_mesh_part(self.transform)

        i = 0
        tot_len = len(input)
        val_str = None
        while i < tot_len:
            val = None
            c = input[i]
            # print("c["+str(i)+"] = "+c)
            if i+2 < tot_len and input[i+1] == '(':
                start = i+2
                end = start
                while end < tot_len:
                    if input[end] == ')':
                        break
                    end += 1
                val_str = input[start:end]
                try:
                    val = float(val_str)
                except:
                    # Not a float, ignore
                    pass
                i = end+1
            else:
                i += 1

            if c == '+':
                if val is None:
                    val = self.angle
                else:
                    val = radians(val)
                self.rotate_y(val)
            elif c == '-':
                if val is None:
                    val = -self.angle
                else:
                    val = -val
                    val = radians(val)
                self.rotate_y(val)
            elif c == '/':
                if val is None:
                    val = self.angle
                else:
                    val = radians(val)
                self.rotate_x(val)
            elif c == '\\':
                if val is None:
                    val = -self.angle
                else:
                    val = -val
                    val = radians(val)
                self.rotate_x(val)
            elif c == '<':
                if val is None:
                    val = self.angle
                else:
                    val = radians(val)
                self.rotate_z(val)
            elif c == '>':
                if val is None:
                    val = self.angle
                else:
                    val = -val
                    val = radians(val)
                self.rotate_z(val)
            elif c == '$':
                self.rotate_upright()
            elif c == '[':
                self.push(bl_obj)
            elif c == ']':
                self.pop(bl_obj)
            elif c == '&':
                self.angle = random.random() * 2 * pi
            elif c == '!':
                if val is None:
                    val = self.expansion
                self.scale_radius(val, bl_obj)
                self.new_vertices(bl_obj)
            elif c == '@':
                if val is None:
                    val = self.shrinkage
                self.scale_radius(val, bl_obj)
                self.new_vertices(bl_obj)
            elif c == '#':
                if val is None:
                    val = self.fat
                self.scale_radius(val, bl_obj)
            elif c == '%':
                if val is None:
                    val = self.slinkage
                self.scale_radius(val, bl_obj)
            elif c == 'F':
                if val is None:
                    val = self.length
                # if bl_obj.is_new_mesh_part():
                #     self.new_vertices(bl_obj)
                self.forward(val)
                self.new_vertices(bl_obj)
            elif c == 'f':
                if val is None:
                    val = self.length
                self.forward(val)
                bl_obj.start_new_mesh_part(self.transform)
            elif c == '~':
                if val_str is not None:
                    self.copy_object(val_str)
                else:
                    print("~ operator has no value")
            elif c == '{':
                self.push(bl_obj)
                self.object_stack.append(bl_obj)
                bl_obj = BlObject(self.radius)
                bl_obj.start_new_mesh_part(self.transform)
                pass
            elif c == '}':
                obj, base = bl_obj.finish(context)
                obj_base_pairs.append((obj, base))
                bl_obj = self.object_stack.pop()
                self.pop(bl_obj)
                pass
            elif c == 's':
                if val is None:
                    val = self.slinkage
                self.scale(val)
            elif c == 'p':
                if val_str is not None:
                    bl_obj.set_pen(val_str, self.transform)
            elif c == 'm':
                if val_str is not None:
                    bl_obj.set_material(val_str)

        obj, base = bl_obj.finish(context)
        obj_base_pairs.append((obj, base))
        return obj_base_pairs

    def new_vertices(self, bl_obj):
        bl_obj.new_vertices(self.transform)


