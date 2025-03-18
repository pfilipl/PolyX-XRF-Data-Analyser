from PyQt6 import QtWidgets, uic
import sys

import add_roi

class SingleWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(SingleWindow, self).__init__(*args, **kwargs)
        uic.loadUi("single.ui", self)
        self.pushButton_ROIsAdd.clicked.connect(self.ROIsAdd_clicked)

    def ROIsAdd_clicked(self):
        addroi = add_roi.AddRoi(self)
        addroi.setWindowTitle("Add Regions od Interest (ROIs)")
        addroi.exec()