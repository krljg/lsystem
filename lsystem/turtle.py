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
            # self.skin = True
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

    def extend(self, vertices, radius):
        self.vertices.extend(vertices)
        self.radii.append(radius)

    def new_vertices(self, transform):
        if self.is_new_mesh_part():
            start = len(self.vertices)
            stop = start + len(self.tmp_vertices)
            self.last_indices = list(range(start, stop))
            self.extend(self.tmp_vertices, self.radius)

        new_vertices = self.pen.create_vertices(self.radius)
        transformed_vertices = []
        for v in new_vertices:
            v = transform * v
            transformed_vertices.append(v)

        new_indices = list(range(len(self.vertices), len(self.vertices) + len(transformed_vertices)))
        self.extend(transformed_vertices, self.radius)

        self.pen.connect(self.edges, self.quads, self.last_indices, new_indices)
        self.last_indices = new_indices

    def finish(self, context):
        new_mesh = self.pen.end()
        if new_mesh is not None:
            self.bmesh.from_mesh(new_mesh)

        # me = bpy.data.meshes.new("lsystem")
        self.bmesh.to_mesh(self.mesh)
        base = context.scene.objects.link(self.object)
        return self.object, base
        # return self.add_obj(me, context)

    def new_object(self, vertices, edges, quads, context):
        try:
            mesh = bpy.data.meshes.new('lsystem')
            mesh.from_pydata(vertices, edges, quads)
            mesh.update()
            obj, base = self.add_obj(mesh, context)
            return obj, base
        except Exception as e:
            print(vertices)
            print(edges)
            print(quads)
            raise e

    def add_obj(self, obdata, context):
        scene = context.scene
        obj_new = bpy.data.objects.new(obdata.name, obdata)

        # if self.material is not None:
        #     mat = bpy.data.materials.get(self.material)
        #     if mat is not None:
        #         if obj_new.data.materials:
        #             obj_new.data.materials[0] = mat
        #        else:
        #             obj_new.data.materials.append(mat)

        base = scene.objects.link(self.object)
        return obj_new, base

    def move_and_draw(self, transform):
        self.pen.move_and_draw(transform)

    def move(self, transform):
        self.pen.move(transform)


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
        self.direction = (0.0, 0.0, 1.0)
        # self.last_indices = None
        # self.stack = []
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
                bl_obj.push(self.transform)
                # self.push(bl_obj)
            elif c == ']':
                t = bl_obj.pop()
                if t is not None:
                    self.transform = t
                # self.pop(bl_obj)
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
            elif c == '¤':
                if val is None:
                    val = 1.0
                self.set_current_radius(val, bl_obj)
            elif c == 'F':
                if val is None:
                    val = self.length
                self.forward(val)
                bl_obj.move_and_draw(self.transform)
            elif c == 'f':
                if val is None:
                    val = self.length
                self.forward(val)
                bl_obj.move(self.transform)
            elif c == '~':
                if val_str is not None:
                    self.copy_object(val_str)
                else:
                    print("~ operator has no value")
            elif c == '{':
                bl_obj.push(self.transform)
                self.object_stack.append(bl_obj)
                bl_obj = BlObject(self.radius)
                bl_obj.start_new_mesh_part(self.transform)
                pass
            elif c == '}':
                obj, base = bl_obj.finish(context)
                obj_base_pairs.append((obj, base))
                bl_obj = self.object_stack.pop()
                t = bl_obj.pop()
                if t is not None:
                    self.transform = t
                # self.pop(bl_obj)
                pass
            elif c == 's':
                if val is None:
                    val = self.slinkage
                self.scale(val, bl_obj)
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


