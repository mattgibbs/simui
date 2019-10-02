import os
import sys
import zmq
from pydm import Display
from orbit_view import OrbitView
from orbit import Orbit
from magnets import MagnetList
from qtpy.QtWidgets import QVBoxLayout, QApplication, QProgressBar, QLabel
from qtpy.QtCore import QTimer, Slot, Qt

class SteeringDisplay(Display):
    def __init__(self, parent=None, macros=None, args=[]):
        super(SteeringDisplay, self).__init__(parent=parent, macros=macros, args=args)
        self._live_orbit = None
        self.setup_ui()
    
    def ui_filename(self):
        return None
        
    def ui_filepath(self):
        return None
    
    def setup_ui(self):
        self.setWindowTitle("Steering Panel")
        self.draw_timer = QTimer(self)
        self.draw_timer.setInterval(int(1000/5))
        self.setLayout(QVBoxLayout())
        self.current_progress = 0
        self.total_progress = 0
        self.loading_label = QLabel(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.x_magnet_list = None
        self.layout().addStretch()
        self.layout().addWidget(self.loading_label)
        self.layout().addWidget(self.progress_bar)
        self.layout().addStretch()
        position_scale = 2.0
        self.orbit_view = OrbitView(parent=self, axis="x", name="X Orbit", label="X Orbit", units="mm", ymin=-position_scale, ymax=position_scale, draw_timer=self.draw_timer)
        self.orbit_view.hide()
        self.layout().addWidget(self.orbit_view)
        self.layout().setStretchFactor(self.orbit_view, 1)
        QTimer.singleShot(50,self.initialize_orbit)
        
    @Slot()
    def initialize_orbit(self):
        QApplication.instance().processEvents() #Need to call processEvents to make the status bar message show up before the live orbit connection stuff starts.
        orbit = Orbit.lcls_bpms(auto_connect=False, parent=self)
        self.x_magnet_list = MagnetList("X", "xcor_list.json", parent=self)
        self.total_progress = orbit.progress_total() + self.x_magnet_list.progress_total()
        num_pvs = orbit.pv_count() + self.x_magnet_list.pv_count()
        self.loading_label.setText("Connecting to {} PVs...".format(num_pvs))
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.progress_bar.setMaximum(self.total_progress)
        orbit.connectionProgress.connect(self.increment_progress)
        self.x_magnet_list.connectionProgress.connect(self.increment_progress)
        orbit.connect()
        orbit.name = "Live Orbit"
        self.live_orbit = orbit
        self.initialize_magnet_lists()
        self.connection_complete()
    
    @Slot()
    def increment_progress(self):
        self.current_progress += 1
        self.progress_bar.setValue(self.current_progress)
    
    @Slot()
    def connection_complete(self):
        self.layout().removeWidget(self.progress_bar)
        self.layout().removeWidget(self.loading_label)
        self.progress_bar.deleteLater()
        self.loading_label.deleteLater()
        self.orbit_view.show()
    
    def initialize_magnet_lists(self):
        self.x_magnet_list.connect()
        self.orbit_view.set_magnet_list(self.x_magnet_list)
        self.orbit_view.show_magnet_views(True)
    
    @property
    def live_orbit(self):
        return self._live_orbit

    @live_orbit.setter
    def live_orbit(self, new_live_orbit):
        if new_live_orbit == self._live_orbit:
            return
        self._live_orbit = new_live_orbit
        self.orbit_view.set_orbit(self._live_orbit, reset_range=False)