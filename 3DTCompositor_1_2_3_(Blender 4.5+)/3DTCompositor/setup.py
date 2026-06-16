import bpy
import addon_utils
import os
from .const import *
from .subpanel import CompositorSubpanel
from .preset import *
import json
import addon_utils

class Add3DTudorCompositorOperator(bpy.types.Operator):
    bl_idname = "object.3dt_add"
    bl_label = "Setup 3DT Compositor"

    apply_settings: bpy.props.BoolProperty(default=True)

    def append_data(self) -> bool:
        '''
        append node tree from nodetree.py + workspace
        '''

        # check if not appended yet
        if NODE_GROUP_NAME in bpy.data.node_groups and WORKSPACE_NAME in bpy.data.workspaces: 
            return True

        # find path of addon
        path = None
        for mod in addon_utils.modules():
            if mod.bl_info['name'] == ADDON_NAME:
                path = mod.__file__

        if path == None: return False

        # get folder
        folder = os.path.dirname(path)

        # create path to .blend file containing needed group
        blend_file = os.path.join(folder, NODE_GROUP_FILE)
        with bpy.data.libraries.load(blend_file) as (data_from, data_to):
            if NODE_GROUP_NAME in data_from.node_groups and WORKSPACE_NAME in data_from.workspaces:
                if not NODE_GROUP_NAME in bpy.data.node_groups:
                    bpy.ops.wm.append(filename=NODE_GROUP_NAME, directory=os.path.join(blend_file, "NodeTree", ""), check_existing=True)
                    print("Node Tree added successfully")
                if not WORKSPACE_NAME in bpy.data.workspaces:
                    bpy.ops.wm.append(filename=WORKSPACE_NAME, directory=os.path.join(blend_file, "WorkSpace", ""), check_existing=True)
                    print("Workspace added successfully")
                return True
        return False
    
    def setup_node_tree(self, context):
        '''
        Setup Compositor to use nodes, add Compositor node group and add all connections
        '''
        scene = bpy.data.scenes["Scene"]
        # use nodes
        scene.use_nodes = True
        # remove all nodes
        nodes = scene.node_tree.nodes
        for node in nodes:
            nodes.remove(node)

        # set cycles as render engine
        scene.render.engine = 'CYCLES'

        if self.apply_settings:
            # enable background transparency
            scene.render.film_transparent = True
            # compositor performace
            scene.render.compositor_device = 'GPU'
            bpy.context.scene.cycles.device = 'GPU'
            # set tile size to 2048
            bpy.context.scene.cycles.tile_size = 2048
            # set output to PNG
            context.scene.render.image_settings.file_format = "PNG"
            # set output color mode to RGBA
            context.scene.render.image_settings.color_mode = "RGBA"

        # enable mist viewport info in all cameras
        for c in bpy.data.cameras:
            c.show_mist = 1

        # add all needed nodes
        render_layers = nodes.new('CompositorNodeRLayers')
        render_layers.location.x = 0
        output = nodes.new("CompositorNodeComposite")
        output.location.x = 500
        comp_group = nodes.new('CompositorNodeGroup')
        comp_group.node_tree = bpy.data.node_groups[NODE_GROUP_NAME]
        comp_group.location.x = 300
        viewer = nodes.new("CompositorNodeViewer")
        viewer.location = (500, -120)
        file_out = nodes.new('CompositorNodeOutputFile')
        file_out.mute = True
        file_out.location = (500, -240)
        conn = scene.node_tree.links

        # move all nodes
        for n in nodes: n.location.x += 2000

        # output connections
        conn.new(comp_group.outputs['Image Output'], output.inputs['Image'])
        # viewer connections
        conn.new(comp_group.outputs['Image Output'], viewer.inputs['Image'])
        # file out connection
        conn.new(comp_group.outputs['Emission Pass'], file_out.inputs['Image'])

        vl = scene.view_layers[0]
        # render layer -> 3DT comps connections
        # alpha
        conn.new(render_layers.outputs['Alpha'], comp_group.inputs['Alpha'])
        # mist
        vl.use_pass_mist = True
        conn.new(render_layers.outputs['Mist'], comp_group.inputs['Mist'])
        # diffuse
        vl.use_pass_diffuse_direct = True
        vl.use_pass_diffuse_indirect = True
        vl.use_pass_diffuse_color = True
        conn.new(render_layers.outputs['DiffDir'], comp_group.inputs['Diff Direct'])
        conn.new(render_layers.outputs['DiffInd'], comp_group.inputs['Diff Indirect'])
        conn.new(render_layers.outputs['DiffCol'], comp_group.inputs['Diff Color'])
        # glossy
        vl.use_pass_glossy_direct = True
        vl.use_pass_glossy_indirect = True
        vl.use_pass_glossy_color = True
        conn.new(render_layers.outputs['GlossDir'], comp_group.inputs['Gloss Direct'])
        conn.new(render_layers.outputs['GlossInd'], comp_group.inputs['Gloss Indirect'])
        conn.new(render_layers.outputs['GlossCol'], comp_group.inputs['Gloss Color'])
        # transmission
        vl.use_pass_transmission_direct = True
        vl.use_pass_transmission_indirect = True
        vl.use_pass_transmission_color = True
        conn.new(render_layers.outputs['TransDir'], comp_group.inputs['Transmission Direct'])
        conn.new(render_layers.outputs['TransInd'], comp_group.inputs['Transmission Indirect'])
        conn.new(render_layers.outputs['TransCol'], comp_group.inputs['Transmission Color'])
        # volume
        bpy.data.scenes['Scene'].view_layers[0]['cycles']['use_pass_volume_direct'] = 1
        bpy.data.scenes['Scene'].view_layers[0]['cycles']['use_pass_volume_indirect'] = 1
        render_layers.update()
        conn.new(render_layers.outputs['VolumeDir'], comp_group.inputs['Volume Direct'])
        conn.new(render_layers.outputs['VolumeInd'], comp_group.inputs['Volume Indirect'])
        # emission
        vl.use_pass_emit = True
        conn.new(render_layers.outputs['Emit'], comp_group.inputs['Emission'])
        # environment
        vl.use_pass_environment = True
        conn.new(render_layers.outputs['Env'], comp_group.inputs['Environment'])
        # AO
        vl.use_pass_ambient_occlusion = True
        conn.new(render_layers.outputs['AO'], comp_group.inputs['AO'])
        # denoising
        bpy.data.scenes['Scene'].view_layers[0]['cycles']['denoising_store_passes'] = True
        render_layers.update()
        conn.new(render_layers.outputs['Denoising Normal'], comp_group.inputs['Denoise Normal'])
        conn.new(render_layers.outputs['Denoising Albedo'], comp_group.inputs['Denoise Albedo'])

        #bpy.ops.node.backimage_fit() # doesn't work :(

    def execute(self, context):
        if not self.append_data(): 
            self.report({'ERROR'}, 'Error while importing Compositor node group or Workspace.')
            return {'CANCELLED'}
        
        self.setup_node_tree(context)
        bpy.context.window.workspace = bpy.data.workspaces[WORKSPACE_NAME]
        self.report({'INFO'}, "3DT Compositor setup was successfull.")

        # set default background type to none
        props = context.scene.threedt_comp_props
        props.bg_type = "none"

        return {'FINISHED'}

    def draw(self, context):
        row = self.layout
        row.prop(self, "apply_settings", text="Apply Recommended Settings")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)