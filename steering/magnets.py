import os
from psp.Pv import Pv
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication
import pyca
import numpy as np
from operator import attrgetter
import json

class Magnet(object):
    kick_delta = 0.0002 #in kG
    def __init__(self, device_name, z_pos):
        self.device_name = device_name
        self.z = z_pos
        self.bctrl_pv = Pv("{}:BCTRL".format(device_name))
        self.bact_pv = Pv("{}:BACT".format(device_name))
    
    @classmethod
    def pv_count(cls):
        return 2
    
    @property
    def name(self):
        return self.device_name
    
    def connect(self):
        self.bctrl_pv.connect()
        self.bact_pv.connect()
    
    def connected(self):
        if self.bctrl_pv.state() == 2 and self.bact_pv.state() == 2:
            return True
        else:
            return False

    def monitor(self):
        self.bctrl_pv.monitor(pyca.DBE_VALUE)
        self.bact_pv.monitor(pyca.DBE_VALUE)

    @property
    def kick_setpoint(self):
        return self.bctrl_pv.data["value"]
    
    @kick_setpoint.setter
    def kick_setpoint(self, new_setpoint):
        return self.bctrl_pv.put(new_setpoint)
    
    @property
    def kick_readback(self):
        return self.bact_pv.data["value"]

    def increase_kick(self):
        before_val = self.kick_setpoint
        new_val = before_val + (self.kick_delta)
        self.kick_setpoint = new_val

    def decrease_kick(self):
        before_val = self.kick_setpoint
        new_val = before_val - (self.kick_delta)
        self.kick_setpoint = new_val

class MagnetList(QObject):
    connectStarted = pyqtSignal()
    connectionProgress = pyqtSignal()
    connectFinished = pyqtSignal()
    def __init__(self, axis, filename, parent=None):
        super(MagnetList, self).__init__(parent=parent)
        if axis not in ("X", "Y"):
            raise Exception("Axis must be either 'X' or 'Y'.")
        self.axis = axis
        self._list = self.get_magnet_names(filename)
        self._zmin = None
        self._zmax = None
        self.saved_readbacks = None
        self.saved_setpoints = None
    
    def progress_total(self):
        return 3
        
    def pv_count(self):
        return len(self._list)*Magnet.pv_count()
    
    def connect(self):
        connection_progress = 0
        for magnet in self._list:
            magnet.connect()
        connection_progress += 1
        self.connectionProgress.emit()
        QApplication.instance().processEvents()
        pyca.pend_event(0.2)
        
        retries = 0
        max_retries = 50
        check_start_connection_progress = connection_progress
        while retries < max_retries:
            all_connected = True
            for i, magnet in enumerate(self._list):
                if not magnet.connected():
                    all_connected = False
            if not all_connected:
                print("Retrying magnet PV connections...")
                pyca.pend_event(0.2)
            else:
                break
            retries = retries + 1
        if retries == max_retries:
            print("Some Magnets failed to connect.  Removing: {}".format([mag.name for mag in self._list if not mag.connected()]))
            self._list = [mag for mag in self._list if mag.connected()]
        connection_progress += 1
        self.connectionProgress.emit()
        QApplication.instance().processEvents()
        
        for magnet in self._list:
            magnet.monitor()
        pyca.pend_event(0.2)
        
        connection_progress += 1
        self.connectionProgress.emit()
        QApplication.instance().processEvents()
        
    
    def get_magnet_names(self, filename):
        magnets = []
        
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)) as f:
            mag_list = json.load(f)
            for mag in mag_list:
                magnets.append(Magnet(mag["device_name"], mag["z_pos"]))
        magnets.sort(key=attrgetter('z'))
        return magnets
    
    def save_setpoints(self):
        self.saved_setpoints = np.zeros(len(self))
        for i, magnet in enumerate(self._list):
            self.saved_setpoints[i] = magnet.kick_setpoint

    def save_readbacks(self):
        self.saved_readbacks = np.zeros(len(self))
        for i, magnet in enumerate(self._list):
            self.saved_readbacks[i] = magnet.kick_readback

    def load_saved_setpoints(self):
        if self.saved_setpoints is None:
            raise Exception("No saved setpoints to load!")
        for i, magnet in enumerate(self._list):
            magnet.kick_setpoint = self.saved_setpoints[i]

    def __getitem__(self, item):
        return self._list[item]
    
    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return iter(self._list)

    def append(self, item):
        self._list.append(item)

    def _find_z_min_and_max(self):
        for magnet in self._list:
            if (self._zmin is None) or magnet.z < self._zmin:
                self._zmin = magnet.z
            if (self._zmax is None) or magnet.z > self._zmax:
                self._zmax = magnet.z

    def zmin(self):
        if self._zmin is None:
            self._find_z_min_and_max()
        return self._zmin

    def zmax(self):
        if self._zmax is None:
            self._find_z_min_and_max()
        return self._zmax
