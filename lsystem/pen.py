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

    def connect(self, last_indices, new_indices):
        return [[last_indices[0], last_indices[1], new_indices[1], new_indices[0]]]


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

    def connect(self, last_indices, new_indices):
        quads = []
        for i in range(0, self.vertices):
            quads.append([last_indices[i], last_indices[i - 1], new_indices[i - 1], new_indices[i]])
        return quads
