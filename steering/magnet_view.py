from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import pyqtSlot, Qt
import math
from pyqtgraph import ViewBox, PlotItem
from magnet_button_item import MagnetButtonItem

class MagnetView(PlotItem):
	def __init__(self, magnet_list=None, direction="up", parent=None):
		super(MagnetView, self).__init__(parent=parent)
		if direction not in ("up", "down"):
			raise Exception("Direction must be 'up' or 'down'")
		self.direction = direction
		#self.use_sector_ticks = use_sector_ticks
		self.setMouseEnabled(x=False, y=False)
		self.hideButtons()
		self.setMenuEnabled(False)
		#Customize the right-click menu.
		self.ymin = -1.0
		self.ymax = 1.0
		self.yminlimit = self.ymin #This is the limit on the Y axis range.
		self.ymaxlimit = self.ymax #This is the upper limit on the Y axis range.
		#self.setLimits(minYRange=abs(self.ymaxlimit - self.yminlimit), maxYRange=abs(self.ymaxlimit - self.yminlimit))
		self.magnet_buttons = []
		self.needs_initial_range = True
		self.magnet_list = None
		if magnet_list is not None:
			self.set_magnets(magnet_list)

	def set_magnets(self, magnet_list, reset_range=True):
		if self.magnet_list == magnet_list:
			return
		old_range = None
		old_zmax = None
		old_zmin = None
		if self.magnet_list is not None:
			old_range = self.viewRect()
		self.magnet_list = magnet_list
		if self.direction == "up":
			direction = 1.0
		else:
			direction = -1.0
		self.clear_magnet_buttons()
		#extent = abs(magnet_list.zmax() - magnet_list.zmin())
		#self.setLimits(xMin=magnet_list.zmin()-(0.02*extent), xMax=magnet_list.zmax()+(0.02*extent))
		self.enableAutoRange(enable=False)
		for magnet in magnet_list:
			button = MagnetButtonItem(magnet=magnet, size=10.0, direction=direction)
			self.vb.addItem(button)
			button.setPos(magnet.z, 0.0)
			self.magnet_buttons.append(button)
		if reset_range or self.needs_initial_range:
			self.reset_range()
			self.needs_initial_range = False
		else:
			self.setRange(old_range, padding=0.0, update=False)
	
	@pyqtSlot(bool)
	def reset_range(self, checked=False):
		self.enableAutoRange(axis=ViewBox.XAxis)
		self.setYRange(self.ymin, self.ymax)

	def wheelEvent(self, event):
		if event.modifiers() == Qt.ShiftModifier:
			s = (1.005) ** (event.delta() * (-1.0/8.0))
			self.scaleBy(y=s)
		else:
			super(MagnetView, self).wheelEvent(event)
	
	def clear_magnet_buttons(self):
		auto_range_x_enabled = self.vb.state['autoRange'][0]
		auto_range_y_enabled = self.vb.state['autoRange'][1]
		self.enableAutoRange(enable=False)
		if self.magnet_list is None:
			return
		for button in self.magnet_buttons:
			self.removeItem(button)
		self.magnet_buttons = []
		self.enableAutoRange(x=auto_range_x_enabled, y=auto_range_y_enabled)
