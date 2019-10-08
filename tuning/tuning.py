from pydm import Display
from pydm.widgets.channel import PyDMChannel
import numpy as np
from qtpy.QtCore import Slot
from qtpy.QtGui import QColor
from pyqtgraph import ColorMap

class TuningDisplay(Display):
    def __init__(self, parent=None, macros=None, args=[]):
        super(TuningDisplay, self).__init__(parent=parent, macros=macros, args=args)
        self.gdetPlot._curves[0].data_changed.connect(self.new_gdet_val)
        
    def ui_filename(self):
        return "tuning.ui"
        
    @Slot()
    def new_gdet_val(self):
        #Update the rolling average
        gdet_mean = np.mean(self.gdetPlot._curves[0].y_waveform[-30:])
        self.latestValueLabel.setText("{:.2f}".format(gdet_mean))
        #color = self.colormap.map(gdet_mean, 'qcolor')
        #self.gdetPlot._curves[0].color = color
        #self.latestValueLabel.setStyleSheet("QLabel#latestValueLabel {{ color: {} }};".format(color.name()))
    
    def color_for_val(self, val):
        diff = np.abs(self.thresholds - val)
        return self.color_table[self.thresholds[np.argmin(diff)]]