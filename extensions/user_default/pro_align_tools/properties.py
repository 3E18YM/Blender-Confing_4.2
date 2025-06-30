from .common_imports import *

from .cache_system import CACHE_update


# -- Panel Properties --

class ALIGNTOOL_Properties(PropertyGroup):

    CACHE = dict()
    gizmo_group_instances = []
    current_gizmo = []
    batches = []
    cache_update: BoolProperty(default=False)
    update_available: BoolProperty(default=True)
    running_modal: BoolProperty(default=False)
    props = dict()

    drag: BoolProperty(default=False)
    drag_star = []
    drag_star_shadow = []
    nearest_axis = []
    last_clicked_axis = []
    last_point = []

    draw_handler_2D = []
    mouse_panel_fill_batch = []
    mouse_panel_outline_batch = []

    shortcuts_panel_fill_batch = []
    shortcuts_panel_outline_batch = []
    region_dicts = []
    show_shortcuts_help: BoolProperty(default=False)

    icons = []

    def tag_cache_update(self, context):
        self.cache_update = True

    def align_buttons_update(self, item):
        buttons = ["align_min", "align_center", "align_max"]
        buttons.remove(item)
        for button in buttons:
            setattr(self, button, False)

    def min_upd(self, context):
        if self.align_min:
            self.align_buttons_update("align_min")
            self.origin_type = "BOUNDS"
            alignments = ["CENTER", "CENTER", "CENTER"]
            alignments[("X", "Y", "Z").index("Z" if self.origin_use_geometry else self.direction_axis)] = "MAX"
            self.origin_depth_X, self.origin_depth_Y, self.origin_depth_Z = alignments
            self.tag_cache_update(context)
    def center_upd(self, context):
        if self.align_center:
            self.align_buttons_update("align_center")
            self.origin_type = "BOUNDS"
            self.origin_depth_X, self.origin_depth_Y, self.origin_depth_Z = ("CENTER", "CENTER", "CENTER")
            self.tag_cache_update(context)
    def max_upd(self, context):
        if self.align_max:
            self.align_buttons_update("align_max")
            self.origin_type = "BOUNDS"
            alignments = ["CENTER", "CENTER", "CENTER"]
            alignments[("X", "Y", "Z").index("Z" if self.origin_use_geometry else self.direction_axis)] = "MIN"
            self.origin_depth_X, self.origin_depth_Y, self.origin_depth_Z = alignments
            self.tag_cache_update(context)
    align_min: BoolProperty(default=False, name="", update=min_upd,
                            description="Set a 'minimum' alignment")
    align_center: BoolProperty(default=False, name="", update=center_upd,
                               description="Set a 'centered' alignment")
    align_max: BoolProperty(default=False, name="", update=max_upd,
                            description="Set a 'maximum' alignment")

    direction_panel: BoolProperty(default=False, name="Direction")
    plane_panel: BoolProperty(default=False, name="Plane")
    origin_panel: BoolProperty(default=False, name="Origin point")
    status_bar: BoolProperty(default=True, name="Show status bar")

    direction_axis: EnumProperty(items=[("X", "X", "X Axis", 0),
                                        ("Y", "Y", "Y Axis", 1),
                                        ("Z", "Z", "Z Axis", 2)],
                                 default="X",
                                 description="Direction Axis",
                                 update=tag_cache_update)

    def fill_direction_custom_orientations(self, context):
        custom_orientation = context.scene.transform_orientation_slots[0].custom_orientation
        text = "(None)" if custom_orientation is None else f"({custom_orientation.name})"
        items = [("", "Default", "Default"),
                 ("GLOBAL", "Global", "Use the Global axes as directions", "WORLD_DATA", 1),
                 ("LOCAL", "Local", "Use the Local axes as directions", "ORIENTATION_LOCAL", 2),
                 ("VIEW", "View", "Use the current View axes as directions", "RESTRICT_VIEW_OFF", 3),
                 ("PERPENDICULAR", "Perpendicular", "Use a direction perpendicular to the current plane (also generates perpendicular Bound Boxes)", "NORMALS_FACE", 0),
                 ("", "Custom", "Custom"),
                 ("CUSTOM", f"Custom {text}", "Use the currently selected Custom Orientation axes as directions", "EMPTY_AXIS", 4)]
        return items
    direction_custom_orientation: EnumProperty(items=fill_direction_custom_orientations, name="Orientations",
                                               description="Orientations",
                                               update=tag_cache_update)

    direction_reference: EnumProperty(items=[("ACTIVE", "Active", "Active Object", 0),
                                             ("INDIVIDUAL", "Individual", "Every Object individually", 1)],
                                      default="INDIVIDUAL",
                                      description="Selection",
                                      update=tag_cache_update)

    plane_show_bounds: BoolProperty(default=False, description="Show geometric bounds when picking the projection plane")

    plane_axis: EnumProperty(items=[("X", "X", "YZ Plane", 0),
                                    ("Y", "Y", "XZ Plane", 1),
                                    ("Z", "Z", "XY Plane", 2)],
                             default="X",
                             description="Projection Axis",
                             update=tag_cache_update)

    plane_depth: EnumProperty(items=[("MIN", "Min", "Minimum Axis Bound", 0),
                                     ("CENTER", "Center", "Bound Box Center", 1),
                                     ("MAX", "Max", "Maximum Axis Bound", 2)],
                              default="MIN",
                              description="Projection Depth",
                              update=tag_cache_update)

    def plane_target_update(self, context):
        if self.plane_target != "CUSTOM":
            self.drag_star.clear()
        self.tag_cache_update(context)
    plane_target: EnumProperty(items=[("WORLD", "World", "Project to World planes", 0),
                                      ("CURSOR", "Cursor", "Project to cursor planes", 1),
                                      ("OBJECT", "Object", "Project to object planes", 2),
                                      ("CUSTOM", "Custom", "Custom plane", 3)],
                               default="OBJECT",
                               description="Projection target",
                               update=plane_target_update)

    def fill_plane_orientations(self, context):
        custom_orientation = context.scene.transform_orientation_slots[0].custom_orientation
        text = "(None)" if custom_orientation is None else f"({custom_orientation.name})"
        items = [("", "Default", "Default"),
                 ("GLOBAL", "Global", "Use the Global axes as plane", "WORLD_DATA", 0),
                 ("LOCAL", "Local", "Use the Local axes as plane", "ORIENTATION_LOCAL", 1),
                 ("VIEW", "View", "Use the current View axes as plane", "RESTRICT_VIEW_OFF", 2),
                 ("", "Custom", "Custom"),
                 ("CUSTOM", f"Custom {text}", "Use the currently selected Custom Orientation axes as plane", "EMPTY_AXIS", 3)]
        return items
    plane_orientation: EnumProperty(items=fill_plane_orientations, name="Orientations",
                                    description="Orientations",
                                    update=tag_cache_update)

    plane_object: StringProperty(default="",
                                 name="Plane Object",
                                 description="Object used for projection plane",
                                 update=tag_cache_update)

    def upd_picker(self, context):
        if self.plane_object_picker is not None:
            self.plane_object = self.plane_object_picker.name
            self.property_unset("plane_object_picker")
    plane_object_picker: PointerProperty(type=bpy.types.Object,
                                         name="Plane Object",
                                         description="Object used for projection plane",
                                         update=upd_picker)

    plane_reference: EnumProperty(items=[("ACTIVE", "Active", "Active Object Bound Box", 0),
                                         ("SELECTED", "Selected", "Selected Objects Bound Box", 1)],
                                  default="SELECTED",
                                  description="Projection Reference",
                                  update=tag_cache_update)

    plane_type: EnumProperty(items=[("LOCATION", "Location", "Active Object's Location", 0),
                                    ("BOUNDS", "Bounds", "Object(s) Bound Box", 1)],
                             default="BOUNDS",
                             description="Projection Type",
                             update=tag_cache_update)

    plane_use_local: BoolProperty(default=False, name="Local bounds",
                                  description="Use local bounds instead of global bounds",
                                  update=tag_cache_update)

    plane_use_geometry: BoolProperty(default=True, name="Use Geometry",
                                     description="Use Object's geometry to calculate a new Bound Box",
                                     update=tag_cache_update)

    origin_show_bounds: BoolProperty(default=False, description="Show geometric bounds when picking the origin")

    origin_target: EnumProperty(items=[("WORLD", "World", "Origin from World", 0),
                                       ("CURSOR", "Cursor", "Origin from Cursor", 1),
                                       ("OBJECTS", "Objects", "Origin from selected objects", 2)],
                                default="OBJECTS",
                                description="Origin target",
                                update=tag_cache_update)

    origin_type: EnumProperty(items=[("LOCATION", "Location", "Object Location", 0),
                                     ("BOUNDS", "Bounds", "Object Bounds", 1),
                                     ("CUSTOM", "Custom", "Custom origin", 2)],
                              default="BOUNDS",
                              description="Origin Type",
                              update=tag_cache_update)

    origin_depth_X: EnumProperty(items=[("MIN", "Min", "Minimum X Axis", 0),
                                        ("CENTER", "Center", "Center X Axis", 1),
                                        ("MAX", "Max", "Maximum X Axis", 2)],
                                 default="CENTER",
                                 description="X Depth",
                                 update=tag_cache_update)

    origin_depth_Y: EnumProperty(items=[("MIN", "Min", "Minimum Y Axis", 0),
                                        ("CENTER", "Center", "Center Y Axis", 1),
                                        ("MAX", "Max", "Maximum Y Axis", 2)],
                                 default="CENTER",
                                 description="Y Depth",
                                 update=tag_cache_update)

    origin_depth_Z: EnumProperty(items=[("MIN", "Min", "Minimum Z Axis", 0),
                                        ("CENTER", "Center", "Center Z Axis", 1),
                                        ("MAX", "Max", "Maximum Z Axis", 2)],
                                 default="MIN",
                                 description="Z Depth",
                                 update=tag_cache_update)

    origin_use_local: BoolProperty(default=False, name="Local bounds",
                                   description="Use local bounds instead of global bounds",
                                   update=tag_cache_update)

    origin_use_geometry: BoolProperty(default=True, name="Use Geometry",
                                      description="Use Object's geometry to calculate a new Bound Box",
                                      update=tag_cache_update)

    origin_all_selected: BoolProperty(default=False, name="All selected",
                                      description="Treat all selected objects as one",
                                      update=tag_cache_update)

    def upd_geometry_update(self, context):
        if self.geometry_update:
            addon = context.window_manager.align_tool
            if bool(addon.CACHE):
                CACHE_update(context)
    geometry_update: BoolProperty(name="Extra Geo Update",
                                  description="Extra geometry update for special cases "
                                              "(displacement texture changes, shape keys, etc)",
                                  default=False,
                                  update=upd_geometry_update)
