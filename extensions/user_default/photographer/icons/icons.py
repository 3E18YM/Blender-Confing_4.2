import os
from bpy.utils import previews
from ..constants import icons_folder

# global variable to store icons in
preview_collections = {}

def register():
    custom_icons = previews.new()

    files = os.listdir(icons_folder)

    for file in files:
        if file.lower().endswith(".png"):
            custom_icons.load(file[:-4].upper(), os.path.join(icons_folder, file), 'IMAGE')
    
    preview_collections["icons"] = custom_icons

def unregister():
    for custom_icons in preview_collections.values():
        previews.remove(custom_icons)
    preview_collections.clear()