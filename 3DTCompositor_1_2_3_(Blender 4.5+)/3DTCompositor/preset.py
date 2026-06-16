import bpy
from .subpanel import *
import json
import addon_utils
import os
from bpy_extras.io_utils import ImportHelper, ExportHelper 
from bpy.types import Operator
import copy

class Preset(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    # .json data in string
    data: bpy.props.StringProperty(default="")
    problematic: bpy.props.BoolProperty(default=False)

    def store_color_ramp(self, ramp):
        return {str(e.position): list(e.color) for e in ramp.elements}

    def store_hsv(self, hsv):
        return [i.default_value for i in hsv.inputs[1:]]

    def store_float_curve(self, curve):
        return [list(p.location) for p in curve.mapping.curves[3].points]

    def store_hue_correct_curve(self, curve):
        return [[list(p.location) for p in c.points] for c in curve.mapping.curves] 

    def store_lgg(self, lgg):
        return [list(i) for i in [lgg.lift, lgg.gamma, lgg.gain]]

    def store_simple_fx(self, node):
        return {
            "enable": 1 if not node.mute else 0,
            "factor": node.inputs[0].default_value
        }

    def store(self, context):
        print(f"storing to {self.name}")
        data = {}
        self.problematic = False

        scene = bpy.data.scenes["Scene"]
        comp = bpy.data.node_groups[NODE_GROUP_NAME]
        # background
        data["bg_type"] = scene.threedt_comp_props.bg_type 

        # mist
        mist_g = bpy.data.node_groups["Mist Controls"]
        data["mist"] = {
            "enable": 1 if not mist_g.nodes["Switch.001"].check else 0,
            #"color": list(mist_g.nodes["Mix.008"].inputs[2].default_value),
            "color": list(mist_g.nodes["RGB"].outputs[0].default_value),
            "_ramp": self.store_color_ramp(mist_g.nodes["Color Ramp"].color_ramp)
        }

        # color
        color_g = bpy.data.node_groups["Color Controls"]
        data["color"] = {
            "factor": comp.nodes["Group.007"].inputs[0].default_value,
            "depth": self.store_float_curve(color_g.nodes["RGB Curves"]),
            "hsv": self.store_hsv(color_g.nodes["Hue/Saturation/Value"])
        }

        # gloss
        gloss_g = bpy.data.node_groups["Gloss Controls"]
        data["gloss"] = {
            "level": self.store_float_curve(gloss_g.nodes["RGB Curves.001"]),
            "bright": gloss_g.nodes["Brightness/Contrast"].inputs[1].default_value,
            "contrast": gloss_g.nodes["Brightness/Contrast"].inputs[2].default_value,
            "metal_glint": gloss_g.nodes["Mix"].inputs[0].default_value
        }

        # transmission
        trans_g = bpy.data.node_groups["Trans Controls"]
        data["trans"] = {
            "depth": self.store_float_curve(trans_g.nodes["RGB Curves"]),
            "lgg": self.store_lgg(trans_g.nodes["Color Balance"]),
            "light_level": scene.threedt_comp_props.transmission_light_level
        }

        # volume
        volume_g = bpy.data.node_groups["Volume Controls"]
        data["volume"] = {
            "enable": 1 if not volume_g.nodes["Switch"].check else 0,
            "depth": self.store_float_curve(volume_g.nodes["RGB Curves"]),
            #"color": list(volume_g.nodes["Mix.006"].inputs[1].default_value),
            "color": list(volume_g.nodes["RGB"].outputs[0].default_value),
            "density": volume_g.nodes["Value"].outputs[0].default_value,
        }

        # light bloom
        light_g = bpy.data.node_groups["Light Controls"]
        data["light_bloom"] = {
            "lvl": scene.threedt_comp_props.glare_level,
            "type": scene.threedt_comp_props.glare_type,
            "lens_flare_strength": light_g.nodes["Mix.001"].inputs[0].default_value,
            "lens_flare_threshold": light_g.nodes["Glare.001"].threshold,
            "streaks": 1 if not light_g.nodes["Glare.002"].mute else 0,
            "increase_light_range": 1 if not light_g.nodes["Gamma"].mute else 0,
            "bright": self.store_float_curve(light_g.nodes["RGB Curves"]),
            "color_change_enable": 1 if not light_g.nodes["Mix"].mute else 0,
            #"color_change_col": list(light_g.nodes["Mix"].inputs[2].default_value),
            "color_change_col": list(light_g.nodes["RGB"].outputs[0].default_value),
            "render_output": 0 if context.scene.node_tree.nodes["File Output"].mute else 1,
        }

        # environment
        env_g = bpy.data.node_groups["Environment Controls"]
        data["environment"] = {
            "factor": comp.nodes["Group.020"].inputs[0].default_value,
            "bright": self.store_float_curve(env_g.nodes["RGB Curves.001"]),
            "lgg": self.store_lgg(env_g.nodes["Color Balance"])
        }

        # AO
        ao_g = bpy.data.node_groups["AO Controls"]
        data["ao"] = {
            "enable": 1 if ao_g.nodes["Switch"].check else 0,
            "_control": self.store_color_ramp(ao_g.nodes["Color Ramp"].color_ramp),
            "color_enable": 1 if not ao_g.nodes["Mix"].mute else 0,
            #"color_col": list(ao_g.nodes["Mix"].inputs[1].default_value),
            "color_col": list(ao_g.nodes["RGB"].outputs[0].default_value),
            "master_control": self.store_float_curve(ao_g.nodes["RGB Curves"])
        }

        # Effects
        data["fx"] = {
            "dia_sharpen": self.store_simple_fx(comp.nodes["Filter"]),
            "box_sharpen": self.store_simple_fx(comp.nodes["Filter.002"]),
            "soften": self.store_simple_fx(comp.nodes["Filter.001"]),
            "anti_aliasing": {
                "enable": 1 if not comp.nodes["Anti-Aliasing"].mute else 0,
                "threshold": comp.nodes["Anti-Aliasing"].threshold,
                "contrast_limit": comp.nodes["Anti-Aliasing"].contrast_limit,
                "corner_rounding": comp.nodes["Anti-Aliasing"].corner_rounding
            },
            "color_balance": {
                "enable": 1 if not comp.nodes["Color Balance"].mute else 0,
                "lgg": self.store_lgg(comp.nodes["Color Balance"])
            },
            "rgb": {
                "enable": 1 if not comp.nodes["RGB Curves"].mute else 0,
                "curve": self.store_float_curve(comp.nodes["RGB Curves"])
            },
            "hue_correct": {
                "enable": 1 if not comp.nodes["Hue Correct"].mute else 0,
                "hue": self.store_hue_correct_curve(comp.nodes["Hue Correct"])
            },
            "bright": {
                "enable": 1 if not comp.nodes["Brightness/Contrast"].mute else 0,
                "bright": comp.nodes["Brightness/Contrast"].inputs[1].default_value,
                "contrast": comp.nodes["Brightness/Contrast"].inputs[2].default_value
            },
            "hsv": {
                "enable": 1 if not comp.nodes["Hue/Saturation/Value"].mute else 0,
                "hsv": self.store_hsv(comp.nodes["Hue/Saturation/Value"])
            },
            "denoise": {
                "enable": 1 if not comp.nodes["Denoise"].mute else 0,
                "prefilter": comp.nodes["Denoise"].prefilter,
                "use_hdr": 1 if comp.nodes["Denoise"].use_hdr else 0
            }
        }
        self.data = json.dumps(data)

    def load_simple_fx(self, node, data):
        node.mute = not data["enable"]
        node.inputs[0].default_value = data["factor"]

    def load_lgg(self, lgg, lgg_values):
        lgg.lift, lgg.gamma, lgg.gain = lgg_values
    
    def load_hsv(self, hsv, hsv_values):
        for i, val in enumerate(hsv_values):
            hsv.inputs[i+1].default_value = val

    def load_float_curve(self, curve, curve_values):
        curve = curve.mapping  # Get the curve mapping

        # Reset the curve by clearing points and adding default ones
        for curve_point in curve.curves:
            while len(curve_point.points) > 2:
                curve_point.points.remove(curve_point.points[0])
            for i in range(len(curve_values) - 2):
                curve_point.points.new(0, 0)
            # set positions
            for i, pos in enumerate(curve_values):
                curve_point.points[i].location = pos
        
        curve.update()

    def load_hue_correct_curve(self, curve, curve_values):
        curve = curve.mapping  # Get the curve mapping

        # Reset the curve by clearing points and adding default ones
        for j, curve_point in enumerate(curve.curves):
            while len(curve_point.points) > 2:
                curve_point.points.remove(curve_point.points[0])
            for i in range(len(curve_values[j]) - 2):
                curve_point.points.new(0, 0)
            # set positions
            for i, pos in enumerate(curve_values[j]):
                curve_point.points[i].location = pos
        
        curve.update()
    
    def load_color_ramp(self, ramp, ramp_values):
        count = len(ramp.elements.values())
        for i in range(count - 1):
            ramp.elements.remove(ramp.elements.values()[0])
        for i in range(len(ramp_values) - 1):
            ramp.elements.new(0)

        # set values
        for i, v in enumerate(ramp_values.keys()):
            ramp.elements[i].position = float(v)
            ramp.elements[i].color = ramp_values[v]
    
    def fix_dict(self, d, ref, path):
        for key in list(ref.keys()):
            if key not in d:
                d[key] = copy.deepcopy(ref[key])
                print(f"Key{path}: '{key}' not found, using defaults")
                self.problematic = True
            elif type(ref[key]) is dict and key[0] != "_":
                self.fix_dict(d[key], ref[key], path + " " + key)

    def load(self, context):
        data = json.loads(self.data)
        
        scene = bpy.data.scenes["Scene"]
        comp = bpy.data.node_groups[NODE_GROUP_NAME]
        # background
        scene.threedt_comp_props.bg_type = data["bg_type"]

        if len(scene.presets_default.data) == 0:
            bpy.ops.object.threedt_default_preset()

        # fix missing fields
        default = json.loads(scene.presets_default.data)
        self.problematic = False
        self.fix_dict(data, default, "")
        # mist
        mist_g = bpy.data.node_groups["Mist Controls"]
        mist_d = data["mist"]
        mist_g.nodes["Switch.001"].check = not mist_d["enable"]
        #mist_g.nodes["Mix.008"].inputs[2].default_value = mist_d["color"]
        mist_g.nodes["RGB"].outputs[0].default_value = mist_d["color"]
        self.load_color_ramp(mist_g.nodes["Color Ramp"].color_ramp, mist_d["_ramp"])

        # color
        color_d = data["color"]
        comp.nodes["Group.007"].inputs[0].default_value = color_d["factor"]
        color_g = bpy.data.node_groups["Color Controls"]
        self.load_float_curve(color_g.nodes["RGB Curves"], color_d["depth"])
        self.load_hsv(color_g.nodes["Hue/Saturation/Value"], color_d["hsv"])

        # gloss
        gloss_g = bpy.data.node_groups["Gloss Controls"]
        gloss_d = data["gloss"]
        self.load_float_curve(gloss_g.nodes["RGB Curves.001"], gloss_d["level"])
        gloss_g.nodes["Brightness/Contrast"].inputs[1].default_value = gloss_d["bright"]
        gloss_g.nodes["Brightness/Contrast"].inputs[2].default_value = gloss_d["contrast"]
        gloss_g.nodes["Mix"].inputs[0].default_value = gloss_d["metal_glint"]

        # transmission
        trans_g = bpy.data.node_groups["Trans Controls"]
        trans_d = data["trans"]
        self.load_float_curve(trans_g.nodes["RGB Curves"], trans_d["depth"])
        self.load_lgg(trans_g.nodes["Color Balance"], trans_d["lgg"])
        scene.threedt_comp_props.transmission_light_level = trans_d["light_level"]

        # volume
        volume_g = bpy.data.node_groups["Volume Controls"]
        volume_d = data["volume"]
        volume_g.nodes["Switch"].check = not volume_d["enable"]
        self.load_float_curve(volume_g.nodes["RGB Curves"], volume_d["depth"])
        volume_g.nodes["RGB"].outputs[0].default_value = volume_d["color"]
        volume_g.nodes["Value"].outputs[0].default_value = volume_d["density"]

        # light bloom
        light_g = bpy.data.node_groups["Light Controls"]
        light_d = data["light_bloom"]
        scene.threedt_comp_props.glare_level = light_d["lvl"]
        scene.threedt_comp_props.glare_type = light_d["type"]
        light_g.nodes["Mix.001"].inputs[0].default_value = light_d["lens_flare_strength"]
        light_g.nodes["Glare.001"].threshold = light_d["lens_flare_threshold"]
        light_g.nodes["Glare.002"].mute = not light_d["streaks"]
        light_g.nodes["Gamma"].mute = not light_d["increase_light_range"]
        self.load_float_curve(light_g.nodes["RGB Curves"], light_d["bright"])
        light_g.nodes["Mix"].mute = not light_d["color_change_enable"]
        light_g.nodes["RGB"].outputs[0].default_value = light_d["color_change_col"]
        context.scene.node_tree.nodes["File Output"].mute = not light_d["render_output"]

        # environment
        env_g = bpy.data.node_groups["Environment Controls"]
        env_d = data["environment"]
        comp.nodes["Group.020"].inputs[0].default_value = env_d["factor"]
        self.load_float_curve(env_g.nodes["RGB Curves.001"], env_d["bright"])
        self.load_lgg(env_g.nodes["Color Balance"], env_d["lgg"])

        # AO
        ao_g = bpy.data.node_groups["AO Controls"]
        ao_d = data["ao"]
        ao_g.nodes["Switch"].check = ao_d["enable"]
        self.load_color_ramp(ao_g.nodes["Color Ramp"].color_ramp, ao_d["_control"])
        ao_g.nodes["Mix"].mute = not ao_d["color_enable"]
        ao_g.nodes["RGB"].outputs[0].default_value = ao_d["color_col"]
        self.load_float_curve(ao_g.nodes["RGB Curves"], ao_d["master_control"])

        # Effects
        fx_d = data["fx"]

        self.load_simple_fx(comp.nodes["Filter"], fx_d["dia_sharpen"])
        self.load_simple_fx(comp.nodes["Filter.002"], fx_d["box_sharpen"])
        self.load_simple_fx(comp.nodes["Filter.001"], fx_d["soften"])

        # anti aliasing
        aa_d = fx_d["anti_aliasing"]
        comp.nodes["Anti-Aliasing"].mute = not aa_d["enable"]
        comp.nodes["Anti-Aliasing"].threshold = aa_d["threshold"]
        comp.nodes["Anti-Aliasing"].contrast_limit = aa_d["contrast_limit"]
        comp.nodes["Anti-Aliasing"].corner_rounding = aa_d["corner_rounding"]

        # color balance
        colb_d = fx_d["color_balance"]
        comp.nodes["Color Balance"].mute = not colb_d["enable"]
        self.load_lgg(comp.nodes["Color Balance"], colb_d["lgg"])

        # rgb
        rgb_d = fx_d["rgb"]
        comp.nodes["RGB Curves"].mute = not rgb_d["enable"]
        self.load_float_curve(comp.nodes["RGB Curves"], rgb_d["curve"])

        # hue correct
        comp.nodes["Hue Correct"].mute = not fx_d["hue_correct"]["enable"]
        self.load_hue_correct_curve(comp.nodes["Hue Correct"], fx_d["hue_correct"]["hue"])
        # TODO: hsv curve

        # brightness / contrast
        brgh_d = fx_d["bright"]
        comp.nodes["Brightness/Contrast"].mute = not brgh_d["enable"]
        comp.nodes["Brightness/Contrast"].inputs[1].default_value = brgh_d["bright"]
        comp.nodes["Brightness/Contrast"].inputs[2].default_value = brgh_d["contrast"]

        # hsv
        hsv_d = fx_d["hsv"]
        comp.nodes["Hue/Saturation/Value"].mute = not hsv_d["enable"]
        self.load_hsv(comp.nodes["Hue/Saturation/Value"], hsv_d["hsv"])

        # denoise
        denoise_d = fx_d["denoise"]
        comp.nodes["Denoise"].mute = not denoise_d["enable"]
        comp.nodes["Denoise"].prefilter = denoise_d["prefilter"]
        comp.nodes["Denoise"].use_hdr = denoise_d["use_hdr"]

class PresetList(bpy.types.UIList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        preset = item
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            if preset:
                #icon = 'SETTINGS'
                layout.prop(preset, "name", text="", emboss=False, icon_value=icon, icon='ERROR' if preset.problematic else 'SETTINGS')
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class PresetImportExportMenu(bpy.types.Menu):
    bl_idname = "NODE_EDITOR_MT_3D_Tudor_Presets_Menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.3dt_export_preset", text="Export Selected Preset", icon="EXPORT")
        layout.operator("object.3dt_import_preset", text="Import Preset", icon="IMPORT")
class NODE_EDITOR_PT_3D_Tudor_Presets(CompositorSubpanel):
    '''
    Subpanel for presets 
    '''
    bl_label = "Presets"
    bl_idname = "NODE_EDITOR_PT_3D_Tudor_Presets"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, context):
        self.layout.operator("object.threedt_default_preset", text="Load Defaults", icon="FILE_REFRESH")
        row = self.layout.row()
        row.template_list(
            "PresetList",
            "3dt_preset_list",
            context.scene,
            "presets",
            context.scene,
            "presets_index",
        )
        col = row.column(align=True)
        col.operator("object.3dt_save_preset", text="", icon="ADD")
        col.operator("object.3dt_remove_preset", text="", icon="REMOVE")
        col.separator()
        col.menu("NODE_EDITOR_MT_3D_Tudor_Presets_Menu", icon='DOWNARROW_HLT', text="")

        #col.operator("object.3dt_default_preset", text="", icon="FILE_REFRESH")

        row = self.layout.row(align=True)
        row.operator("object.3dt_save_preset_to_selected", text="Save")
        row.operator("object.3dt_load_preset", text="Load")

