import bpy, os, bpy.utils.previews
from .. import __package__ as base_package
from .. constants import (
    photographer_folder,
    HDR_FORMATS,
    SDR_FORMATS,
    IES_FORMATS,
    MOVIE_FORMATS,
)
from ..functions.functions import show_message
from subprocess import run
from time import sleep

preview_collections = {}
hdri_subfolders_enum = []
gobo_subfolders_enum = []
ies_subfolders_enum = []

def hdri_subfolders_return(self,context):
    # print (hdri_subfolders_enum)
    return hdri_subfolders_enum

def gobo_subfolders_return(self,context):
    # print (gobo_subfolders_enum)
    return gobo_subfolders_enum

def ies_subfolders_return(self,context):
    # print (ies_subfolders_enum)
    return ies_subfolders_enum


def scan_for_elements(path,type):
    if type in {'hdri', 'stmap'}:
        if path.lower().endswith(HDR_FORMATS):
            return (path, True)
        else:
            return None
    elif type == 'ies':
        if path.lower().endswith(IES_FORMATS):
            return (path, True)
        else:
            return None
    elif type in {'bokeh'}:
        if path.lower().endswith(SDR_FORMATS) or path.lower().endswith(HDR_FORMATS):
            return (path, True)
        else:
            return None
    elif type in {'gobo'}:
        if any(path.lower().endswith(format) for format in SDR_FORMATS + HDR_FORMATS + MOVIE_FORMATS):
            return (path, True)
        else:
            return None
    else:
        if path.lower().endswith(SDR_FORMATS):
            return (path, True)
        else:
            return None


def gen_thumbnails(image_paths, enum_items, pcoll):
    empty_path = os.path.join(os.path.dirname(__file__), 'empty.png')
    needs_thumb_path = os.path.join(os.path.dirname(__file__), 'needs_thumb.png')
    # For each image in the directory, load the thumb
    # unless it has already been loaded
    for i, im in enumerate(sorted(image_paths)):
        filepath, prev = im
        name = os.path.splitext(os.path.basename(filepath))[0]
        name = name.replace('.', ' ').replace('_', ' ').lower().capitalize()
        if filepath in pcoll:
            enum_items.append((filepath, name,
                               "", pcoll[filepath].icon_id, i))
        else:
            if prev:
                imgpath = filepath
                if any(filepath.lower().endswith(format) for format in HDR_FORMATS+MOVIE_FORMATS):
                    png = os.path.splitext(filepath)[0]+'.png'
                    thumb = thumbnail_path(filepath)
                    if os.path.exists(thumb):
                        imgpath = thumb
                    else:
                        imgpath = png

                    if not os.path.exists(imgpath):
                        if os.stat(filepath).st_size <100000000:
                            imgpath = filepath
                        else:
                            imgpath = needs_thumb_path
                elif filepath.lower().endswith(IES_FORMATS):
                    thumb = thumbnail_path(filepath)
                    if os.path.exists(thumb):
                        imgpath = thumb
                    if not os.path.exists(imgpath):
                        imgpath = needs_thumb_path
                        
                thumb = pcoll.load(filepath, imgpath, 'IMAGE')
            else:
                thumb = pcoll.load(filepath, empty_path, 'IMAGE')
            enum_items.append((filepath, name,
                               "", thumb.icon_id, i))
    return enum_items


def list_subfolders(subfolders_enum, folder_path, formats=HDR_FORMATS+SDR_FORMATS+IES_FORMATS+MOVIE_FORMATS):
    subfolders_enum.clear()
    if folder_path and os.path.exists(folder_path):
        folder = bpy.path.abspath(folder_path)
        base_files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(formats)]
        if base_files:
            subfolders_enum.append(('.','- Base Folder -',''))
        subfolders = [ f.path for f in os.scandir(folder) if f.is_dir() and f.name != '_thumbnails']
        for s in subfolders:
            files = [f for f in os.listdir(s) if os.path.isfile(os.path.join(s, f)) and f.lower().endswith(formats)]
            if files:
                folder_name = os.path.basename(s)
                subfolders_enum.append((folder_name, folder_name, ''))


def hdri_lib_path_update(self,context):
    prefs = bpy.context.preferences.addons[base_package].preferences
    list_subfolders(hdri_subfolders_enum,prefs.hdri_lib_path, HDR_FORMATS)
    # Refresh Thumbnails
    previews_unregister()
    previews_register()

def gobo_lib_path_update(self,context):
    prefs = bpy.context.preferences.addons[base_package].preferences
    list_subfolders(gobo_subfolders_enum,prefs.gobo_lib_path,HDR_FORMATS+SDR_FORMATS+MOVIE_FORMATS)
    # Refresh Thumbnails
    previews_unregister()
    previews_register()

def ies_lib_path_update(self,context):
    prefs = bpy.context.preferences.addons[base_package].preferences
    list_subfolders(ies_subfolders_enum,prefs.ies_lib_path,IES_FORMATS)
    # Refresh Thumbnails
    previews_unregister()
    previews_register()


