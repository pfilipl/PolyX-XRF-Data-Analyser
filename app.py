from PyQt6 import QtWidgets, uic
import sys

class BatchWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(BatchWindow, self).__init__(*args, **kwargs)
        uic.loadUi("batch.ui", self)

class SingleWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(SingleWindow, self).__init__(*args, **kwargs)
        uic.loadUi("single.ui", self)
        self.pushButton_ROIsAdd.clicked.connect(self.ROIsAdd_clicked)

    def ROIsAdd_clicked(self):
        addroi = AddRoi(self)
        addroi.setWindowTitle("Add Regions od Interest (ROIs) Hello World!")
        addroi.exec()

class StitchWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(StitchWindow, self).__init__(*args, **kwargs)
        uic.loadUi("stitch.ui", self)

class PeriodicTable(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(PeriodicTable, self).__init__(*args, **kwargs)
        uic.loadUi("periodic_table.ui", self)

class AddRoi(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(AddRoi, self).__init__(*args, **kwargs)
        uic.loadUi("add_roi.ui", self)
        self.setWindowTitle('Add Regions of Interest (ROIs)')

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi("main.ui", self)
        self.setWindowTitle('PolyX Data Analyser')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())