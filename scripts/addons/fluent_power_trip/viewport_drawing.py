import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader

import math

from .helpers import *
from .shapes import *
from .math_functions import *

def draw_callback_px(self, context):

    for item in self.ui_items_list:
        item.draw(self.events)