def enum_previews_from_directory_items(self, context, type):
    pcoll = preview_collections["main"]
    prefs = context.preferences.addons[base_package].preferences
    light = None

    if type == 'bokeh':
        directory = bpy.path.abspath(prefs.bokeh_lib_path)
    elif type == 'opt_vignetting':
        directory = bpy.path.abspath(prefs.opt_vignetting_lib_path)
    elif type == 'gobo':
        directory = bpy.path.abspath(prefs.gobo_lib_path)
        if hasattr(context,'object'):
            if hasattr(context.object,'type') and context.object.type == 'LIGHT':
                light = context.object
        if light:
            category = light.data.photographer.gobo_category
            if category != ('.', '-Base Folder-',''):
                directory = os.path.join(directory, category)
    elif type == 'ies':
        directory = bpy.path.abspath(prefs.ies_lib_path)
        if hasattr(context,'object'):
            if hasattr(context.object,'type') and context.object.type == 'LIGHT':
                light = context.object
        if light:
            category = light.data.photographer.ies_category
            if category != ('.', '-Base Folder-',''):
                directory = os.path.join(directory, category)
    elif type == 'stmap':
        directory = bpy.path.abspath(prefs.stmap_lib_path)
    elif type == 'film_grain':
        directory = bpy.path.abspath(prefs.film_grain_lib_path)
    elif type == 'hdri':
        directory = bpy.path.abspath(prefs.hdri_lib_path)
        category = context.scene.lightmixer.hdri_category
        if category != ('.', '-Base Folder-',''):
            directory = os.path.join(directory, category)

    empty_path = os.path.join(os.path.dirname(__file__), 'empty.png')
    hdri_click_path = os.path.join(os.path.dirname(__file__), 'hdri_click.png')
    enum_items = []
    if type == 'hdri' and not prefs.hdri_auto_load:
        if 'hdri_click' in pcoll:
            enum_items=[(('hdri_click', '',
                               "", pcoll['hdri_click'].icon_id, -1))]
        else:
            hdri_click = pcoll.load('hdri_click', hdri_click_path, 'IMAGE')
            enum_items=[(('hdri_click', '', '', hdri_click.icon_id, -1))]

    if context is None:
        return enum_items
    # wm = context.window_manager
    if directory == pcoll.library_prev_dir:
        return pcoll.library_prevs

    if directory and os.path.exists(directory):
        image_paths = []
        for fn in os.listdir(directory):
            prev = scan_for_elements(os.path.join(directory, fn),type)
            if prev:
                image_paths.append(prev)

        enum_items = gen_thumbnails(image_paths, enum_items, pcoll)

    # Return validation
    if len(enum_items) == 0:
        if 'empty' in pcoll:
            enum_items.append(('empty', '',
                               "", pcoll['empty'].icon_id, 0))
        else:
            empty = pcoll.load('empty', empty_path, 'IMAGE')
            enum_items.append(('empty', '', '', empty.icon_id, 0))
    pcoll.library_prevs = enum_items
    pcoll.library_prev_dir = directory

    return pcoll.library_prevs

def thumbnail_path(source_image):
    path, file = os.path.split(source_image)
    thumbnail_path = os.path.join(path,"_thumbnails/")+os.path.splitext(file)[0]+".png"
    return thumbnail_path


