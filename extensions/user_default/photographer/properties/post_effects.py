import bpy
from math import radians
from ..ui.library import enum_previews_from_directory_items
from ..functions.functions import should_update
from ..functions.nodes import get_comp_group_node, get_comp_node_in_group, post_effects_cleanup

PFX_VERSION = 12

postfx_grp_name = 'Photographer PostFX v' + str(PFX_VERSION)
stmap_tex_name = 'STMap Texture'
effects = {
    'lens_distortion',
    'lateral_ca',
    'lens_softness',
    'fringing',
    'lens_vignetting',
    'sharpen',
    'film_grain',
}
effects_params = {
    'lens_distortion_amount',
    'lens_distortion_scale_comp',
    'lateral_ca_amount',
    'lens_softness_amount',
    'center_softness_amount',
    'corner_softness_amount',
    'corner_softness_falloff',
    'corner_softness_mask',
    'fringing_amount',
    'fringing_size',
    'fringing_threshold',
    'lens_vignetting_amount',
    'lens_vignetting_falloff',
    'lens_vignetting_mask',
    'sharpen_amount',
    'sharpen_radius',
    'film_grain_amount',
    'film_grain_size',
    'film_grain_displace',
}
effects_color_params = {
    'fringing_color',
}

def update_post_effects(self,context):
    scene = context.scene
    pg_main_cam = scene.photographer.main_camera

    if self.post_effects_enabled:
        if not scene.use_nodes:
            scene.use_nodes = True
        if self == scene.camera.data.post_effects:
            update_post_effects_enabled(scene.camera.data.post_effects,context)
    elif pg_main_cam:
        update_post_effects_enabled(pg_main_cam.post_effects,context)
    else:
        pfx_node = get_comp_group_node(context,postfx_grp_name)
        if pfx_node:
            pfx_enable_node = get_comp_node_in_group(pfx_node,'pfx_enable')
            if pfx_enable_node:
                pfx_enable_node.mute = not self.post_effects_enabled

def update_post_effects_enabled(self,context):

    post_effects_cleanup(self,context,postfx_grp_name)
    update = should_update(self,context,'post_effects_enabled',True)
    if update:
        # Get Lens Effects node. If none, create one.
        pfx_node = get_comp_group_node(context,postfx_grp_name)
        if not pfx_node:
            if self.post_effects_enabled:
                bpy.ops.photographer.post_effects_add()
        else:
            pfx_node.mute = False
            pfx_enable_node = get_comp_node_in_group(pfx_node,'pfx_enable')
            if pfx_enable_node:
                pfx_enable_node.mute = not self.post_effects_enabled

        # if self.post_effects_enabled:
        update_post_effects_params(self,context)
        update_lateral_ca_type(self,context)
        update_post_effects_color_params(self,context)
        update_lens_distortion_type(self,context)
        update_stmap_tex(self,context)
        update_film_grain_tex(self,context)
        update_streaks(self,context)
        update_bloom(self,context)

def update_lens_distortion_type(self,context):
    pfx_node = get_comp_group_node(context,postfx_grp_name)
    if pfx_node:
        node = get_comp_node_in_group(pfx_node,'lens_distortion_type')
        if self.lens_distortion_type == 'SIMPLE':
            node.outputs[0].default_value = 0.0
        elif self.lens_distortion_type == 'STMAP':
            node.outputs[0].default_value = 1.0
            update_stmap_tex(self,context)

def update_post_effects_params(self,context):
    pfx_node = get_comp_group_node(context,postfx_grp_name)
    if pfx_node:
        for e in effects:
            node = get_comp_node_in_group(pfx_node,e)
            if node:
                node.mute = not self.get(e,False)
                if not node.mute:
                    if node.name == 'lens_distortion':
                        update_stmap_tex(self,context)
                    elif node.name == 'film_grain':
                        update_film_grain_tex(self,context)
        for p in effects_params:
            node = get_comp_node_in_group(pfx_node,p)
            if node:
                if node.name == "corner_softness_mask":
                    if bpy.app.version >= (4,2,0):
                        node.mask_width = self.corner_mask_width
                        node.mask_height = self.corner_mask_height     
                    else:
                        node.width = self.corner_mask_width
                        node.height = self.corner_mask_height
                elif node.name == "lens_vignetting_mask":
                    if bpy.app.version >= (4,2,0):
                        node.mask_width = self.lens_vignetting_width
                        node.mask_height = self.lens_vignetting_height                        
                    else:
                        node.width = self.lens_vignetting_width
                        node.height = self.lens_vignetting_height
                else:
                    default_value = self.bl_rna.properties[p].default
                    node.outputs[0].default_value = self.get(p,default_value)

