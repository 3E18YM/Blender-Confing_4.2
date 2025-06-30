'''
Copyright (C) 2019
rudy.michau@gmail.com

Created by RUDY MICHAU

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from bpy.types import Operator, Menu, AddonPreferences
import bpy.utils.previews
import rna_keymap_ui
import urllib
import os
from os.path import join, dirname, realpath

from .operators import *
from .toolbox import *
from .helpers import *
from .primitives import *

bl_info = {
    "name": "Fluent : Power Trip",
    "description": "Hard surface modeling tools",
    "author": "Rudy MICHAU",
    "version": (2, 1, 2),
    "blender": (3, 3, 1),
    "location": "View3D",
    "wiki_url": "https://cgthoughts.com/fluent/doc/",
    "category": "Object"}

# if "bpy" in locals():
#     import importlib
#     reloadable_modules = [
#         'bevels',
#         'drawing',
#         'helpers',
#         'independant_helpers',
#         'math_functions',
#         'modifiers',
#         'operators',
#         'primitives',
#         'shapes',
#         'toolbox',
#         'ui_button',
#         'viewport_drawing'
#     ]
#
#     for module in reloadable_modules:
#         if module in locals():
#             try:
#                 importlib.reload(locals()[module])
#             except:pass

init_pref = False
init_change = False
TEMPS = 0

translation = {
    "ENGLISH": {
        "cutCall": "Cut/Add",
        "sliceCall": "Slice",
        "createCall": "Create",
        "addLatestBevel": "Add a bevel",
        "symetrizePlan": "Symetrize a Plan",
        "autoComplete": "Auto-Complete",
        "booleanDisplay": "Show boolean",
        "wireframe": "Show wireframe",
        "latestBevelWidth": "Bevel width",
        "angleLimit": "Angle Limit",
        "defaultDepth": "Default depth",
        "corner": "Default bevel width",
        "bevelResolution": "Bevel resolution",
        "circleResolution": "Default circle resolution",
        "autoMirror": "Auto-mirror",
        "otherAdjustment": "Other adjustments",
        "moveObj": "Move object along plane : G, Shift+Z+Z",
        "moveObjZ": "Up/Down object along normal of plane : G, Z, Z",
        "finish": "Finish : Right Click",
        "showBoolObj": "Show / Hide boolean object : H",
        "cancel": "Cancel : Esc",
        "finishCurrentadjustment": "Finish current adjustment : Left Click",
        "horizontalMouseMove": "Horizontal mouse move",
        "fastSlow": "Fast/Slow",
        "thicknessOffset": "Thickness / Offset toggle",
        "crossModel": "Cross the model",
        "useFlyMenu": "Use the fly-out menu : hold left-click",
        "roundStraight": "Round/Straight",
        "remove": "Remove",
        "steps": "Steps",
        "smoothCircle": "High resolution",
        "pressAxis": "Press an axis to show it, press it again to hide it",
        "axisSelection": "Current axis",
        "offset": "Offset",
        "count": "Count",
        'radius': 'Radius',
        'number': "Number of elements",
        'rotation90': '90° rotation',
        'solidify': 'Solidify',
        'firstBevel': 'First Bevel',
        'secondbevel': 'Second Bevel',
        'mirror': 'mirror',
        'array': 'Array',
        'circularArray': 'Circular Array',
        'adjustment': 'adjustment',
        'latestBevelSegments': 'Latest bevel segments',
        'validateDrawing': 'Validate polygon',
        'validatePath': 'Validate path',
        'fakeSlice': 'Fake slice',
        'duplicateExtract': 'Duplicate/Extract',
        'synchBool': 'Synchronize boolean objects',
        'makePreset': 'Make/Clear preset',
        'cutAgain': 'Cut again',
        'cleanBooleanApplication': 'Boolean supports',
        'editCall': 'Edit',
        'technicalDisplay': 'Technical Display',
        'displayGrid': 'Display grid : Right Click on a face',
        'drawOutside': 'Draw outside : Shift + Left Click on face to set plane',
        'snap': 'Snap : Hold Ctrl',
        'drawFromCenter': 'Draw from center : Hold Shift',
        'drawSquare': 'Draw square : Hold Ctrl',
        'drawOrtho': 'Draw in ortho direction',
        'undo': 'Undo',
        'gridResolution': 'Grid resolution',
        'gridRotation': 'Grid rotation',
        'alignmentHelper': 'Alignment helper',
        'revolveMode': 'Revolver Mode',
        'revolve': 'Revolve',
        'vertexSelection': 'Vertex selection',
        'convexeConcaveStraight': 'Concave/Straight/Convex',
        'latestBevelGlobal': 'Latest bevel Factor',
        'hideGrid': 'Show/Hide de the grid',
        'wireStart': 'Place the first point',
        'wireEnd': 'Place the last point',
        'snapCenterFace': 'Snap the center of the face',
        'howToPlate': 'Select faces and press Enter/Space',
        'bevelAdjustment': 'BEVEL ADJUSTMENT',
        'solidifyAdjustment': 'SOLIDIFY ADJUSTMENT',
        'segments': 'Segments',
        'ringSelect': 'Select a ring',
        'snapDirection': 'Align the second point with the first',
        'bevelProfile': 'Concave profile value',
        'loopSlide': 'Loop Slide',
        'previousSize': 'Back to previous bevel size',
        'cleanVertexGroup': 'VG cleaner',
        'outerBevelSegments': 'Outer bevel segement',
        'exit': 'Exit',
        'setMirrorObject': 'Set the mirror object',
        'normalRepair': 'Normal repair',
        'plate': 'Plate',
        'wire': 'Wire',
        'pipe': 'Pipe',
        'grid': 'Grid',
        'sim_set': 'Simulation settings',
        'angle': 'Angle',
        'MoveAxis': 'Align rotation to object',
        'centerArray': 'Centered array',
        'axisLock': 'Axis locked',
        'duplicate': 'Duplicate',
        'convexeStraight': 'Convex/Straight',
        'axisAlign': 'Axis align'
    },
    "CHINESE": {
        "cutCall": "切割/添加",
        "sliceCall": "切片",
        "createCall": "创建",
        "addLatestBevel": "给当前对象添加倒角",
        "symetrizePlan": "使对称",
        "autoComplete": "自动完成",
        "booleanDisplay": "显示/隐藏布尔对象",
        "wireframe": "线框",
        "latestBevelWidth": "当前倒角宽度",
        "angleLimit": "角度限制",
        "defaultDepth": "默认深度",
        "corner": "默认倒角宽度",
        "bevelResolution": "倒角分辨率",
        "circleResolution": "默认棱分段数",
        "autoMirror": "自动镜像",
        "otherAdjustment": "其他调整",
        "moveObj": "沿平面移动 : G, Shift+Z+Z",
        "moveObjZ": "沿平面法线上/下移动对象 : G, Z, Z",
        "finish": "完成 : 点击右键",
        "showBoolObj": "显示/隐藏 布尔对象 : H",
        "cancel": "取消 : Esc",
        "finishCurrentadjustment": "完成当前调整: 点击左键",
        "horizontalMouseMove": "水平移动鼠标",
        "fastSlow": "快速/慢速",
        "thicknessOffset": "厚度/偏移模式切换",
        "crossModel": "贯穿模型",
        "useFlyMenu": "使用浮动菜单 : 按住左键, 把鼠标指针移动到你想使用的工具上去, 然后松开左键",
        "roundStraight": "圆角/直角",
        "remove": "移除",
        "steps": "分辨率",
        "smoothCircle": "高分辨",
        "pressAxis": "按下一个轴显示，再按一次隐藏",
        "axisSelection": "激活轴",
        "offset": "偏移",
        "count": "计数",
        'radius': '半径',
        'number': "元素数量",
        'rotation90': '90° 旋转',
        'solidify': '固化',
        'firstBevel': '倒角（一）',
        'secondbevel': '倒角（二）',
        'mirror': '镜像',
        'array': '阵列',
        'circularArray': '圆形阵列',
        'adjustment': '调整',
        'latestBevelSegments': '最新一次的倒角段数',
        'validateDrawing': '完成多边形',
        'validatePath': '完成路径',
        'fakeSlice': '伪切割',
        'duplicateExtract': '复制',
        'synchBool': '同步布尔对象',
        'makePreset': '创建/清除预设',
        'cutAgain': '再切割',
        'cleanBooleanApplication': '布尔修复(实体)',
        'editCall': '编辑',
        'technicalDisplay': '显示/隐藏 全部',
        'displayGrid': '显示网格 : 右键选择一个面',
        'drawOutside': '物体外绘制 : Shift+鼠标左键 选择参照面',
        'snap': '45°角绘制 : 按住 Ctrl',
        'drawFromCenter': '中心绘制 : 按住 Shift',
        'drawSquare': '绘制正方形 : 按住 Ctrl',
        'drawOrtho': '从其他方向绘制',
        'undo': '撤销',
        'gridResolution': '网格密度',
        'gridRotation': '网格旋转',
        'alignmentHelper': '直线参照',
        'revolveMode': '旋转模式',
        'revolve': '旋转',
        'vertexSelection': '顶点选择',
        'convexeConcaveStraight': '倒角模式：凸/平/凹',
        'latestBevelGlobal': 'Latest bevel Factor',
        'hideGrid': '显示/隐藏 网格',
        'wireStart': '设置第一个点',
        'wireEnd': '设置最后一个点',
        'snapCenterFace': '选择面的中心',
        'howToPlate': '选择面后按Enter/Space',
        'bevel': '倒角调整',
        'solidifyAdjustment': '实体化调整',
        'segments': '倒角段数',
        'ringSelect': 'Select a ring',
        'snapDirection': '将第二个点与第一个点对齐',
        'bevelProfile': 'Concave profile value',
        'loopSlide': 'Loop Slide',
        'previousSize': '返回上一个倒角值',
        'cleanVertexGroup': '清理顶点组',
        'outerBevelSegments': '外轮廓倒角段数',
        'exit': '退出',
        'setMirrorObject': '设置镜像对象',
        'normalRepair': '法线修复',
        'plate': '挤出平面',
        'wire': '添加线',
        'pipe': '添加管道',
        'grid': '添加网格',
        'sim_set': 'Simulation settings',
        'angle': 'Angle',
        'MoveAxis': 'Move axis',
        'centerArray': 'Centered array',
        'axisLock': 'Axis locked',
        'duplicate': 'Duplicate',
        'convexeStraight': 'Convex/Straight',
        'axisAlign': 'Axis align'
    },
    "TRAD_CHINESE": {
        "cutCall": "切/增加",
        "sliceCall": "切片",
        "createCall": "創造",
        "addLatestBevel": "新增最後斜角",
        "symetrizePlan": "對稱平面",
        "autoComplete": "自動完成",
        "booleanDisplay": "顯示/隱藏布林物件",
        "wireframe": "顯示/隱藏線架構",
        "latestBevelWidth": "最後斜角寬度",
        "angleLimit": "角度極限",
        "defaultDepth": "預設深度",
        "corner": "預設斜角寬度",
        "bevelResolution": "斜角解析度",
        "circleResolution": "預設圓解析度",
        "autoMirror": "自動鏡射",
        "otherAdjustment": "其他調整",
        "moveObj": "沿平面移動物件 : G, Shift+Z+Z",
        "moveObjZ": "沿平面法向移動物件 : G, Z, Z",
        "finish": "完成 : 右鍵",
        "showBoolObj": "顯示/隱藏布林物件 : H",
        "cancel": "取消 : Esc",
        "finishCurrentadjustment": "完成目前調整 : 左鍵",
        "horizontalMouseMove": "滑鼠水平移動",
        "fastSlow": "快/慢",
        "thicknessOffset": "厚度/偏移切換",
        "crossModel": "模型剖面",
        "useFlyMenu": "使用懸空面板 : 按住左鍵, 游標移到欲選工具, 放開左鍵",
        "roundStraight": "圓/直",
        "remove": "移除",
        "steps": "階數",
        "smoothCircle": "高解析度",
        "pressAxis": "在軸上按一次顯示, 再按一次隱藏",
        "axisSelection": "啟動軸",
        "offset": "偏移",
        "count": "數量",
        'radius': '半徑',
        'number': "元素數量",
        'rotation90': '90度旋轉',
        'solidify': '實體化',
        'firstBevel': '第一斜角',
        'secondbevel': '第二斜角',
        'mirror': '鏡射',
        'array': '陣列',
        'circularArray': '圓形陣列',
        'adjustment': '調整',
        'latestBevelSegments': '最後斜角段數',
        'validateDrawing': '驗證多邊形',
        'validatePath': '驗證路徑',
        'fakeSlice': '假切片',
        'duplicateExtract': '複製',
        'synchBool': '同步布林物件',
        'makePreset': '建立/清空預設',
        'cutAgain': '再切',
        'cleanBooleanApplication': '布林優化',
        'editCall': '編輯',
        'technicalDisplay': '技術顯示',
        'displayGrid': '顯示格線：在面上按右鍵',
        'drawOutside': '從外面畫：畫之前在面上按Shift +左鍵',
        'snap': 'Snap : 鎖點：按住Ctrl鍵',
        'drawFromCenter': '從中心畫：按住Shift鍵',
        'drawSquare': '畫方形：按住Ctrl鍵',
        'drawOrtho': '沿平行向畫',
        'undo': '復原',
        'gridResolution': '格線解析度',
        'gridRotation': '格線角度',
        'alignmentHelper': '對齊輔助器',
        'revolveMode': '輪盤模式',
        'revolve': '迴轉',
        'vertexSelection': 'Vertex selection',
        'convexeConcaveStraight': 'Concave/Straight/Convex',
        'latestBevelGlobal': 'Latest bevel Factor',
        'hideGrid': 'Show/Hide de the grid',
        'wireStart': 'Place the first point',
        'wireEnd': 'Place the last point',
        'snapCenterFace': 'Snap the center of the face',
        'howToPlate': 'Select faces and press Enter/Space',
        'bevelAdjustment': 'BEVEL ADJUSTMENT',
        'solidifyAdjustment': 'SOLIDIFY ADJUSTMENT',
        'segments': 'Segments',
        'ringSelect': 'Select a ring',
        'snapDirection': 'Align the second point with the first',
        'bevelProfile': 'Concave profile value',
        'loopSlide': 'Loop Slide',
        'previousSize': 'Back to previous bevel size',
        'cleanVertexGroup': 'Clean vertex groups',
        'outerBevelSegments': 'Outer bevel segement',
        'exit': 'Exit',
        'setMirrorObject': 'Set the mirror object',
        'normalRepair': 'Normal repair',
        'plate': 'Plate',
        'wire': 'Wire',
        'pipe': 'Pipe',
        'grid': 'Grid',
        'sim_set': 'Simulation settings',
        'angle': 'Angle',
        'MoveAxis': 'Move axis',
        'centerArray': 'Centered array',
        'axisLock': 'Axis locked',
        'duplicate': 'Duplicate',
        'convexeStraight': 'Convex/Straight',
        'axisAlign': 'Axis align'
    },
    "JAPANESE": {
        "cutCall": "カット/追加",
        "sliceCall": "スライス",
        "createCall": "生成",
        "addLatestBevel": "最終ベベルの追加",
        "symetrizePlan": "対称化する",
        "autoComplete": "オートコンプリート",
        "booleanDisplay": "ブーリアンオブジェクト表示/非表示",
        "wireframe": "ワイヤーフレーム表示/非表示",
        "latestBevelWidth": "最新ベベルの幅",
        "angleLimit": "アングル制限",
        "defaultDepth": "デフォルトの深さ",
        "corner": "デフォルトのベベル幅",
        "bevelResolution": "ベベル解像度",
        "circleResolution": "デフォルトの円解像度",
        "autoMirror": "オートミラー",
        "otherAdjustment": "その他の調整",
        "moveObj": "平面に沿ったオブジェクトの移動 : G, Shift+Z+Z",
        "moveObjZ": "平面の法線に沿ったオブジェクトの上下移動 : G, Z, Z",
        "finish": "終了 : 右クリック",
        "showBoolObj": "ブーリアンオブジェクト表示/非表示 : H",
        "cancel": "キャンセル : Esc",
        "finishCurrentadjustment": "現在の調整を終了する : 左クリック",
        "horizontalMouseMove": "マウスの水平移動",
        "fastSlow": "速い/遅い",
        "thicknessOffset": "厚み/オフセット 切り替え",
        "crossModel": "モデルの交差",
        "useFlyMenu": "フライメニューを使用 : 左クリックを押したままツールを選び、左クリックを解除します。",
        "roundStraight": "丸型/ストレート型",
        "remove": "削除",
        "steps": "解像度",
        "smoothCircle": "高解像度",
        "pressAxis": "軸を押すと表示され、もう一度押すと非表示になります",
        "axisSelection": "軸をアクティブ",
        "offset": "オフセット",
        "count": "数",
        'radius': '半径',
        'number': "要素数",
        'rotation90': '90°回転',
        'solidify': '固める',
        'firstBevel': '1st ベベル',
        'secondbevel': '2nd ベベル',
        'mirror': '対称',
        'array': '配列',
        'circularArray': '円形配列',
        'adjustment': '調整',
        'latestBevelSegments': '最新ベベルのセグメント',
        'validateDrawing': 'ポリゴンをアクセプト',
        'validatePath': 'パスをアクセプト',
        'fakeSlice': '偽のスライス',
        'duplicateExtract': '複製',
        'synchBool': 'ブーリアンオブジェクトの同期',
        'makePreset': 'プリセットを作成/空にする',
        'cutAgain': 'もう一度切る',
        'cleanBooleanApplication': 'ブーリアン最適化',
        'editCall': '編集',
        'technicalDisplay': 'テクニカルディスプレイ',
        'displayGrid': 'グリッド線を表示：面を右クリック',
        'drawOutside': '外側から描く：ペイントする前に顔の上でShift +左ボタンを描く',
        'snap': 'Snap : スナップ：Ctrlキーを押しながら',
        'drawFromCenter': '中心から描く：Shiftキーを押しながら',
        'drawSquare': '正方形を描く：Ctrlキーを押しながら',
        'drawOrtho': '正射影',
        'undo': '元に戻す',
        'gridResolution': 'グリッドの解像度',
        'gridRotation': 'グリッド回転',
        'alignmentHelper': 'アライメント補助',
        'revolveMode': '回るモード',
        'revolve': '回る',
        'vertexSelection': 'Vertex selection',
        'convexeConcaveStraight': 'Concave/Straight/Convex',
        'latestBevelGlobal': 'Latest bevel Factor',
        'hideGrid': 'Show/Hide de the grid',
        'wireStart': 'Place the first point',
        'wireEnd': 'Place the last point',
        'snapCenterFace': 'Snap the center of the face',
        'howToPlate': 'Select faces and press Enter/Space',
        'bevelAdjustment': 'BEVEL ADJUSTMENT',
        'solidifyAdjustment': 'SOLIDIFY ADJUSTMENT',
        'segments': 'Segments',
        'ringSelect': 'Select a ring',
        'snapDirection': 'Align the second point with the first',
        'bevelProfile': 'Concave profile value',
        'loopSlide': 'Loop Slide',
        'previousSize': 'Back to previous bevel size',
        'cleanVertexGroup': 'Clean vertex groups',
        'outerBevelSegments': 'Outer bevel segement',
        'exit': 'Exit',
        'setMirrorObject': 'Set the mirror object',
        'normalRepair': 'Normal repair',
        'plate': 'Plate',
        'wire': 'Wire',
        'pipe': 'Pipe',
        'grid': 'Grid',
        'sim_set': 'Simulation settings',
        'angle': 'Angle',
        'MoveAxis': 'Move axis',
        'centerArray': 'Centered array',
        'axisLock': 'Axis locked',
        'duplicate': 'Duplicate',
        'convexeStraight': 'Convex/Straight',
        'axisAlign': 'Axis align'
    },
    "FRANCAIS": {
        "cutCall": "Creuser/Ajouter",
        "sliceCall": "Découper",
        "createCall": "Nouvel objet",
        "addLatestBevel": "Ajouter un chamfrein",
        "symetrizePlan": "Symétrie axiale d'un plan",
        "autoComplete": "Finalisation",
        "booleanDisplay": "Montrer/Cacher les booléens",
        "wireframe": "Afficher/Cacher le maillage",
        "latestBevelWidth": "Taille du chamfrein",
        "angleLimit": "Angle limite",
        "defaultDepth": "Profondeur par défaut",
        "corner": "Largeur du premier bevel",
        "bevelResolution": "Résolution des chamfreins",
        "circleResolution": "Résolution par défaut des cercles",
        "autoMirror": "Miroir automatique",
        "otherAdjustment": "Autres options",
        "moveObj": "Déplacer l'objet dans le plan : G, Shift+Z+Z",
        "moveObjZ": "Monter/Descendre l'objet : G, Z, Z",
        "finish": "Terminer : Right Click",
        "showBoolObj": "Montrer/Cacher les objets booléens : H",
        "cancel": "Annuler : Esc",
        "finishCurrentadjustment": "Quitter l'ajustement en cours : Left Click",
        "horizontalMouseMove": "Bouger la souris horizontalement",
        "fastSlow": "Rapide / Lent",
        "thicknessOffset": "Épaisseur / Décalage, basculer avec",
        "crossModel": "Traverser le modèle",
        "useFlyMenu": "Menu vollant : maintenir click gauche et relacher sur l'icône shouaité",
        "roundStraight": "Arrondi/Droit",
        "remove": "Supprimer",
        "steps": "Résolution",
        "smoothCircle": "Haute résolution",
        "pressAxis": "Appuyer un axe pour l'activer, ré-appuyer pour le désactiver",
        "axisSelection": "Activation des axes",
        "offset": "Décalage",
        "count": "Nombre",
        'radius': 'Rayon',
        'number': "Nombre d'éléments",
        'rotation90': 'Rotation à 90°',
        'solidify': 'Extrusion',
        'firstBevel': 'Premier Chamfrein',
        'secondbevel': 'Second Chamfrein',
        'mirror': 'Miroir',
        'array': 'Répétition',
        'circularArray': 'Répétition Circulaire',
        'adjustment': 'Ajustement',
        'latestBevelSegments': 'Résolution du dernier chamfrein',
        'validateDrawing': 'Validate polygon',
        'validatePath': 'Validate path',
        'fakeSlice': 'Fausse découpe',
        'duplicateExtract': 'Dupliquer/Extraire',
        'synchBool': 'Synchroniser les booléens',
        'makePreset': 'Créer/Supprimer préconfiguration',
        'cutAgain': 'Nouvelle coupe',
        'cleanBooleanApplication': 'Création de support',
        'editCall': 'Éditer',
        'technicalDisplay': 'Vue Technique',
        'displayGrid': 'Afficher la grille : Click droit sur une face',
        'drawOutside': 'Dessin à l\'extérieur : Shift + clique gauche sur une face avant de dessiner',
        'snap': 'Snap : Maintenir Ctrl',
        'drawFromCenter': 'Dessin à partir du centre : Maintenir Shift',
        'drawSquare': 'Dessiner un carré : Maintenir Ctrl',
        'drawOrtho': 'Dessiner dans les directions X/Y/Z',
        'undo': 'Retour',
        'gridResolution': 'Résolution de la grille',
        'gridRotation': 'Rotation de la grille',
        'alignmentHelper': 'Aide à l\'alignement',
        'revolveMode': 'Tracer un profil de révolution',
        'revolve': 'Révolution',
        'vertexSelection': 'Sélection des sommets',
        'convexeConcaveStraight': 'Concave/Droit/Convexe',
        'latestBevelGlobal': 'Latest bevel Factor',
        'hideGrid': 'Montrer/cacher la grille',
        'wireStart': 'Place the first point',
        'wireEnd': 'Place the last point',
        'snapCenterFace': 'Snap the center of the face',
        'howToPlate': 'Select faces and press Enter/Space',
        'bevelAdjustment': 'BEVEL ADJUSTMENT',
        'solidifyAdjustment': 'SOLIDIFY ADJUSTMENT',
        'segments': 'Segments',
        'ringSelect': 'Select a ring',
        'snapDirection': 'Align the second point with the first',
        'bevelProfile': 'Concave profile value',
        'loopSlide': 'Loop Slide',
        'previousSize': 'Retour à la taille du bevel précédent',
        'cleanVertexGroup': 'Nettoyer vertex groups',
        'outerBevelSegments': 'Segment du dernier bevel',
        'exit': 'Quitter',
        'setMirrorObject': 'Choisir l\'objet servant d\'axe de symetrie',
        'normalRepair': 'Réparation des normales',
        'plate': 'Plaque',
        'wire': 'Câble',
        'pipe': 'Tuyau',
        'grid': 'Grille',
        'sim_set': 'Paramètre simulation',
        'angle': 'Angle',
        'MoveAxis': 'Move axis',
        'centerArray': 'Répétitions centrées',
        'axisLock': 'Axe verrouillé',
        'duplicate': 'Dupliquer',
        'convexeStraight': 'Convexe/Droit',
        'axisAlign': 'Aligner sur'
    },
    "DEUTSCH": {
        "cutCall": "Schneiden/Hinzufügen",
        "sliceCall": "Schnitt",
        "createCall": "Neu erstellen",
        "addLatestBevel": "Letzte Fase hinzufügen",
        "symetrizePlan": "Symmetrisch machen",
        "autoComplete": "Auto-Vervollständigen",
        "booleanDisplay": "Boolean Objekte ein-/ausblenden",
        "wireframe": "Drahtgitter ein-/ausblenden",
        "latestBevelWidth": "Breite der letzten Fase",
        "angleLimit": "Winkel Limit",
        "defaultDepth": "Standard Tiefe",
        "corner": "Standard Fasenbreite",
        "bevelResolution": "Fasenauflösung",
        "circleResolution": "Standardauflösung Kreis",
        "autoMirror": "Auto-Spiegeln",
        "otherAdjustment": "Weitere Anpassungen",
        "moveObj": "Bewege Objekt entlang der Fläche : G, Shift+Z+Z",
        "moveObjZ": "Bewege Objekt nach oben/unten entlang Flächennormale : G, Z, Z",
        "finish": "Bearbeitung abschließen : Rechtsklick",
        "showBoolObj": "Boolean Objekt ein-/ausblenden: H",
        "cancel": "Abbrechen : Esc",
        "finishCurrentadjustment": "Aktuelle Bearbeitung abschließen : Linksklick",
        "horizontalMouseMove": "Die Maus horizontal bewegen",
        "fastSlow": "Schnell/Langsam",
        "thicknessOffset": "Dicke/Achsenverschiebung umschalten",
        "crossModel": "Durch das ganze Modell schneiden",
        "useFlyMenu": "Das Fly-Menü benutzen : Klicke und halte die linke Maustaste, auf den gewünschten Eintrag zeigen, Maustaste loslassen",
        "roundStraight": "Rund/Gerade",
        "remove": "Entfernen",
        "steps": "Schritte",
        "smoothCircle": "Hohe Auflösung",
        "pressAxis": "Zum Aktivieren den Buchstaben für die Achse drücken, zum Deaktivieren den Buchstaben nochmal drücken",
        "axisSelection": "Achse aktivieren",
        "offset": "Verschiebung zur Achse",
        "count": "Anzahl",
        'radius': 'Radius',
        'number': "Anzahl der Elemente",
        'rotation90': '90° rotieren',
        'solidify': 'Dicke',
        'firstBevel': 'Erste Fase',
        'secondbevel': 'Zweite Fase',
        'mirror': 'Spiegeln',
        'array': 'Array',
        'circularArray': 'Kreisförmiges Array',
        'adjustment': 'Einstellung',
        'latestBevelSegments': 'Letzte Fase Segmente',
        'validateDrawing': 'Validiere als Fläche',
        'validatePath': 'Validiere als Pfad',
        'fakeSlice': 'Imitierter Schnitt',
        'duplicateExtract': 'Duplizieren',
        'synchBool': 'Synchronisiere Boolean Objekte',
        'makePreset': 'Vorgabe erstellen/löschen',
        'cutAgain': 'Nochmal schneiden',
        'cleanBooleanApplication': 'Boolean supports',
        'editCall': 'Bearbeiten',
        'technicalDisplay': 'Darstellung',
        'displayGrid': 'Gitter anzeigen : Rechtsklick auf eine Fläche',
        'drawOutside': 'Außerhalb zeichnen : Shift + Linksklick auf das Objekts, dann außerhalb zeichnen',
        'snap': 'Einrasten : halte Strg',
        'drawFromCenter': 'Vom Zentrum aus zeichnen : halte Shift',
        'drawSquare': 'Quadrat zeichnen : halte Strg',
        'drawOrtho': 'Zeichne in Achsen-Richtung',
        'undo': 'Rückgängig machen: ',
        'gridResolution': 'Gitter-Auflösung',
        'gridRotation': 'Gitter-Drehung',
        'alignmentHelper': 'Ausrichtungshilfe',
        'revolveMode': 'Schrauben-Modus',
        'revolve': 'Schrauben',
        'vertexSelection': 'Vertex auswählen',
        'convexeConcaveStraight': 'Konkav/Gerade/Konvex',
        'latestBevelGlobal': 'Letzter Fasen Faktor',
        'hideGrid': 'Zeige/Verstecke das Gitter',
        'wireStart': 'Platziere den Startpunkt',
        'wireEnd': 'Platziere den Endpunkt',
        'snapCenterFace': 'Starte von der Mitte der Fläche aus',
        'howToPlate': 'Wähle Flächen und drücke Enter/Space',
        'bevelAdjustment': 'Fase anpassen',
        'solidifyAdjustment': 'Solidify(3d Dimensionieren) Wert anpassen',
        'segments': 'Segmente',
        'ringSelect': 'Markiere einen Ring',
        'snapDirection': 'Richte den zweiten an dem ersten Punkt aus',
        'bevelProfile': 'Profil der Fase',
        'loopSlide': 'Loop slide',
        'previousSize': 'Zurück zur vorherigen Fasen Grösse',
        'cleanVertexGroup': 'Bereinige Vertex Gruppen',
        'outerBevelSegments': 'Äusseres Fasen Segment',
        'exit': 'Beenden',
        'setMirrorObject': 'Lege das zu spiegelnde Objekt fest',
        'normalRepair': 'Normal\'s reparieren',
        'plate': 'Platte',
        'wire': 'Kabel',
        'pipe': 'Rohr',
        'grid': 'Gitter',
        'sim_set': 'Simulation settings',
        'angle': 'Winkel',
        'MoveAxis': 'Move axis',
        'centerArray': 'Centered array',
        'axisLock': 'Axis locked',
        'duplicate': 'Duplicate',
        'convexeStraight': 'Convex/Straight',
        'axisAlign': 'Axis align'
    },
    "RUSSIAN": {
        "cutCall": "Вырезать / Добавить",
        "sliceCall": "Разрезать",
        "createCall": "Создать",
        "addLatestBevel": "Добавить финальную фаску",
        "symetrizePlan": "Симметрия",
        "autoComplete": "Автозавершение",
        "booleanDisplay": "Показать / Скрыть булевы объекты",
        "wireframe": "Показать / Скрыть сетку",
        "latestBevelWidth": "Ширина финальной фаски",
        "angleLimit": "Предельный угол",
        "defaultDepth": "Толщина по умолчанию",
        "corner": "Ширина фаски по умолчанию",
        "bevelResolution": "Плавность фаски",
        "circleResolution": "Вершин в круге по умолчанию",
        "autoMirror": "Авто-зеркалирование",
        "otherAdjustment": "Прочие настройки",
        "moveObj": "Перемещение объекта по плоскости : G, Shift+Z+Z",
        "moveObjZ": "Поднять/опустить объекта на плоскости : G, Z, Z",
        "finish": "Завершить : Right Click",
        "showBoolObj": "Показать / скрыть булевый объект : H",
        "cancel": "Отменить : Esc",
        "finishCurrentadjustment": "Завершить настройку : Left Click",
        "horizontalMouseMove": "Горизонатальное перемещение мыши",
        "fastSlow": "Быстрее / Медленнее",
        "thicknessOffset": "Толщина / Смещение",
        "crossModel": "Пересечение модель",
        "useFlyMenu": "Используйте Fly-меню : удерживая левую кнопку мыши, перейдите к нужному инструменту и отпустите кнопку",
        "roundStraight": "Скругленный / Прямой",
        "remove": "Удалить",
        "steps": "Вершины",
        "smoothCircle": "Сглаживание",
        "pressAxis": "Нажмите на ось, чтобы показать ее, нажмите еще раз, чтобы скрыть",
        "axisSelection": "Активировать оси",
        "offset": "Сдвиг",
        "count": "Количество",
        'radius': 'Радиус',
        'number': "Кол-во сегментов",
        'rotation90': 'Поворот на 90°',
        'solidify': 'Добавить толщины',
        'firstBevel': 'Первая фаска',
        'secondbevel': 'Вторая фаска',
        'mirror': 'Зеркало',
        'array': 'Массив',
        'circularArray': 'Кольцевой массив',
        'adjustment': 'настройка',
        'latestBevelSegments': 'Сегменты финальной фаски',
        'validateDrawing': 'Проверить полигон',
        'validatePath': 'Проверить направление',
        'fakeSlice': 'Псевдо-разрез',
        'duplicateExtract': 'Дублировать',
        'synchBool': 'Синхронизация булевых объектов',
        'makePreset': 'Создать/убрать заготовку',
        'cutAgain': 'Вырезать еще раз',
        'cleanBooleanApplication': 'Поддержка булевой топологиии',
        'editCall': 'Изменить',
        'technicalDisplay': 'Техническое отображение',
        'displayGrid': 'Вспомогательная сетка : Правый клик по полигону',
        'drawOutside': 'Отрисовка снаружи : сначала Shift + Левый клик по полигону',
        'snap': 'Выровнять : Удерживайте Ctrl',
        'drawFromCenter': 'Отрисовка из центра : Удерживайте Shift',
        'drawSquare': 'Отрисовка квадрата : Удерживайте Ctrl',
        'drawOrtho': 'Отрисовка в ортографическом режиме',
        'undo': 'Отменить',
        'gridResolution': 'Плотность сетки',
        'gridRotation': 'Поворот сетки',
        'alignmentHelper': 'Помощь в выравнивании',
        'revolveMode': 'Режим повторения',
        'revolve': 'Крутануть',
        'vertexSelection': 'Vertex selection',
        'convexeConcaveStraight': 'Concave/Straight/Convex',
        'latestBevelGlobal': 'Latest bevel Factor',
        'hideGrid': 'Show/Hide de the grid',
        'wireStart': 'Place the first point',
        'wireEnd': 'Place the last point',
        'snapCenterFace': 'Snap the center of the face',
        'howToPlate': 'Select faces and press Enter/Space',
        'bevelAdjustment': 'BEVEL ADJUSTMENT',
        'solidifyAdjustment': 'SOLIDIFY ADJUSTMENT',
        'segments': 'Segments',
        'ringSelect': 'Select a ring',
        'snapDirection': 'Align the second point with the first',
        'bevelProfile': 'Concave profile value',
        'loopSlide': 'Loop Slide',
        'previousSize': 'Back to previous bevel size',
        'cleanVertexGroup': 'Clean vertex groups',
        'outerBevelSegments': 'Outer bevel segement',
        'exit': 'Exit',
        'setMirrorObject': 'Set the mirror object',
        'normalRepair': 'Normal repair',
        'plate': 'Plate',
        'wire': 'Wire',
        'pipe': 'Pipe',
        'grid': 'Grid',
        'sim_set': 'Simulation settings',
        'angle': 'у́гол',
        'MoveAxis': 'Move axis',
        'centerArray': 'Centered array',
        'axisLock': 'Axis locked',
        'duplicate': 'Duplicate',
        'convexeStraight': 'Convex/Straight',
        'axisAlign': 'Axis align'
    }
}


def translate(key):
    global translation

    return translation.get(get_addon_preferences().language).get(key)


def check_update():
    adresse = 'http://cgthoughts.com/fluent_current_version/index.html'
    response = urllib.request.urlopen(adresse)
    html = str(response.read())
    last_version = html[2:11]
    current_version = str(bl_info['version'])
    if last_version != current_version:
        return True, last_version
    else:
        return False, False


class FLUENT_MT_PieMenu(Menu):
    bl_label = 'Fluent ' + str(bl_info['version'][0]) + '.' + str(bl_info['version'][1]) + '.' + str(
        bl_info['version'][2])
    bl_options = {'REGISTER'}

    def __init__(self):
        global init_pref
        if not init_pref:
            bpy.context.scene.fluentProp.model_resolution = get_addon_preferences().model_resolution
            bpy.context.scene.fluentProp.width = get_addon_preferences().latest_bevel_width_preference
            bpy.context.scene.fluentProp.min_auto_bevel_segments = get_addon_preferences().min_auto_bevel_segments
            bpy.context.scene.fluentProp.min_auto_cylinder_segments = get_addon_preferences().min_auto_cylinder_segments

            init_pref = True

    def menu_zero(self, context):
        icons = load_icons()
        autocomplete_one_ico = icons.get("autocomplete_one").get('previews')
        latest_bevel_ico = icons.get("latest_bevel").get('previews')
        sym_ico = icons.get("sym").get('previews')
        show_bool_ico = icons.get("show_bool").get('previews')
        cut_ico = icons.get("cut").get('previews')
        slice_ico = icons.get("slice").get('previews')
        inset_ico = icons.get("inset").get('previews')
        creation_ico = icons.get("creation").get('previews')
        wireframe_ico = icons.get("wireframe").get('previews')
        duplicate_ico = icons.get("duplicate").get('previews')
        warning_ico = icons.get("warning").get('previews')
        preset_ico = icons.get("preset").get('previews')
        edit_ico = icons.get("edit").get('previews')
        boolean_ico = icons.get("boolean").get('previews')
        wire_ico = icons.get("wire").get('previews')
        pipe_ico = icons.get("pipe").get('previews')
        plate_ico = icons.get("plate").get('previews')
        grid_ico = icons.get("grid").get('previews')
        settings_ico = icons.get("settings").get('previews')
        normal_ico = icons.get("normal").get('previews')
        cloth_ico = icons.get("cloth").get('previews')
        tool_ico = icons.get("tool").get('previews')
        td_ico = icons.get("technical_display").get('previews')
        show_bool_02_ico = icons.get("show_bool_02").get('previews')
        screw_ico = icons.get("screw").get('previews')

        layout = self.layout
        scn = context.scene

        pie = layout.menu_pie()

        # gauche
        box = pie.column(align=True)
        line_01 = box.row(align=True)
        line_01.scale_x = 1.2
        line_01.scale_y = 1.5
        line_01.operator('fluent.cutstarter', text='', icon_value=cut_ico.icon_id)
        line_01.operator('fluent.slicestarter', text='', icon_value=slice_ico.icon_id)

        line_02 = box.row(align=True)
        line_02.scale_x = 1.2
        line_02.scale_y = 1.5
        line_02.operator('fluent.insetstarter', text='', icon_value=inset_ico.icon_id)
        line_02.operator('fluent.booleanoperator', text='', icon_value=boolean_ico.icon_id)

        line_03 = box.row(align=True)
        line_03.scale_x = 1.2
        line_03.scale_y = 1.5
        line_03.operator('fluent.createstarter', text='', icon_value=creation_ico.icon_id)
        line_03.operator("fluent.booleanduplicate", text='', icon_value=duplicate_ico.icon_id)

        # droite
        box = pie.column(align=True)
        box.scale_x = 1.2
        box.scale_y = 1.5

        if 'fluent_catalyst' in bpy.context.preferences.addons:
            dr_02 = box.row(align=True)
            dr_02.operator('fluent.editor', text='', icon_value=edit_ico.icon_id).operation = 'EDIT'
            dr_02.operator('fluentcatalyst.geometrymenu', text='', icon='OUTLINER_DATA_GP_LAYER')
        else:
            box.operator('fluent.editor', text='', icon_value=edit_ico.icon_id).operation = 'EDIT'

        box.operator("fluent.autocompleteone", text='', icon_value=autocomplete_one_ico.icon_id)
        box.operator("fluent.normalrepair", text='', icon_value=normal_ico.icon_id)
        dr_03 = box.row(align=True)
        if get_addon_preferences().pie_option_other_adjustments:
            dr_03.operator("fluent.otheradjustments", text='', icon_value=settings_ico.icon_id)
        if get_addon_preferences().pie_option_toolbox:
            dr_03.menu("FLUENT_MT_ToolBox_Menu", text='', icon_value=tool_ico.icon_id)

        # bas
        box = pie.column(align=True)
        box.alignment = 'CENTER'
        r_01 = box.row(align=False)

        box.operator('fluent.addlatestbevel', text=translate('addLatestBevel'))

        box.prop(context.scene.fluentProp, 'width', text=translate('latestBevelWidth'))

        box.prop(context.scene.fluentProp, 'bevel_angle_limit', text='Angle limit')

        try:
            if get_addon_preferences().pie_option_pt:
                box.separator()
                power_trip = box.column(align=True)
                power_trip.scale_x = 1.2
                power_trip.scale_y = 1.5

                pt_01 = power_trip.row(align=True)
                pt_01.alignment = 'CENTER'
                pt_01.operator("fluent.plates", text='', icon_value=plate_ico.icon_id)
                pt_01.operator("fluent.screw", text='', icon_value=screw_ico.icon_id).operation = 'ADD'
                pt_01.operator("fluent.grids", text='', icon_value=grid_ico.icon_id).operation = 'ADD'

                pt_02 = power_trip.row(align=True)
                pt_02.alignment = 'CENTER'
                pt_02.operator("fluent.wire", text='', icon_value=wire_ico.icon_id).operation = 'ADD'
                pt_02.operator("fluent.pipe", text='', icon_value=pipe_ico.icon_id).operation = 'ADD'

                pt_03 = power_trip.row(align=True)
                pt_03.alignment = 'CENTER'
                pt_03.operator("fluent.clothpanel", text='', icon_value=cloth_ico.icon_id)
                pt_03.operator("fluent.clothsettings", text='', icon='OPTIONS')
        except:
            pass

        # haut
        box = pie.row(align=True)
        box.scale_x = 1.2
        box.scale_y = 1.5
        box.operator("fluent.technicaldisplay", text='', icon_value=td_ico.icon_id)
        box.operator("fluent.booleandisplay", text='', icon_value=show_bool_02_ico.icon_id)
        box.operator("fluent.wireframedisplay", text='', icon_value=wireframe_ico.icon_id)

    def draw(self, context):
        self.menu_zero(context)


class FLUENT_MT_ToolBox_Menu(Menu):
    bl_label = "Toolbox"

    def draw(self, context):
        icons = load_icons()
        sym_ico = icons.get("sym").get('previews')
        become_ico = icons.get("become").get('previews')

        layout = self.layout
        scn = context.scene

        # box = layout.column()
        # layout.operator("fluent.alignview", text='Align view')
        layout.operator("fluent.alignview", text='Align view')
        layout.operator("fluent.vgcleaner", text=translate('cleanVertexGroup'))
        layout.separator()

        layout.operator("fluent.allcuttermirror", icon_value=sym_ico.icon_id)
        layout.operator("fluent.becomefluent", icon_value=become_ico.icon_id)
        layout.separator()
        try:
            layout.operator("fluent.texttomesh", text='Text2Mesh')
            layout.operator("fluent.chaintomesh", text='Chain to mesh')
        except:
            pass
        layout.separator()

        layout.operator("fluent.autosupport", text=translate('cleanBooleanApplication'))
        layout.operator("fluent.applytoboolean", text='Apply to boolean')
        layout.separator()

        layout.operator("fluent.booleansynchronization", text='Boolean synchronization')
        layout.separator()

        layout.operator("fluent.cleanbooleanobjects", text='Remove unused boolean objects')
        # layout.operator("class.resetmenuposition", text='Reset menu position')


class FLUENT_PT_Basic_Panel(bpy.types.Panel):
    "Fluent"
    bl_idname='FLUENT_PT_Basic_Panel'
    bl_label = "Fluent"
    bl_name = "Fluent"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Fluent'

    def __init__(self):
        global init_pref
        if not init_pref:
            bpy.context.scene.fluentProp.model_resolution = get_addon_preferences().model_resolution
            bpy.context.scene.fluentProp.width = get_addon_preferences().latest_bevel_width_preference
            bpy.context.scene.fluentProp.min_auto_bevel_segments = get_addon_preferences().min_auto_bevel_segments
            bpy.context.scene.fluentProp.min_auto_cylinder_segments = get_addon_preferences().min_auto_cylinder_segments

            init_pref = True

    def draw(self, context):
        icons = load_icons()
        autocomplete_one_ico = icons.get("autocomplete_one").get('previews')
        latest_bevel_ico = icons.get("latest_bevel").get('previews')
        sym_ico = icons.get("sym").get('previews')
        show_bool_ico = icons.get("show_bool").get('previews')
        cut_ico = icons.get("cut").get('previews')
        slice_ico = icons.get("slice").get('previews')
        inset_ico = icons.get("inset").get('previews')
        creation_ico = icons.get("creation").get('previews')
        wireframe_ico = icons.get("wireframe").get('previews')
        duplicate_ico = icons.get("duplicate").get('previews')
        warning_ico = icons.get("warning").get('previews')
        preset_ico = icons.get("preset").get('previews')
        edit_ico = icons.get("edit").get('previews')
        boolean_ico = icons.get("boolean").get('previews')
        wire_ico = icons.get("wire").get('previews')
        pipe_ico = icons.get("pipe").get('previews')
        plate_ico = icons.get("plate").get('previews')
        grid_ico = icons.get("grid").get('previews')
        settings_ico = icons.get("settings").get('previews')
        normal_ico = icons.get("normal").get('previews')
        cloth_ico = icons.get("cloth").get('previews')
        tool_ico = icons.get("tool").get('previews')
        td_ico = icons.get("technical_display").get('previews')
        show_bool_02_ico = icons.get("show_bool_02").get('previews')

        layout = self.layout
        scn = context.scene

        box = layout.column(align=True)
        box.scale_x = 1.2
        box.scale_y = 1.5
        line_01 = box.row(align=True)
        line_01.operator("fluent.technicaldisplay", text='Technical display', icon_value=td_ico.icon_id)
        line_02 = box.row(align=True)
        line_02.operator("fluent.booleandisplay", text='Show boolean', icon_value=show_bool_02_ico.icon_id)
        line_02.operator("fluent.wireframedisplay", text='Wireframe', icon_value=wireframe_ico.icon_id)

        # gauche
        box = layout.column(align=True)
        line_01 = box.row(align=True)
        line_01.scale_x = 1.2
        line_01.scale_y = 1.5
        line_01.operator('fluent.cutstarter', text='Cut/Add', icon_value=cut_ico.icon_id)
        line_01.operator('fluent.slicestarter', text='Slice', icon_value=slice_ico.icon_id)

        line_02 = box.row(align=True)
        line_02.scale_x = 1.2
        line_02.scale_y = 1.5
        line_02.operator('fluent.insetstarter', text='Inset', icon_value=inset_ico.icon_id)
        line_02.operator('fluent.booleanoperator', text='Boolean', icon_value=boolean_ico.icon_id)

        line_03 = box.row(align=True)
        line_03.scale_x = 1.2
        line_03.scale_y = 1.5
        line_03.operator('fluent.createstarter', text='Creation', icon_value=creation_ico.icon_id)
        line_03.operator("fluent.booleanduplicate", text='Duplicate/Extract', icon_value=duplicate_ico.icon_id)

        # droite
        box = layout.column(align=True)
        box.scale_x = 1.2
        box.scale_y = 1.5
        box.operator('fluent.editor', text=translate('editCall'), icon_value=edit_ico.icon_id).operation = 'EDIT'
        finish = box.row(align=True)
        finish.scale_x = 1.2
        box.operator("fluent.autocompleteone", text='Complete', icon_value=autocomplete_one_ico.icon_id)
        box.operator("fluent.normalrepair", text='N Repair', icon_value=normal_ico.icon_id)
        box.operator("fluent.otheradjustments", text=translate('otherAdjustment'), icon_value=settings_ico.icon_id)
        box.menu("FLUENT_MT_ToolBox_Menu", text='ToolBox', icon_value=tool_ico.icon_id)

        # bas
        box = layout.column()
        bevel_tool = box.column(align=True)
        bevel_tool.operator('fluent.addlatestbevel', text=translate('addLatestBevel'))
        bevel_tool.prop(context.scene.fluentProp, 'width', text=translate('latestBevelWidth'))
        bevel_tool.prop(context.scene.fluentProp, 'bevel_angle_limit', text='Angle limit')
        bevel_tool.operator("fluent.toggleloopslide", text='Toggle loop slide')

###


class fluentProp(bpy.types.PropertyGroup):

    def latestBevelUpdate(self, context):
        global init_pref
        if init_pref:
            for obj in bpy.context.selected_objects:
                if obj.type == 'MESH':
                    outer_bevel = F_outer_bevel(obj)
                    if get_addon_preferences().bevel_system == 'SIMPLE':
                        a = outer_bevel.find_last()
                        if a:
                            outer_bevel.last_as_current()
                    else:
                        a = outer_bevel.find_first()
                        if a:
                            outer_bevel.first_as_current()
                    if a:
                        outer_bevel.set_width(b_width=bpy.context.scene.fluentProp.width, same=None, first=None)

    def latestBevelUniversalUpdate(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                for m in obj.modifiers:
                    if fluent_modifiers_name['outer_bevel'] in m.name:
                        m.width = m.width * float(bpy.context.scene.fluentProp.width_amount)

    def bevelResolutionUpdate(self, context):
        global init_pref
        if init_pref:
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH' and obj.get('fluent_type') not in [None, 'unknow']:
                    if len(obj.modifiers):
                        for mod in obj.modifiers:
                            if mod.type == 'BEVEL':
                                if mod.segments > 1 and mod.profile != 0.25:
                                    angle = math.sqrt(math.asin(min(mod.width, 1)))
                                    segments = int(
                                        bpy.context.scene.fluentProp.bevel_resolution * (angle + (1 - math.cos(angle))))
                                    if segments < 4:
                                        segments = 4
                                    mod.segments = segments

    def bevelProfilUpdate(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.get('fluent_object'):
                if len(obj.modifiers):
                    for mod in obj.modifiers:
                        if mod.type == 'BEVEL':
                            if mod.segments > 1 and mod.profile != 0.25:
                                mod.profile = bpy.context.scene.fluentProp.bevel_profile

    def outer_bevel_update(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                if len(obj.modifiers):
                    for mod in obj.modifiers:
                        if mod.type == 'BEVEL' and fluent_modifiers_name['outer_bevel'] in mod.name:
                            if bpy.context.scene.fluentProp.outer_bevel_segments == 0:
                                mod.segments = auto_bevel_segments(mod)
                            else:
                                mod.segments = bpy.context.scene.fluentProp.outer_bevel_segments

    def loop_slide_update(self, context):
        for o in bpy.context.selected_objects:
            if o.type == 'MESH':
                bevel = F_outer_bevel()
                bevel.set_target(o)
                b = bevel.find_last()
                if b:
                    b.loop_slide = bpy.context.scene.fluentProp.loop_slide

    def limit_angle_update(self, context):
        for o in bpy.context.selected_objects:
            if o.type == 'MESH':
                bevel = F_outer_bevel()
                bevel.set_target(o)
                b = bevel.find_last()
                if b:
                    b.angle_limit = math.radians(bpy.context.scene.fluentProp.bevel_angle_limit)

    def update_resolution(self, context):
        global init_pref
        if init_pref:
            # mise à jour de tous les bevels, les cylindres et spheres
            for o in bpy.data.objects:
                if o.type == 'MESH' and o.get('fluent_type'):
                    for m in o.modifiers:
                        if fluent_modifiers_name['outer_bevel'] in m.name and bpy.context.scene.fluentProp.outer_bevel_segments == 0:
                            m.segments = auto_bevel_segments(bevel=m)
                        if fluent_modifiers_name['first_bevel'] in m.name:
                            if m.profile != 0.25:
                                m.segments = auto_bevel_segments(bevel=m)
                        if fluent_modifiers_name['second_bevel'] in m.name:
                            if m.profile != 0.25:
                                m.segments = auto_bevel_segments(bevel=m)
                        if o.get('fluent_type') == 'prism' and (o.get('fluent_auto_res') == 'ENABLE' or not o.get('fluent_auto_res')):
                            if fluent_modifiers_name['screw'] in m.name:
                                m.steps = m.render_steps = auto_bevel_segments(
                                    displace=o.modifiers[fluent_modifiers_name['radius']])
                        if o.get('fluent_type') == 'revolver' and (o.get('fluent_auto_res') == 'ENABLE' or not o.get('fluent_auto_res')):
                            if fluent_modifiers_name['screw'] in m.name:
                                m.steps = m.render_steps = auto_bevel_segments(revolver_obj=o)
                    if o.get('fluent_type') == 'sphere' and (o.get('fluent_auto_res') == 'ENABLE' or not o.get('fluent_auto_res')):
                        if fluent_modifiers_name['screw'] in m.name:
                            screw_2 = o.modifiers[fluent_modifiers_name['screw_2']]
                            screw_2.steps = screw_2.render_steps = auto_bevel_segments(
                                displace=o.modifiers[fluent_modifiers_name['radius']]) / 2
                            screw = o.modifiers[fluent_modifiers_name['screw']]
                            screw.steps = screw.render_steps = screw_2.steps / 3

    width: bpy.props.FloatProperty(
        description="Latest Bevel Width",
        name="Latest bevel width",
        default=0.002,
        min=0.0001,
        step=0.01,
        precision=4,
        update=latestBevelUpdate
    )
    width_amount: bpy.props.StringProperty(
        description="Global factor of width of the latest bevel",
        name="Latest Bevel Global",
        default="1",
        update=latestBevelUniversalUpdate
    )
    corner: bpy.props.FloatProperty(
        description="Default first bevel width",
        name="Default first bevel width",
        default=0,
        min=0,
        max=10,
        step=0.01,
        precision=3
    )
    bevel_width: bpy.props.StringProperty(
        description="Default bevel width",
        name='Default bevel width',
        default=''
    )
    # segments: bpy.props.FloatProperty(
    #     description="Segments of latestest bevel",
    #     name="Segments",
    #     default=4,
    #     min=0,
    #     max=10,
    #     step=0.01,
    #     precision=3
    # )
    bevel_angle_limit: bpy.props.FloatProperty(
        description="Limit angle of the latest bevel",
        name="Limit angle",
        default=35,
        min=0,
        max=180,
        step=1,
        precision=3,
        update=limit_angle_update
    )
    model_resolution: bpy.props.IntProperty(
        description='Resolution of bevels, cylinders and spheres (segments/m)',
        name='Model resolution',
        default=16,
        min=1,
        max=512,
        update=update_resolution
    )
    min_auto_bevel_segments: bpy.props.IntProperty(
        description='Minimum resolution of bevels (segments/m)',
        name='Minimum of segments for auto-bevel',
        default=1,
        min=1,
        max=64,
        update=update_resolution
    )
    min_auto_cylinder_segments: bpy.props.IntProperty(
        description='Minimum resolution of cylinders and spheres (segments/m)',
        name='Minimum of segments for auto-resolution',
        default=16,
        min=3,
        max=64,
        update=update_resolution
    )
    # latest_bevel_segments: bpy.props.IntProperty(
    #     description="Latest Bevel Segments",
    #     name="Latest Bevel Segments",
    #     default=4,
    #     min=0,
    #     max=64,
    #     step=1,
    #     update=latestBevelUpdate
    # )
    depth: bpy.props.FloatProperty(
        description="Default Depth",
        name="Default Depth",
        default=0,
        min=-100,
        max=100,
        step=0.01,
        precision=3
    )
    solidify_offset: bpy.props.FloatProperty(
        description="solidify offset",
        name="solidify_offset",
        default=0,
        min=-1,
        max=1,
        precision=4
    )
    # prism_segments: bpy.props.IntProperty(
    #     description="Default Prism Segment",
    #     name="Default Prism Segment",
    #     default=64,
    #     min=0,
    #     step=1,
    #     update=prismResolutionUpdate
    # )
    # bevel_resolution: bpy.props.IntProperty(
    #     description="Bevel Resolution",
    #     name="Bevel resolution",
    #     default=32,
    #     min=0,
    #     step=1,
    #     update=bevelResolutionUpdate
    # )
    # sphere_segments: bpy.props.IntProperty(
    #     description="Default sphere Segment",
    #     name="Sphere segements",
    #     default=17,
    #     min=0,
    #     step=1,
    #     update=sphereResolutionUpdate
    # )
    bevel_profile: bpy.props.FloatProperty(
        description="Bevel profil",
        name="Bevel profil",
        default=0.48,
        min=0,
        max=1,
        step=0.01,
        update=bevelProfilUpdate
    )
    auto_mirror_x: bpy.props.BoolProperty(
        description="Auto Mirror X",
        name="X",
        default=False
    )
    auto_mirror_y: bpy.props.BoolProperty(
        description="Auto Mirror Y",
        name="Y",
        default=False
    )
    auto_mirror_z: bpy.props.BoolProperty(
        description="Auto Mirror Z",
        name="Z",
        default=False
    )
    straight_bevel: bpy.props.BoolProperty(
        description="straight_bevel",
        name="straight_bevel",
        default=False
    )
    second_bevel_width: bpy.props.FloatProperty(
        description="second_bevel_width",
        name="second_bevel_width",
        default=0,
        min=0,
        max=100
    )
    second_bevel_straight: bpy.props.BoolProperty(
        description="second_bevel_straight",
        name="second_bevel_straight",
        default=False
    )
    grid_resolution: bpy.props.IntProperty(
        description="Default Prism Segment",
        name="Default Prism Segment",
        default=5,
        min=0,
        step=1
    )
    grid_size: bpy.props.FloatProperty(
        description="grid size",
        name="Grid Size",
        default=2,
        min=0,
        step=0.01,
        precision=2
    )
    last_tool: bpy.props.StringProperty(
        description="last toole used",
        name='last_tool',
        default='box'
    )
    plate_bevel_width: bpy.props.FloatProperty(
        description="plate bevel width",
        name="plate_bevel_width",
        default=0
    )
    plate_solidify_thickness: bpy.props.FloatProperty(
        description="plate bevel width",
        name="plate_bevel_width",
        default=0
    )
    centered_array: bpy.props.BoolProperty(
        description="Draw array from the center",
        name="Centered array",
        default=True
    )
    loop_slide: bpy.props.BoolProperty(
        description="Use the loop slide option",
        name="Loop Slide",
        default=False,
        update=loop_slide_update
    )
    outer_bevel_segments: bpy.props.IntProperty(
        description="0 = automatic",
        name="Outer bevel segement",
        default=4,
        min=0,
        step=1,
        update=outer_bevel_update
    )
    screw_scale: bpy.props.FloatProperty(
        description="Head screw scale",
        name="screw_scale",
        default=.1
    )

    screw_offset: bpy.props.FloatProperty(
        description="Head screw offset",
        name="screw_offset",
        default=.1
    )


###

############################################################################


class FluentAddonPreferences(AddonPreferences):
    def bevel_compatibility(self, context):
        if get_addon_preferences().bevel_system == 'MULTIPLE':
            get_addon_preferences().auto_beveled_cut = True

    def panel_toggle(self, context):
        if get_addon_preferences().show_panel:
            from bpy.utils import register_class
            register_class(FLUENT_PT_Basic_Panel)
            register_class(power_trip_panel.classes)
        else:
            from bpy.utils import unregister_class
            unregister_class(FLUENT_PT_Basic_Panel)
            unregister_class(power_trip_panel.classes)

    def toggle_primitive(self, context):
        if get_addon_preferences().fluent_primitive:
            bpy.types.VIEW3D_MT_mesh_add.prepend(primitive_add)
        else:
            bpy.types.VIEW3D_MT_mesh_add.remove(primitive_add)

    bl_idname = __name__

    font_size: bpy.props.IntProperty(
        description='UI font size',
        name='Font size',
        default=18
    )

    icon_size: bpy.props.EnumProperty(
        description='Size of icons',
        name='Icon size',
        items=(('32', '32', '32'),
               ('48', '48', '48'),
               ),
        default='32'
    )

    corner_preference: bpy.props.FloatProperty(
        description="Default Bevel Width",
        name="Default Bevel Width",
        default=0,
        min=0,
        max=10,
        step=0.01,
        precision=3
    )

    model_resolution: bpy.props.IntProperty(
        description='Resolution of bevels, cylinders and spheres (segments/m)',
        name='Model resolution',
        default=16,
        min=1,
        max=256
    )
    min_auto_bevel_segments: bpy.props.IntProperty(
        description='Minimum resolution of bevels (segments/m)',
        name='Minimum of segments for auto-bevel',
        default=4,
        min=0,
        max=64
    )
    min_auto_cylinder_segments: bpy.props.IntProperty(
        description='Minimum resolution of cylinders and spheres (segments/m)',
        name='Minimum of segments for auto-resolution',
        default=16,
        min=3,
        max=64
    )

    latest_bevel_width_preference: bpy.props.FloatProperty(
        description="Latest Bevel Width",
        name="Latest Bevel Width",
        default=0.01,
        min=0,
        step=0.001,
        precision=3
    )

    fluent_menu_shortcut_key: bpy.props.EnumProperty(
        items=(("A", "A", "A"),
               ("B", "B", "B"),
               ("C", "C", "C"),
               ("D", "D", "D"),
               ("E", "E", "E"),
               ("F", "F", "F"),
               ("G", "G", "G"),
               ("H", "H", "H"),
               ("I", "I", "I"),
               ("J", "J", "J"),
               ("K", "K", "K"),
               ("L", "L", "L"),
               ("M", "M", "M"),
               ("N", "N", "N"),
               ("O", "O", "O"),
               ("P", "P", "P"),
               ("Q", "Q", "Q"),
               ("R", "R", "R"),
               ("S", "S", "S"),
               ("T", "T", "T"),
               ("U", "U", "U"),
               ("V", "V", "V"),
               ("W", "W", "W"),
               ("X", "X", "X"),
               ("Y", "Y", "Y"),
               ("Z", "Z", "Z"),
               ),
        default='F'
    )

    fluent_menu_shortcut_alt: bpy.props.BoolProperty(
        description="Use alt to call Fluent",
        name="Use alt to call Fluent",
        default=False
    )

    fluent_menu_shortcut_ctrl: bpy.props.BoolProperty(
        description="Use ctrl to call Fluent",
        name="Use ctrl to call Fluent",
        default=False
    )

    fluent_menu_shortcut_shift: bpy.props.BoolProperty(
        description="Use shift to call Fluent",
        name="Use shift to call Fluent",
        default=False
    )

    fluent_cut_shortcut_key: bpy.props.EnumProperty(
        items=(("A", "A", "A"),
               ("B", "B", "B"),
               ("C", "C", "C"),
               ("D", "D", "D"),
               ("E", "E", "E"),
               ("F", "F", "F"),
               ("G", "G", "G"),
               ("H", "H", "H"),
               ("I", "I", "I"),
               ("J", "J", "J"),
               ("K", "K", "K"),
               ("L", "L", "L"),
               ("M", "M", "M"),
               ("N", "N", "N"),
               ("O", "O", "O"),
               ("P", "P", "P"),
               ("Q", "Q", "Q"),
               ("R", "R", "R"),
               ("S", "S", "S"),
               ("T", "T", "T"),
               ("U", "U", "U"),
               ("V", "V", "V"),
               ("W", "W", "W"),
               ("X", "X", "X"),
               ("Y", "Y", "Y"),
               ("Z", "Z", "Z"),
               ),
        default='F'
    )

    fluent_cut_shortcut_alt: bpy.props.BoolProperty(
        description="Use alt to call Fluent cut",
        name="fluent_cut_shortcut_alt",
        default=True
    )

    fluent_cut_shortcut_ctrl: bpy.props.BoolProperty(
        description="Use ctrl to call Fluent cut",
        name="fluent_cut_shortcut_ctrl",
        default=False
    )

    fluent_cut_shortcut_shift: bpy.props.BoolProperty(
        description="Use shift to call Fluent cut",
        name="fluent_cut_shortcut_shift",
        default=False
    )

    fluent_slice_shortcut_key: bpy.props.EnumProperty(
        items=(("A", "A", "A"),
               ("B", "B", "B"),
               ("C", "C", "C"),
               ("D", "D", "D"),
               ("E", "E", "E"),
               ("F", "F", "F"),
               ("G", "G", "G"),
               ("H", "H", "H"),
               ("I", "I", "I"),
               ("J", "J", "J"),
               ("K", "K", "K"),
               ("L", "L", "L"),
               ("M", "M", "M"),
               ("N", "N", "N"),
               ("O", "O", "O"),
               ("P", "P", "P"),
               ("Q", "Q", "Q"),
               ("R", "R", "R"),
               ("S", "S", "S"),
               ("T", "T", "T"),
               ("U", "U", "U"),
               ("V", "V", "V"),
               ("W", "W", "W"),
               ("X", "X", "X"),
               ("Y", "Y", "Y"),
               ("Z", "Z", "Z"),
               ),
        default='F'
    )

    fluent_slice_shortcut_alt: bpy.props.BoolProperty(
        description="Use alt to call Fluent slice",
        name="fluent_slice_shortcut_alt",
        default=False
    )

    fluent_slice_shortcut_ctrl: bpy.props.BoolProperty(
        description="Use ctrl to call Fluent slice",
        name="fluent_slice_shortcut_ctrl",
        default=True
    )

    fluent_slice_shortcut_shift: bpy.props.BoolProperty(
        description="Use shift to call Fluent slice",
        name="fluent_slice_shortcut_shift",
        default=False
    )

    fluent_edit_shortcut_key: bpy.props.EnumProperty(
        items=(("A", "A", "A"),
               ("B", "B", "B"),
               ("C", "C", "C"),
               ("D", "D", "D"),
               ("E", "E", "E"),
               ("F", "F", "F"),
               ("G", "G", "G"),
               ("H", "H", "H"),
               ("I", "I", "I"),
               ("J", "J", "J"),
               ("K", "K", "K"),
               ("L", "L", "L"),
               ("M", "M", "M"),
               ("N", "N", "N"),
               ("O", "O", "O"),
               ("P", "P", "P"),
               ("Q", "Q", "Q"),
               ("R", "R", "R"),
               ("S", "S", "S"),
               ("T", "T", "T"),
               ("U", "U", "U"),
               ("V", "V", "V"),
               ("W", "W", "W"),
               ("X", "X", "X"),
               ("Y", "Y", "Y"),
               ("Z", "Z", "Z"),
               ),
        default='F'
    )

    fluent_edit_shortcut_alt: bpy.props.BoolProperty(
        description="Use alt to call Fluent edit",
        name="fluent_edit_shortcut_alt",
        default=False
    )

    fluent_edit_shortcut_ctrl: bpy.props.BoolProperty(
        description="Use ctrl to call Fluent edit",
        name="fluent_edit_shortcut_ctrl",
        default=False
    )

    fluent_edit_shortcut_shift: bpy.props.BoolProperty(
        description="Use shift to call Fluent edit",
        name="fluent_edit_shortcut_shift",
        default=True
    )

    language: bpy.props.EnumProperty(
        items=(
            ("ENGLISH", "English", "ENGLISH"),
            ("FRANCAIS", "Français", "FRANCAIS"),
            ("CHINESE", "Chinese", "CHINESE"),
            ("TRAD_CHINESE", "Traditional Chinese", "TRAD_CHINESE"),
            ("JAPANESE", "Japanese", "JAPANESE"),
            ("RUSSIAN", "Russian", "RUSSIAN"),
            ("DEUTSCH", "Deutsch", "DEUTSCH"),
        ),
        default='ENGLISH'
    )

    auto_hide_bool: bpy.props.BoolProperty(
        name="auto_hide_bool",
        default=True,
        description="Hide boolean object after creation"
    )

    auto_parent: bpy.props.BoolProperty(
        name="auto_parent",
        default=True,
        description="Auto parent between the boolean object and his target"
    )

    need_updating: bpy.props.BoolProperty(
        description="need updating",
        name="need_updating",
        default=False
    )

    last_version: bpy.props.StringProperty(
        description="last version",
        name="last_version",
        default="(1.0.6)"
    )

    hightlight_text: bpy.props.FloatVectorProperty(name="Color of hightlight text",
        subtype='COLOR',
        size=4,
        default=(0.0, 0.8, 1, 1)
    )

    hightlight_dot: bpy.props.FloatVectorProperty(name="Color of hightlight dots",
        subtype='COLOR',
        size=4,
        default=(0, 1, 1, 1)
    )

    clamp_overlap: bpy.props.BoolProperty(
        description="Use the clamp overlap bevel option",
        name="Clamp overlap",
        default=False
    )

    snap_grid_plane_color: bpy.props.FloatVectorProperty(
        name="Color of snap grid plane",
        subtype='COLOR',
        size=4,
        default=(0, .75, 1, .25)
    )

    snap_grid_dots_color: bpy.props.FloatVectorProperty(
        name="Color of snap grid plane",
        subtype='COLOR',
        size=4,
        default=(1, 1, 1, 1)
    )

    auto_beveled_cut: bpy.props.BoolProperty(
        description="Add a bevel after your cut.",
        name="Auto beveled cut",
        default=True,
        update=bevel_compatibility
    )

    bevel_system: bpy.props.EnumProperty(
        items=(("SIMPLE", "SIMPLE", "Only one bevel on your model."),
               ("MULTIPLE", "MULTIPLE", "Need more knowledge about the Blender modifiers.")
               ),
        default='SIMPLE',
        update=bevel_compatibility
    )

    instant_mesh_file: bpy.props.StringProperty(
        name="Instant Meshes Executable",
        subtype='FILE_PATH',
    )

    show_panel: bpy.props.BoolProperty(
        description="Show the Fluent panel",
        name="Fluent panel",
        default=True,
        update=panel_toggle
    )

    pie_option_pt: bpy.props.BoolProperty(
        description="Show the Power Trip tool in the pie menu",
        name="PT in the pie menu",
        default=True
    )

    pie_option_toolbox: bpy.props.BoolProperty(
        description="Show the toolbox in the pie menu",
        name="Toolbox in the pie menu",
        default=True
    )

    pie_option_other_adjustments: bpy.props.BoolProperty(
        description="Show the other adjustment button in the pie menu",
        name="Other adjustment button in the pie menu",
        default=True
    )

    fluent_primitive: bpy.props.BoolProperty(
        description="Add Fluent primitive in Shift+A menu",
        name="Show Fluent primitive menu",
        default=True,
        update=toggle_primitive
    )

    cloth_resolution: bpy.props.IntProperty(
        description="Cloth resolution face/m²",
        name="Cloth resolution",
        default=2000,
        min=0,
        step=10
    )
    cloth_shrink: bpy.props.FloatProperty(
        description="Shrink",
        name="Cloth shrink",
        default=-0.1,
        step=0.01
    )
    cloth_pressure: bpy.props.FloatProperty(
        description="Pressure",
        name="Cloth pressure",
        default=20,
        step=0.1
    )
    cloth_freeze: bpy.props.BoolProperty(
        description="Apply the simulation",
        name="Freeze",
        default=True
    )
    cloth_remesh: bpy.props.BoolProperty(
        description="Remesh the selected faces",
        name="Remesh",
        default=True
    )
    cloth_remesh_after: bpy.props.BoolProperty(
        description="Remesh the simulation",
        name="Remesh after simulation",
        default=False
    )
    cloth_triangulation: bpy.props.BoolProperty(
        description="Use a triangulate mesh",
        name="Triangulate",
        default=False
    )
    cloth_stiffness: bpy.props.FloatProperty(
        description="How much the cloth resist to the pressure",
        name="Stiffness",
        default=5,
        min=0
    )
    cloth_end_frame: bpy.props.IntProperty(
        description="Simulation duration.",
        name="End frame",
        default=30,
        min=0
    )
    cloth_remesh_tool: bpy.props.EnumProperty(
        name='Select the remesh tool',
        items=(("INSTANT_MESH", "Instant Mesh", "Instant Mesh"),
               ("QUADREMESHER", "QuadRemesher", "QuadRemesher")
               ),
        default='INSTANT_MESH'
    )
    cloth_topology: bpy.props.EnumProperty(
        name='Select the type of topology',
        items=(
            ("QUAD", "Quad", "Quad"),
            ("TRIANGULATE", "Triangulate", "Triangulate"),
            ("POKE", "Poke", "Poke"),
            ("GARMENT", "Garment", "Garment")
        ),
        default='QUAD'
    )
    cloth_separate_face: bpy.props.BoolProperty(
        description="One panel by faces",
        name="Separate by faces",
        default=False
    )
    cloth_self_collision: bpy.props.BoolProperty(
        description="Self collision",
        name="Self collision",
        default=False
    )
    cloth_gathering: bpy.props.BoolProperty(
        description="gathering",
        name="gathering",
        default=False
    )

    def draw(self, context):

        icons = load_icons()
        gumroad_ico = icons.get("gumroad")
        bm_ico = icons.get("bm")
        layout = self.layout
        wm = context.window_manager
        layout = self.layout

        box = layout.box()
        box.label(text="After change, save your preferences and restart Blender.")
        AddonKeymaps.draw_keymap_items(wm, layout)
        box = layout.box()
        box.label(text='--- Default value ---')
        box.prop(self, "model_resolution")
        box.prop(self, "min_auto_bevel_segments")
        box.prop(self, "min_auto_cylinder_segments")
        box.prop(self, "latest_bevel_width_preference")
        box.prop(self, "clamp_overlap")

        box = layout.box()
        box.label(text='--- Display ---')
        box.prop(self, "font_size")
        box.prop(self, "icon_size")
        box.prop(self, "show_panel", text="Show the panel")
        box.prop(self, "pie_option_pt")
        box.prop(self, "pie_option_toolbox")
        box.prop(self, "pie_option_other_adjustments")
        box.prop(self, "fluent_primitive")

        box.prop(self, "language", text="Language ")
        box.label(text="Translation is in progress. Whole text isn't translated.")
        box.prop(self, "hightlight_text", text='Hightlight text')
        box.prop(self, "hightlight_dot", text='Hightlight dots')
        box.prop(self, "snap_grid_plane_color", text='Snap grid plane')
        box.prop(self, "snap_grid_dots_color", text='Snap grid dots')

        box = layout.box()
        box.label(text='--- Behavior ---')
        box.prop(self, "bevel_system", text="Bevel system")
        box.prop(self, "auto_beveled_cut", text="Add a bevel after your cut.")
        box.prop(self, "auto_hide_bool", text="Hide boolean object when Fluent is closed.")
        box.prop(self, "auto_parent", text="Auto parent between the boolean object and his target.")
        if 'Power Trip' in bl_info['name']:
            box = box.box()
            box.label(text='To use the cloth panel tool, you have to select and install a remesher tool.')
            box.prop(self, "cloth_remesh_tool")
            if get_addon_preferences().cloth_remesh_tool == 'INSTANT_MESH':
                box.label(text='To use the cloth panel, download Instant Mesh for your OS.')
                box.label(text='Then set the path of the executable file in the input below.')
                row = box.row()
                row.prop(self, "instant_mesh_file", text="Instant mesh file")
                row.operator("fluent.instantmeshdownload", text='Download Instant Mesh here')
            elif get_addon_preferences().cloth_remesh_tool == 'QUADREMESHER':
                box.label(
                    text='Check the installation and activation of QuadRemesher before to use the cloth panel tool.')


class AddonKeymaps:
    _addon_keymaps = []
    _keymaps = {}

    @classmethod
    def new_keymap(cls, name, kmi_name, kmi_value=None, km_name='3D View',
                   space_type="VIEW_3D", region_type="WINDOW",
                   event_type=None, event_value=None, ctrl=False, shift=False,
                   alt=False, key_modifier="NONE"):
        """
        Adds a new keymap
        :param name: str, Name that will be displayed in the panel preferences
        :param kmi_name: str
                - bl_idname for the operators (exemple: 'object.cube_add')
                - 'wm.call_menu' for menu
                - 'wm.call_menu_pie' for pie menu
        :param kmi_value: str
                - class name for Menu or Pie Menu
                - None for operators
        :param km_name: str, keymap name (exemple: '3D View Generic')
        :param space_type: str, space type keymap is associated with, see:
                https://docs.blender.org/api/current/bpy.types.KeyMap.html?highlight=space_type#bpy.types.KeyMap.space_type
        :param region_type: str, region type keymap is associated with, see:
                https://docs.blender.org/api/current/bpy.types.KeyMap.html?highlight=region_type#bpy.types.KeyMap.region_type
        :param event_type: str, see:
                https://docs.blender.org/api/current/bpy.types.Event.html?highlight=event#bpy.types.Event.type
        :param event_value: str, type of the event, see:
                https://docs.blender.org/api/current/bpy.types.Event.html?highlight=event#bpy.types.Event.value
        :param ctrl: bool
        :param shift: bool
        :param alt: bool
        :param key_modifier: str, regular key pressed as a modifier
                https://docs.blender.org/api/current/bpy.types.KeyMapItem.html?highlight=modifier#bpy.types.KeyMapItem.key_modifier
        :return:
        """
        cls._keymaps.update({name: [kmi_name, kmi_value, km_name, space_type,
                                    region_type, event_type, event_value,
                                    ctrl, shift, alt, key_modifier]
                             })

    @classmethod
    def add_hotkey(cls, kc, keymap_name):

        items = cls._keymaps.get(keymap_name)
        if not items:
            return

        kmi_name, kmi_value, km_name, space_type, region_type = items[:5]
        event_type, event_value, ctrl, shift, alt, key_modifier = items[5:]
        km = kc.keymaps.new(name=km_name, space_type=space_type,
                            region_type=region_type)

        kmi = km.keymap_items.new(kmi_name, event_type, event_value,
                                  ctrl=ctrl,
                                  shift=shift, alt=alt,
                                  key_modifier=key_modifier
                                  )
        if kmi_value:
            kmi.properties.name = kmi_value

        kmi.active = True

        cls._addon_keymaps.append((km, kmi))

    @staticmethod
    def register_keymaps():
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        # In background mode, there's no such thing has keyconfigs.user,
        # because headless mode doesn't need key combos.
        # So, to avoid error message in background mode, we need to check if
        # keyconfigs is loaded.
        if not kc:
            return

        for keymap_name in AddonKeymaps._keymaps.keys():
            AddonKeymaps.add_hotkey(kc, keymap_name)

    @classmethod
    def unregister_keymaps(cls):
        kmi_values = [item[1] for item in cls._keymaps.values() if item]
        kmi_names = [item[0] for item in cls._keymaps.values() if
                     item not in ['wm.call_menu', 'wm.call_menu_pie']]

        for km, kmi in cls._addon_keymaps:
            # remove addon keymap for menu and pie menu
            if hasattr(kmi.properties, 'name'):
                if kmi_values:
                    if kmi.properties.name in kmi_values:
                        km.keymap_items.remove(kmi)

            # remove addon_keymap for operators
            else:
                if kmi_names:
                    if kmi.idname in kmi_names:
                        km.keymap_items.remove(kmi)

        cls._addon_keymaps.clear()

    @staticmethod
    def get_hotkey_entry_item(name, kc, km, kmi_name, kmi_value, col):

        # for menus and pie_menu
        if kmi_value:
            for km_item in km.keymap_items:
                if km_item.idname == kmi_name and km_item.properties.name == kmi_value:
                    col.context_pointer_set('keymap', km)
                    rna_keymap_ui.draw_kmi([], kc, km, km_item, col, 0)
                    return

            col.label(text=f"No hotkey entry found for {name}")
            col.operator(TEMPLATE_OT_restore_hotkey.bl_idname,
                         text="Restore keymap",
                         icon='ADD').km_name = km.name

        # for operators
        else:
            if km.keymap_items.get(kmi_name):
                col.context_pointer_set('keymap', km)
                rna_keymap_ui.draw_kmi([], kc, km, km.keymap_items[kmi_name],
                                       col, 0)

            else:
                col.label(text=f"No hotkey entry found for {name}")
                col.operator(TEMPLATE_OT_restore_hotkey.bl_idname,
                             text="Restore keymap",
                             icon='ADD').km_name = km.name

    @staticmethod
    def draw_keymap_items(wm, layout):
        kc = wm.keyconfigs.user

        box = layout.box()
        for name, items in AddonKeymaps._keymaps.items():
            kmi_name, kmi_value, km_name = items[:3]
            split = box.split()
            col = split.column()
            # col.label(text=name)
            # col.separator()
            km = kc.keymaps[km_name]
            AddonKeymaps.get_hotkey_entry_item(name, kc, km, kmi_name,
                                               kmi_value, col)


class TEMPLATE_OT_restore_hotkey(Operator):
    bl_idname = "template.restore_hotkey"
    bl_label = "Restore hotkeys"
    bl_options = {'REGISTER', 'INTERNAL'}

    km_name: StringProperty()

    def execute(self, context):
        context.preferences.active_section = 'KEYMAP'
        wm = context.window_manager
        kc = wm.keyconfigs.addon
        km = kc.keymaps.get(self.km_name)
        if km:
            km.restore_to_default()
            context.preferences.is_dirty = True
        context.preferences.active_section = 'ADDONS'
        return {'FINISHED'}


############################################################################

############################################################################
############################################################################


basic_classes = [
    FLUENT_OT_Cutter,
    FLUENT_OT_CutStarter,
    FLUENT_OT_SliceStarter,
    FLUENT_OT_InsetStarter,
    FLUENT_OT_CreateStarter,
    FLUENT_OT_Editor,
    FLUENT_OT_BooleanOperator,
    FLUENT_OT_BooleanDisplay,
    FLUENT_OT_AddLatestBevel,
    FLUENT_MT_PieMenu,
    FLUENT_MT_ToolBox_Menu,
    FLUENT_PT_Basic_Panel,
    FLUENT_OT_WireframeDisplay,
    FLUENT_OT_TechnicalDisplay,
    FLUENT_OT_AutoCompleteOne,
    FLUENT_OT_NormalRepair,
    FLUENT_OT_BooleanDuplicate,
    FLUENT_OT_BooleanSynchronization,
    FLUENT_OT_VGCleaner,
    FLUENT_OT_ToggleLoopSlide,
    FLUENT_OT_AlignView,
    FLUENT_OT_CleanBooleanObjects,
    FLUENT_OT_ApplyToBoolean,
    FLUENT_OT_AutoSupport,
    FLUENT_OT_AllCutterMirror,
    FLUENT_OT_BecomeFluent,
    FLUENT_OT_FaceExtraction,
    FLUENT_OT_OtherAdjustments,
    FLUENT_OT_AddPrimitive,
    FLUENT_MT_Primitive_Menu,
    fluentProp,
    FluentAddonPreferences,
    TEMPLATE_OT_restore_hotkey
]
classes = basic_classes
# CHARGE POWER TRIP
try:
    from .power_trip import (
        power_trip_panel,
        power_trip_plate,
        power_trip_grids,
        power_trip_cloth_panel,
        power_trip_wire,
        power_trip_pipe,
        power_trip_text2mesh,
        power_trip_screw
    )

    classes.append(power_trip_panel.classes)
    classes.append(power_trip_plate.classes)
    classes.append(power_trip_grids.classes)
    classes.extend(power_trip_cloth_panel.classes)
    classes.extend(power_trip_wire.classes)
    classes.extend(power_trip_pipe.classes)
    classes.append(power_trip_text2mesh.classes)
    classes.append(power_trip_screw.classes)

    print('--- power trip detected')
except:
    print('--- power trip not detected')

def register():
    from bpy.utils import register_class
    for cls in classes:
        try:
            register_class(cls)
        except:
            pass

    if not get_addon_preferences().show_panel:
        from bpy.utils import unregister_class
        unregister_class(power_trip_panel.classes)
        unregister_class(FLUENT_PT_Basic_Panel)

    bpy.types.Scene.fluentProp = bpy.props.PointerProperty(type=fluentProp)

    AddonKeymaps.new_keymap('Pie Menu', 'wm.call_menu_pie', 'FLUENT_MT_PieMenu',
                            '3D View Generic', 'VIEW_3D', 'WINDOW', 'F',
                            'PRESS', False, False, False, 'NONE'
                            )

    AddonKeymaps.new_keymap('Cut', 'fluent.cutstarter', None,
                            '3D View Generic', 'VIEW_3D', 'WINDOW', 'F',
                            'PRESS', False, False, True, 'NONE'
                            )

    AddonKeymaps.new_keymap('Slice', 'fluent.slicestarter', None,
                            '3D View Generic', 'VIEW_3D', 'WINDOW', 'F',
                            'PRESS', True, False, False, 'NONE'
                            )

    AddonKeymaps.new_keymap('Inset', 'fluent.insetstarter', None,
                            '3D View Generic', 'VIEW_3D', 'WINDOW', 'F',
                            'PRESS', False, True, False, 'NONE'
                            )

    AddonKeymaps.new_keymap('Show/Hide boolean', 'fluent.booleandisplay', None,
                            '3D View Generic', 'VIEW_3D', 'WINDOW', 'GRLESS',
                            'PRESS', False, False, False, 'NONE'
                            )

    AddonKeymaps.new_keymap('VG Cleaner', 'fluent.vgcleaner', None,
                            'Mesh', 'EMPTY', 'WINDOW', 'F',
                            'PRESS', False, True, False, 'NONE'
                            )

    AddonKeymaps.register_keymaps()

    if get_addon_preferences().fluent_primitive:
        bpy.types.VIEW3D_MT_mesh_add.prepend(primitive_add)

    load_icons(False)

def unregister():
    AddonKeymaps.unregister_keymaps()
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        try:
            unregister_class(cls)
        except:pass

    clear_icons()

if __name__ == "__main__":
    register()
