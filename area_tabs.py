import os
import json
from collections import OrderedDict
from utilities import model_list
from pydm import Display
from pydm.widgets import PyDMEmbeddedDisplay, PyDMTabWidget
from qtpy.QtWidgets import QVBoxLayout, QScrollArea, QWidget, QLabel
from qtpy.QtCore import Slot

class AreaTabs(Display):
    def __init__(self, parent=None, macros=None, args=[]):
        super(AreaTabs, self).__init__(parent=parent, macros=macros, args=args)
        self.selected_area = macros['area']
        self.subsystem = macros['subsystem']
        self.setWindowTitle("{} {}".format(self.selected_area.upper(), self.subsystem.upper()))
        self.setup_ui()
        
    
    def ui_filename(self):
        return None
        
    def ui_filepath(self):
        return None
    
    @Slot(int)
    def tab_changed(self, new_tab_index):
        emb = self.tab_widget.currentWidget().findChildren(PyDMEmbeddedDisplay)[0]
        if emb.embedded_widget is not None:
            print("Area {} already has an embedded widget.".format(self.tab_widget.tabText(new_tab_index)))
            return
        top = os.path.dirname(os.path.realpath(__file__))
        emb.filename = os.path.join(top, self.subsystem, "dev_list_display.py")
        
    
    def setup_ui(self):
        self.setLayout(QVBoxLayout())
        self.titleLabel = QLabel(self)
        formatted_subsystem = self.subsystem
        formatted_subsystem = formatted_subsystem[0].upper() + formatted_subsystem[1:]
        if formatted_subsystem[-1] == "s":
            formatted_subsystem = formatted_subsystem[:-1]
        self.titleLabel.setText("{} Displays".format(formatted_subsystem))
        self.layout().addWidget(self.titleLabel)
        self.tab_widget = PyDMTabWidget(self)
        self.layout().addWidget(self.tab_widget)
        top = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(top, 'utilities', 'sectors.json')) as f:
            sectors = json.load(f)
            for i, sector in enumerate(sectors):
                page = QWidget()
                page.setLayout(QVBoxLayout())
                page.layout().setContentsMargins(0,0,0,0)
                emb = PyDMEmbeddedDisplay()
                emb.macros = json.dumps(sector)
                emb.loadWhenShown = False
                emb.disconnectWhenHidden = True
                page.layout().addWidget(emb)
                self.tab_widget.addTab(page, sector['name'])
                if sector['name'] == self.selected_area:
                    self.tab_widget.setCurrentIndex(i)
                    self.tab_changed(i)
        self.tab_widget.currentChanged.connect(self.tab_changed)