import bpy
import requests
from bpy.types import Operator
import addon_utils

# URL на JSON-файл с версией
VERSION_URL = "https://raw.githubusercontent.com/ilumetric/versions/main/PivotTransform.json"


def get_current_version():
    """
    Получить текущую версию аддона из bl_info.
    """
    for addon in addon_utils.modules():
        if addon.bl_info["name"] == "Pivot Transform":
            return addon.bl_info.get("version", (0, 0, 0))
    return (0, 0, 0)


def fetch_latest_version():
    """
    Получить последнюю версию аддона с GitHub.
    """
    try:
        # Выполняем HTTP-запрос
        response = requests.get(VERSION_URL, headers={"Cache-Control": "no-cache"})
        response.raise_for_status()
        version_data = response.json()

        # Парсим данные версии
        latest_version = tuple(map(int, version_data.get("version", "0.0.0").split(".")))
        return {
            "latest_version": latest_version,
            "supported_blender_versions": version_data.get("supported_blender_versions", []),
            "date": version_data.get("date", "N/A"),
            "download_url": version_data.get("download_url", ""),
            "release_notes": version_data.get("release_notes", "")
        }
    except Exception as e:
        print(f"Error while getting the version: {e}")
        return None


class PT_OT_check_updates(Operator):
    bl_idname = "pt.check_updates"
    bl_label = "Check for Updates"
    bl_description = "Check if there is an update available for Pivot Transform"

    update_available: bpy.props.BoolProperty(default=False)  # Есть ли обновление
    latest_version: bpy.props.StringProperty(default="")  # Последняя версия
    release_notes: bpy.props.StringProperty(default="")  # Примечания к релизу
    download_url: bpy.props.StringProperty(default="")  # Ссылка для загрузки
    current_version: bpy.props.StringProperty(default="")  # Текущая версия

    def invoke(self, context, event):
        # Получаем текущую версию
        current_version = get_current_version()
        self.current_version = ".".join(map(str, current_version))

        # Получаем данные о последней версии
        version_data = fetch_latest_version()
        if not version_data:
            self.report({"ERROR"}, "Could not fetch version information.")
            return {"CANCELLED"}

        # Сравниваем версии
        latest_version = version_data["latest_version"]
        if latest_version > current_version:
            self.update_available = True
            self.latest_version = ".".join(map(str, latest_version))
            self.release_notes = version_data["release_notes"]
            self.download_url = version_data["download_url"]
        else:
            self.update_available = False

        return context.window_manager.invoke_popup(self, width=400)

    def draw(self, context):
        layout = self.layout

        if self.update_available:
            layout.label(text="Update Available!", icon="INFO")
            layout.label(text=f"Latest Version: {self.latest_version}")
            layout.label(text=f"Current Version: {self.current_version}")
            layout.label(text=f"Release Notes: {self.release_notes}")
            layout.operator("wm.url_open", text="Download Update").url = self.download_url
        else:
            layout.label(text="You are using the latest version.", icon="CHECKMARK")
            layout.label(text=f"Current Version: {self.current_version}")

    def execute(self, context):
        return {"FINISHED"}



classes = [
    PT_OT_check_updates,
    ]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)