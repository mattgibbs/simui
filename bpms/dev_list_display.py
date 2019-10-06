import os
from collections import OrderedDict
from pydm import Display
from pydm.widgets import PyDMLabel
from qtpy.QtWidgets import QVBoxLayout, QGridLayout, QScrollArea, QLabel, QTableWidget
from qtpy.QtCore import QSize, Qt
from utilities import model_list

def dev_list(start_marker, end_marker):
    l = model_list.model_list(start_element=start_marker, end_element=end_marker)
    bpm_dev_list = [i['device_name'] for i in l if i['device_name'].startswith('BPM')]
    devlist = [{"device": devname} for devname in bpm_dev_list]
    return devlist

class BPMDeviceList(Display):
    def __init__(self, parent=None, macros=None, args=[]):
        super(BPMDeviceList, self).__init__(parent=parent, macros=macros, args=args)
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
        bpm_table = QTableWidget(self)
        col_labels = ["X Pos (mm)", "Y Pos (mm)"]
        bpm_table.setColumnCount(len(col_labels))
        bpm_table.setHorizontalHeaderLabels(col_labels)
        data = dev_list(self.start_marker, self.end_marker)
        bpm_names = [bpm['device'] for bpm in data]
        bpm_table.setRowCount(len(bpm_names))
        bpm_table.setVerticalHeaderLabels(bpm_names)
        for row, bpm_name in enumerate(bpm_names):
            for col, axis in enumerate(("X", "Y")):
                pos = PyDMLabel()
                pos.channel = "ca://{}:{}".format(bpm_name, axis)
                pos.showUnits = True
                bpm_table.setCellWidget(row, col, pos)
        self.layout().addWidget(bpm_table)
        
