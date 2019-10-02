from pydm import Display
from pydm.widgets.channel import PyDMChannel
import numpy as np
from qtpy.QtCore import Slot
from qtpy.QtGui import QColor
from pyqtgraph import ColorMap
import appnope

class TuningDisplay(Display):
    def __init__(self, parent=None, macros=None, args=[]):
        super(TuningDisplay, self).__init__(parent=parent, macros=macros, args=args)
        self.gdet_buffer = np.zeros(30, dtype=np.float64)
        self.gdet_scalar = PyDMChannel(address="ca://GDET:FEE1:241:ENRC", value_slot=self.new_gdet_val)
        appnope.nope()
        color_table = (
                    (0.2, (255,102,102)),
                    (1.0, (255,102,255)),
                    (3.0, (102,102,255)),
                    (4.8, (102,255,217)),
                )
                
        thresholds, colors = zip(*color_table)
        self.colormap = ColorMap(thresholds, colors, mode=ColorMap.RGB)
        self.prev_val = 0
        self.encouragement_text = [
            "Good Job!",
            "Awesome!",
            "Woohoo!",
            "WOW!!"
        ]
        
        # Watch out, assumes dict keys remain sorted.
        self.current_encouragement_threshold = 0
        self.gdet_scalar.connect()
        
        
    def ui_filename(self):
        return "tuning.ui"
        
    @Slot(float)
    def new_gdet_val(self, new_val):
        if new_val is None:
            return
        #Update the rolling average
        self.gdet_buffer = np.roll(self.gdet_buffer, -1)
        self.gdet_buffer[-1] = new_val * 5.0
        gdet_mean = np.mean(self.gdet_buffer)
        self.latestValueLabel.setText("{:.2f}".format(gdet_mean))
        color = self.colormap.map(gdet_mean, 'qcolor')
        self.gdetPlot._curves[0].color = color
        #self.latestValueLabel.setStyleSheet("QLabel#latestValueLabel {{ color: {} }};".format(color.name()))
    
    def color_for_val(self, val):
        diff = np.abs(self.thresholds - val)
        return self.color_table[self.thresholds[np.argmin(diff)]]