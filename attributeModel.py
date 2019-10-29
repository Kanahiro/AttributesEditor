# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt, QAbstractTableModel

class AttributeModel(QAbstractTableModel):

    def __init__(self, list, headers = [], ids = [], parent = None):
        QAbstractTableModel.__init__(self, parent)
        self.list = list
        self.headers = headers
        self.ids = ids

    def rowCount(self, parent):
        return len(self.list)

    def columnCount(self, parent):
        return len(self.headers)

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            return self.list[row][column]

        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.list[row][column]
            return value

    def setData(self, index, value, role = Qt.EditRole):
        row = index.row()
        column = index.column()
        
        if role == Qt.EditRole:
            self.list[row][column] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self.headers):
                    return self.headers[section]
                else:
                    return "not implemented"
            else:
                return self.ids[section]
