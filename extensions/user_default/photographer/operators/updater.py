import re
import requests
import bpy
from .. import __package__ as base_package

update_url = 'https://api.github.com/repos/michelchafouin/photographer_updater/releases'
version_regex = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
changelog = []
latest_msg = "You are running the latest version of the add-on."

class PHOTOGRAPHER_OT_CheckForUpdate(bpy.types.Operator):
    bl_idname = "photographer.check_for_update"
    bl_label = "Check for Updates"
    bl_description = "Verify if you are running the latest version of the add-on"

    def execute(self,context):
        prefs = bpy.context.preferences.addons[base_package].preferences
        prefs.needs_update = ""

        # try:
        response = requests.get(update_url)
        if response.status_code == 200:
            resp_json = response.json()
            versions = {}
            for rel in resp_json:
                v_info = {tuple(map(int, rel['tag_name'].split('.'))):rel['body']}          
                # if version_regex.match(v_info[0]):
                #     versions.append(v_info)
                versions.update(v_info)
            versions = dict(sorted(versions.items(), key=lambda item: item[0]))
            versions = dict(reversed(versions.items()))

            # addon_version is set at registration in __init__
            latest_version = list(versions.keys())[0]
            latest_version_str = '.'.join(map(str, latest_version))

            # Can't compare strings directly, so convert to a tuple of ints
            print (addon_version, latest_version)
            if addon_version < latest_version:
                needs_update = f"Photographer {latest_version_str} is available!"
                changelog.clear()
                for v in versions:
                    if v > addon_version:
                        v_str = '.'.join(map(str, v))
                        changelog.append([v_str,versions[v]])
                
                print(changelog)
                prefs.needs_update = needs_update
            else:
                prefs.needs_update = latest_msg

        # except:
        #     prefs.needs_update = 'Update Check: Connection Failed.'
            
        return{'FINISHED'}
