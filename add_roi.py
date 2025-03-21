from PyQt6 import QtWidgets, uic
import sys

import main, periodic_table

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

        # XRF lines
        self.XRFLines                   = self.tab_XRFLines
        self.XRFWarning                 = self.label_XRFWarning
        self.XRFSigmaWidth              = self.doubleSpinBox_XRFSigmaWidth.value()
        self.XRFWidth                   = self.spinBox_XRFWidth.value()

        # self.XRFLines.setEnabled(True)

        # - Periodic tables
        self.Kalpha                     = self.tab_Kalpha
        self.Kbeta                      = self.tab_Kbeta
        self.Lalpha                     = self.tab_Lalpha
        self.Lbeta                      = self.tab_Lbeta
        self.M                          = self.tab_M

        # self.Kalpha.setRange(20, 100)

        # Button box
        self.ButtonBox                  = self.buttonBox

        self.ButtonBox.clicked.connect(self.ButtonBox_clicked)

    def CustomAdd_clicked(self):
        return

    def CustomDelete_clicked(self):
        return

    def CustomDeletaALl_clicked(self):
        return
    
    def ButtonBox_clicked(self, button):
        if button.text() == "Reset":
            print("Reset")
        elif button.text() == "Discard":
            print("Discard")
            self.close()
        else:
            print("Apply")
            self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())