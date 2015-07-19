__author__ = 'Krister'

import mathutils
#from pen import Pen
from . import pen
from math import radians

# A turtle has three attributes: location, orientation, a pen
class Turtle():
    def __init__(self, pen):
        #self.location = None
        #self.orientation = None
        self.pen = pen
        self.angle = radians(25.7)
        #self.radius = 1.0
        self.transform = mathutils.Matrix.Identity(4)
        self.last_indices = None
        self.stack = []

    def set_angle(self, angle_degrees):
        self.angle = radians(angle_degrees)

    def rotate_y(self, angle):
        self.transform = self.transform * mathutils.Matrix.Rotation(angle, 4, mathutils.Vector((0.0, 1.0, 0.0)))

    def rotate_x(self, angle):
        self.transform = self.transform * mathutils.Matrix.Rotation(angle, 4, mathutils.Vector((1.0, 0.0, 0.0)))

    def rotate_z(self, angle):
        self.transform = self.transform * mathutils.Matrix.Rotation(angle, 4, mathutils.Vector((0.0, 0.0, 1.0)))

    def push(self):
        t = (self.transform, self.last_indices)
        self.stack.append(t)

    def pop(self):
        t = self.stack.pop()
        (self.transform, self.last_indices) = t

    def expand(self):
        self.transform = self.transform * mathutils.Matrix.Scale(1.1, 4)

    def shrink(self):
        self.transform = self.transform * mathutils.Matrix.Scale(0.9, 4)

    def fatten(self):
        self.transform = self.transform * mathutils.Matrix.Scale(1.1, 4)

    def slink(self):
        self.transform = self.transform * mathutils.Matrix.Scale(0.9, 4)

    def forward(self):
        #print(self.transform)
        #print(mathutils.Matrix.Translation((0.0, 0.0, 1.0)))
        self.transform = self.transform * mathutils.Matrix.Translation((0.0, 0.0, 1.0))

    def leaf(self):
        pass

# +,- rotate around the right axis
# /,\ rotate around the up axis
# <,> rotate around the forward axis
# [,] push or pop state
# &   rotate random amount
# !,@ expand or shrink the size of a forward step (a branch segment or leaf)
# #,% fatten or slink the radius of a branch
# F produce an edge ( a branch segment)
# Q produce an instance of a uv-mapped square ( a leaf)

    def interpret(self, input):
        vertices = self.pen.create_vertices()
        self.last_indices = range(0, len(vertices))
        edges = []
        quads = []
        for c in input:
            if c == '+':
                self.rotate_y(self.angle)
            elif c == '-':
                self.rotate_y(-self.angle)
            elif c == '/':
                self.rotate_x(self.angle)
            elif c == '\\':
                self.rotate_x(-self.angle)
            elif c == '<':
                self.rotate_z(self.angle)
            elif c == '>':
                self.rotate_z(-self.angle)
            elif c == '[':
                self.push()
            elif c == ']':
                self.pop()
            elif c == '&':
                pass # todo
            elif c == '!':
                self.expand()
            elif c == '@':
                self.shrink()
            elif c == '#':
                self.fatten()
            elif c == '%':
                self.slink()
            elif c == 'F':
                self.forward()
                new_vertices = self.pen.create_vertices()
                modified_vertices = []
                new_indices = range(len(vertices), len(vertices)+len(new_vertices))
                for v in new_vertices:
                    v = self.transform * v
                    modified_vertices.append(v)
                    vertices.append(v)

                for i in range(0, len(new_vertices)):
                    quads.append([self.last_indices[i], self.last_indices[i-1], new_indices[i-1], new_indices[i]])
                vertices.extend(modified_vertices)
                self.last_indices = new_indices
                #nv = self.transform * nv
                #vertices.extend(nv)
            elif c == 'Q':
                self.leaf()
        return (vertices, edges, quads)