def update_post_effects_color_params(self,context):
    pfx_node = get_comp_group_node(context,postfx_grp_name)
    if pfx_node:
        for e in effects:
            node = get_comp_node_in_group(pfx_node,e)
            if node:
                node.mute = not self.get(e,False)
        for p in effects_color_params:
            node = get_comp_node_in_group(pfx_node,p)
            if node:
                # default_color = self.bl_rna.properties[p].default
                # Not working, returns a float and not a color?
                node.outputs[0].default_value = self.get(p,(0.35,0.085,0.66,1.0))

def update_lateral_ca_type(self,context):
    pfx_node = get_comp_group_node(context,postfx_grp_name)
    if pfx_node:
        node = get_comp_node_in_group(pfx_node,'lateral_ca_type')
        if node:
            if self.lateral_ca_type == 'RED':
                node.outputs[0].default_value = (1.0,0.0,0.0,1.0)
            elif self.lateral_ca_type == 'GREEN':
                node.outputs[0].default_value = (0.0,1.0,0.0,1.0)
            elif self.lateral_ca_type == 'BLUE':
                node.outputs[0].default_value = (0.0,0.0,1.0,1.0)
            elif self.lateral_ca_type == 'DISPERSION':
                node.outputs[0].default_value = (0.0,0.0,0.0,1.0)

def update_streaks(self,context):
    pfx_node = get_comp_group_node(context,postfx_grp_name)
    if pfx_node:
        node = get_comp_node_in_group(pfx_node,'glare_streaks')
        if node:
            node.mute = not self.get('streaks',False)
            if bpy.app.version >= (4,4,0):
                node.inputs['Strength'].default_value = self.streaks_amount
            else:
                node.mix = self.streaks_amount - 1.0
            node.threshold = self.streaks_threshold
            node.streaks = self.streaks_number
            node.angle_offset = self.streaks_angle_offset
            node.fade = self.streaks_fade

def update_bloom(self,context):
    pfx_node = get_comp_group_node(context,postfx_grp_name)
    #  print (self.get('bloom_type',None))
    if pfx_node:
        if self.get('bloom_type',0) in {1,2}:
            node = get_comp_node_in_group(pfx_node,'glare_bloom')
            if node:
                node.mute = not self.get('bloom',False)
                if bpy.app.version>= (4,4,0) and self.get('bloom_type',0) == 2:
                    node.glare_type = 'BLOOM'
                else:
                    node.glare_type = 'FOG_GLOW'

                if bpy.app.version>= (4,4,0):
                    node.inputs['Threshold'].default_value = self.bloom_threshold
                    node.inputs['Smoothness'].default_value = self.bloom_smoothness
                    node.inputs['Maximum'].default_value = self.bloom_maximum
                    node.inputs['Saturation'].default_value = self.bloom_saturation
                    node.inputs['Tint'].default_value = self.bloom_tint
                    node.inputs['Strength'].default_value = self.bloom_amount
                    node.inputs['Size'].default_value = self.bloom_size / 100
                    node.quality = self.bloom_quality
                else:
                    node.mix = self.bloom_amount - 1.0
                    node.threshold = self.bloom_threshold
                    node.size = self.bloom_glare_size
                    node.quality = self.bloom_quality
                
                gaussian_node = get_comp_node_in_group(pfx_node,'bloom')
                if gaussian_node:
                    gaussian_node.mute = True
        else:
            node = get_comp_node_in_group(pfx_node,'bloom')
            if node:
                node.mute = not self.get('bloom',False)
                node.inputs['Bloom Amount'].default_value = self.bloom_amount
                node.inputs['Bloom Tint'].default_value = self.bloom_tint
                blur = get_comp_node_in_group(node,'bloom_blur')
                secondary_blur = get_comp_node_in_group(node,'bloom_secondary_blur')
                blurs = [blur,secondary_blur]
                for blur in blurs:
                    blur.factor_x = blur.factor_y = self.bloom_size
                    if self.bloom_stretch_ratio > 0.5:
                        blur.factor_x *= 1 - self.bloom_stretch_ratio
                    else:
                        blur.factor_y *= self.bloom_stretch_ratio * 2 
                
                luma = get_comp_node_in_group(node,'bloom_luminance')
                luma.limit_max = self.bloom_threshold
                # luma.limit_min = self.bloom_threshold - 1.0 if self.bloom_threshold >= 1.0 else 0
                node.inputs['Bloom Saturation'].default_value = self.bloom_saturation
                
                glare_node = get_comp_node_in_group(pfx_node,'glare_bloom')
                if glare_node:
                    glare_node.mute = True

