# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import bpy
from .. import bfu_cached_asset_list
from .. import bfu_check_potential_error


class BFU_OT_ShowAssetToExport(bpy.types.Operator):
    bl_label = "Show asset(s)"
    bl_idname = "object.showasset"
    bl_description = "Click to show assets that are to be exported."

    def execute(self, context):

        obj = context.object
        if obj:
            if obj.type == "ARMATURE":
                animation_asset_cache = bfu_cached_asset_list.GetAnimationAssetCache(obj)
                animation_asset_cache.UpdateActionCache()
                

        final_asset_cache = bfu_cached_asset_list.GetfinalAssetCache()
        final_asset_list_to_export = final_asset_cache.GetFinalAssetList()
        popup_title = "Assets list"
        if len(final_asset_list_to_export) > 0:
            popup_title = str(len(final_asset_list_to_export))+' asset(s) will be exported.'
        else:
            popup_title = 'No exportable assets were found.'

        def draw(self, context: bpy.types.Context):
            col = self.layout.column()
            for asset in final_asset_list_to_export:
                asset :bfu_cached_asset_list.AssetToExport
                row = col.row()
                if asset.obj is not None:
                    if asset.action is not None:
                        if (type(asset.action) is bpy.types.Action):
                            # Action name
                            action = asset.action.name
                        elif (type(asset.action) is bpy.types.AnimData):
                            # Nonlinear name
                            action = asset.obj.bfu_anim_nla_export_name
                        else:
                            action = "..."
                        row.label(
                            text="- ["+asset.name+"] --> " +
                            action+" ("+asset.asset_type+")")
                    else:
                        if asset.asset_type != "Collection StaticMesh":
                            row.label(
                                text="- "+asset.name +
                                " ("+asset.asset_type+")")
                        else:
                            row.label(
                                text="- "+asset.obj.name +
                                " ("+asset.asset_type+")")

                else:
                    row.label(text="- ("+asset.asset_type+")")
        bpy.context.window_manager.popup_menu(
            draw,
            title=popup_title,
            icon='PACKAGE')
        return {'FINISHED'}

class BFU_OT_CheckPotentialErrorPopup(bpy.types.Operator):
    bl_label = "Check Potential Errors"
    bl_idname = "object.checkpotentialerror"
    bl_description = "Check potential errors."
    text = "none"

    def execute(self, context):
        fix_info = bfu_check_potential_error.bfu_check_utils.process_general_fix()
        invoke_info = ""
        for x, fix_info_key in enumerate(fix_info):
            fix_info_data = fix_info[fix_info_key]
            invoke_info += fix_info_key + ": " + str(fix_info_data) 
            if x < len(fix_info)-1:
                invoke_info += "\n"

        
        bfu_check_potential_error.bfu_check_utils.update_unreal_potential_error()
        bpy.ops.object.openpotentialerror(
            "INVOKE_DEFAULT", 
            invoke_info=invoke_info,
            )
        return {'FINISHED'}