class LIGHTMIXER_OT_generate_thumbnails(bpy.types.Operator):
    "Creates small PNG thumbnails next to your files"
    bl_idname = 'lightmixer.generate_thumbnails'
    bl_label = 'Generate Missing Thumbnails'
    bl_options = {'INTERNAL'}

    size_limit = 100

    image_type: bpy.props.EnumProperty(
        name = "Image Type",
        items = [('HDRI','HDRI',''),('GOBO','Gobo','')],
        default = 'HDRI',
    )

    include_small_hdris: bpy.props.BoolProperty(
        name="Include all HDRIs for faster menus",
        description=("Disable to only generate thumbnails "
                    "for HDRIs larger than " + str(size_limit) + "MB"),
        default=True
    )

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label(text="Will create small PNGs next to the Images sources if they do not have thumbnails.")
        col.label(text="This may take a long time, depending on the size of the library.")

        col.separator()
        col = layout.column(align=True)
        if self.image_type == 'HDRI':
            col.prop(self, 'include_small_hdris')

    def generate_thumb(self, source_image):
        thumb = thumbnail_path(source_image)
        cmd = [bpy.app.binary_path]
        cmd.append("--background")
        cmd.append("--factory-startup")
        cmd.append("--python")
        cmd.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "thumbnail_resize.py"))
        cmd.append('--')
        cmd.append(source_image)
        cmd.append('200')
        cmd.append(thumb)
        run(cmd)

    def execute(self, context):
        prefs = context.preferences.addons[base_package].preferences
        if self.image_type == 'HDRI':
            lib_path = prefs.hdri_lib_path
        elif self.image_type == 'GOBO':
            lib_path = prefs.gobo_lib_path

        sources = []
        thumbnails = []
        small_sources = []

        # List HDRIs in Library folder
        for root, dirs, files in os.walk(lib_path):
            for f in files:
                if any(f.lower().endswith(format) for format in HDR_FORMATS + MOVIE_FORMATS):
                    sources.append(os.path.join(root, f))

        # Remove HDRIs that already have a PNG thumbnail
        for s in sources:
            png = os.path.splitext(s)[0]+'.png'
            if os.path.exists(png):
                thumbnails.append(s)

            thumb = thumbnail_path(s)
            if os.path.exists(thumb):
                thumbnails.append(s)
        sources = set(sources) - set(thumbnails)

        # Remove HDRIs under 100 MB to only fix Missing Previews
        if not self.include_small_hdris:
            for s in sources:
                if os.stat(s).st_size <100000000:
                    small_sources.append(s)
            sources = set(sources) - set(small_sources)

        # print (hdris)

        if not sources:
            show_message("No missing thumbnails, the Images menu should be faster!")
            return {'FINISHED'}

        # Refresh Thumbnails
        previews_unregister()
        previews_register()

        threaded = True  # Set to False for debugging

        errors = []
        if threaded:
            from concurrent.futures import ThreadPoolExecutor
            executor = ThreadPoolExecutor(max_workers=4)
            threads = []
            for i, s in enumerate(sources):
                t = executor.submit(self.generate_thumb, s)
                threads.append(t)

            while (any(t._state != "FINISHED" for t in threads)):
                num_finished = 0
                for tt in threads:
                    if tt._state == "FINISHED":
                        num_finished += 1
                        if tt.result() is not None:
                            errors.append(tt.result())
                sleep(2)
        else:
            for num_finished, h in enumerate(sources):
                self.generate_thumb(h)

        if errors:
            for e in errors:
                print(e)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class LIGHTMIXER_OT_ies_thumb_gen(bpy.types.Operator):
    "Creates small PNG thumbnails next to your IES profiles"
    bl_idname = 'lightmixer.generate_ies_thumbs'
    bl_label = 'Generate IES profiles Thumbnails'
    bl_options = {'INTERNAL'}

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label(text="Will create PNG thumbnails to preview IES profiles.")
        col.label(text="This may take a few minutes.")

    def generate_thumb(self, ies):
        thumb = thumbnail_path(ies)
        cmd = [bpy.app.binary_path]
        blends_folder = os.path.join(photographer_folder,"blends")
        cmd.append(os.path.join(blends_folder,"ies_thumbnail.blend"))
        cmd.append("--background")
        cmd.append("--python")
        cmd.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ies_thumbnail.py"))
        cmd.append('--')
        cmd.append(ies)
        cmd.append('200')
        cmd.append(thumb)
        print(cmd)
        run(cmd)

    def execute(self, context):
        prefs = context.preferences.addons[base_package].preferences
        lib_path = prefs.ies_lib_path

        ies_profiles = []
        thumbnails = []

        # List IES in Library folder
        for root, dirs, files in os.walk(lib_path):
            for f in files:
                if f.lower().endswith(IES_FORMATS):
                    ies_profiles.append(os.path.join(root, f))

        # Remove IES that already have a PNG thumbnail
        for ies in ies_profiles:
            png = os.path.splitext(ies)[0]+'.png'
            if os.path.exists(png):
                thumbnails.append(ies)

            thumb = thumbnail_path(ies)
            if os.path.exists(thumb):
                thumbnails.append(ies)
        ies_profiles = set(ies_profiles) - set(thumbnails)

        if not ies_profiles:
            show_message("No missing thumbnails")
            return {'FINISHED'}

        # Refresh Thumbnails
        previews_unregister()
        previews_register()

        threaded = True  # Set to False for debugging

        errors = []
        if threaded:
            from concurrent.futures import ThreadPoolExecutor
            executor = ThreadPoolExecutor(max_workers=8)
            threads = []
            for i, ies in enumerate(ies_profiles):
                t = executor.submit(self.generate_thumb, ies)
                threads.append(t)

            while (any(t._state != "FINISHED" for t in threads)):
                num_finished = 0
                for tt in threads:
                    if tt._state == "FINISHED":
                        num_finished += 1
                        if tt.result() is not None:
                            errors.append(tt.result())
                sleep(2)
        else:
            for num_finished, ies in enumerate(ies_profiles):
                self.generate_thumb(ies)

        if errors:
            for e in errors:
                print(e)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

classes = (
    LIGHTMIXER_OT_generate_thumbnails,
    LIGHTMIXER_OT_ies_thumb_gen,
)

def previews_register():
    pcoll = bpy.utils.previews.new()
    pcoll.library_prev_dir = ""
    pcoll.library_prevs = ""

    preview_collections["main"] = pcoll

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    previews_register()

    prefs = bpy.context.preferences.addons[base_package].preferences
    list_subfolders(hdri_subfolders_enum,prefs.hdri_lib_path,HDR_FORMATS)
    list_subfolders(gobo_subfolders_enum,prefs.gobo_lib_path,HDR_FORMATS + SDR_FORMATS + MOVIE_FORMATS)
    list_subfolders(ies_subfolders_enum,prefs.ies_lib_path, IES_FORMATS)

def previews_unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

def unregister():
    previews_unregister()
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
