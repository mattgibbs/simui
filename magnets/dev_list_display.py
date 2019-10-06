import os
from collections import OrderedDict
from pydm import Display
from pydm.widgets import PyDMTemplateRepeater, PyDMTabWidget
from pydm.utilities import establish_widget_connections, close_widget_connections
from qtpy.QtWidgets import QVBoxLayout, QScrollArea
from qtpy.QtCore import QSize, Slot
from utilities import model_list

def dev_list(start_marker, end_marker, magtype):
    print("Getting magnet list.")
    l = model_list.model_list(start_element=start_marker, end_element=end_marker)
    mag_dev_list = [i['device_name'] for i in l if i['device_name'].startswith(magtype)]
    #De-duplicate this list using an ordered dict.
    mag_dev_list = list(OrderedDict.fromkeys(mag_dev_list))
    devlist = [{"device_name": devname} for devname in mag_dev_list]
    print("Mag list is: {}".format(devlist))
    return devlist

class MagnetDeviceList(Display):
    def __init__(self, parent=None, macros=None, args=[]):
        super(MagnetDeviceList, self).__init__(parent=parent, macros=macros, args=args)
        self.start_marker = macros['start_marker']
        self.end_marker = macros['end_marker']
        self.selected_area = macros['name']
        self._is_connected = False
        self.setup_ui()
    
    def ui_filename(self):
        return None
        
    def ui_filepath(self):
        return None
    
    @Slot(int)
    def magtype_tab_changed(self, new_tab_index):
        scroll = self.tab_widget.currentWidget()
        if scroll.widget():
            return
        magtype = self.tab_widget.tabText(new_tab_index)
        tr = PyDMTemplateRepeater()
        tr.templateFilename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "magnet-list-item.ui")
        tr.data = dev_list(self.start_marker, self.end_marker, magtype)
        scroll.setWidget(tr)
        tr.show()
    
    def setup_ui(self):
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.tab_widget = PyDMTabWidget(self)
        self.tab_widget.setTabPosition(PyDMTabWidget.West)
        for magtype in ("QUAD", "XCOR", "YCOR", "BEND"):
            page = QScrollArea()
            self.tab_widget.addTab(page, magtype)
        self.layout().addWidget(self.tab_widget)
        self.magtype_tab_changed(0)
        self.tab_widget.currentChanged.connect(self.magtype_tab_changed)
        
        
