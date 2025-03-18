from PyQt6 import QtWidgets, uic
import sys

import main

class PeriodicTable(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(PeriodicTable, self).__init__(parent)
        uic.loadUi("periodic_table.ui", self)

class AddRoi(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super(AddRoi, self).__init__(parent)
        uic.loadUi("add_roi.ui", self)
        self.setWindowTitle('Add Regions of Interest (ROIs)')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())