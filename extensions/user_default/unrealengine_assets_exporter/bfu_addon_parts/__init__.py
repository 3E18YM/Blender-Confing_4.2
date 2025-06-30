import bpy
import importlib

from . import bfu_panel_object
from . import bfu_panel_tools
from . import bfu_panel_export
from . import bfu_export_correct_and_improv_panel


if "bfu_panel_object" in locals():
    importlib.reload(bfu_panel_object)
if "bfu_panel_tools" in locals():
    importlib.reload(bfu_panel_tools)
if "bfu_panel_export" in locals():
    importlib.reload(bfu_panel_export)
if "bfu_export_correct_and_improv_panel" in locals():
    importlib.reload(bfu_export_correct_and_improv_panel)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_panel_object.register()
    bfu_panel_tools.register()
    bfu_panel_export.register()
    bfu_export_correct_and_improv_panel.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_export_correct_and_improv_panel.unregister()
    bfu_panel_export.unregister()
    bfu_panel_tools.unregister()
    bfu_panel_object.unregister()
