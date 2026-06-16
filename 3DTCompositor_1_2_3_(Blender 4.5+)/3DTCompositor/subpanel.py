import bpy
from .const import *

class CompositorSubpanel(bpy.types.Panel):
    '''
    Simple subpanel for 3D Tudor Compositor
    '''
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = CATEGORY
    bl_parent_id = "NODE_EDITOR_PT_3D_Tudor_Compositor"
    bl_options = {'DEFAULT_CLOSED'}

    main_group = None
    group = None
    group_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if NODE_GROUP_NAME in bpy.data.node_groups:
            self.main_group = bpy.data.node_groups[NODE_GROUP_NAME]

    @classmethod
    def poll(cls, context):
        return NODE_GROUP_NAME in bpy.data.node_groups
    
    def draw_color_ramp(self, label, ramp):
        box = self.layout.box()
        box.row().label(text=label + ":")
        box.template_color_ramp(ramp, "color_ramp", expand=False)
    
    def draw_rgb_curve(self, label, curve, in_box=True, type='NONE'):
        box = self.layout
        if in_box:
            box = self.layout.box()
            box.row().label(text=label + ":")
        box.template_curve_mapping(curve, "mapping", type=type)   
    
    def draw_hsv(self, hsv, label="HSV", in_box=True):
        box = self.layout
        if in_box:
            box = self.layout.box()
            box.label(text=label + ":")

        for i in list(hsv.inputs)[1:4]:
            box.row().prop(i, "default_value", text=i.name)
            
    def draw_color_balance(self, col, label="Color", in_box = True):
        if in_box:
            box = self.layout.box()
            box.label(text=label + ":")
        else:
            box = self.layout

        for i in ["lift", "gamma", "gain"]:
            box.row().prop(col, i, text=i.capitalize())
    
    def apply_values(values):
        print(f"{bl_idname}: applying values")
