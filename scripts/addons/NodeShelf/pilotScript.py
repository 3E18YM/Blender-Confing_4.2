import random
import bpy
import os
import csv

import addon_utils



def get_node_groups(self, context):
    ns_prefs = context.preferences.addons['NodeShelf'].preferences
    data_folder = ns_prefs.data_folder
    items = []
    for f in os.listdir(data_folder):
        if (".csv" in f) and ("_InOuts" not in f) and ("_Links" not in f):
            groupName=f.removesuffix(".csv")
            item = (groupName, groupName, "")
            items.append(item)

    return items

class NSProps(bpy.types.PropertyGroup):
    width: bpy.props.FloatProperty(
        name="Width",
        description="Room Width",
        default=4,
        min=0, soft_max=10
    )
    folder_path: bpy.props.StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default=""
    )
    group_name: bpy.props.StringProperty(
        name="Group Name",
        default="Node Group Name",
        description="your node group will be saved with this name"
    )
    node_library: bpy.props.EnumProperty(
        name="Node Groups",
        description="Select the node group you want to load",
        items=get_node_groups
    )



class NODESHELF_PT_Main(bpy.types.Panel):
    bl_idname = 'NODESHELF_PT_Main'
    bl_label = 'NodeShelf '
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'NodeShelf'

    def draw(self, context):
        nodeshelf_props = context.scene.nodeshelf_props
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.operator("nodeshelf.initiate")
        row = box.row()
        row.prop(nodeshelf_props, "group_name")
        row = box.row()
        row.operator("nodeshelf.save")
        box = layout.box()
        row = box.row()
        row.prop(nodeshelf_props, "node_library")
        row = box.row()
        row.operator("nodeshelf.load")
        row.operator("nodeshelf.load_all")


class NODESHELF_OT_start(bpy.types.Operator):
    bl_idname = 'nodeshelf.initiate'
    bl_label = 'Initiate your Node Shelf'

    def execute(self, context):
        ns_prefs = context.preferences.addons['NodeShelf'].preferences
        data_folder = ns_prefs.data_folder
        exists = False
        for f in os.listdir(data_folder):
            if f == "NodeShelf.blend":
                exists = True
                blendPath = os.path.join(data_folder, f)
        if not exists:
            print("DOESNT EXIST")
        else:
            with bpy.data.libraries.load(blendPath, link=False) as (data_from, data_to):
                data_to.node_groups = data_from.node_groups
                print(f"appended {data_to.node_groups}")
            print("EXISTS")
        return {'FINISHED'}


def formatNode(name):
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "NodeShelf":
            filepath = mod.__file__
    folder = filepath.replace("__init__.py", "")
    csvNames = os.path.join(folder, "NodeNames.csv")
    with open(csvNames, "r") as f:
        readout = csv.reader(f)
        for i, n in enumerate(readout):
            if n[1] == name:
                actualName = n[0]

    return actualName

class NODESHELF_OT_save(bpy.types.Operator):
    bl_idname = 'nodeshelf.save'
    bl_label = 'Save Group'

    def execute(self, context):
        nodeshelf_props = context.scene.nodeshelf_props
        ns_prefs = context.preferences.addons['NodeShelf'].preferences
        data_folder = ns_prefs.data_folder
        group_name = nodeshelf_props.group_name
        csvFile = os.path.join(data_folder, f"{group_name}.csv")
        linkFile = os.path.join(data_folder, f"{group_name}_Links.csv")
        inOutFile = os.path.join(data_folder, f"{group_name}_InOuts.csv")
        active_tree = context.space_data.node_tree
        print("")
        for node in active_tree.nodes:
            if node.select == True:
                try:
                    grp_tree = node.node_tree
                    with open(csvFile, "a", newline="") as f:
                        writer = csv.writer(f)
                        theRow = ["Node Name", "Node Type", "Location X", "Location Y", "Color", "Dimensions"]

                        writer.writerow(theRow)

                        for n in grp_tree.nodes:
                            theRow = []

                            theRow.append(n.name)
                            theRow.append(n.type)
                            theRow.append(n.location[0])
                            theRow.append(n.location[1])
                            if n.type == 'FRAME':
                                theRow.append(tuple(n.color))
                                theRow.append(tuple(n.dimensions))


                            writer.writerow(theRow)

                    with open(inOutFile, "a", newline="") as lf:
                        writer = csv.writer(lf)
                        theRow = ["InOut", "Socket Name", "Socket Type"]
                        writer.writerow(theRow)
                        if grp_tree.inputs != []:
                            for inp in grp_tree.inputs:
                                theRow = []
                                theRow.append("INPUT")
                                theRow.append(inp.name)
                                theType = formatNode(inp.type)
                                theRow.append(theType)
                                writer.writerow(theRow)
                        if grp_tree.outputs != []:
                            for outp in grp_tree.outputs:
                                theRow = []
                                theRow.append("OUTPUT")
                                theRow.append(outp.name)
                                theType = formatNode(outp.type)
                                theRow.append(theType)
                                writer.writerow(theRow)

                    with open(linkFile, "a", newline="") as lf:
                        writer = csv.writer(lf)
                        theRow = ["From Socket Name", "From Socket Node", "To Socket Name", "To Socket Node",]
                        writer.writerow(theRow)
                        for link in grp_tree.links:
                            theRow = []
                            theRow.append(link.from_socket.name)
                            theRow.append(link.from_socket.node.name)
                            theRow.append(link.to_socket.name)
                            theRow.append(link.to_socket.node.name)
                            writer.writerow(theRow)


                except:
                    self.report({"WARNING"}, message="This is not a Group")
                    print("apparently this aint a group")






        return {'FINISHED'}


