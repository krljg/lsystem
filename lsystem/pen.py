import mathutils
import math


class Pen():
    pass


class LinePen(Pen):
    def __init__(self, radius):
        self.radius = radius

    def create_vertices(self):
        return [mathutils.Vector((self.radius, 0, 0)),
                mathutils.Vector((-self.radius, 0, 0))]


class TrianglePen(Pen):
    def __init__(self, radius):
        self.radius = radius

    #return (1,0,0), (0,1,0), (0,-1,0)
    def create_vertices(self):
        return [mathutils.Vector((self.radius, 0, 0)),
                mathutils.Vector((0,self.radius,0)),
                mathutils.Vector((0,-self.radius,0))]


class QuadPen(Pen):
    def __init__(self, radius):
        self.radius = radius

    def create_vertices(self):
        return [mathutils.Vector((self.radius, self.radius, 0)),
                mathutils.Vector((self.radius, -self.radius,0)),
                mathutils.Vector((-self.radius,-self.radius,0)),
                mathutils.Vector((-self.radius, self.radius, 0))]


class CylPen(Pen):
    def __init__(self, radius, vertices):
        self.radius = radius
        self.vertices = vertices

    def create_vertices(self):
        v = []
        angle = 0.0
        inc = 2*math.pi/self.vertices
        for i in range(0, self.vertices):
            vertex = mathutils.Vector((self.radius * math.cos(angle), self.radius * math.sin(angle), 0))
            v.append(vertex)
            angle += inc
        return v