class SavePresetToSelected(bpy.types.Operator):
    bl_idname = "object.3dt_save_preset_to_selected"
    bl_label = "SavePreset2Selected3DTudorCompositor"

    @classmethod
    def poll(cls, context):
        s = context.scene
        return s.presets_index < len(s.presets)

    def execute(self, context):
        s = context.scene
        selected = s.presets[s.presets_index]
        selected.store(context)
        self.report({'INFO'}, f"Current state saved to '{selected.name}'")
        return {'FINISHED'}

class RemovePreset(bpy.types.Operator):
    bl_idname = "object.3dt_remove_preset"
    bl_label = "RemovePresetTudorCompositor"

    @classmethod
    def poll(cls, context):
        s = context.scene
        return s.presets_index < len(s.presets)

    def execute(self, context):
        i = context.scene.presets_index
        context.scene.presets.remove(i)
        return {'FINISHED'}

class LoadPreset(bpy.types.Operator):
    bl_idname = "object.3dt_load_preset"
    bl_label = "LoadPresetTudorCompositor"

    @classmethod
    def poll(cls, context):
        s = context.scene
        if s.presets_index >= len(s.presets): return False
        return len(s.presets[s.presets_index].data) > 0

    def execute(self, context):
        s = context.scene
        selected = s.presets[s.presets_index]
        selected.load(context)
        self.report({'INFO'}, f"State loaded from '{selected.name}'")
        return {'FINISHED'}

