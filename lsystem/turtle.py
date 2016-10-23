__author__ = 'Krister'

import mathutils
#from pen import Pen
from . import pen
from math import radians
from math import pi
import random


# A turtle has three attributes: location, orientation, a pen
class Turtle():
    def __init__(self, seed, pen):
        self.pen = pen
        self.angle = radians(25.7)
        self.base_angle = self.angle
        self.length = 1.0
        self.expansion = 1.1
        self.shrinkage = 0.9
        self.fat = 1.2
        self.slinkage = 0.8
        self.transform = mathutils.Matrix.Identity(4)
        self.last_indices = None
        self.stack = []
        random.seed(seed)

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

    def push(self):
        t = (self.transform, self.last_indices)
        self.stack.append(t)

    def pop(self):
        t = self.stack.pop()
        (self.transform, self.last_indices) = t

    def expand(self):
        self.transform = self.transform * mathutils.Matrix.Scale(self.expansion, 4)

    def shrink(self):
        self.transform = self.transform * mathutils.Matrix.Scale(self.shrinkage, 4)

    def fatten(self, scale):
        self.transform = self.transform * mathutils.Matrix.Scale(scale, 4)

    def slink(self, scale):
        self.transform = self.transform * mathutils.Matrix.Scale(scale, 4)

    def forward(self, length):
        self.transform = self.transform * mathutils.Matrix.Translation((0.0, 0.0, length))

    def leaf(self):
        pass

# +,- rotate around the right axis (y-axis)
# /,\ rotate around the up axis (x-axis)
# <,> rotate around the forward axis (z-axis)
# [,] push or pop state
# &   rotate random amount
# !,@ expand or shrink the size of a forward step (a branch segment or leaf)
# #,% fatten or slink the radius of a branch
# F produce an edge ( a branch segment)
# todo: Q produce an instance of a uv-mapped square ( a leaf)
# todo: {,} Start, end a polygon/object
# todo: parametric rotations, random values, etc
# todo: change pens

    def interpret(self, input):
        vertices = self.pen.create_vertices()
        self.last_indices = range(0, len(vertices))
        edges = []
        quads = []
        i = 0
        tot_len = len(input)
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
                val = float(val_str)
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
            elif c == '[':
                self.push()
            elif c == ']':
                self.pop()
            elif c == '&':
                self.angle = random.random() * 2 * pi
            elif c == '!':
                self.expand()
                self.new_vertices(vertices, quads)
            elif c == '@':
                self.shrink()
                self.new_vertices(vertices, quads)
            elif c == '#':
                if val is None:
                    val = self.fat
                self.fatten(val)
            elif c == '%':
                if val is None:
                    val = self.slinkage
                self.slink(val)
            elif c == 'F' or c == 'A' or c == 'B':
                if val is None:
                    val = self.length
                self.forward(val)
                self.new_vertices(vertices, quads)
            elif c == 'Q':
                self.leaf()
        return vertices, edges, quads

    def new_vertices(self, vertices, quads):
        new_vertices = self.pen.create_vertices()
        new_indices = range(len(vertices), len(vertices) + len(new_vertices))
        for v in new_vertices:
            v = self.transform * v
            vertices.append(v)

        for i in range(0, len(new_vertices)):
            quads.append([self.last_indices[i], self.last_indices[i - 1], new_indices[i - 1], new_indices[i]])

        self.last_indices = new_indices
