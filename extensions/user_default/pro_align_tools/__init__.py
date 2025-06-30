from .common_imports import *

from .context_functions import align_tool_selected
from .tools import ALIGNTOOL_tool_object, ALIGNTOOL_tool_edit
from .gizmos import ALIGNTOOL_GGT_common_gizmo_group, ALIGNTOOL_GT_custom_gizmo
from .properties import ALIGNTOOL_Properties
from .operators import (ALIGNTOOL_OT_align_objects,
                        ALIGNTOOL_OT_add_event_to_current_gizmo,
                        ALIGNTOOL_OT_shortcuts_handler,

                        ALIGNTOOL_OT_click_handler,
                        ALIGNTOOL_OT_shift_click_handler,
                        ALIGNTOOL_OT_ctrl_click_handler,
                        ALIGNTOOL_OT_check_running_modal,
                        ALIGNTOOL_OT_redraw,
                        ALIGNTOOL_OT_pick_plane,

                        ALIGNTOOL_OT_set_origin,
                        ALIGNTOOL_OT_delete_origin,
                        ALIGNTOOL_OT_set_plane,
                        ALIGNTOOL_OT_delete_plane)

classes = (ALIGNTOOL_OT_align_objects,
           ALIGNTOOL_OT_add_event_to_current_gizmo,
           ALIGNTOOL_OT_shortcuts_handler,

           ALIGNTOOL_OT_click_handler,
           ALIGNTOOL_OT_shift_click_handler,
           ALIGNTOOL_OT_ctrl_click_handler,
           ALIGNTOOL_OT_check_running_modal,
           ALIGNTOOL_OT_redraw,
           ALIGNTOOL_OT_pick_plane,

           ALIGNTOOL_OT_set_origin,
           ALIGNTOOL_OT_delete_origin,
           ALIGNTOOL_OT_set_plane,
           ALIGNTOOL_OT_delete_plane,

           ALIGNTOOL_GT_custom_gizmo,
           ALIGNTOOL_GGT_common_gizmo_group,
           ALIGNTOOL_Properties)

tools = (ALIGNTOOL_tool_object,
         ALIGNTOOL_tool_edit)

addon_keymap_items = []


class BatchesDB:
    """The database of GPU Batches"""

    def __init__(self):
        self.mouse_panel_fill_batch = []
        self.mouse_panel_outline_batch = []
        self.shortcuts_panel_fill_batch = []
        self.shortcuts_panel_outline_batch = []

    def clear(self):
        for attr in dir(self):
            if attr != "clear":
                if not attr.startswith("_"):
                    if isinstance(getattr(self, attr), list):
                        getattr(self, attr).clear()
                    else:
                        delattr(self, attr)


BATCHES = BatchesDB()

def clean():

    global BATCHES

    if hasattr(BATCHES, "cached_objects"):

        for name in BATCHES.cached_objects:

            del BATCHES.cached_objects[name]["batch_shader"]

    BATCHES.clear()


import atexit
atexit.register(clean)


