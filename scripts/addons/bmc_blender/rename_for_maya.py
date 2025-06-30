
def maya_name(obj_name):    
    if not obj_name: #name is emty
        obj_name = "untitle"
    else:  
        for i in range(len(obj_name)): #replace char is not char A-Z a-z underscore and colon  
            if ord(obj_name[i]) not in range(48,58) and ord(obj_name[i]) not in range(65,91) and ord(obj_name[i]) not in range(97,123) and ord(obj_name[i]) is not 95:
                obj_name = obj_name[:i] + "_" + obj_name[i+1:]
        
        for i in range(len(obj_name)+1): # remove char if first char is number         
            if ord(obj_name[0]) in range(48,58): 
                obj_name = obj_name[1:]
    return obj_name

def maya_name_check(obj_name):
    if not obj_name: #name is emty
        return False
    else:  
        for i in range(len(obj_name)): #char is not char A-Z a-z underscore and colon  
            if ord(obj_name[i]) not in range(48,58) and ord(obj_name[i]) not in range(65,91) and ord(obj_name[i]) not in range(97,123) and ord(obj_name[i]) is not 95:
                return False
        
        for i in range(len(obj_name)+1): #first char is number         
            if ord(obj_name[0]) in range(48,58): 
                return False
    return True



    