def enum_previews_stmap(self, context):
    return enum_previews_from_directory_items(self, context,'stmap')

def update_stmap_tex(self,context):
    if self.lens_distortion_type == 'STMAP':
        pfx_node = get_comp_group_node(context,postfx_grp_name)
        if pfx_node:
            node = get_comp_node_in_group(pfx_node,'stmap_tex')
            if node:
                if self.stmap_tex and self.stmap_tex != 'empty':
                    node.image = bpy.data.images.load(self.stmap_tex, check_existing=True)
                    colorspaces = ['Non-Color']
                    for cs in colorspaces:
                        try:
                            node.image.colorspace_settings.name = cs
                        except:
                            pass

def enum_previews_film_grain(self, context):
    return enum_previews_from_directory_items(self, context,'film_grain')

def update_film_grain_tex(self,context):
    if self.film_grain:
        pfx_node = get_comp_group_node(context,postfx_grp_name)
        if pfx_node:
            node = get_comp_node_in_group(pfx_node,'film_grain_tex')
            if node:
                if self.film_grain_tex and self.film_grain_tex != 'empty':
                    node.image = bpy.data.images.load(self.film_grain_tex, check_existing=True)
                    colorspaces = ['Non-Color']
                    for cs in colorspaces:
                        try:
                            node.image.colorspace_settings.name = cs
                        except:
                            pass
        update_film_grain_animated(self,context)

def update_film_grain_animated(self,context):
    pfx_node = get_comp_group_node(context,postfx_grp_name)
    if pfx_node:
        film_grain_group = get_comp_node_in_group(pfx_node,'film_grain')
        if film_grain_group:
            animated_node = get_comp_node_in_group(film_grain_group,'film_grain_animated')
            if animated_node:
                animated_node.mute = not self.film_grain_animated
                if bpy.app.version >= (4,2,0) and bpy.app.version < (4,4,0):
                    animated_node.interpolation = 'Bilinear'
                elif bpy.app.version >= (4,4,0):
                    animated_node.interpolation = 'BILINEAR'

