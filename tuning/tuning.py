from pydm import Display
from pydm.widgets.channel import PyDMChannel
import numpy as np
from qtpy.QtCore import Slot


class TuningDisplay(Display):
    def __init__(self, parent=None, macros=None, args=[]):
        super(TuningDisplay, self).__init__(parent=parent, macros=macros, args=args)
        self.gdet_buffer = np.zeros(30, dtype=np.float64)
        self.gdet_scalar = PyDMChannel(address="ca://GDET:FEE1:241:ENRC", value_slot=self.new_gdet_val)
        self.gdet_scalar.connect()
        self.encouragement_map = {
            0.2: ((255,102,102), "")
            0.4: ((255,102,140), "")
            0.6: ((255,102,179), "")
            0.8: ((255,102,217), "")
            1.0: ((255,102,255), "")
            1.5: ((217,102,255), "")
            2.0: ((179,102,255), "")
            2.5: ((140,102,255), "Good Job!")
            3.0: ((102,102,255), "")
            3.5: ((102,140,255), "Awesome!")
            4.0: ((102,179,255), "")
            4.5: ((102,217,255), "Woohoo!")
            4.8: ((102,255,217), "WOW!!")
        }
        
        
    def ui_filename(self):
        return "tuning.ui"
        
    @Slot(float)
    def new_gdet_val(self, new_val):
        self.gdet_buffer = np.roll(self.gdet_buffer, -1)
        self.gdet_buffer[-1] = new_val
        self.latestValueLabel.setText("{:.2f}".format(np.mean(self.gdet_buffer)))