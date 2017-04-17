bl_info = {
    "name": "LSystem",
    "author": "krljg",
    "version": (0, 1),
    "blender": (2, 78, 0),
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

import math
import time
import random

import bpy
import bpy_extras.mesh_utils
import mathutils


# todo: Add ability to select pens and set materials/texture

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
        condition = 'condition'+str(n+1)
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


class LSystemOperator(bpy.types.Operator):
    """Add LSystem"""
    bl_idname="mesh.lsystem"
    bl_label = "LSystem"
    bl_description = "Create a new Lsystem mesh"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    instances = bpy.props.IntProperty(
        name="instances",
        default=1,
        min=1,
        max=1000000
    )
    seed = bpy.props.IntProperty(
        name="seed",
        default=0,
        min=0,
        max=1000000
    )
    min_iterations = bpy.props.IntProperty(
        name="min iterations",
        default=4,
        min=0,
        max=1000
    )
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
    length = bpy.props.FloatProperty(
        name='length',
        default=1.0,
        min=0.0,
        max=1000.0
    )
    radius = bpy.props.FloatProperty(
        name='radius',
        default=0.1,
        min=0.0,
        max=1000.0
    )
    expansion = bpy.props.FloatProperty(
        name='expansion',
        default=1.1,
        min=0.0,
        max=1000.0
    )
    shrinkage = bpy.props.FloatProperty(
        name='shrinkage',
        default=0.9,
        min=0.0,
        max=1000.0
    )
    fat = bpy.props.FloatProperty(
        name='fat',
        default=1.2,
        min=0.0,
        max=1000.0
    )
    slinkage = bpy.props.FloatProperty(
        name='slinkage',
        default=0.8,
        min=0.0,
        max=1000.0
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

    def run_once(self, context, instance, position, normal, seed, iterations, parent):
        start_time = time.time()
        self.print(start_time, "lsystem: execute\n  position = "+str(position)+"\n  seed = "+str(seed)+"\n  iterations = "+str(iterations))
        rules = []
        self.print(start_time, "axiom: "+self.axiom)
        for i in range(self.nrules):
            input_name = "input"+str(i+1)
            condition_name = "condition"+str(i+1)
            rule_name = "rule"+str(i+1)
            input = getattr(self, input_name)
            condition = getattr(self, condition_name)
            rule = getattr(self, rule_name)
            if len(input) == 0 or len(rule) == 0:
                print("Invalid rule: '"+input+"', '"+rule+"'")
                continue
            rule = lsystem.ProductionRule(input, rule, condition)
            print(rule_name+": "+str(rule))
            rules.append(rule)
        result = lsystem.iterate(instance, self.axiom, iterations, rules)
        self.print(start_time, "result: "+result)
        t = turtle.Turtle(seed)
        t.set_radius(self.radius)
        t.set_length(self.length)
        t.set_angle(self.angle)
        t.set_expansion(self.expansion)
        t.set_shrinkage(self.shrinkage)
        t.set_fat(self.fat)
        t.set_slinkage(self.slinkage)
        t.set_direction(mathutils.Vector((normal[0], normal[1], normal[2])))
        self.print(start_time, "turtle interpreting")
        object_base_pairs = t.interpret(result, context)
        self.print(start_time, "turtle finished")

        if position is not None:
            for pair in object_base_pairs:
                object = pair[0]
                object.location = position
                if parent is not None:
                    object.parent = parent

        return object_base_pairs

    def add_lsystem_to_object(self, ob, context):
        positions = []
        for i in range(0, self.instances):
            x = random.uniform(0, ob.dimensions.x) - ob.dimensions.x*0.5
            y = random.uniform(0, ob.dimensions.y) - ob.dimensions.y*0.5
            start = mathutils.Vector((x,y,-(ob.dimensions.z+1.0)))
            direction = mathutils.Vector((0, 0, 1))
            res, location, normal, index = ob.ray_cast(start, direction)
            if index == -1:
                print("dimensions = "+str(ob.dimensions))
                print("scale = "+str(ob.scale))
                print("start " + str(start))
                print("end " + str(direction))
                print("res: " + str(res) + ", location: " + str(location) + ", normal = " + str(
                    normal) + ", index = " + str(index))
                print("no intersection found")
                continue
            positions.append((i, location+ob.location))

        obj_base_pairs = []
        for i, position in positions:
            random.seed()
            seed = random.randint(0, 1000)
            iterations = random.randint(self.min_iterations, self.iterations)
            new_obj_base_pairs = self.run_once(context, i, position, mathutils.Vector((0.0, 0.0, 1.0)), seed, iterations, None)
            obj_base_pairs.extend(new_obj_base_pairs)
        return obj_base_pairs

    def add_lsystems_to_selected_faces(self, selected, context):
        random.seed(self.seed)
        tessfaces = []
        for ob in selected:
            me = ob.data
            me.calc_tessface()
            tessfaces_select = [(f, ob) for f in me.tessfaces if f.select]
            tessfaces.extend(tessfaces_select)

        positions = []
        for i in range(0, self.instances):
            face, ob = random.choice(tessfaces)
            new_positions = bpy_extras.mesh_utils.face_random_points(1, [face])
            position = new_positions[0]
            seed = random.randint(0,1000)
            if self.min_iterations >= self.iterations:
                iterations = self.min_iterations
            else:
                iterations = random.randint(self.min_iterations, self.iterations)
            positions.append((i, position, face.normal, seed, iterations, ob))

        obj_base_pairs = []
        for i, position, normal, seed, iterations, parent in positions:
            new_obj_base_pairs = self.run_once(context, i, position, normal, seed, iterations, parent)

            obj_base_pairs.extend(new_obj_base_pairs)
        return obj_base_pairs

    def add_lsystems_grid(self, context):
        seed = self.seed
        start_iter = self.min_iterations
        end_iter = self.iterations
        if start_iter >= end_iter:
            end_iter = start_iter+1
        object_base_pairs = []
        i = 0
        y = 0
        while i < self.instances:
            seed += 1
            max_ydim = 0
            x = 0
            row = []
            for iter in range(start_iter, end_iter):
                new_obj_base_list = self.run_once(context,
                                                      i,
                                                      mathutils.Vector((0.0, 0.0, 0.0)),
                                                      mathutils.Vector((0.0, 0.0, 1.0)),
                                                      seed,
                                                      iter,
                                                      None)
                object = new_obj_base_list[0][0]  # todo: handle multiple objects
                if iter == start_iter:
                    object.location.x = 0
                else:
                    object.location.x = x + object.dimensions.x * 0.75
                x = object.location.x + (object.dimensions.x * 0.75)
                if object.dimensions.y > max_ydim:
                    max_ydim = object.dimensions.y
                row.append(object)
                object_base_pairs.extend(new_obj_base_list)
                i += 1
                if i >= self.instances:
                    break
            if i >= end_iter:
                for object in row:
                    object.location.y = y + max_ydim * 0.75
                y += max_ydim * 1.5
            else:
                y = max_ydim * 0.75

        return object_base_pairs

    def execute(self, context):
        # Need to call scene.update for ray_cast method.
        # See http://blender.stackexchange.com/questions/40429/error-object-has-no-mesh-data-to-be-used-for-ray-casting
        bpy.context.scene.update()
        selected = bpy.context.selected_objects
        print("selected: "+str(selected))
        if len(selected) == 0:
            object_base_pairs = self.add_lsystems_grid(context)
        else:
            object_base_pairs = self.add_lsystems_to_selected_faces(selected, context)

        for ob in context.scene.objects:
            ob.select = False

        for obj_base_pair in object_base_pairs:
            base = obj_base_pair[1]
            base.select = True
        context.scene.objects.active = object_base_pairs[-1][0]

        return {'FINISHED'}

    def print(self, start_time, message):
        elapsed = time.time() - start_time
        print("%.5fs: %s" % (elapsed, message))

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
            input = 'input'+str(i+1)
            condition = 'condition'+str(i+1)
            rule = 'rule'+str(i+1)

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


def register():
    bpy.utils.register_module(__name__)

    # Add "Extras" menu to the "Add Mesh" menu
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    # Remove "Extras" menu from the "Add Curve" menu.
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()



