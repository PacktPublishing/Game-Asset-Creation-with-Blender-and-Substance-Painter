bl_info = {
    "name": "3D Tudor Compositor",
    "author": "3D Tudor, Vladan Trhlik",
    "version": (1, 2, 3),
    "blender": (4, 5, 0),
    "location": "Compositor > 3DT Compositor",
    "description": "",
    "category": "Compositing",
}

import bpy
from .panels import *
from .panels_fx import *
from .setup import *
from .preset import *
from bl_ui.generic_ui_list import draw_ui_list
        
class NODE_EDITOR_PT_3D_Tudor_Compositor(bpy.types.Panel):
    '''
    Main addon panel containing all sub panels
    '''
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = CATEGORY
    bl_label = "3D Tudor Compositor"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Compositor"

    group_name = "3D Tudor Compositor"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (self.group_name in bpy.data.node_groups):
            self.group = bpy.data.node_groups[self.group_name]
    
    def draw(self, context):
        self.layout.operator("object.3dt_add", text="Setup Compositor")
    
subpanels = [NODE_EDITOR_PT_3D_Tudor_Presets,  NODE_EDITOR_PT_3D_Tudor_Output, NODE_EDITOR_PT_3D_Tudor_Background, NODE_EDITOR_PT_3D_Tudor_Mist,
            NODE_EDITOR_PT_3D_Tudor_Color, NODE_EDITOR_PT_3D_Tudor_Gloss,
            NODE_EDITOR_PT_3D_Tudor_Trans, NODE_EDITOR_PT_3D_Tudor_Volume,
            NODE_EDITOR_PT_3D_Tudor_Light, NODE_EDITOR_PT_3D_Tudor_Environment,
            NODE_EDITOR_PT_3D_Tudor_AO
            ]

operators = [
    PresetImportExportMenu, Add3DTudorCompositorOperator, DefaultPreset, SavePreset, SavePresetToSelected, LoadPreset, RemovePreset, ImportPreset, ExportPreset
]
       
def register():    
    # operators
    for s in operators:
        bpy.utils.register_class(s)
    # properties
    bpy.utils.register_class(NODE_EDITOR_PT_3D_Tudor_Props)
    bpy.types.Scene.threedt_comp_props = bpy.props.PointerProperty(type=NODE_EDITOR_PT_3D_Tudor_Props)

    bpy.utils.register_class(Preset)
    bpy.utils.register_class(PresetList)
    bpy.utils.register_class(NODE_EDITOR_PT_3D_Tudor_Compositor)

    for s in subpanels + fx_panels:
        bpy.utils.register_class(s)


    # add properties
    bpy.types.Scene.presets = bpy.props.CollectionProperty(type=Preset)
    bpy.types.Scene.presets_index = bpy.props.IntProperty()
    bpy.types.Scene.presets_default = bpy.props.PointerProperty(type=Preset)
    bpy.types.Scene.settings = bpy.props.BoolProperty(default=True)

def unregister():
    bpy.utils.unregister_class(NODE_EDITOR_PT_3D_Tudor_Props)
    bpy.utils.unregister_class(NODE_EDITOR_PT_3D_Tudor_Compositor)
    bpy.utils.unregister_class(Preset)
    bpy.utils.unregister_class(PresetList)
    for s in subpanels + fx_panels:
        bpy.utils.unregister_class(s)
    for s in operators:
        bpy.utils.unregister_class(s)
    # delete props
    del bpy.types.Scene.threedt_comp_props
    del bpy.types.Scene.presets
    del bpy.types.Scene.presets_index
    del bpy.types.Scene.presets_default
    del bpy.types.Scene.settings

if __name__ == "__main__":
    register()
    
