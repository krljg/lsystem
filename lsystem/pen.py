import mathutils
import math


class Pen():
    pass


class LinePen(Pen):
    def __init__(self):
        pass

    def create_vertices(self, radius):
        return [mathutils.Vector((radius, 0, 0)),
                mathutils.Vector((-radius, 0, 0))]


class TrianglePen(Pen):
    def __init__(self):
        pass

    #return (1,0,0), (0,1,0), (0,-1,0)
    def create_vertices(self, radius):
        return [mathutils.Vector((radius, 0, 0)),
                mathutils.Vector((0,radius,0)),
                mathutils.Vector((0,-radius,0))]


class QuadPen(Pen):
    def __init__(self):
        pass

    def create_vertices(self, radius):
        return [mathutils.Vector((radius, radius, 0)),
                mathutils.Vector((radius, -radius,0)),
                mathutils.Vector((-radius,-radius,0)),
                mathutils.Vector((-radius, radius, 0))]


class CylPen(Pen):
    def __init__(self, vertices):
        self.vertices = vertices

    def create_vertices(self, radius):
        v = []
        angle = 0.0
        inc = 2*math.pi/self.vertices
        for i in range(0, self.vertices):
            vertex = mathutils.Vector((radius * math.cos(angle), radius * math.sin(angle), 0))
            v.append(vertex)
            angle += inc
        return v