def register():

    for c in classes:
        bpy.utils.register_class(c)

    for tool in tools:
        bpy.utils.register_tool(tool, after={"builtin.transform"}, separator=False)

    WM = bpy.types.WindowManager
    WM.align_tool = PointerProperty(type=ALIGNTOOL_Properties)

    wm = bpy.context.window_manager

    global BATCHES
    wm.align_tool.batches[:] = [BATCHES]

    import os

    icons = bpy.utils.previews.new()
    icons["last_icon"] = ""
    wm.align_tool.icons[:] = [icons]

    directory = os.path.dirname(__file__)

    icons.load("min", os.path.join(directory, "icons", "min.png"), 'IMAGE')
    icons.load("center", os.path.join(directory, "icons", "center.png"), 'IMAGE')
    icons.load("max", os.path.join(directory, "icons", "max.png"), 'IMAGE')

    addons_keymaps = wm.keyconfigs.addon.keymaps

    for mode in ("Object Mode", "Mesh"):

        if mode in addons_keymaps:
            km = addons_keymaps[mode] # para modo edición: "Mesh"
        else:
            km = addons_keymaps.new(name=mode, space_type="EMPTY")

        kmi = km.keymap_items.new(idname="wm.tool_set_by_id", type='A', value='PRESS', ctrl=True, alt=True)
        kmi.properties["name"] = "align_tool.tool_edit" if mode == "Mesh" else "align_tool.tool_object"
        addon_keymap_items.append((km, kmi))

        kmi = km.keymap_items.new(idname="proaligntools.click_handler", type='LEFTMOUSE', value='PRESS', any=True)
        addon_keymap_items.append((km, kmi))

        kmi = km.keymap_items.new(idname="proaligntools.shortcuts_handler", type='D', value='PRESS')
        addon_keymap_items.append((km, kmi))

        # The "redraw" operator is mainly used in Object Mode, but it's also used to update the DummyEvent object, so
        # ensure here that a MOUSEMOVE event triggers an update in Edit Mode, to update the mouse position
        kmi = km.keymap_items.new(idname="proaligntools.redraw", type='MOUSEMOVE', value='ANY', any=True)
        kmi.properties["name"] = "Redraw 3D View when moving the Mouse"
        addon_keymap_items.append((km, kmi))


    km = addons_keymaps["Object Mode"]

    kmi = km.keymap_items.new(idname="proaligntools.align_objects", type='RET', value='PRESS')
    addon_keymap_items.append((km, kmi))

    kmi = km.keymap_items.new(idname="proaligntools.align_objects", type='NUMPAD_ENTER', value='PRESS')
    addon_keymap_items.append((km, kmi))

    kmi = km.keymap_items.new(idname="proaligntools.pick_plane",
                              type='P', value='PRESS', shift=True)
    addon_keymap_items.append((km, kmi))

    kmi = km.keymap_items.new(idname="proaligntools.shift_click_handler",
                              type='LEFTMOUSE', value='PRESS', shift=True, alt=True)
    kmi.properties["name"] = "proaligntools.shift_click_handler"
    addon_keymap_items.append((km, kmi))

    kmi = km.keymap_items.new(idname="proaligntools.shift_click_handler",
                              type='LEFTMOUSE', value='PRESS', shift=True)
    kmi.properties["name"] = "proaligntools.shift_click_handler"
    addon_keymap_items.append((km, kmi))

    kmi = km.keymap_items.new(idname="proaligntools.ctrl_click_handler",
                              type='LEFTMOUSE', value='PRESS', ctrl=True, alt=True)
    kmi.properties["name"] = "proaligntools.ctrl_click_handler"
    addon_keymap_items.append((km, kmi))

    kmi = km.keymap_items.new(idname="proaligntools.ctrl_click_handler",
                              type='LEFTMOUSE', value='PRESS', ctrl=True)
    kmi.properties["name"] = "proaligntools.ctrl_click_handler"
    addon_keymap_items.append((km, kmi))


    shortcuts = (
        {"name": "Select X direction",
         "idname": "proaligntools.shortcuts_handler",
         "type": "X", "value": "PRESS"},

        {"name": "Select Y direction",
         "idname": "proaligntools.shortcuts_handler",
         "type": "Y", "value": "PRESS"},

        {"name": "Select Z direction",
         "idname": "proaligntools.shortcuts_handler",
         "type": "Z", "value": "PRESS"},

        {"name": "Toggle Global/Local direction orientation",
         "idname": "proaligntools.shortcuts_handler",
         "type": "L", "value": "PRESS"},

        {"name": "Toggle Global/View direction orientation",
         "idname": "proaligntools.shortcuts_handler",
         "type": "V", "value": "PRESS"},

        {"name": "Toggle Global/Perpendicular direction orientation",
         "idname": "proaligntools.shortcuts_handler",
         "type": "P", "value": "PRESS"},

        {"name": "Toggle Use Geometry",
         "idname": "proaligntools.shortcuts_handler",
         "type": "G", "value": "PRESS"},

        {"name": "Toggle All selected",
         "idname": "proaligntools.shortcuts_handler",
         "type": "O", "value": "PRESS"},

        {"name": "Select next plane orientation",
         "idname": "proaligntools.shortcuts_handler",
         "type": "WHEELUPMOUSE", "value": "PRESS"},

        {"name": "Select previous plane orientation",
         "idname": "proaligntools.shortcuts_handler",
         "type": "WHEELDOWNMOUSE", "value": "PRESS"},


        # These shortcuts are aimed to update the status of the DummyEvent object,
        # check running_modal and refresh the drawing of the UI
        # running_modal hides the gizmo elements while some other important operation is running

        # These are mainly aimed to SET running_modal to allow standard Grab, Rotate, Scale
         {"name": "Redraw 3D View when pressing the G Key",
         "idname": "proaligntools.check_running_modal",
         "type": "G", "value": "PRESS"},
        {"name": "Redraw 3D View when pressing the R Key",
         "idname": "proaligntools.check_running_modal",
         "type": "R", "value": "PRESS"},
        {"name": "Redraw 3D View when pressing the S Key",
         "idname": "proaligntools.check_running_modal",
         "type": "S", "value": "PRESS"},

        # These are mainly aimed to RELEASE running_modal, and recover the gizmos
        {"name": "Redraw 3D View when releasing the ESC Key",
         "idname": "proaligntools.check_running_modal",
         "type": "ESC", "value": "RELEASE"},
        {"name": "Redraw 3D View when releasing the RET Key",
         "idname": "proaligntools.check_running_modal",
         "type": "RET", "value": "RELEASE"},
        {"name": "Redraw 3D View when releasing the SPACE Key",
         "idname": "proaligntools.check_running_modal",
         "type": "SPACE", "value": "RELEASE"},
        {"name": "Redraw 3D View when releasing the LEFTMOUSE button",
         "idname": "proaligntools.check_running_modal",
         "type": "LEFTMOUSE", "value": "RELEASE"},
        {"name": "Redraw 3D View when releasing the RIGHTMOUSE button",
         "idname": "proaligntools.check_running_modal",
         "type": "RIGHTMOUSE", "value": "RELEASE"},

        # These are regularly needed to update the DummyEvent object and refresh the UI
        {"name": "Redraw 3D View when pressing/releasing the MIDDLEMOUSE button",
         "idname": "proaligntools.redraw",
         "type": "MIDDLEMOUSE", "value": "ANY"},

        {"name": "Redraw 3D View when pressing/releasing LEFT_CTRL",
         "idname": "proaligntools.redraw",
         "type": "LEFT_CTRL", "value": "ANY"},
        {"name": "Redraw 3D View when pressing/releasing RIGHT_CTRL",
         "idname": "proaligntools.redraw",
         "type": "RIGHT_CTRL", "value": "ANY"},

        {"name": "Redraw 3D View when pressing/releasing LEFT_ALT",
         "idname": "proaligntools.redraw",
         "type": "LEFT_ALT", "value": "ANY"},
        {"name": "Redraw 3D View when pressing/releasing RIGHT_ALT",
         "idname": "proaligntools.redraw",
         "type": "RIGHT_ALT", "value": "ANY"},

        {"name": "Redraw 3D View when pressing/releasing LEFT_SHIFT",
         "idname": "proaligntools.redraw",
         "type": "LEFT_SHIFT", "value": "ANY"},
        {"name": "Redraw 3D View when pressing/releasing RIGHT_SHIFT",
         "idname": "proaligntools.redraw",
         "type": "RIGHT_SHIFT", "value": "ANY"},
    )

    for shortcut in shortcuts:

        kmi = km.keymap_items.new(idname=shortcut["idname"],
                                  type=shortcut["type"],
                                  value=shortcut["value"],
                                  any=True)
        kmi.properties["name"] = shortcut["name"]
        addon_keymap_items.append((km, kmi))


def unregister():

    if align_tool_selected(bpy.context):

        bpy.ops.wm.tool_set_by_id(name="builtin.select_box", space_type="VIEW_3D")

    from .cache_system import CACHE_clear
    CACHE_clear()

    for km, kmi in addon_keymap_items:
        km.keymap_items.remove(kmi)

    wm = bpy.context.window_manager

    for km, kmi in addon_keymap_items:
        if km in wm.keyconfigs.addon.keymaps.values():
            if len(km.keymap_items) == 0:
                wm.keyconfigs.addon.keymaps.remove(km)

    addon_keymap_items.clear()

    for tool in tools:
        bpy.utils.unregister_tool(tool)

    for c in classes:
        bpy.utils.unregister_class(c)

    icons = wm.align_tool.icons[0]
    bpy.utils.previews.remove(icons)
    del icons

    del bpy.types.WindowManager.align_tool
