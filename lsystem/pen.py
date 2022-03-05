import bpy
import bmesh
import mathutils
import math
from . import util


def create_mesh(vertices, edges, faces):
    try:
        mesh = bpy.data.meshes.new('lsystem-tmp')
        # print("create_mesh\n  vertices {}\n  edges {}\n  faces {}".format(vertices, edges, faces))
        mesh.from_pydata(vertices, edges, faces)
        mesh.validate()
        mesh.update()
        return mesh
    except Exception as ex:
        print("vertices")
        print(vertices)
        print("edges")
        print(edges)
        print("faces")
        print(faces)
        raise ex


class Pen():
    def __init__(self):
        self.radius = 0.1
        self.material = None

    def get_radius(self):
        return self.radius

    def set_radius(self, radius):
        self.radius = radius

    def get_material(self):
        return self.material

    def set_material(self, material):
        self.material = material

    def start(self, trans_mat):
        pass

    def move_and_draw(self, trans_mat):
        pass

    def move(self, trans_mat):
        pass

    def end(self):
        """Return a mesh"""
        return None

    def start_branch(self):
        pass

    def end_branch(self):
        return None

    def start_face(self):
        pass

    def end_face(self):
        return None


# Todo: implment support for surface specification, see abop chapter 5
class SurfacePen(Pen):
    def __init__(self):
        Pen.__init__(self)
        self.vertices = []
        self.face_start_index = 0
        self.faces = []
        self.stack = []

    # def start(self, trans_mat):
        #v = trans_mat * mathutils.Vector((0, 0, 0))
        #self.vertices.append(v)

    def move_and_draw(self, trans_mat):
        if not self.faces:
            self.start_face()

        v = util.matmul(trans_mat, mathutils.Vector((0, 0, 0)))
        # print("vertex {}".format(v))
        self.vertices.append(v)
        face = self.faces[self.stack[-1]]
        face.append(len(self.vertices)-1)

    def end(self):
        self.end_face()
        if not self.faces:
            # print("Invalid surface, no faces")
            return None
        return create_mesh(self.vertices, [], self.faces)

    def start_face(self):
        self.faces.append([])
        self.stack.append(len(self.faces)-1)

    def end_face(self):
        # print("end_face stack={} faces={}".format(self.stack, self.faces))
        if self.stack:
            self.stack.pop()


class PolPen(Pen):
    def __init__(self):
        Pen.__init__(self)
        self.vertices = []

    def start(self, trans_mat):
        v = util.matmul(trans_mat, mathutils.Vector((0, 0, 0)))
        self.vertices.append(v)

    def move_and_draw(self, trans_mat):
        v = util.matmul(trans_mat, mathutils.Vector((0, 0, 0)))
        self.vertices.append(v)

    def end(self):
        # todo: end needs to check if it ends the whole thing or just a branch
        if len(self.vertices) < 3:
            print("Invalid polygon, number of vertices = "+str(len(self.vertices)))
            return None

        return create_mesh(self.vertices, [], [range(0, len(self.vertices))])

    def start_branch(self):
        print("Branches not supported for PolPen")

    def end_branch(self):
        return self.end()