class PostEffectsSettings(bpy.types.PropertyGroup):

    post_effects_enabled : bpy.props.BoolProperty(
        name = 'Lens Effects',
        description = "Enable Lens Effects (uses Compositing)",
        default = False,
        options = {'HIDDEN'},
        update = update_post_effects
    )
    lens_distortion : bpy.props.BoolProperty(
        name = "Distortion",
        description = "Enable Distortion",
        default = False,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    lens_distortion_type : bpy.props.EnumProperty(
        name = "Distortion Type",
        description = "Choose between Simple (Blender Lens Distortion) or an STMap to create Lens Distortion",
        items = [('SIMPLE','Simple', 'Uses Blender Lens Distortion node'),('STMAP','STMap','Uses STMap. Warning: Viewport rendering is not supported yet')],
        default = 'SIMPLE',
        options = {'HIDDEN'},
        update = update_lens_distortion_type
    )
    lens_distortion_amount : bpy.props.FloatProperty(
        name = "Distortion Amount",
        description = "Barrel distortion using positive values, Pin cushion distortio using negative values",
        default = 0.25, soft_min = -1, soft_max = 1,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    lens_distortion_scale_comp : bpy.props.FloatProperty(
        name = "Scale Compensation",
        description = "Percentage of scaling up to fix missing potential missing pixels after STMap distortion",
        default = 0, soft_min=0, soft_max = 10,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    stmap_tex: bpy.props.EnumProperty(
        name="STMap Image",
        items=enum_previews_stmap,
        default=0,
        update=update_stmap_tex,
    )
    lateral_ca : bpy.props.BoolProperty(
        name = "Lateral Chromatic Aberration",
        description = "Enable Lateral Chromatic Aberration",
        default = False,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    lateral_ca_amount : bpy.props.FloatProperty(
        name = "Lateral Chromatic Aberration Amount",
        description = "Amount of channels and blur offset to create Lateral Chromatic Aberration on the corner of the image",
        default = 0.5, min=0.0, soft_max = 1.0,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    lateral_ca_type : bpy.props.EnumProperty(
        name = "Lateral Chromatic Aberration Colors",
        description = "Choose Red and Cyan, Blue and Yellow or Green and Purple chromatic aberration",
        items = [('DISPERSION','Dispersion', 'Uses Blender Lens Dispersion'),
                 ('RED','Red/Cyan', 'Red and Cyan Chromatic Aberration'),
                 ('GREEN','Green/Magenta', 'Green and Magenta Chromatic Aberration'),
                 ('BLUE','Blue/Yellow', 'Blue and Yellow Chromatic Aberration'),
                 ],
        default = 'DISPERSION',
        options = {'HIDDEN'},
        update = update_lateral_ca_type,
    )
    fringing : bpy.props.BoolProperty(
        name = "Fringing",
        description = "Enable Fringing from bright areas of the image",
        default = False,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    fringing_amount : bpy.props.FloatProperty(
        name = "Fringing Amount",
        description = "Amount of Fringing",
        default = 0.5, min=0, soft_max = 1.0,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    fringing_size : bpy.props.FloatProperty(
        name = "Fringing Size",
        description = "Fringing bluriness",
        default = 0.25, min=0, max = 1.0,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    fringing_threshold : bpy.props.FloatProperty(
        name = "Fringing Threshold",
        description = "Pixels with brightness higher than this value participate to fringing",
        default = 0.9, min=0,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    fringing_color : bpy.props.FloatVectorProperty(
        name='Fringing Color',
        description="Fringing from lenses is usually purple behind the focus point due to longitudinal chromatic aberration",
        subtype='COLOR', min=0.0, max=1.0, size=4, default=(0.35,0.085,0.66,1.0),
        options = {'HIDDEN'},
        update = update_post_effects_color_params,
    )
    bloom: bpy.props.BoolProperty(
        name = "Bloom",
        description = "Enable Glare Streaks",
        default = False,
        options = {'HIDDEN'},
        update = update_bloom,
    )
    bloom_amount : bpy.props.FloatProperty(
        name = "Bloom Amount",
        default = 0.5, min=0.0, soft_max=1.0,
        options = {'HIDDEN'},
        update = update_bloom,
    )
    bloom_type : bpy.props.EnumProperty(
        name = "Bloom Type",
        description = "Choose between Gaussian (compatible with Viewport) and  Glare node (not compatible with 4.2 Viewport)",
        items = [('GAUSSIAN','Gaussian', 'Uses Gaussian Blur graph, compatible with Viewport Render'),
                 ('GLARE','Glare Fog Glow', 'Uses Glare node with Fog Glow'),
                 ('BLOOM','Glare Bloom', 'Uses Glare node of Bloom type (added in Blender 4.4)'),
                ],
        default = 'GAUSSIAN',
        options = {'HIDDEN'},
        update = update_bloom,
    )
    glare_type : bpy.props.EnumProperty(
        name = "Glare Type",
        description = "Choose between Gaussian (compatible with Viewport) and  Glare node (not compatible with 4.2 Viewport)",
        items = [('GAUSSIAN','Gaussian', 'Uses Gaussian Blur, compatible with Viewport Render'),
                 ('GLARE','Glare', 'Uses Glare Node, soon to be deprecated'),
                ],
        default = 'GAUSSIAN',
        options = {'HIDDEN'},
        update = update_bloom,
    )
    bloom_threshold : bpy.props.FloatProperty(
        name = "Bloom Threshold",
        description = "Pixels with brightness higher than this value will create Bloom",
        default = 1.0, min = 0.0,
        options = {'HIDDEN'},
        update = update_bloom,
    )
    # Blender 4.4 new Glare properties
    bloom_smoothness : bpy.props.FloatProperty(
        name = "Bloom Smoothness",
        description = "Smoothness of the extracted highlights",
        default = 0.1, soft_min = 0.0, soft_max = 1.0,
        options = {'HIDDEN'},
        update = update_bloom,
    )   
    bloom_maximum : bpy.props.FloatProperty(
        name = "Bloom Maximum",
        description = "Suppresses bright highlights such that their brightness are not higher than this value. 0 to disable",
        default = 0, soft_min = 0.0,
        options = {'HIDDEN'},
        update = update_bloom,
    )   
    # Using Glare Node
    bloom_glare_size : bpy.props.IntProperty(
        name = "Bloom Size",
        description = "Relative to the initial size of bright area of pixels",
        default = 8, min= 6, max=9,
        options = {'HIDDEN'},
        update = update_bloom,
    )
    bloom_quality : bpy.props.EnumProperty(
        name = "Bloom Quality",
        description = "If not set to High, the effect will be applied to a low-res copy of the image",
        items = [('LOW','Low', '' , 0),
                 ('MEDIUM','Medium', '' ,1),
                 ('HIGH','High', '', 2),
                ],
        default = 0,        
        options = {'HIDDEN'},
        update = update_bloom,
    )
    bloom_size : bpy.props.FloatProperty(
        name = "Bloom Size",
        description = "Relative to the initial size of bright area of pixels",
        default = 15, min=0.000, max=100,
        subtype='PERCENTAGE',
        options = {'HIDDEN'},
        update = update_bloom,
    )
    bloom_stretch_ratio : bpy.props.FloatProperty(
        name = "Bloom Stretch Ratio",
        description = "Stretches Bloom horizontally or vertically",
        default = 0.5, min = 0.0, max = 1.0,
        options = {'HIDDEN'},
        update = update_bloom,
    )
    bloom_tint : bpy.props.FloatVectorProperty(
        name = "Bloom Amount",
        subtype='COLOR', min=0.0, max=1.0, size=4, default=(1.0,1.0,1.0,1.0),
        options = {'HIDDEN'},
        update = update_bloom,
    )
    bloom_saturation : bpy.props.FloatProperty(
        name = "Bloom Saturation",
        description = "Controls saturation of Bloom",
        default = 1.0, min = 0.0, max = 2.0,
        options = {'HIDDEN'},
        update = update_bloom,
    )
    streaks: bpy.props.BoolProperty(
        name = "Streaks",
        description = "Enable Glare Streaks",
        default = False,
        options = {'HIDDEN'},
        update = update_streaks,
    )
    streaks_amount : bpy.props.FloatProperty(
        name = "Streaks Amount",
        default = 0.5, min=0.0, soft_max=1.0,
        options = {'HIDDEN'},
        update = update_streaks,
    )
    streaks_number : bpy.props.IntProperty(
        name = "Number of Streaks",
        description = "Usually corresponds to the number of Aperture blades",
        default = 6, min= 1, max=16,
        options = {'HIDDEN'},
        update = update_streaks,
    )
    streaks_threshold : bpy.props.FloatProperty(
        name = "Streaks Threshold",
        description = "Pixels with brightness higher than this value will create Streaks",
        default = 0.9, min=0,
        options = {'HIDDEN'},
        update = update_streaks,
    )
    streaks_angle_offset : bpy.props.FloatProperty(
        name = "Streaks Angle offset",
        default = radians(15), min=0, max=radians(180),subtype="ANGLE",
        options = {'HIDDEN'},
        update = update_streaks,
    )
    streaks_fade : bpy.props.FloatProperty(
        name = "Streaks Fade Length",
        default = 0.8, min=0.75,max=1.0,
        options = {'HIDDEN'},
        update = update_streaks,
    )
    lens_vignetting: bpy.props.BoolProperty(
        name = "Vignetting",
        description = "Enable Vignetting. Note that Optical Vignetting can also be used to achieve such effect",
        default = False,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    lens_vignetting_amount : bpy.props.FloatProperty(
        name = "Vignetting Amount",
        description = "Vignetting opacity",
        default = 0.5, min=0, soft_max = 1,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    lens_vignetting_falloff : bpy.props.FloatProperty(
        name = "Vignetting Falloff",
        description = "Vignetting Mask Falloff",
        default = 0.75, min=0.0, soft_min=0.1, max=1.0,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    lens_vignetting_width : bpy.props.FloatProperty(
        name = "Vignetting Width",
        default = 0.75, min=0, soft_max = 2,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    lens_vignetting_height : bpy.props.FloatProperty(
        name = "Vignetting Height",
        default = 0.75, min=0, soft_max = 2,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    sharpen: bpy.props.BoolProperty(
        name = "Sharpen",
        description = "Enable Sharpen controls for image post-sharpening",
        default = False,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    sharpen_amount : bpy.props.FloatProperty(
        name = "Sharpen Amount",
        description = "Sharpen Amount",
        default = 0, min=-2, soft_max = 2,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    sharpen_radius : bpy.props.FloatProperty(
        name = "Sharpen Radius",
        description = "Sharpen Radius",
        default = 0.5, min=0, soft_max = 1,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    lens_softness: bpy.props.BoolProperty(
        name = "Lens Softness",
        description = "Enable Lens Softness controls",
        default = False,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    lens_softness_amount : bpy.props.FloatProperty(
        name = "Lens Softness Amount",
        default = 0.5, min=0.0, max=1.0,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    corner_softness_amount : bpy.props.FloatProperty(
        name = "Blur Size",
        default = 0.5, min=0, soft_max = 4.0,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    center_softness_amount : bpy.props.FloatProperty(
        name = "Center Softness",
        default = 0.0, min=0.0, soft_max = 1.0,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    corner_softness_falloff : bpy.props.FloatProperty(
        name = "Corner Falloff",
        default = 0.75, min=0.0, max=1.0,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    corner_mask_width : bpy.props.FloatProperty(
        name = "Corner Width",
        default = 0.5, min=0, max = 2,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    corner_mask_height : bpy.props.FloatProperty(
        name = "Corner Height",
        default = 0.5, min=0, max = 2,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    film_grain: bpy.props.BoolProperty(
        name = "Film Grain",
        description = "Enable Film Grain controls",
        default = False,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    film_grain_amount : bpy.props.FloatProperty(
        name = "Film Grain Amount",
        default = 0.5, min=0.0, soft_max=1.0,
        update = update_post_effects_params,
    )
    film_grain_size : bpy.props.FloatProperty(
        name = "Film Grain Scale",
        default = 1.0, min=0.001, soft_max = 10.0,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    film_grain_displace : bpy.props.FloatProperty(
        name = "Film Grain Displace",
        default = 0.5, min=0, soft_max = 5.0,
        options = {'HIDDEN'},
        update = update_post_effects_params,
    )
    film_grain_tex: bpy.props.EnumProperty(
        name="Film Grain texture",
        items=enum_previews_film_grain,
        default=0,
        options = {'HIDDEN'},
        update=update_film_grain_tex,
    )
    film_grain_animated: bpy.props.BoolProperty(
        name = "Film Grain Animated",
        description = "Enable frame animation",
        default = True,
        options = {'HIDDEN'},
        update = update_film_grain_animated,
    )