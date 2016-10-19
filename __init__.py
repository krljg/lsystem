bl_info = {
    "name": "LSystem",
    "author": "Krister Ljung",
    "version": (0, 1),
    "blender": (2, 63, 0),
    "location": "View3D > Add > Mesh > LSystem",
    "description": "Add LSystem",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh"}

if "bpy" in locals():
    import imp
    imp.reload(lsystem)

else:
    from . import lsystem
    from . import turtle
    from . import pen

import bpy
import mathutils
import math


class INFO_MT_curve_extras_add(bpy.types.Menu):
    # Define the "Extras" menu
    bl_idname = "mesh_lsystem_add"
    bl_label = "LSystem"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.lsystem",
            text="LSystem")


# Define "Extras" menu
def menu_func(self, context):
    self.layout.operator("mesh.lsystem",
                         text="LSystem")


def nupdate(self, context):
    for n in range(self.nrules):
        input = 'input'+str(n+1)
        rule = 'rule'+str(n+1)

        try:
            s = getattr(self, rule)
        except AttributeError:
            setattr(
                self.__class__,
                rule,
                bpy.props.StringProperty(
                    name=rule,
                    description="replacement string"
                )
            )
        try:
            s = getattr(self, input)
        except AttributeError:
            setattr(
                self.__class__,
                input,
                bpy.props.StringProperty(
                    name=input,
                    description="a single character module",
                    maxlen=1
                )
            )


class LSystemOperator(bpy.types.Operator):
    """Add LSystem"""
    bl_idname="mesh.lsystem"
    bl_label = "LSystem"
    bl_description = "Create a new Lsystem mesh"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    iterations = bpy.props.IntProperty(
        name="iterations",
        default=4,
        min=0,
        max=1000)
    angle = bpy.props.FloatProperty(
        name='angle',
        default=math.radians(25),
        subtype='ANGLE',
        description="size in degrees of angle"
    )
    axiom = bpy.props.StringProperty(
        name='start',
        default='X'
    )

    nrules = bpy.props.IntProperty(
        name="rules",
        min=0,
        max=50,
        update=nupdate
    )

    def add_obj(self, obdata, context):
        scene = context.scene
        obj_new = bpy.data.objects.new(obdata.name, obdata)
        base = scene.objects.link(obj_new)

        return obj_new, base

    def koch_curve(self):
        axiom = "-F"
        rule1 = lsystem.ProductionRule("F", "F+F-F-F+F")
        rules = [rule1]
        return axiom, rules, 90

    def sierpinski_triangle(self):
        axiom = "A"
        rule1 = lsystem.ProductionRule("A", "+B-A-B+")
        rule2 = lsystem.ProductionRule("B", "-A+B+A-")
        return axiom, [rule1, rule2], 60

    def fractal_plant(self):
        axiom = "X"
        rule1 = lsystem.ProductionRule("X", "F-[[X]+X]+F[+FX]-X")
        rule2 = lsystem.ProductionRule("F", "FF")
        return axiom, [rule1, rule2], 25

    def execute(self, context):
        # iterations = 4
        # angle = 90
        # axiom = "-F"
        # rule1 = lsystem.ProductionRule("F", "F+F-F-F+F")
        # rules = [rule1]

        # axiom, rules = self.koch_curve()
        # axiom, rules, angle = self.fractal_plant()

        rules = []
        for i in range(self.nrules):
            input_name = "input"+str(i+1)
            rule_name = "rule"+str(i+1)
            input = getattr(self, input_name)
            rule = getattr(self, rule_name)
            rule = lsystem.ProductionRule(input, rule)
            rules.append(rule)
        result = lsystem.iterate(self.axiom, self.iterations, rules)
        print(self.axiom)
        for rule in rules:
            print(rule)
        print(result)
        t = turtle.Turtle(pen.TrianglePen())
        t.set_angle(self.angle)
        (vertices, edges, quads) = t.interpret(result)
        mesh = bpy.data.meshes.new('lsystem')
        mesh.from_pydata(vertices, edges, quads)
        mesh.update()
        obj, base = self.add_obj(mesh, context)
        for ob in context.scene.objects:
            ob.select = False
        base.select = True
        context.scene.objects.active = obj

        # bpy.ops.object.modifier_add(type='SKIN')
        # context.active_object.modifiers[0].use_smooth_shade = True

        # skinverts = context.active_object.data.skin_vertices[0].data

        # for i,v in enumerate(skinverts):
        #    v.radius = [1.0, 1.0] # does not work
        #  v.radius = [self.radii[i], self.radii[i]] //todo have no radius

        # bpy.ops.object.modifier_add(type='SUBSURF')
        # context.active_object.modifiers[1].levels = 2

        # self.rescale(obj)

        # return base
        # lsystem.test_algae()
        return {'FINISHED'}

    def rescale(self, obj):
        msize = obj.dimensions.x
        if obj.dimensions.y > msize:
            msize = obj.dimensions.y
        if obj.dimensions.z > msize:
            msize = obj.dimensions.z

        s = 1.0/msize
        obj.scale = ((s, s, s))

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, 'nrules')
        box = layout.box()
        if getattr(self, 'axiom') == '':
            box.alert = True
        box.prop(self, 'axiom')

        for i in range(self.nrules):
            input = 'input'+str(i+1)
            rule = 'rule'+str(i+1)

            box = layout.box()
            row = box.row(align=True)
            if getattr(self, input) == '' or getattr(self, rule) == '':
                row.alert = True
            row.prop(self, input)
            row.prop(self, rule, text="")

        box = layout.box()
        box.label(text="Interpretation section")
        box.prop(self, "iterations")
        box.prop(self, "angle")


def register():
    bpy.utils.register_module(__name__)
    #bpy.utils.register_class(LSystemOperator)

    # Add "Extras" menu to the "Add Mesh" menu
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.utils.unregister_class(LSystemOperator)

    # Remove "Extras" menu from the "Add Curve" menu.
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()

    vertices = [
        mathutils.Vector((0, -1 / math.sqrt(3),0)),
        mathutils.Vector((0.5, 1 / (2 * math.sqrt(3)), 0)),
        mathutils.Vector((-0.5, 1 / (2 * math.sqrt(3)), 0)),
        mathutils.Vector((0, 0, math.sqrt(2 / 3))),
    ]
    faces = [[0,1,2], [0,1,3], [1,2,3], [2,0,3]]
    newMesh = bpy.data.meshes.new("Tetahedron")
    newMesh.from_pydata(vertices, [], faces)
    newMesh.update()
    newObj = bpy.data.objects.new("Tetrahedron", newMesh)
    bpy.context.scene.objects.link(newObj)
    bpy.ops.object.select_all(action = "DESELECT")
    newObj.select = True
    bpy.context.scene.objects.active = newObj
    #register()


