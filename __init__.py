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


class LSystemOperator(bpy.types.Operator):
    """Add LSystem"""
    bl_idname="mesh.lsystem"
    bl_label = "LSystem"

    def add_obj(self, obdata, context):
        scene = context.scene
        obj_new = bpy.data.objects.new(obdata.name, obdata)
        base = scene.objects.link(obj_new)
        return obj_new, base

    def execute(self, context):
        iterations = 4
        angle = 90
        axiom = "-F"
        rule1 = lsystem.ProductionRule("F", "F+F-F-F+F")
        rules = [rule1]
        result = lsystem.iterate(axiom, iterations, rules)
        print(axiom)
        for rule in rules:
            print(rule)
        print(result)
        t = turtle.Turtle(pen.TrianglePen())
        t.set_angle(angle)
        (vertices, edges, quads) = t.interpret(result)
        mesh = bpy.data.meshes.new('lsystem')
        mesh.from_pydata(vertices, edges, quads)
        mesh.update()
        obj, base = self.add_obj(mesh, context)
        for ob in context.scene.objects:
            ob.select = False
        base.select = True
        context.scene.objects.active = obj
        #return base
        #lsystem.test_algae()
        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)
    #bpy.utils.register_class(LSystemOperator)

    # Add "Extras" menu to the "Add Curve" menu
    bpy.types.INFO_MT_curve_add.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.utils.unregister_class(LSystemOperator)

    # Remove "Extras" menu from the "Add Curve" menu.
    bpy.types.INFO_MT_curve_add.remove(menu_func)

if __name__ == "__main__":
    register()

