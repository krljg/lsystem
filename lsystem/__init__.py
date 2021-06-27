bl_info = {
    "name": "LSystem",
    "author": "krljg",
    "version": (0, 1),
    "blender": (2, 90, 0),
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
    from . import exec
    from . import util

import math
import time
import random

import bpy
import bpy_extras.mesh_utils
import mathutils


# todo: Add ability to select pens and set materials/texture

class INFO_MT_curve_extras_add(bpy.types.Menu):
    # Define the "Extras" menu
    bl_idname = "INFO_MT_mesh_lsystem_add"
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
        input = 'input' + str(n + 1)
        condition = 'condition' + str(n + 1)
        rule = 'rule' + str(n + 1)

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
            s = getattr(self, condition)
        except AttributeError:
            setattr(
                self.__class__,
                condition,
                bpy.props.StringProperty(
                    name=condition,
                    description="condition string"
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
                    description="a module to be replaced"
                )
            )


class JsonPanel(bpy.types.Panel):
    bl_label = "JSON"
    bl_idname = "OBJECT_PT_JSON"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    textblock = None  # text are to use for this panel

    @classmethod
    def poll(self, context):

        return bpy.data.texts.get("PASTE TEXT HERE") is not None

    def draw(self, context):
        layout = self.layout

        obj = context.object
        textbox = bpy.data.texts.get("PASTE TEXT HERE")
        row = layout.row()
        row.label(text="Text Block", icon='WORLD_DATA')
        row = layout.row()
        box = row.box()
        box.prop(textbox, "open_in_info_window", text="OPEN TEXT IN INFO WINDOW")
        for line in textbox.lines:
            row = layout.row()
            row.label(text=line.body)

        #use below if in text editor properties
        #row.prop(context.space_data.text,"open_in_info_window")
        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.operator("text.simple_operator")


def openInInfoWin(self,context):

    if self.open_in_info_window:
        for area in context.screen.areas:
            if area.type == 'INFO':

                area.type = 'TEXT_EDITOR'
                area.spaces[0].text = JsonPanel.textblock
                break
    else:
        for area in context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                area.type = 'INFO'
                break
    return None


class LSystemOperator(bpy.types.Operator):
    """Add LSystem"""
    bl_idname = "mesh.lsystem"
    bl_label = "LSystem"
    bl_description = "Create a new Lsystem mesh"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    instances: bpy.props.IntProperty(
        name="instances",
        default=1,
        min=1,
        max=1000000
    )
    seed: bpy.props.IntProperty(
        name="seed",
        default=0,
        min=0,
        max=1000000
    )
    min_iterations: bpy.props.IntProperty(
        name="min iterations",
        default=4,
        min=0,
        max=1000
    )
    iterations: bpy.props.IntProperty(
        name="max iterations",
        default=4,
        min=0,
        max=1000)
    angle: bpy.props.FloatProperty(
        name='angle',
        default=math.radians(25),
        subtype='ANGLE',
        description="size in degrees of angle"
    )
    length: bpy.props.FloatProperty(
        name='length',
        default=1.0,
        min=0.0,
        max=1000.0
    )
    radius: bpy.props.FloatProperty(
        name='radius',
        default=0.1,
        min=0.0,
        max=1000.0
    )
    expansion: bpy.props.FloatProperty(
        name='expansion',
        default=1.1,
        min=0.0,
        max=1000.0
    )
    shrinkage: bpy.props.FloatProperty(
        name='shrinkage',
        default=0.9,
        min=0.0,
        max=1000.0
    )
    fat: bpy.props.FloatProperty(
        name='fat',
        default=1.2,
        min=0.0,
        max=1000.0
    )
    slinkage: bpy.props.FloatProperty(
        name='slinkage',
        default=0.8,
        min=0.0,
        max=1000.0
    )
    axiom: bpy.props.StringProperty(
        name='start',
        default='X'
    )

    nrules:  bpy.props.IntProperty(
        name="rules",
        default=0,
        min=0,
        max=50,
        update=nupdate
    )

    def get_rules(self):
        rules = []
        for i in range(self.nrules):
            input_name = "input" + str(i + 1)
            condition_name = "condition" + str(i + 1)
            rule_name = "rule" + str(i + 1)
            input = getattr(self, input_name)
            condition = getattr(self, condition_name)
            rule = getattr(self, rule_name)
            if len(input) == 0 or len(rule) == 0:
                print("Invalid rule: '" + input + "', '" + rule + "'")
                continue
            rule = lsystem.ProductionRule(input, rule, condition)
            print(rule_name + ": " + str(rule))
            rules.append(rule)
        return rules

    def execute(self, context):
        axiomRule = lsystem.ProductionRule("", self.axiom)
        rules = self.get_rules()
        exec.execute(context,
                     axiomRule,
                     rules,
                     [],
                     self.instances,
                     self.seed,
                     self.min_iterations,
                     self.iterations,
                     self.angle,
                     self.length,
                     self.radius,
                     self.expansion,
                     self.shrinkage,
                     self.fat,
                     self.slinkage)

        return {'FINISHED'}

    def rescale(self, obj):
        msize = obj.dimensions.x
        if obj.dimensions.y > msize:
            msize = obj.dimensions.y
        if obj.dimensions.z > msize:
            msize = obj.dimensions.z

        s = 1.0 / msize
        obj.scale = ((s, s, s))

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, 'instances')
        box.prop(self, "seed")
        box.prop(self, "min_iterations")
        box.prop(self, "iterations")

        box = layout.box()
        box.label(text="Rules")
        box.prop(self, 'nrules')
        if getattr(self, 'axiom') == '':
            box.alert = True
        box.prop(self, 'axiom')

        for i in range(self.nrules):
            input = 'input' + str(i + 1)
            condition = 'condition' + str(i + 1)
            rule = 'rule' + str(i + 1)

            row = box.row(align=True)
            if getattr(self, input) == '' or getattr(self, rule) == '':
                row.alert = True
            row.prop(self, input, text=str(i))
            row.prop(self, condition, text="")
            row.prop(self, rule, text="")

        box = layout.box()
        box.label(text="Interpretation section")
        box.prop(self, "angle")
        box.prop(self, "length")
        box.prop(self, "expansion")
        box.prop(self, "shrinkage")
        box.prop(self, "fat")
        box.prop(self, "slinkage")


