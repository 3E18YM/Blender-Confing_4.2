import bpy
from ..operators import world as wd
from ..constants import DEFAULT_COLOR_TEMPERATURE, DEFAULT_TINT
from bpy.types import PropertyGroup
from bpy.props import (BoolProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       )

class LightMixerWorldSettings(PropertyGroup):
    hdri_rotation: FloatProperty(
        name="Rotation",
        default=0, soft_min=-3.141593, soft_max=3.141593, unit='ROTATION',
        precision=3,
        get=wd.get_hdri_rotation,
        set=wd.set_hdri_rotation,
    )
    hdri_horizon_level: FloatProperty(
        name="Horizon Level",
        default=0,soft_min=-1, soft_max=1,
        get=wd.get_hdri_horizon_level,
        set=wd.set_hdri_horizon_level,
    )
    hdri_projection_height: FloatProperty(
        name="Projection Height",
        description='Best results when using the height (in meters) of the camera that was used during the capture',
        default=0,soft_min=0,
        get=wd.get_hdri_projection_height,
        set=wd.set_hdri_projection_height,
    )
    hdri_blur: FloatProperty(
        name="Blur",
        default=0, min=0, soft_max=1,
        get=wd.get_hdri_blur,
        set=wd.set_hdri_blur,
    )
    hdri_use_temperature: BoolProperty(
        name="Use Color Temperature",
        default=True,
        options = {'HIDDEN'},
        update = wd.update_hdri_use_temperature,
    )
    hdri_temperature: FloatProperty(
        name="Temperature",
        default=DEFAULT_COLOR_TEMPERATURE, min=0, soft_min=1100, soft_max=13000,
        get=wd.get_hdri_temperature,
        set=wd.set_hdri_temperature,
    )
    hdri_tint: FloatProperty(
        name="Tint",
        default=DEFAULT_TINT, min=-100, max=100,
        get=wd.get_hdri_tint,
        set=wd.set_hdri_tint,
    )
    hdri_hue: FloatProperty(
        name="Hue",
        default=0.5, min=0, soft_max=1,
        get=wd.get_hdri_hue,
        set=wd.set_hdri_hue,
    )
    hdri_saturation: FloatProperty(
        name="Saturation",
        default=1.0, min=0, soft_max=2.0,
        get=wd.get_hdri_saturation,
        set=wd.set_hdri_saturation,
    )
    hdri_value: FloatProperty(
        name="Value",
        default=1.0, min=0, soft_max=5.0,
        get=wd.get_hdri_value,
        set=wd.set_hdri_value,
    )
    hdri_exposure_comp: FloatProperty(
        name="Exposure Compensation",
        default=0, soft_min=-10, soft_max=10,
        get=wd.get_hdri_exposure_comp,
        set=wd.set_hdri_exposure_comp,
    )
    hdri_clamp: FloatProperty(
        name="Clamp",
        default=0.0, min=0,
        get=wd.get_hdri_clamp,
        set=wd.set_hdri_clamp,
    )
    hdri_color: FloatVectorProperty(
        name="Color Multiplier",
        subtype='COLOR',
        min=0.0, max=1.0, size=4,
        default=(1.0,1.0,1.0,1.0),
        get=wd.get_hdri_color,
        set=wd.set_hdri_color,
    )
    bg_color: FloatVectorProperty(
        name="Background Color",
        description='Solid Color that replaced the Skuy visible to Camera, while keeping its lighting contribution',
        subtype='COLOR',
        min=0.0, max=1.0, size=4,
        default=(1.0,1.0,1.0,1.0),
        get=wd.get_bg_color,
        set=wd.set_bg_color,
    )
    bg_color_opacity: FloatProperty(
        name="Background Color Opacity",
        description='Replace visble Sky with Solid Color while keeping its lighting contribution',
        default=0, min=0, soft_max=1,
        get=wd.get_bg_color_opacity,
        set=wd.set_bg_color_opacity,
    )
    hdri_ground_emissive: FloatProperty(
        name="Emissive Strength",
        default=1,min=0,
        get=wd.get_hdri_ground_emissive,
        set=wd.set_hdri_ground_emissive,
    )
    film_transparent_override: BoolProperty(
        name="Film Transparent Override",
        description='Overrides Film Transparent render setting for this World',
        default=False,
        update = wd.update_film_transparent_override,
        options = {'HIDDEN'},
    )
    film_transparent: BoolProperty(
        name="Transparent Background",
        description='Enable Transparent Background',
        default=False,
        get=wd.get_film_transparent,
        set=wd.set_film_transparent,
        options = {'HIDDEN'},
    )