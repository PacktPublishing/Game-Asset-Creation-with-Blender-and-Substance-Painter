import bpy
from .subpanel import CompositorSubpanel
from .const import *

class NODE_EDITOR_PT_3D_Tudor_Effects(CompositorSubpanel):
    '''
    Subpanel for controlling background image
    '''
    bl_label = "Effects"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Effects"

    def draw(self, context): pass

#
# Filter Nodes (box sharpen, diamond sharpen, soften)
#

class CompositorSubpanelNode(CompositorSubpanel):
    bl_parent_id = "NODE_EDITOR_PT_3D_Tudor_Effects"
    bl_label = "Filter"
    bl_idname = "3DCompFXFilter"

    node = None
    prop_start, prop_end = 0, -1

    def __init__(self, node_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node = self.main_group.nodes[node_name]

    def draw_header(self,context):
        # enable
        self.layout.prop(self.node, "mute", text="", invert_checkbox=True)

    def draw(self, context):
        for i in list(self.node.inputs)[self.prop_start : self.prop_end]:
            self.layout.row().prop(i, "default_value", text=i.name)

    def rewrite_prop(self, p: str):
        return p.capitalize().replace("_", " ")

class NODE_EDITOR_PT_3D_Tudor_FX_Filter_DS(CompositorSubpanelNode):
    bl_label = "Diamond Sharpen"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_FX_Filter_DS"

    def __init__(self, *args, **kwargs):
        super().__init__("Filter", *args, **kwargs)

class NODE_EDITOR_PT_3D_Tudor_FX_Filter_BS(CompositorSubpanelNode):
    bl_label = "Box Sharpen"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_FX_Filter_BS"

    def __init__(self, *args, **kwargs):
        super().__init__("Filter.002", *args, **kwargs)

class NODE_EDITOR_PT_3D_Tudor_FX_Filter_S(CompositorSubpanelNode):
    bl_label = "Soften"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_FX_Filter_S"

    def __init__(self, *args, **kwargs):
        super().__init__("Filter.001", *args, **kwargs)

class NODE_EDITOR_PT_3D_Tudor_FX_AntiAliasing(CompositorSubpanelNode):
    bl_label = "Anti-Aliasing"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_FX_AntiAliasing"

    def __init__(self, *args, **kwargs):
        super().__init__("Anti-Aliasing", *args, **kwargs)
    
    def draw(self, context):
        for p in ["threshold", "contrast_limit", "corner_rounding"]:
            self.layout.row().prop(self.node, p, text=self.rewrite_prop(p))


class NODE_EDITOR_PT_3D_Tudor_FX_ColorBalance(CompositorSubpanelNode):
    bl_label = "Color Balance"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_FX_ColorBalance"

    def __init__(self, *args, **kwargs):
        super().__init__("Color Balance", *args, **kwargs)
    
    def draw(self, context):
        self.draw_color_balance(self.node, in_box=False)

class NODE_EDITOR_PT_3D_Tudor_FX_RGBCurves(CompositorSubpanelNode):
    bl_label = "RGB Curves"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_FX_RGBCurves"

    def __init__(self, *args, **kwargs):
        super().__init__("RGB Curves", *args, **kwargs)
    
    def draw(self, context):
        self.draw_rgb_curve("", self.node, in_box=False)

class NODE_EDITOR_PT_3D_Tudor_FX_HueCorrect(CompositorSubpanelNode):
    bl_label = "Hue Correct"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_FX_HueCorrect"

    def __init__(self, *args, **kwargs):
        super().__init__("Hue Correct", *args, **kwargs)
    
    def draw(self, context):
        self.draw_rgb_curve("", self.node, in_box=False, type='HUE')

class NODE_EDITOR_PT_3D_Tudor_FX_BrightContrast(CompositorSubpanelNode):
    bl_label = "Brightness/Contrast"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_FX_BrightContrast"

    def __init__(self, *args, **kwargs):
        super().__init__("Brightness/Contrast", *args, **kwargs)
        self.prop_start = 1
        self.prop_end = 3
    
class NODE_EDITOR_PT_3D_Tudor_FX_HSV(CompositorSubpanelNode):
    bl_label = "Hue/Saturation/Value"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_FX_HSV"

    def __init__(self, *args, **kwargs):
        super().__init__("Hue/Saturation/Value", *args, **kwargs)

    def draw(self, context):
        self.draw_hsv(self.node, in_box = False)

class NODE_EDITOR_PT_3D_Tudor_FX_Denoise(CompositorSubpanelNode):
    bl_label = "Denoise"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_FX_Denoise"

    def __init__(self, *args, **kwargs):
        super().__init__("Denoise", *args, **kwargs)

    def draw(self, context):
        self.layout.row().prop(self.node, "prefilter", text="Prefilter")
        self.layout.row().prop(self.node, "use_hdr", text="Use HDR")

fx_panels = [
    NODE_EDITOR_PT_3D_Tudor_Effects, NODE_EDITOR_PT_3D_Tudor_FX_Filter_DS,
    NODE_EDITOR_PT_3D_Tudor_FX_Filter_BS, NODE_EDITOR_PT_3D_Tudor_FX_Filter_S,
    NODE_EDITOR_PT_3D_Tudor_FX_AntiAliasing, NODE_EDITOR_PT_3D_Tudor_FX_ColorBalance,
    NODE_EDITOR_PT_3D_Tudor_FX_RGBCurves, NODE_EDITOR_PT_3D_Tudor_FX_HueCorrect,
    NODE_EDITOR_PT_3D_Tudor_FX_BrightContrast, NODE_EDITOR_PT_3D_Tudor_FX_HSV,
    NODE_EDITOR_PT_3D_Tudor_FX_Denoise
]