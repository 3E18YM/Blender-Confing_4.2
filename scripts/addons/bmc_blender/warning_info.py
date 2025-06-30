import bpy

def ShowMessageBox(message="", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
    return {'FINISHED'}

#not allow if char is not char A-Z a-z and underscore in Maya
def check_name(objects): 
    found =  False    

    for obj in objects: 
        if not obj.name: #name is emty
            found = True
            break
        else:  
            for i in range(len(obj.name)): 
                # find number in first char
                if ord(obj.name[0]) in range(48,57):
                    found =  True
                    break 
                #find char is not char A-Z a-z and underscore
                if ord(obj.name[i]) not in range(48,58) and ord(obj.name[i]) not in range(65,91) and ord(obj.name[i]) not in range(97,123) and ord(obj.name[i]) is not 95:
                    found =  True
                    break
    
    return found