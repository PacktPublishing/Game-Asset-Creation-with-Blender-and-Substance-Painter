import bpy
from .subpanel import CompositorSubpanel
from .const import *
from bpy_extras.node_utils import find_node_input
from .preset import *

class NODE_EDITOR_PT_3D_Tudor_Mist(CompositorSubpanel):
    '''
    Subpanel for controlling Mist
    '''
    bl_label = "Mist"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Mist"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = bpy.data.node_groups["Mist Controls"]
    
    def draw_header(self,context):
        # enable
        self.layout.prop(self.group.nodes["Switch.001"], "check", text="", invert_checkbox=True)
    
    def draw(self, context):
        # color
        box1 = self.layout.box()
        box1.row().prop(self.group.nodes["RGB"].outputs[0], "default_value", text="Color")
        box1.row().prop(bpy.data.worlds["World"].mist_settings, "start", text="Min")
        box1.row().prop(bpy.data.worlds["World"].mist_settings, "depth", text="Depth")
        self.draw_color_ramp("Depth", self.group.nodes["Color Ramp"])
        
class NODE_EDITOR_PT_3D_Tudor_AO(CompositorSubpanel):
    '''
    Subpanel for controlling Ambient Oclusion
    '''
    bl_label = "Ambient Oclusion"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_AO"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = bpy.data.node_groups["AO Controls"]
    
    def draw_header(self,context):
        # enable
        self.layout.prop(self.group.nodes["Switch"], "check", text="")
    
    def draw(self, context):
        # colorramp control 
        self.draw_color_ramp("Control", self.group.nodes["Color Ramp"])
        #color
        box = self.layout.row().box()
        mix_node = self.group.nodes["Mix"]
        row = box.row()
        row.prop(mix_node, "mute", text="", invert_checkbox=True)
        row.label(text="Color")
        row.prop(self.group.nodes["RGB"].outputs[0], "default_value", text="")
        # curve master control
        self.draw_rgb_curve("Master Control", self.group.nodes["RGB Curves"])
        
class NODE_EDITOR_PT_3D_Tudor_Color(CompositorSubpanel):
    '''
    Subpanel for controlling color
    '''
    bl_label = "Color"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Color"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = bpy.data.node_groups["Color Controls"]
    
    def draw(self, context):
        # factor
        self.layout.row().prop(self.main_group.nodes["Group.007"].inputs[0], "default_value", text="Color Factor")
        # depth
        self.draw_rgb_curve("Depth", self.group.nodes["RGB Curves"])
        # HSV
        self.draw_hsv(self.group.nodes["Hue/Saturation/Value"])
        
class NODE_EDITOR_PT_3D_Tudor_Gloss(CompositorSubpanel):
    '''
    Subpanel for controlling color
    '''
    bl_label = "Gloss"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Gloss"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = bpy.data.node_groups["Gloss Controls"]
    
    def draw(self, context):
        self.draw_rgb_curve("Level", self.group.nodes["RGB Curves.001"])
        # brightness
        # # # # # # # # nodes["Brightness/Contrast"].inputs[1].default_value
        box = self.layout.box()
        box.prop(self.group.nodes["Brightness/Contrast"].inputs[1], "default_value", text="Bright")
        box.prop(self.group.nodes["Brightness/Contrast"].inputs[2], "default_value", text="Contrast")
        # self.draw_color_ramp("Depth", self.group.nodes["Color Ramp"])
        box.prop(self.group.nodes["Mix"].inputs[0], "default_value", text="Metal Glint")
        
class NODE_EDITOR_PT_3D_Tudor_Trans(CompositorSubpanel):
    # TODO: switch changed
    '''
    Subpanel for controlling transmission
    '''
    bl_label = "Transmission"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Trans"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = bpy.data.node_groups["Trans Controls"]

    def update_light(props, context):
        node_names = ["Glare", "Glare.001"]
        group = bpy.data.node_groups["Trans Controls"]
        for i in range(len(node_names)):
            group.nodes[node_names[i]].mute = i >= props.transmission_light_level
        return None
    
    def draw(self, context):
        props = context.scene.threedt_comp_props

        self.draw_rgb_curve("Depth", self.group.nodes["RGB Curves"])
        self.draw_color_balance(self.group.nodes["Color Balance"])
        self.layout.box().prop(props, "transmission_light_level", text="Light Level")
        