def get_groups(self, context):
    ns_prefs = context.preferences.addons['NodeShelf'].preferences
    data_folder = ns_prefs.data_folder
    items = []
    for f in os.listdir(data_folder):
        if ".csv" in f:
            groupName=f.removesuffix(".csv")
            items.append(groupName)

    return items



def load_group(self, context):
    nodeshelf_props = context.scene.nodeshelf_props
    ns_prefs = context.preferences.addons['NodeShelf'].preferences
    data_folder = ns_prefs.data_folder
    node_library = nodeshelf_props.node_library

    csvFile = os.path.join(data_folder, f"{node_library}.csv")
    inOutFile = os.path.join(data_folder, f"{node_library}_InOuts.csv")
    linkFile = os.path.join(data_folder, f"{node_library}_Links.csv")
    active_tree = context.space_data.node_tree

    exists = False
    for ng in bpy.data.node_groups:
        if ng.name == node_library:
            exists = True
    if not exists:
        with open(csvFile, "r") as f:
            readout = csv.reader(f)
            l_group = bpy.data.node_groups.new(f"{node_library}", "GeometryNodeTree")
            for i, n in enumerate(readout):
                if i != 0:
                    print(f"working on {n[0]}")
                    l_node = l_group.nodes.new(type=formatNode(n[1]))

                    if l_node.type == 'FRAME':
                        l_node.use_custom_color = True
                        colorList = n[4].strip(')(').split(', ')
                        nuColor = []
                        for c in colorList:
                            nuColor.append(float(c))
                        l_node.color = tuple(nuColor)

                        dimList = n[5].strip(')(').split(', ')
                        nuDims = []
                        for c in dimList:
                            nuDims.append(float(c))
                        l_node.width = nuDims[0]
                        l_node.height = nuDims[1]

                    l_node.name = n[0]
                    l_node.location[0] = float(n[2])
                    l_node.location[1] = float(n[3])

        with open(inOutFile, "r") as lf:
            readout = csv.reader(lf)
            for i, n in enumerate(readout):
                if i != 0:
                    if n[0] == "INPUT":
                        l_group.inputs.new(n[2], n[1])
                    else:
                        l_group.outputs.new(n[2], n[1])

        with open(linkFile, "r") as lf:
            readout = csv.reader(lf)
            for i, n in enumerate(readout):
                if i != 0:
                    fromNode = l_group.nodes[n[1]]
                    toNode = l_group.nodes[n[3]]
                    l_group.links.new(fromNode.outputs[n[0]], toNode.inputs[n[2]])
                    print(f"creating a link between {n[1]} with output {n[0]} and {n[3]} in input {n[2]}")


    else:
        self.report({"INFO"}, message="Node Group is already in this Blend file")


class NODESHELF_OT_load(bpy.types.Operator):
    bl_idname = 'nodeshelf.load'
    bl_label = 'Load Group'

    def execute(self, context):

        load_group(self, context)

        return {'FINISHED'}



class NODESHELF_OT_load_all(bpy.types.Operator):
    bl_idname = 'nodeshelf.load_all'
    bl_label = 'Load All'

    def execute(self, context):
        nodeshelf_props = context.scene.nodeshelf_props
        grps = get_groups(self, context)
        for gr in grps:
            nodeshelf_props.node_library = gr
            load_group(self, context)

        return {'FINISHED'}


classes = [
    NSProps,
    NODESHELF_OT_start,
    NODESHELF_OT_save,
    NODESHELF_OT_load,
    NODESHELF_OT_load_all,
    NODESHELF_PT_Main,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.nodeshelf_props = bpy.props.PointerProperty(type=NSProps)



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.nodeshelf_props

