__author__ = 'Krister'

import mathutils

class Pen():
    pass

class TrianglePen(Pen):

    #return (1,0,0), (0,1,0), (0,-1,0)
    def create_vertices(self):
        return [mathutils.Vector((0.1, 0, 0)), mathutils.Vector((0,0.1,0)), mathutils.Vector((0,-0.1,0))]