class EdgePen(Pen):
    def __init__(self, skin, subdiv):
        Pen.__init__(self)
        self.skin = skin
        self.subdiv = subdiv
        self.vertices = []
        self.last_index = None
        self.edges = []
        self.radii = []
        self.stack = []

    def start(self, trans_mat):
        self.vertices.append(self.create_vertices(trans_mat))
        self.last_index = 0
        self.radii.append(self.radius)

    def move_and_draw(self, trans_mat):
        self.vertices.append(self.create_vertices(trans_mat))
        self.radii.append(self.radius)
        new_index = len(self.vertices)-1
        self.edges.append((self.last_index, new_index))
        self.last_index = new_index

    def move(self, trans_mat):
        v = self.create_vertices(trans_mat)
        self.radii.append(self.radius)
        self.last_index = len(self.vertices)
        self.vertices.append(v)

    def end(self):
        # print("EdgePen.end()")
        if self.stack:
            self.last_index, self.radius = self.stack.pop()
            return None

        if len(self.vertices) > len(self.edges)+1:
            del self.vertices[-1]
            del self.radii[-1]

        if not self.vertices:
            return None

        # print("vertices "+str(len(self.vertices)))
        # print(self.vertices)
        # print("radii "+str(len(self.radii)))
        # print(self.radii)
        # print("edges")
        # print(self.edges)
        mesh = create_mesh(self.vertices, self.edges, [])
        if not self.skin and self.subdiv <= 0:
            return mesh

        obj_new = bpy.data.objects.new(mesh.name, mesh)

        if self.skin:
            skin_mod = obj_new.modifiers.new('Skin', 'SKIN')
            skin_mod.use_x_symmetry = False
            # print(obj_new.data.skin_vertices[0].data)
            # for i,v in enumerate(obj_new.data.skin_vertices[0].data):
            #     print(str(i)+" "+str(v.radius[0])+", "+str(v.radius[1]))
            for i, r in enumerate(self.radii):
                v = obj_new.data.skin_vertices[0].data[i]
                v.radius = r,r
            # for i,v in enumerate(obj_new.data.skin_vertices[0].data):
            #     print(str(i)+" "+str(v.radius[0])+", "+str(v.radius[1]))

            # for i in range(0, len(self.radii)):
            #     v = obj_new.data.skin_vertices[0].data[i]
            #     v.radius = self.radii[i], self.radii[i]
        if self.subdiv > 0:
            # print(self.subdiv)
            subdiv_mod = obj_new.modifiers.new('Subd', 'SUBSURF')
            subdiv_mod.levels = self.subdiv
            subdiv_mod.render_levels = self.subdiv

        new_mesh = util.to_mesh(obj_new)
        return new_mesh

    def start_branch(self):
        self.stack.append((self.last_index, self.radius))

    def end_branch(self):
        return self.end()

    def create_vertices(self, trans_mat):
        return util.matmul(trans_mat, mathutils.Vector((0, 0, 0)))


class VertexPen(Pen):
    def __init__(self):
        Pen.__init__(self)
        self.stack = []
        self.faces = []
        self.last_indices = None
        self.vertices = []

    def reset(self):
        self.stack = []
        self.faces = []
        self.last_indices = None
        self.vertices = []

    def start(self, trans_mat):
        self.reset()
        v = self.create_vertices(trans_mat)
        self.last_indices = range(0, len(v))
        self.vertices.extend(v)

    def move_and_draw(self, trans_mat):
        start_index = len(self.vertices)
        v = self.create_vertices(trans_mat)
        self.vertices.extend(v)

        new_indices = range(start_index, start_index+len(v))
        self.connect(self.faces, self.last_indices, new_indices)
        self.last_indices = new_indices

    def move(self, trans_mat):
        v = self.create_vertices(trans_mat)
        start_index = len(self.vertices)
        self.last_indices = range(start_index, start_index+len(v))
        self.vertices.extend(v)

    def end(self):
        if not self.stack:
            if not self.faces:
                return create_mesh([], [],[])
            return create_mesh(self.vertices, [], self.faces)

        self.last_indices, self.radius = self.stack.pop()
        return None

    def start_branch(self):
        self.stack.append((self.last_indices, self.radius))

    def end_branch(self):
        if not self.stack:
            if not self.faces:
                return create_mesh([], [],[])
            return create_mesh(self.vertices, [], self.faces)
        self.last_indices, self.radius = self.stack.pop()
        return None

    def create_vertices(self, trans_mat):
        return util.matmul(trans_mat, mathutils.Vector((0, 0, 0)))

    def connect(self, quads, last_indices, new_indices):
        print("'connect' not implemented")


class LinePen(VertexPen):
    def __init__(self):
        VertexPen.__init__(self)

    def create_vertices(self, trans_matrix):
        return [util.matmul(trans_matrix, mathutils.Vector((self.radius, 0, 0))),
                util.matmul(trans_matrix * mathutils.Vector((-self.radius, 0, 0)))]

    def connect(self, quads, last_indices, new_indices):
        quads.append([last_indices[0], last_indices[1], new_indices[1], new_indices[0]])


class CylPen(VertexPen):
    def __init__(self, num_vertices):
        VertexPen.__init__(self)
        self.num_vertices = num_vertices

    def create_vertices(self, trans_mat):
        v = []
        angle = 0.0
        inc = 2*math.pi/self.num_vertices
        for i in range(0, self.num_vertices):
            vertex = mathutils.Vector((self.radius * math.cos(angle), self.radius * math.sin(angle), 0))
            vertex = util.matmul(trans_mat, vertex)
            v.append(vertex)
            angle += inc
        return v

    def connect(self, quads, last_indices, new_indices):
        for i in range(0, self.num_vertices):
            quads.append([last_indices[i], last_indices[i - 1], new_indices[i - 1], new_indices[i]])


