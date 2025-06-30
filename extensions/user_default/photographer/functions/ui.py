import blf, bpy

def draw_object_name_under_mouse(self, target=False, parent=False):
    fontid = 0
    blf.position(fontid, self.mouse_pos[0] + 28, self.mouse_pos[1] + 12, 0)
    if bpy.app.version < (4, 0, 0):  
        blf.size(fontid, 12, 72)
    else:
        blf.size(fontid, 12)
    blf.color(fontid, 1.0,1.0,1.0,1.0)
    blf.draw(fontid, "Surface: ")

    blf.position(fontid, self.mouse_pos[0] + 86, self.mouse_pos[1] + 12, 0)
    blf.color(fontid, 1.0,0.7,0.02,1.0)
    blf.draw(fontid, self.object_name)

    if target:
        if parent:
            if bpy.app.version < (4, 0, 0):  
                blf.size(fontid, 12, 72)
            else:
                blf.size(fontid, 12)
            blf.position(fontid, self.mouse_pos[0] + 28, self.mouse_pos[1]-2, 0)
            blf.color(fontid, 0.85,0.85,0.85,0.7)
            blf.draw(fontid, "Parenting")
        else:
            if bpy.app.version < (4, 0, 0):  
                blf.size(fontid, 12, 72)
            else:
                blf.size(fontid, 12)
            blf.position(fontid, self.mouse_pos[0] + 28, self.mouse_pos[1]-2, 0)
            blf.color(fontid, 0.85,0.85,0.85,0.7)
            blf.draw(fontid, "Hold Shift to Parent")