class BFU_OT_OpenPotentialErrorPopup(bpy.types.Operator):
    bl_label = "Open potential errors"
    bl_idname = "object.openpotentialerror"
    bl_description = "Open potential errors"
    invoke_info: bpy.props.StringProperty(default="...")

    class BFU_OT_FixitTarget(bpy.types.Operator):
        bl_label = "Fix it !"
        bl_idname = "object.fixit_objet"
        bl_description = "Correct target error"
        errorIndex: bpy.props.IntProperty(default=-1)

        def execute(self, context):
            result = bfu_check_potential_error.bfu_check_utils.TryToCorrectPotentialError(self.errorIndex)
            self.report({'INFO'}, result)
            return {'FINISHED'}

    class BFU_OT_SelectObjectButton(bpy.types.Operator):
        bl_label = "Select(Object)"
        bl_idname = "object.select_error_objet"
        bl_description = "Select target Object."
        errorIndex: bpy.props.IntProperty(default=-1)

        def execute(self, context):
            bfu_check_potential_error.bfu_check_utils.select_potential_error_object(self.errorIndex)
            return {'FINISHED'}

    class BFU_OT_SelectVertexButton(bpy.types.Operator):
        bl_label = "Select(Vertex)"
        bl_idname = "object.select_error_vertex"
        bl_description = "Select target Vertex."
        errorIndex: bpy.props.IntProperty(default=-1)

        def execute(self, context):
            bfu_check_potential_error.bfu_check_utils.SelectPotentialErrorVertex(self.errorIndex)
            return {'FINISHED'}

    class BFU_OT_SelectPoseBoneButton(bpy.types.Operator):
        bl_label = "Select(PoseBone)"
        bl_idname = "object.select_error_posebone"
        bl_description = "Select target Pose Bone."
        errorIndex: bpy.props.IntProperty(default=-1)

        def execute(self, context):
            bfu_check_potential_error.bfu_check_utils.SelectPotentialErrorPoseBone(self.errorIndex)
            return {'FINISHED'}

    class BFU_OT_OpenPotentialErrorDocs(bpy.types.Operator):
        bl_label = "Open docs"
        bl_idname = "object.open_potential_error_docs"
        bl_description = "Open potential error docs."
        octicon: bpy.props.StringProperty(default="")

        def execute(self, context):
            os.system(
                "start \"\" " +
                "https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/How-avoid-potential-errors" +
                "#"+self.octicon)
            return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=1020)

    def check(self, context):
        return True

    def draw(self, context: bpy.types.Context):

        layout = self.layout
        if len(bpy.context.scene.potentialErrorList) > 0:
            popup_title = (
                str(len(bpy.context.scene.potentialErrorList)) +
                " potential error(s) found!")
        else:
            popup_title = "No potential error to correct!"


        layout.label(text=popup_title)
        invoke_info_lines = self.invoke_info.split("\n")
        for invoke_info_line in invoke_info_lines:
            layout.label(text="- "+invoke_info_line)
        
        layout.separator()
        row = layout.row()
        col = row.column()
        for x in range(len(bpy.context.scene.potentialErrorList)):
            error = bpy.context.scene.potentialErrorList[x]

            myLine = col.box().split(factor=0.85)
            # ----
            if error.type == 0:
                msgType = 'INFO'
                msgIcon = 'INFO'
            elif error.type == 1:
                msgType = 'WARNING'
                msgIcon = 'ERROR'
            elif error.type == 2:
                msgType = 'ERROR'
                msgIcon = 'CANCEL'
            # ----

            # Text
            TextLine = myLine.column()
            errorFullMsg = msgType+": "+error.text
            splitedText = errorFullMsg.split("\n")

            for text, Line in enumerate(splitedText):
                if (text < 1):

                    FisrtTextLine = TextLine.row()
                    if (error.docsOcticon != "None"):  # Doc button
                        props = FisrtTextLine.operator(
                            "object.open_potential_error_docs",
                            icon="HELP",
                            text="")
                        props.octicon = error.docsOcticon

                    FisrtTextLine.label(text=Line, icon=msgIcon)
                else:
                    TextLine.label(text=Line)

            # Select and fix button
            ButtonLine = myLine.column()
            if (error.correctRef != "None"):
                props = ButtonLine.operator(
                    "object.fixit_objet",
                    text=error.correctlabel)
                props.errorIndex = x
            if (error.object is not None):
                if (error.selectObjectButton):
                    props = ButtonLine.operator(
                        "object.select_error_objet")
                    props.errorIndex = x
                if (error.selectVertexButton):
                    props = ButtonLine.operator(
                        "object.select_error_vertex")
                    props.errorIndex = x
                if (error.selectPoseBoneButton):
                    props = ButtonLine.operator(
                        "object.select_error_posebone")
                    props.errorIndex = x



# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_ShowAssetToExport,
    BFU_OT_CheckPotentialErrorPopup,
    BFU_OT_OpenPotentialErrorPopup,
    BFU_OT_OpenPotentialErrorPopup.BFU_OT_FixitTarget,
    BFU_OT_OpenPotentialErrorPopup.BFU_OT_SelectObjectButton,
    BFU_OT_OpenPotentialErrorPopup.BFU_OT_SelectVertexButton,
    BFU_OT_OpenPotentialErrorPopup.BFU_OT_SelectPoseBoneButton,
    BFU_OT_OpenPotentialErrorPopup.BFU_OT_OpenPotentialErrorDocs,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

