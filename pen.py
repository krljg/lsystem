import mathutils


class Pen():
    pass


class TrianglePen(Pen):
    def __init__(self, radius):
        self.radius = radius

    #return (1,0,0), (0,1,0), (0,-1,0)
    def create_vertices(self):
        return [mathutils.Vector((self.radius, 0, 0)),
                mathutils.Vector((0,self.radius,0)),
                mathutils.Vector((0,-self.radius,0))]
