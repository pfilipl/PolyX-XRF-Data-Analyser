from PyQt6 import QtWidgets, uic
import sys

class PeriodicTable(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(PeriodicTable, self).__init__(*args, **kwargs)
        uic.loadUi("periodic_table.ui", self)

class AddRoi(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(AddRoi, self).__init__(*args, **kwargs)
        uic.loadUi("add_roi.ui", self)
        self.setWindowTitle('Add Regions of Interest (ROIs)')