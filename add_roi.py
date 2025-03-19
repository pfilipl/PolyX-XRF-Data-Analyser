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

        # Custom
        self.CustomName                 = self.lineEdit_CustomName.text

        # - Energy
        self.CustomEnergyLine           = self.doubleSpinBox_CustomEnergyLine.value()
        self.CustomEnergyWidth          = self.doubleSpinBox_CustomEnergyWidth.value()
        self.CustomEnergyChannelWidth   = self.spinBox_CustomEnergyChannelWidth.value()
        self.CustomEnergyStart          = self.doubleSpinBox_CustomEnergyStart.value()
        self.CustomEnergyStop           = self.doubleSpinBox_CustomEnergyStop.value()
        self.CustomWarning              = self.label_CustomWarning
        
        # - Channel
        self.CustomLine                 = self.spinBox_CustomLine.value()
        self.CustomWidth                = self.spinBox_CustomWidth.value()
        self.CustomStart                = self.spinBox_CustomStart.value()
        self.CustomStop                 = self.spinBox_CustomStop.value()

        # - Regions of interest (ROIs)
        self.CustomROIs                 = self.tableView_CustomROIs

        self.pushButton_CustomAdd.clicked.connect(self.CustomAdd_clicked)
        self.pushButton_CustomDelete.clicked.connect(self.CustomDelete_clicked)
        self.pushButton_CustomDeleteAll.clicked.connect(self.CustomDeletaALl_clicked)

    def CustomAdd_clicked(self):
        return

    def CustomDelete_clicked(self):
        return

    def CustomDeletaALl_clicked(self):
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())