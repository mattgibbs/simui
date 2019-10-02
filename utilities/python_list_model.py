from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex, QVariant

class PythonListModel(QAbstractListModel):
	def __init__(self, initial_list=[], parent=None, edit_method=None, can_edit_method=None):
		super(PythonListModel, self).__init__(parent=parent)
		self._list = initial_list
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

	def clear(self):
		self.list = []

	def flags(self, index):
		f = Qt.ItemIsSelectable | Qt.ItemIsEnabled
		if self.edit_method is not None:
			editable = True
			if self.can_edit_method is not None:
				editable = self.can_edit_method(self._list[index.row()])
			if editable:
				f = f | Qt.ItemIsEditable
		return f

	def rowCount(self, parent=None):
		return len(self._list)

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return QVariant()
		if index.row() >= self.rowCount():
			return QVariant()
		if role == Qt.DisplayRole:
			return str(self._list[index.row()])
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
		success = self.edit_method(self._list[index.row()], value.toPyObject())
		if success:
			self.dataChanged.emit(index, index)
		return success

	def __len__(self):
		return len(self._list)

	def __iter__(self):
		return iter(self._list)

	def __contains__(self, value):
		return value in self._list

	def __getitem__(self, index):
		return self._list[index]

	def __setitem__(self, index, value):
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

	def insert(self, index, value):
		self.beginInsertRows(QModelIndex(), index, index)
		self._list.insert(index, value)
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

	#def index(self, item):
	#	return self._list.index(item)
	
	def count(self, item):
		return self._list.count(item)

	def sort(self, cmp=None, key=None, reverse=False):
		self.layoutAboutToBeChanged.emit()
		self._list.sort(cmp, key, reverse)
		self.layoutChanged.emit()

	def reverse(self):
		self.layoutAboutToBeChanged.emit()
		self._list.reverse()
		self.layoutChanged.emit()

	
