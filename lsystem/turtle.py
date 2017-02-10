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
        self.radii = []
        self.skin = False
        self.last_indices = None
        self.radius = radius
        self.pen = pen.CylPen(4)
        self.material = None

    def set_pen(self, name, transform):
        if name == "edge":
            self.pen = pen.EdgePen()
        elif name == "skin":
            self.pen = pen.EdgePen()
            self.skin = True
        elif name == "curve":
            self.pen = pen.CurvePen()
        elif name == "line":
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
        if isinstance(self.pen, pen.CurvePen):
            return self.new_curve_object()
        else:
            return self.new_object(self.vertices, self.edges, self.quads, context)

    def create_bevel_object(self):
        # Create Bevel curve and object
        cu = bpy.data.curves.new('BevelCurve', 'CURVE')
        cu.use_fill_deform = True
        ob = bpy.data.objects.new('BevelObject', cu)
        bpy.context.scene.objects.link(ob)

        # Set some attributes
        cu.dimensions = '2D'
        cu.resolution_u = 6
        cu.twist_mode = 'MINIMUM'
        ob.show_name = True

        # Control point coordinates
        # coords = [
        #     (0.00, 0.08, 0.00, 1.00),
        #     (-0.20, 0.08, 0.00, 0.35),
        #     (-0.20, 0.19, 0.00, 1.00),
        #     (-0.20, 0.39, 0.00, 0.35),
        #     (0.00, 0.26, 0.00, 1.00),
        #     (0.20, 0.39, 0.00, 0.35),
        #     (0.20, 0.19, 0.00, 1.00),
        #     (0.20, 0.08, 0.00, 0.35)
        # ]
        coords = [
            (-1.0,  0.0, 0.0, 1.0),
            (-1.0,  1.0, 0.0, 1.0),
            ( 1.0,  1.0, 0.0, 1.0),
            ( 1.0, -1.0, 0.0, 1.0),
            (-1.0, -1.0, 0.0, 1.0)
        ]

        # Create spline and set control points
        spline = cu.splines.new('NURBS')
        nPointsU = len(coords)
        spline.points.add(nPointsU-1)
        for n in range(nPointsU):
            spline.points[n].co = coords[n]

        # Set spline attributes. Points probably need to exist here
        spline.use_cyclic_u = True
        spline.resolution_u = 12
        spline.order_u = 4

        return ob

    def create_taper_object(self):
        cu = bpy.data.curves.new('TaperCurve', 'CURVE')
        ob = bpy.data.objects.new('TaperCurve', cu)
        bpy.context.scene.objects.link(ob)

        cu.dimensions = '2D'
        cu.resolution_u = 6
        cu.twist_mode = 'MINIMUM'
        ob.show_name = True

        spline = cu.splines.new('BEZIER')
        spline.bezier_points.add(len(self.vertices)-1)
        for i, vertex in enumerate(self.vertices):
            spline.bezier_points[i].co = (float(i), self.radii[i], 0.0)
            spline.bezier_points[i].handle_right_type = 'VECTOR'
            spline.bezier_points[i].handle_left_type = 'VECTOR'

        return ob

    def new_curve_object(self):
        # create the Curve Datablock
        curveData = bpy.data.curves.new('lsystem', 'CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
        curveData.bevel_object = self.create_bevel_object()
        curveData.taper_object = self.create_taper_object()

        if len(self.edges) > 0:
            # map coords to spline
            branches = []
            branch = []
            last_vi = -1
            for edge in self.edges:
                if last_vi != edge[0]:
                    # new branch
                    branches.append(branch)
                    branch = [edge[0], edge[1]]
                    last_vi = edge[1]
                else:
                    branch.append(edge[1])
                    last_vi = edge[1]

            if len(branch) > 0:
                branches.append(branch)

            for branch in branches:
                polyline = curveData.splines.new('BEZIER')
                polyline.bezier_points.add(len(branch)-1)
                for i, v in enumerate(branch):
                    vertex = self.vertices[v]
                    polyline.bezier_points[i].co = vertex
                    polyline.bezier_points[i].handle_right_type = 'VECTOR'
                    polyline.bezier_points[i].handle_left_type = 'VECTOR'

        # polyline = curveData.splines.new('NURBS')
        # polyline.use_cyclic_u = False
        # polyline.use_bezier_u = True
        # polyline.use_endpoint_u = True
        # polyline.order_u = 2
        # polyline.points.add(len(self.vertices))
        # for i, vertex in enumerate(self.vertices):
        #     polyline.points[i].co = (vertex[0], vertex[1], vertex[2], 1)

        # create Object
        curveOB = bpy.data.objects.new('lsystem', curveData)

        # attach to scene
        scn = bpy.context.scene
        base = scn.objects.link(curveOB)

        return curveOB, base

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
        if self.material is not None:
            mat = bpy.data.materials.get(self.material)
            if mat is not None:
                if obj_new.data.materials:
                    obj_new.data.materials[0] = mat
                else:
                    obj_new.data.materials.append(mat)
        if self.skin:
            skin_mod = obj_new.modifiers.new('Skin', 'SKIN')
            for i in range(0, len(self.radii)):
                v = obj_new.data.skin_vertices[0].data[i]
                v.radius = self.radii[i], self.radii[i]

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
        if not self.stack:
            return
        t = self.stack.pop()
        (self.transform, last_indices, radius) = t
        bl_obj.set_last_indices(last_indices)
        bl_obj.set_radius(radius)

    def scale_radius(self, scale, bl_obj):
        bl_obj.set_radius(bl_obj.get_radius()*scale)

    def set_current_radius(self, radius, bl_obj):
        bl_obj.set_radius(radius)

    def scale(self, scaling, bl_obj):
        self.transform = self.transform * mathutils.Matrix.Scale(scaling, 4)
        self.scale_radius(scaling, bl_obj)

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
            elif c =='¤':
                if val is None:
                    val = 1.0
                self.set_current_radius(val, bl_obj)
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