def make_annotations(cls):
    """Converts class fields to annotations if running with Blender 2.8"""
    if bpy.app.version < (2, 80):
        return cls
    bl_props = {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls


classes = (LSystemOperator,
           INFO_MT_curve_extras_add)


def register():
    bpy.types.Text.open_in_info_window = bpy.props.BoolProperty("Open in INFO window",
                                                                default=False,
                                                                update=openInInfoWin)
    #Traceback (most recent call last):
    # File "F:\SteamLibrary\steamapps\common\Blender\2.79\scripts\modules\addon_utils.py", line 350, in enablemod.register()
    # File "F:\SteamLibrary\steamapps\common\Blender\2.79\scripts\addons\lsystem\__init__.py", line 459, in register
    # textblock = bpy.data.texts.get("PASTE TEXT HERE")
    # AttributeError: '_RestrictData' object has no attribute 'texts'

    # textblock = bpy.data.texts.get("PASTE TEXT HERE")
    # if textblock is None:
    #     textblock = bpy.data.texts.new("PASTE TEXT HERE")
    #
    # JsonPanel.textblock = textblock

    for cls in classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)

    # Add "Extras" menu to the "Add Mesh" menu
    if bpy.app.version < (2, 80):
        bpy.types.INFO_MT_mesh_add.append(menu_func)
    else:
        bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # Remove "Extras" menu from the "Add Curve" menu.
    if bpy.app.version < (2,80):
        bpy.types.INFO_MT_mesh_add.remove(menu_func)
    else:
        bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()
