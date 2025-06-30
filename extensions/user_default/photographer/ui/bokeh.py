import bpy
from ..functions.functions import get_camera_object

# Function to add Bokeh and Optical Vignetting to Camera Properties UI
def bokeh_ui(self, context, layout=None, add_on_panel=False):
    if layout is None:
        layout = self.layout
    if add_on_panel:
        settings = context.scene.camera.data.photographer
        cam_obj = context.scene.camera
    else:
        settings = context.camera.photographer
        cam_obj = context.object

    no_textures = "No texture found in folder."
    no_textures2 = "Set Path in Add-on Preferences."

    engine = context.scene.render.engine
    if engine in {'CYCLES','LUXCORE'} or (engine=='BLENDER_EEVEE' and bpy.app.version >= (2, 93, 0)):
        box = layout.box()
        top_row = box.row(align=True)
        top_row.prop(settings,'opt_vignetting')
        for c in cam_obj.children:
            if c.get("is_opt_vignetting", False):
                top_row.prop(c, "hide_viewport", text='', icon_only=True, emboss=False)
                top_row.prop(c, "hide_render", text='', icon_only=True, emboss=False)
                        
        if settings.opt_vignetting:
            for c in cam_obj.children:
                if c.get("is_opt_vignetting", False):
                    if c.display_type != 'TEXTURED' and engine=='BLENDER_EEVEE':
                        box.operator('photographer.fix_display_type', icon='ERROR').obj=c.name
            col = box.column(align=True)
            col.prop(settings,'ov_scale', text='Scale', slider=True)
            if not engine == 'LUXCORE':
                col.prop(settings,'ov_rotation', slider=True)
            col.template_icon_view(settings, "opt_vignetting_tex",
                                   show_labels=True, scale=5)
                                   
            if engine in {"BLENDER_EEVEE","BLENDER_EEVEE_NEXT"}:
                col = box.column(align=True)
                col.label(text='Requires Jitter and high Sample count', icon='ERROR')
                col.prop(context.scene.eevee,'use_bokeh_jittered')
                row = col.row(align=True)
                row.active = context.scene.eevee.use_bokeh_jittered
                row.prop(context.scene.eevee,'bokeh_overblur')
                col.separator()
                col.prop(context.scene.eevee,'taa_render_samples')
                col.prop(context.scene.eevee,'taa_samples')
        
        if engine in {'CYCLES','LUXCORE'}:    
            box = layout.box()
            top_row = box.row(align=True)
            top_row.prop(settings,'bokeh')
            if not engine == 'LUXCORE':
                for c in cam_obj.children:
                    if c.get("is_bokeh_plane", False):
                        top_row.prop(c, "hide_viewport", text='', icon_only=True, emboss=False)
                        top_row.prop(c, "hide_render", text='', icon_only=True, emboss=False)
            if settings.bokeh:
                col = box.column(align=True)
                if not engine == 'LUXCORE':
                    col.prop(settings,'bokeh_brightness', slider=True)
                    col.prop(settings,'bokeh_saturation', slider=True)
                    col.prop(settings,'bokeh_rotation', slider=True)
                col.template_icon_view(settings, "bokeh_tex",
                                       show_labels=True, scale=5)
                                              
    # else:
    #     layout.label(text="Check Lens Panel for settings")

def dof_ui(self,context):
    layout = self.layout
    layout.use_property_split = True

    cam = context.camera
    dof = cam.dof
    layout.active = dof.use_dof

    flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

    row = flow.row(align=True)
    settings = cam.photographer
    if not settings.aperture_slider_enable:
        row.prop(settings, 'aperture_preset')
    else:
        row.prop(settings, 'aperture')
    sub = row.row(align=False)
    sub.prop(settings,'aperture_slider_enable', icon='SETTINGS',
        text='',emboss=False)

    col = flow.column()
    col.prop(dof, "aperture_blades")
    col.prop(dof, "aperture_rotation")
    col.prop(dof, "aperture_ratio", text= 'Anamorphic Ratio')
    col.prop(settings,'lock_vertical_fov')
    
    col.separator()
    
    bokeh_ui(self, context, col)
    col.enabled = not cam.id_data.get('lens_sim_cam',False)

class DATA_PT_PG_camera_dof_aperture(bpy.types.Panel):
    bl_label = "Aperture (Photographer)"
    bl_parent_id = "DATA_PT_camera_dof"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.camera and (context.engine in {'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH'})	

    def draw(self, context):
        dof_ui(self,context)

class CYCLES_CAMERA_PT_PG_dof_aperture(bpy.types.Panel):
    bl_label = "Aperture (Photographer)"
    bl_parent_id = "CYCLES_CAMERA_PT_dof"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.camera and context.engine == 'CYCLES'

    def draw(self, context):
        dof_ui(self,context)