class BMeshPen(Pen):
    def __init__(self):
        Pen.__init__(self)
        self.bmesh = None
        self.last_vertices = None
        self.material = None
        self.stack = []

    def set_material(self, material):
        self.material = material

    def reset(self):
        self.bmesh = bmesh.new()
        self.stack = []

    def start(self, trans_mat):
        self.reset()
        self.last_vertices = self.create_vertices(trans_mat)

    def move_and_draw(self, trans_mat):
        new_vertices = self.create_vertices(trans_mat)
        new_faces = self.connect(self.last_vertices, new_vertices)
        self.last_vertices = new_vertices

        if self.material is not None:
            for f in new_faces:
                f.material_index = self.material

    def move(self, trans_mat):
        self.last_vertices = self.create_vertices(trans_mat)

    def end(self):
        """Return a mesh"""
        if not self.stack:
            if self.bmesh is None:  # end() can be called before start()
                return None
            mesh = bpy.data.meshes.new("lsystem.bmesh")
            self.bmesh.to_mesh(mesh)
            return mesh

        self.last_vertices, self.radius, self.material = self.stack.pop()
        return None

    def start_branch(self):
        self.stack.append((self.last_vertices, self.radius, self.material))

    def end_branch(self):
        return self.end()

    def create_vertices(self, trans_mat):
        raise Exception("create_vertices not implemented")

    def connect(self, last_vertices, new_vertices):
        raise Exception("connect not implemented")


class BLinePen(BMeshPen):
    def __init__(self):
        BMeshPen.__init__(self)

    def create_vertices(self, trans_mat):
        v1 = self.bmesh.verts.new(util.matmul(trans_mat, mathutils.Vector((self.radius, 0, 0))))
        v2 = self.bmesh.verts.new(util.matmul(trans_mat, mathutils.Vector((-self.radius, 0, 0))))
        return [v1, v2]

    def connect(self, last_vertices, new_vertices):
        return [self.bmesh.faces.new((last_vertices[0], last_vertices[1], new_vertices[1], new_vertices[0]))]


class BCylPen(BMeshPen):
    def __init__(self, num_vertices):
        BMeshPen.__init__(self)
        self.num_vertices = num_vertices

    def create_vertices(self, trans_mat):
        v = []
        angle = 0.0
        inc = 2*math.pi/self.num_vertices
        for i in range(0, self.num_vertices):
            vertex = mathutils.Vector((self.radius * math.cos(angle), self.radius * math.sin(angle), 0))
            vertex = util.matmul(trans_mat, vertex)
            v.append(self.bmesh.verts.new(vertex))
            angle += inc
        return v

    def connect(self, last_vertices, new_vertices):
        faces = []
        for i in range(0, self.num_vertices):
            face = self.bmesh.faces.new((last_vertices[i], last_vertices[i - 1], new_vertices[i - 1], new_vertices[i]))
            faces.append(face)
        return faces


