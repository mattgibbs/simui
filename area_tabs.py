import os
import json
from collections import OrderedDict
from utilities import model_list
from pydm import Display
from pydm.widgets import PyDMEmbeddedDisplay, PyDMTabWidget
from qtpy.QtWidgets import QVBoxLayout, QScrollArea, QWidget, QLabel

class AreaTabs(Display):
    def __init__(self, parent=None, macros=None, args=[]):
        super(AreaTabs, self).__init__(parent=parent, macros=macros, args=args)
        self.selected_area = macros['area']
        self.subsystem = macros['subsystem']
        self.setWindowTitle("{} {}".format(self.selected_area, self.subsystem))
        self.setup_ui()
        
    
    def ui_filename(self):
        return None
        
    def ui_filepath(self):
        return None
    
    def setup_ui(self):
        self.setLayout(QVBoxLayout())
        self.titleLabel = QLabel(self)
        self.titleLabel.setText("RF Displays")
        self.layout().addWidget(self.titleLabel)
        self.tab_widget = PyDMTabWidget(self)
        self.layout().addWidget(self.tab_widget)
        top = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(top, 'utilities', 'sectors.json')) as f:
            sectors = json.load(f)
            for i, sector in enumerate(sectors):
                page = QWidget()
                page.setLayout(QVBoxLayout())
                emb = PyDMEmbeddedDisplay()
                emb.macros = json.dumps(sector)
                emb.loadWhenShown = True
                emb.filename = os.path.join(top, self.subsystem, "dev_list_display.py")
                page.layout().addWidget(emb)
                self.tab_widget.addTab(page, sector['name'])
                if sector['name'] == self.selected_area:
                    self.tab_widget.setCurrentIndex(i)