class NODE_EDITOR_PT_3D_Tudor_Volume(CompositorSubpanel):
    '''
    Subpanel for controlling volume
    '''
    bl_label = "Volume"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Volume"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = bpy.data.node_groups["Volume Controls"]
    
    def draw_header(self,context):
        # enable
        self.layout.prop(self.group.nodes["Switch"], "check", text="", invert_checkbox=True)
    
    def draw(self, context):
        #self.draw_color_ramp("Controls", self.group.nodes["Color Ramp"])
        self.draw_rgb_curve("Depth", self.group.nodes["RGB Curves"])
        
        box = self.layout.box()
        row = box.row()
        #row.prop(self.group.nodes["Mix.006"].inputs[1], "default_value", text="Color")
        row.prop(self.group.nodes["RGB"].outputs[0], "default_value", text="Color")
        row = box.row()

        #row.prop(self.group.nodes["Math"].inputs[1], "default_value", text="Density")
        row.prop(self.group.nodes["Value"].outputs[0], "default_value", text="Density")

class NODE_EDITOR_PT_3D_Tudor_Light(CompositorSubpanel):
    '''
    Subpanel for controlling volume
    '''
    bl_label = "Light / Bloom"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Light"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = bpy.data.node_groups["Light Controls"]

    def update_glare(props, context):
        node_names = ["Glare", "Glare.003", "Glare.004"]
        group = bpy.data.node_groups["Light Controls"]
        for i in range(len(node_names)):
            group.nodes[node_names[i]].mute = i >= props.glare_level
            group.nodes[node_names[i]].glare_type = props.glare_type
        return None
    
    def draw(self, context):
        props = context.scene.threedt_comp_props

        layout = self.layout.box()
        # bloom level
        layout.row().prop(props, "glare_level", text="Bloom Level")
        # bloom type
        layout.row().prop(props, "glare_type", text="Bloom Type")
        # bloom
        '''
        row = layout.row()
        row.prop(self.group.nodes["Glare.001"], "mute", text="Bloom", invert_checkbox = True)
        '''
        # lens flare strength
        row = layout.row()
        row.prop(self.group.nodes["Mix.001"].inputs[0], "default_value", text="Lens Flare Strength")
        # lens flare glare threshold
        row = layout.row()
        row.prop(self.group.nodes["Glare.001"], "threshold", text="Lens Flare Threshold")
        # streaks
        row = layout.row()
        row.prop(self.group.nodes["Glare.002"], "mute", text="Streaks", invert_checkbox = True)
        # increase light range
        row = layout.row()
        row.prop(self.group.nodes["Gamma"], "mute", text="Increase Light Range", invert_checkbox = True)

        # brightness
        self.draw_rgb_curve("Brightness", self.group.nodes["RGB Curves"])
        # color change
        row = self.layout.box().row()
        row.prop(self.group.nodes["Mix"], "mute", text="", invert_checkbox=True)
        
        row.prop(self.group.nodes["RGB"].outputs[0], "default_value", text="Color Change")
        # box.prop(self.group.nodes["Mix"].inputs[0], "default_value", text="Factor")

class NODE_EDITOR_PT_3D_Tudor_Environment(CompositorSubpanel):
    '''
    Subpanel for controlling volume
    '''
    bl_label = "Environment"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Environment"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = bpy.data.node_groups["Environment Controls"]

    def draw(self, context):
        self.layout.row().prop(self.main_group.nodes["Group.020"].inputs[0], "default_value", text="Environment Factor")
        self.draw_rgb_curve("Brightness", self.group.nodes["RGB Curves.001"])
        self.draw_color_balance(self.group.nodes["Color Balance"])
