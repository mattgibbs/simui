from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsItem
from PyQt5.QtGui import QBrush, QColor, QPolygonF, QTransform
from PyQt5.QtCore import QPointF, QRectF
from pyqtgraph import GraphicsWidget, Point

class MagnetButtonItem(GraphicsWidget):
  fill_brush = QBrush(QColor(255,255,255))

  def __init__(self, magnet, size, direction=1.0, parent=None):
    super(MagnetButtonItem, self).__init__(parent)
    self.magnet = magnet
    self.direction = direction
    tri_poly = QPolygonF([QPointF(-size,direction*size/2.0), QPointF(0.0,-direction*size/2.0), QPointF(size,direction*size/2.0)])
    self.triangle = QGraphicsPolygonItem(tri_poly, parent=self)
    self.triangle.setBrush(self.fill_brush)
    self.setFixedHeight(size)
    self.setFixedWidth(size)
    self._bounds = QRectF(0,0,1,1)
    self._boundingRect = None
    self.anchor = Point(0.5,0.5)
    self._lastScene = None
    self._lastTransform = None
    self.setToolTip(self.magnet.name)
    self.default_opacity = 0.7
    self.disabled_opacity = 0.4
    self.hovering_opacity = 1.0
    self.setOpacity(self.default_opacity)
    self.enabled = True
  
  def mouseClickEvent(self, ev):
    if not self.enabled:
      return
    if self.direction == 1.0:
      self.magnet.increase_kick()
    elif self.direction == -1.0:
      self.magnet.decrease_kick()
    ev.accept()

  def hoverEvent(self, ev):
    #Note this is the custom pyqtgraph.GraphicsWidget hover event, not the Qt version.
    if not self.enabled:
      return
    if ev.enter:
      self.setOpacity(self.hovering_opacity)
    elif ev.exit:
      self.setOpacity(self.default_opacity)    

  def disable(self):
    self.enabled = False
    self.setOpacity(self.disabled_opacity)

  def enable(self):
    self.enabled = True
    self.setOpacity(self.default_opacity)

  def boundingRect(self):
    return self.triangle.mapToParent(self.triangle.boundingRect()).boundingRect()

  def viewTransformChanged(self):
    # called whenever view transform has changed.
    # Do this here to avoid double-updates when view changes.
    self.updateTransform()

  def dataBounds(self, axis, frac=1.0, orthoRange=None):
  #  """Called by ViewBox for determining the auto-range bounds.
    return None
  
  def updateTransform(self):
    # update transform such that this item has the correct orientation
    # and scaling relative to the scene, but inherits its position from its
    # parent.
    # This is similar to setting ItemIgnoresTransformations = True, but 
    # does not break mouse interaction and collision detection.
    p = self.parentItem()
    if p is None:
      pt = QTransform()
    else:
      pt = p.sceneTransform()
    if pt == self._lastTransform:
      return
    t = pt.inverted()[0]
    # reset translation
    t.setMatrix(t.m11(), t.m12(), t.m13(), t.m21(), t.m22(), t.m23(), 0, 0, t.m33())
    self.setTransform(t)
    self._lastTransform = pt
        
  def setNewBounds(self):
    """Update the item's bounding rect to match the viewport"""
    self._boundingRect = None  ## invalidate bounding rect, regenerate later if needed.
    self.prepareGeometryChange()
  
  def itemChange(self, change, value):
    if change == QGraphicsItem.ItemSceneChange:
      s = value
      ls = self.scene()
      if ls is not None:
        ls.sigPrepareForPaint.disconnect(self.updateTransform)
      if s is not None:
        try:
          s.sigPrepareForPaint.connect(self.updateTransform)
        except AttributeError:
          #When the whole GUI closes, all the magnet buttons get re-parented to a plain old QGraphicsScene, which doesnt have the signal.
          pass
      self.updateTransform()
    return super(MagnetButtonItem, self).itemChange(change, value)
