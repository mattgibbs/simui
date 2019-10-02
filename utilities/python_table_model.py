from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant
from operator import itemgetter

class PythonTableModel(QAbstractTableModel):
	def __init__(self, column_names, initial_list=[], parent=None, edit_method=None, can_edit_method=None):
		super(PythonTableModel, self).__init__(parent=parent)
		self._list = initial_list
		self._column_names = column_names
		self.edit_method = edit_method
		self.can_edit_method = can_edit_method

	@property
	def list(self):
		return self._list

	@list.setter
	def list(self, new_list):
		self.beginResetModel()
		self._list = new_list
		self.endResetModel()

	#QAbstractItemModel Implementation
	def clear(self):
		self.list = []

	def flags(self, index):
		f = Qt.ItemIsSelectable | Qt.ItemIsEnabled
		if self.edit_method is not None:
			editable = True
			if self.can_edit_method is not None:
				editable = self.can_edit_method(self._list[index.row()][index.column()])
			if editable:
				f = f | Qt.ItemIsEditable
		return f

	def rowCount(self, parent=None):
		if parent is not None and parent.isValid():
			return 0
		return len(self._list)

	def columnCount(self, parent=None):
		return len(self._column_names)

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return QVariant()
		if index.row() >= self.rowCount():
			return QVariant()
		if index.column() >= self.columnCount():
			return QVariant()
		if role == Qt.DisplayRole:
			return str(self._list[index.row()][index.column()])
		else:
			return QVariant()

	def setData(self, index, value, role=Qt.EditRole):
		if self.edit_method is None:
			return False
		if role != Qt.EditRole:
			return False
		if not index.isValid():
			return False
		if index.row() >= self.rowCount():
			return False
		if index.column() >= self.columnCount():
			return False
		success = self.edit_method(self._list[index.row()][index.column()], value.toPyObject())
		if success:
			self.dataChanged.emit(index, index)
		return success

	def headerData(self, section, orientation, role=Qt.DisplayRole):
		if role != Qt.DisplayRole:
			return super(PythonTableModel, self).headerData(section, orientation, role)
		if orientation == Qt.Horizontal and section < self.columnCount():
			return str(self._column_names[section])
		elif orientation == Qt.Vertical and section < self.rowCount():
			return section

	def sort(self, col, order=Qt.AscendingOrder):
		self.layoutAboutToBeChanged.emit()
		sort_reversed = (order == Qt.AscendingOrder)
		self._list.sort(key=itemgetter(col), reverse=sort_reversed)
		self.layoutChanged.emit()
	#End QAbstractItemModel implementation.

	#Python collection implementation.
	def __len__(self):
		return len(self._list)

	def __iter__(self):
		return iter(self._list)

	def __contains__(self, value):
		return value in self._list

	def __getitem__(self, index):
		return self._list[index]

	def __setitem__(self, index, value):
		if len(value) != self.columnCount():
			raise ValueError("Items must have the same length as the column count ({})".format(self.columnCount()))
		self._list[index] = value
		self.dataChanged.emit(index, index)

	def __delitem__(self, index):
		if (index+1) > len(self):
			raise IndexError("list assignment index out of range")
		self.beginRemoveRows(QModelIndex(), index, index)
		del self._list[index]
		self.endRemoveRows()

	def append(self, value):
		self.beginInsertRows(QModelIndex(), len(self._list), len(self._list))
		self._list.append(value)
		self.endInsertRows()

	def extend(self, values):
		self.beginInsertRows(QModelIndex(), len(self._list), len(self._list) + len(values) - 1)
		self._list.extend(values)
		self.endInsertRows()

	def remove(self, item):
		index = None
		try:
			index = self._list.index(item)
		except ValueError:
			raise ValueError("list.remove(x): x not in list")
		del self[index]

	def pop(self, index=None):
		if len(self._list) < 1:
			raise IndexError("pop from empty list")
		if index is None:
			index = len(self._list) - 1
		del self[index]

	def count(self, item):
		return self._list.count(item)

	def reverse(self):
		self.layoutAboutToBeChanged.emit()
		self._list.reverse()
		self.layoutChanged.emit()

	