class NODE_EDITOR_PT_3D_Tudor_Background(CompositorSubpanel):
    '''
    Subpanel for controlling background image
    '''
    bl_label = "Background"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Background"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = bpy.data.node_groups["Background Image"]

    def update_bg_type(props, context):
        val = props.bg_type
        main_group = bpy.data.node_groups[NODE_GROUP_NAME]
        # alpha
        main_group.nodes["Switch"].check = val == "none"
        # image
        props.bg_image = val == "img"

        return None

    def update_img(props, context):
        val = props.bg_image
        group = bpy.data.node_groups["Background Image"]
        # change value of both switch nodes
        group.nodes["Switch.002"].check = val
        group.nodes["Switch.001"].check = val
        return None

    def draw(self, context):
        props = context.scene.threedt_comp_props
        # bg type
        self.layout.row().prop(props, "bg_type", text="Type")

        if props.bg_type != "img": return

        # get image node
        img_node = self.group.nodes['Image.001']
        input = find_node_input(img_node, "Image")
        # image source
        box = self.layout.box()
        box.label(text="Image Source:")
        box.template_node_view(self.group, img_node, input)
        # image transform
        box = self.layout.box()
        box.label(text="Transform:")
        for i in list(self.group.nodes['Transform'].inputs)[1:]:
            box.row().prop(i, "default_value", text=i.name)
        # image brightness
        self.draw_rgb_curve("Brightness", self.group.nodes["RGB Curves.001"])

class NODE_EDITOR_PT_3D_Tudor_Output(CompositorSubpanel):
    '''
    Subpanel for output files (render, emission pass)
    '''
    bl_label = "Output"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Output"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, context):
        res = self.layout.box()
        res.label(text = "Resolution")
        res.row().prop(bpy.context.scene.render, "resolution_x", text="X")
        res.row().prop(bpy.context.scene.render, "resolution_y", text="Y")

        r = bpy.data.scenes["Scene"].render
        render = self.layout.box()
        render.label(text="Render")
        render.row().prop(r, "filepath", text="Base Path")
        render.row().prop(r.image_settings, "file_format", text="File Format")
        render.row().prop(r.image_settings, "color_depth", text="Color Depth")
        render.row().prop(r.image_settings, "compression", text="Compression")

        node = context.scene.node_tree.nodes["File Output"]
        emission_pass = self.layout.box()

        emission_pass.row().prop(node, "mute", text="Bloom Pass", invert_checkbox=True)
        emission_pass.row().prop(node, "base_path", text="Base Path")
        emission_pass.row().prop(node.format, "file_format", text="File Format")
        emission_pass.row().prop(node.format, "color_depth", text="Color Depth")
        emission_pass.row().prop(node.format, "compression", text="Compression")


class NODE_EDITOR_PT_3D_Tudor_Props(bpy.types.PropertyGroup):
    bg_image: bpy.props.BoolProperty(name="Toggle Option", update=NODE_EDITOR_PT_3D_Tudor_Background.update_img)
    glare_level: bpy.props.IntProperty(name="Glare Level", min=0, max=3, update=NODE_EDITOR_PT_3D_Tudor_Light.update_glare)
    transmission_light_level: bpy.props.IntProperty(name="Trans Light Level", min=0, max=2, update=NODE_EDITOR_PT_3D_Tudor_Trans.update_light)
    bg_type: bpy.props.EnumProperty(
        items=(
            ("none", "None", ""),
            ("alpha", "Alpha", ""),
            ("img", "Image", "")
        ), 
        name="Background Type", default="none", update=NODE_EDITOR_PT_3D_Tudor_Background.update_bg_type
    )
    glare_type: bpy.props.EnumProperty(
        items=(
            ("BLOOM", "Bloom", ""),
            ("GHOSTS", "Ghosts", ""),
            ("STREAKS", "Streaks", ""),
            ("FOG_GLOW", "Fog Glow", ""),
            ("SIMPLE_STAR", "Simple Star", ""),
        ),
        name="Bloom Type", default="BLOOM", update=NODE_EDITOR_PT_3D_Tudor_Light.update_glare
    )

    settings = bpy.props.BoolProperty()
    presets = bpy.props.CollectionProperty(type=Preset)
    presets_index = bpy.props.IntProperty()