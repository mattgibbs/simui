import os
from collections import OrderedDict
from pydm import Display
from pydm.widgets import PyDMTemplateRepeater
from qtpy.QtWidgets import QVBoxLayout, QScrollArea
from qtpy.QtCore import QSize
from utilities import model_list

def dev_list(start_marker, end_marker):
    l = model_list.model_list(start_element=start_marker, end_element=end_marker)
    klystron_dev_list = [i['device_name'] for i in l if i['device_name'].startswith('KLYS')]
    #De-duplicate this list using an ordered dict.
    klystron_dev_list = list(OrderedDict.fromkeys(klystron_dev_list))
    devlist = [{"device": devname} for devname in klystron_dev_list]
    return devlist

class RFDeviceList(Display):
    def __init__(self, parent=None, macros=None, args=[]):
        super(RFDeviceList, self).__init__(parent=parent, macros=macros, args=args)
        self.start_marker = macros['start_marker']
        self.end_marker = macros['end_marker']
        self.setup_ui()
        self.selected_area = macros['name']
    
    def ui_filename(self):
        return None
        
    def ui_filepath(self):
        return None
    
    def setup_ui(self):
        self.setLayout(QVBoxLayout())
        scroll = QScrollArea(self)
        tr = PyDMTemplateRepeater()
        tr.templateFilename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "klys_item_template.ui")
        tr.data = dev_list(self.start_marker, self.end_marker)
        scroll.setWidget(tr)
        self.layout().addWidget(scroll)
        self.layout().addStretch()
        