class SavePreset(bpy.types.Operator):
    bl_idname = "object.3dt_save_preset"
    bl_label = "SavePresetTudorCompositor"

    def execute(self, context):
        s = context.scene
        presets = s.presets
        new = presets.add()

        # generate new unique name
        names = [str(p.name) for p in presets]
        i = 1
        while f"Preset {i}" in names: i += 1
        new.name = f"Preset {i}"

        new.store(context)
        return {'FINISHED'}

class DefaultPreset(bpy.types.Operator):
    bl_idname = "object.threedt_default_preset"
    bl_label = "DefaultPreset3DTudorCompositor"

    def execute(self, context):
        d_preset = context.scene.presets_default
        if len(d_preset.data) == 0:
            # get working dir
            dir = None
            for mod in addon_utils.modules():
                if mod.bl_info.get("name") == ADDON_NAME:
                    dir = os.path.dirname(mod.__file__)

            with open(os.path.join(dir, 'defaults.json')) as f:
                defaults_dict = json.load(f)
                d_preset.data = json.dumps(defaults_dict)
        
        d_preset.load(context)
        return {'FINISHED'}

class ImportPreset(bpy.types.Operator, ImportHelper):
    bl_idname = "object.3dt_import_preset"
    bl_label = "Import Preset"

    def execute(self, context):
        with open(self.filepath) as f:
            try:
                d = json.load(f)
                data = json.dumps(d)
                s = context.scene
                presets = s.presets
                new = presets.add()
                new.name = os.path.basename(self.filepath)
                new.data = data
            except Exception as e:
                self.report({'WARNING'}, f"Invalid preset file ({e})")
                return {'CANCELLED'}
        self.report({'INFO'}, f"Preset imported successfully")
        return {'FINISHED'}

class ExportPreset(bpy.types.Operator, ExportHelper):
    bl_idname = "object.3dt_export_preset"
    bl_label = "Export Preset"
    filename_ext = ".json"

    @classmethod
    def poll(cls, context):
        s = context.scene
        if s.presets_index >= len(s.presets): return False
        return len(s.presets[s.presets_index].data) > 0

    def execute(self, context):
        s = context.scene
        selected = s.presets[s.presets_index]
        data = json.loads(selected.data)
        try:
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=4)
            self.report({'INFO'}, "Preset exported successfully")
        except:
            self.report({'WARNING'}, "Error while exporting preset")
        return {'FINISHED'}