class CurvePen(Pen):
    def __init__(self):
        Pen.__init__(self)
        self.vertices = []
        self.radii = []
        self.stack = []

    def start(self, trans_mat):
        self.vertices.append(util.matmul(trans_mat, mathutils.Vector((0, 0, 0))))
        self.radii.append(self.radius)

    def move_and_draw(self, trans_mat):
        self.vertices.append(util.matmul(trans_mat, mathutils.Vector((0, 0, 0))))
        self.radii.append(self.radius)

    def move(self, trans_mat):
        # todo
        pass

    def end(self):
        # create curve object, convert to mesh, return mesh
        mesh = None
        if len(self.vertices) > 1:
            mesh = self.new_curve()
        if self.stack:
            self.vertices, self.radii, self.radius = self.stack.pop()
        return mesh

    def start_branch(self):
        last_vertex = self.vertices[-1]
        last_radius = self.radii[-1]
        self.stack.append((self.vertices, self.radii, self.radius))
        self.vertices = [last_vertex]
        self.radii = [last_radius]

    def end_branch(self):
        return self.end()

    def create_bevel_object(self):
        # Create Bevel curve and object
        cu = bpy.data.curves.new('BevelCurve', 'CURVE')
        # cu.use_fill_deform = True
        ob = bpy.data.objects.new('BevelObject', cu)
        util.link(bpy.context, ob)

        # Set some attributes
        cu.dimensions = '2D'
        cu.resolution_u = 6
        cu.twist_mode = 'MINIMUM'
        ob.show_name = True

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
        util.link(bpy.context, ob)

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

    def new_curve(self):
        # create the Curve Datablock
        curveData = bpy.data.curves.new('lsystem-tmp', 'CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
        # bevel_object = self.create_bevel_object()
        taper_object = self.create_taper_object()
        # curveData.bevel_object = bevel_object
        curveData.bevel_depth = 1.0
        curveData.bevel_mode = 'ROUND'
        curveData.taper_object = taper_object
        curveData.use_map_taper = True

        if len(self.vertices) > 1:
            polyline = curveData.splines.new('BEZIER')
            polyline.bezier_points.add(len(self.vertices)-1)
            for i,v in enumerate(self.vertices):
                polyline.bezier_points[i].co = v
                polyline.bezier_points[i].handle_right_type = 'VECTOR'
                polyline.bezier_points[i].handle_left_type = 'VECTOR'

            polyline.use_cyclic_u = False
            polyline.use_bezier_u = True
            polyline.use_endpoint_u = True
            polyline.order_u = 2

        # if len(self.edges) > 0:
        #     # map coords to spline
        #     branches = []
        #     branch = []
        #     last_vi = -1
        #     for edge in self.edges:
        #         if last_vi != edge[0]:
        #             # new branch
        #             branches.append(branch)
        #             branch = [edge[0], edge[1]]
        #            last_vi = edge[1]
        #         else:
        #             branch.append(edge[1])
        #             last_vi = edge[1]
        #
        #     if len(branch) > 0:
        #         branches.append(branch)
        #
        #     for branch in branches:
        #         polyline = curveData.splines.new('BEZIER')
        #         polyline.bezier_points.add(len(branch)-1)
        #         for i, v in enumerate(branch):
        #             vertex = self.vertices[v]
        #             polyline.bezier_points[i].co = vertex
        #             polyline.bezier_points[i].handle_right_type = 'VECTOR'
        #             polyline.bezier_points[i].handle_left_type = 'VECTOR'

        # polyline = curveData.splines.new('NURBS')
        # polyline.use_cyclic_u = False
        # polyline.use_bezier_u = True
        # polyline.use_endpoint_u = True
        # polyline.order_u = 2
        # polyline.points.add(len(self.vertices))
        # for i, vertex in enumerate(self.vertices):
        #     polyline.points[i].co = (vertex[0], vertex[1], vertex[2], 1)

        # create Object
        curve_ob = bpy.data.objects.new('lsystem-tmp', curveData)
        mesh = util.to_mesh(curve_ob)
        # bevel_object.user_clear()
        # bpy.data.objects.remove(bevel_object, do_unlink=True)
        # taper_object.user_clear()
        bpy.data.objects.remove(taper_object, do_unlink=True)
        return mesh


class BmeshSpinPen(Pen):
    def __init__(self):
        Pen.__init__(self)
        self.geom = None
        self.bm = None
        self.materials = []

    def set_material(self, material):
        Pen.set_material(self, material)
        self.materials.append(material)

    def start(self, trans_mat):
        self.bm = bmesh.new()
        bmesh.ops.create_circle(
            self.bm,
            cap_ends=False,
            diameter=self.radius*2.0,
            segments=8)
        loc, rot, scale = trans_mat.decompose()
        bmesh.ops.translate(self.bm, self.bm.verts[:], vec=(loc))
        edges_start_a = self.bm.edges[:]
        self.geom = self.bm.verts[:] + edges_start_a

    def move_and_draw(self, trans_mat):
        loc, rot, scale = trans_mat.decompose()
        # todo: move_and_draw_internal(self, trans_mat, dvec, angle, axis)

    def move_and_draw_internal(self, trans_mat, dvec, angle, axis):

        # dvec = mathutils.Vector((0.0, 0.0, 1.0))
        self.geom = bmesh.ops.spin(
            self.bm,
            geom=self.geom,
            angle=angle,
            dvec=dvec,
            steps=1,
            axis=axis,
            cent=(0.0, 1.0, 0.0))
        if self.material is not None:
            mat_index = self.materials.index(self.material)
            for g in self.geom:
                if isinstance(g, bmesh.types.BMFace):
                    g.material_index=mat_index

    def move(self, trans_mat):
        pass

    def end(self):
        """Return a mesh"""
        mesh = bpy.data.meshes.new("lsystem.bmesh")
        for material in self.materials:
            mat = bpy.data.materials.get(self.material)
            mesh.materials.append(mat)
        self.bm.to_mesh(mesh)
        return mesh

    def start_branch(self):
        pass

    def end_branch(self):
        return None
