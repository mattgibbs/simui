import os
from collections import OrderedDict
from pydm import Display
from pydm.widgets import PyDMTemplateRepeater, PyDMTabWidget
from pydm.utilities import establish_widget_connections, close_widget_connections
from qtpy.QtWidgets import QVBoxLayout, QScrollArea
from qtpy.QtCore import QSize
from utilities import model_list

def dev_list(start_marker, end_marker, magtype):
    l = model_list.model_list(start_element=start_marker, end_element=end_marker)
    mag_dev_list = [i['device_name'] for i in l if i['device_name'].startswith(magtype)]
    #De-duplicate this list using an ordered dict.
    mag_dev_list = list(OrderedDict.fromkeys(mag_dev_list))
    devlist = [{"device_name": devname} for devname in mag_dev_list]
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
    
    def connect(self):
        if self._is_connected or self.tab_widget is None:
            return
        print("Connecting!", self.selected_area)
        establish_widget_connections(self.tab_widget)
        self._is_connected = True

    def disconnect(self):
        if not self._is_connected or self.tab_widget is None:
            return
        print("Disconnecting!", self.selected_area)
        close_widget_connections(self.tab_widget)
        self._is_connected = False
    
    def showEvent(self, e):
        """
        Show events are sent to widgets that become visible on the screen.

        Parameters
        ----------
        event : QShowEvent
        """
        self.connect()

    def hideEvent(self, e):
        """
        Hide events are sent to widgets that become invisible on the screen.

        Parameters
        ----------
        event : QHideEvent
        """
        self.disconnect()
    
    def setup_ui(self):
        self.setLayout(QVBoxLayout())
        self.tab_widget = PyDMTabWidget(self)
        self.tab_widget.setTabPosition(PyDMTabWidget.West)
        for magtype in ("QUAD", "XCOR", "YCOR", "BEND"):
            page = QScrollArea()
            #page.setLayout(QVBoxLayout())
            tr = PyDMTemplateRepeater()
            tr.templateFilename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "magnet-list-item.ui")
            tr.data = dev_list(self.start_marker, self.end_marker, magtype)
            page.setWidget(tr)
            self.tab_widget.addTab(page, magtype)
        self.layout().addWidget(self.tab_widget)
        
        
