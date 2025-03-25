from PyQt6 import QtWidgets, uic
import sys, numpy, xraylib

import main

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
        self.CustomROIs                 = self.tableWidget_CustomROIs

        self.pushButton_CustomAdd.clicked.connect(self.CustomAdd_clicked)
        self.pushButton_CustomDelete.clicked.connect(self.CustomDelete_clicked)
        self.pushButton_CustomDeleteAll.clicked.connect(self.CustomDeletaAll_clicked)

        # XRF lines
        self.XRFLines                   = self.tab_XRFLines
        self.XRFWarning                 = self.label_XRFWarning
        self.XRFSigmaWidth              = self.doubleSpinBox_XRFSigmaWidth.value()
        self.XRFWidth                   = self.spinBox_XRFWidth.value()

        self.XRFLines.setEnabled(True)

        # - Periodic tables
        self.Kalpha                     = self.tab_Kalpha
        self.Kbeta                      = self.tab_Kbeta
        self.Lalpha                     = self.tab_Lalpha
        self.Lbeta                      = self.tab_Lbeta
        self.M                          = self.tab_M

        self.KalphaChecked              = numpy.ones(119, numpy.bool_) * False
        self.KbetaChecked               = numpy.ones(119, numpy.bool_) * False
        self.LalphaChecked              = numpy.ones(119, numpy.bool_) * False
        self.LbetaChecked               = numpy.ones(119, numpy.bool_) * False
        self.MChecked                   = numpy.ones(119, numpy.bool_) * False

        self.Kalpha.setLine("Ka")
        self.Kbeta.setLine("Kb")
        self.Lalpha.setLine("La")
        self.Lbeta.setLine("Lb")
        self.M.setLine("M")

        self.Kalpha.setRange(20, 100)
        self.Kbeta.setRange(20, 100)
        self.Lalpha.setRange(20, 100)
        self.Lbeta.setRange(20, 100)
        self.M.setRange(20, 100)

        CALIB_NBINS = 4096      # [ch]
        CALIB_A     = 0.007016  # [keV/ch]
        CALIB_B     = -0.71138  # [keV]
        CALIB_NOISE = 142.61    # [eV]
        CALIB_FANO  = 0.06269   # [-]

        self.Kalpha.setCalibration(CALIB_NBINS, CALIB_A, CALIB_B, CALIB_NOISE, CALIB_FANO)
        self.Kbeta.setCalibration(CALIB_NBINS, CALIB_A, CALIB_B, CALIB_NOISE, CALIB_FANO)
        self.Lalpha.setCalibration(CALIB_NBINS, CALIB_A, CALIB_B, CALIB_NOISE, CALIB_FANO)
        self.Lbeta.setCalibration(CALIB_NBINS, CALIB_A, CALIB_B, CALIB_NOISE, CALIB_FANO)
        self.M.setCalibration(CALIB_NBINS, CALIB_A, CALIB_B, CALIB_NOISE, CALIB_FANO)

        # Button box
        self.ButtonBox                  = self.buttonBox

        self.ButtonBox.clicked.connect(self.ButtonBox_clicked)

    def CustomAdd_clicked(self):
        return

    def CustomDelete_clicked(self):
        rows = []
        for item in self.CustomROIs.selectedItems():
            rows.append(item.row())
        rows = list(set(rows))
        rows.sort(reverse = True)
        for row in rows:
            name = self.CustomROIs.item(row, 0).text().split("-")
            if name[1] == "Ka": self.Kalpha.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), False)
            elif name[1] == "Kb": self.Kbeta.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), False)
            elif name[1] == "La": self.Lalpha.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), False)
            elif name[1] == "Lb": self.Lbeta.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), False)
            elif name[1] == "M": self.M.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), False)
            self.CustomROIs.removeRow(row)

    def CustomDeletaAll_clicked(self):
        self.CustomROIs.setCurrentCell(0, 0)
        while self.CustomROIs.rowCount() > 0:
            self.CustomROIs.removeRow(self.CustomROIs.currentRow())
        self.Kalpha.resetElementsChecked()
        self.Kbeta.resetElementsChecked()
        self.Lalpha.resetElementsChecked()
        self.Lbeta.resetElementsChecked()
        self.M.resetElementsChecked()
    
    def ButtonBox_clicked(self, button):
        if button.text() == "Reset":
            self.CustomDeletaAll_clicked()

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