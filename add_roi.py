from PyQt6 import QtWidgets, QtCore, uic
import sys, numpy, xraylib, math

import main, PDA

class AddRoi(QtWidgets.QDialog):
    def __init__(self, parent = None, calib = None, sigma = None, roiCount = 0):
        super(AddRoi, self).__init__(parent)
        uic.loadUi("add_roi.ui", self)
        self.setWindowTitle('Add Regions of Interest (ROIs)')

        self.Calib                      = calib
        self.Sigma                      = sigma

        # Custom
        self.CustomName                 = self.lineEdit_CustomName
        self.LastCustom                 = "channel line"

        # - Energy
        self.CustomEnergyLine           = self.doubleSpinBox_CustomEnergyLine
        self.CustomEnergyWidth          = self.doubleSpinBox_CustomEnergyWidth
        self.CustomEnergySigmaWidth     = self.doubleSpinBox_CustomEnergySigmaWidth
        self.CustomEnergyStart          = self.doubleSpinBox_CustomEnergyStart
        self.CustomEnergyStop           = self.doubleSpinBox_CustomEnergyStop
        self.CustomWarning              = self.label_CustomWarning

        self.CustomEnergyLine.valueChanged.connect(lambda value: self.setLastCustom(value, "energy line"))
        self.CustomEnergyWidth.valueChanged.connect(lambda value: self.setLastCustom(value, "energy line"))
        self.CustomEnergySigmaWidth.valueChanged.connect(lambda value: self.setLastCustom(value, "energy line"))
        self.CustomEnergyStart.valueChanged.connect(lambda value: self.setLastCustom(value, "energy range"))
        self.CustomEnergyStop.valueChanged.connect(lambda value: self.setLastCustom(value, "energy range"))
        
        # - Channel
        self.CustomLine                 = self.spinBox_CustomLine
        self.CustomWidth                = self.spinBox_CustomWidth
        self.CustomStart                = self.spinBox_CustomStart
        self.CustomStop                 = self.spinBox_CustomStop

        self.CustomLine.valueChanged.connect(lambda value: self.setLastCustom(value, "channel line"))
        self.CustomWidth.valueChanged.connect(lambda value: self.setLastCustom(value, "channel line"))
        self.CustomStart.valueChanged.connect(lambda value: self.setLastCustom(value, "channel range"))
        self.CustomStop.valueChanged.connect(lambda value: self.setLastCustom(value, "channel range"))

        # - Regions of interest (ROIs)
        self.CustomROIs                 = self.tableWidget_CustomROIs
        self.RoiCountStart              = roiCount
        self.RoiCount                   = roiCount

        self.pushButton_CustomAdd.clicked.connect(self.CustomAdd_clicked)
        self.pushButton_CustomDelete.clicked.connect(self.CustomDelete_clicked)
        self.pushButton_CustomDeleteAll.clicked.connect(self.CustomDeletaAll_clicked)

        # XRF lines
        self.XRFLines                   = self.tab_XRFLines
        self.XRFWarning                 = self.label_XRFWarning
        self.XRFSigmaWidth              = self.doubleSpinBox_XRFSigmaWidth
        self.XRFWidth                   = self.spinBox_XRFWidth

        self.Kalpha                     = self.tab_Kalpha
        self.Kbeta                      = self.tab_Kbeta
        self.Lalpha                     = self.tab_Lalpha
        self.Lbeta                      = self.tab_Lbeta
        self.M                          = self.tab_M

        self.Kalpha.setLine("Ka")
        self.Kbeta.setLine("Kb")
        self.Lalpha.setLine("La")
        self.Lbeta.setLine("Lb")
        self.M.setLine("M")

        if self.Calib is not None and self.Sigma is not None:
            self.CustomEnergyLine.setEnabled(True)
            self.CustomEnergyWidth.setEnabled(True)
            self.CustomEnergySigmaWidth.setEnabled(True)
            self.CustomEnergyStart.setEnabled(True)
            self.CustomEnergyStop.setEnabled(True)
            self.CustomWarning.hide()
            
            self.XRFLines.setEnabled(True)
            self.XRFWarning.hide()

            # Periodic tables
            self.KalphaChecked          = numpy.ones(119, numpy.bool_) * False
            self.KbetaChecked           = numpy.ones(119, numpy.bool_) * False
            self.LalphaChecked          = numpy.ones(119, numpy.bool_) * False
            self.LbetaChecked           = numpy.ones(119, numpy.bool_) * False
            self.MChecked               = numpy.ones(119, numpy.bool_) * False

            # Maximum ranges
            self.Kalpha.setRange(xraylib.SymbolToAtomicNumber("B"), xraylib.SymbolToAtomicNumber("Rf"))
            self.Kbeta.setRange(xraylib.SymbolToAtomicNumber("Al"), xraylib.SymbolToAtomicNumber("Rf"))
            self.Lalpha.setRange(xraylib.SymbolToAtomicNumber("Sc"), xraylib.SymbolToAtomicNumber("Rf"))
            self.Lbeta.setRange(xraylib.SymbolToAtomicNumber("Al"), xraylib.SymbolToAtomicNumber("Cf"))
            self.M.setRange(xraylib.SymbolToAtomicNumber("Ce"), xraylib.SymbolToAtomicNumber("Rf"))

            self.Kalpha.setCalibration(self.Calib, self.Sigma)
            self.Kbeta.setCalibration(self.Calib, self.Sigma)
            self.Lalpha.setCalibration(self.Calib, self.Sigma)
            self.Lbeta.setCalibration(self.Calib, self.Sigma)
            self.M.setCalibration(self.Calib, self.Sigma)

        # Button box
        self.ButtonBox                  = self.buttonBox

        self.ButtonBox.clicked.connect(self.ButtonBox_clicked)

    def setLastCustom(self, value, lastCustom):
        self.LastCustom = lastCustom

    def CustomAdd_clicked(self):
        self.RoiCount += 1
        name = self.CustomName.text()
        if len(self.CustomROIs.findItems(name, QtCore.Qt.MatchFlag.MatchExactly)) > 0:
            name = f"{name}_{self.RoiCount}"

        if self.LastCustom == "energy line":
            idx = (numpy.abs(self.Calib - self.CustomEnergyLine.value() * 1000)).argmin()
            sigma_width = math.floor((self.CustomEnergySigmaWidth.value() * self.Sigma[idx]) / 2 + 1)
            idx_minus = (numpy.abs(self.Calib - (self.CustomEnergyLine.value() * 1000 - self.CustomEnergyWidth.value() * 1000 / 2))).argmin()
            idx_plus = (numpy.abs(self.Calib - (self.CustomEnergyLine.value() * 1000 + self.CustomEnergyWidth.value() * 1000 / 2))).argmin()
            width = max(sigma_width, idx - idx_minus, idx - idx_plus)
            start = idx - width
            stop = idx + width
        elif self.LastCustom == "energy range":
            start = (numpy.abs(self.Calib - self.CustomEnergyStart.value() * 1000)).argmin()
            stop = (numpy.abs(self.Calib - self.CustomEnergyStop.value() * 1000)).argmin()
        elif self.LastCustom == "channel line":
            idx = self.CustomLine.value()
            width = math.floor(self.CustomWidth.value() / 2)
            start = idx - width
            stop = idx + width
        elif self.LastCustom == "channel range":
            start = self.CustomStart.value()
            stop = self.CustomStop.value()

        self.CustomROIs.insertRow(self.CustomROIs.currentRow() + 1)
        self.CustomROIs.setItem(self.CustomROIs.currentRow() + 1, 0, QtWidgets.QTableWidgetItem(f'{name if name != "" else f"roi{self.RoiCount}"}'))
        self.CustomROIs.setItem(self.CustomROIs.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(str(int(max(start, 1)))))
        self.CustomROIs.setItem(self.CustomROIs.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(str(int(min(stop, 4096)))))
        self.CustomROIs.setItem(self.CustomROIs.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(str(1.00)))
        self.CustomROIs.setCurrentCell(self.CustomROIs.currentRow() + 1, 0)

    def CustomDelete_clicked(self):
        rows = []
        for item in self.CustomROIs.selectedItems():
            rows.append(item.row())
        rows = list(set(rows))
        rows.sort(reverse = True)
        for row in rows:
            try:
                name = self.CustomROIs.item(row, 0).text().split("-")
                if name[1] == "Ka": self.Kalpha.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), False)
                elif name[1] == "Kb": self.Kbeta.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), False)
                elif name[1] == "La": self.Lalpha.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), False)
                elif name[1] == "Lb": self.Lbeta.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), False)
                elif name[1] == "M": self.M.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), False)
            except:
                continue
            finally:
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
            self.RoiCount = self.RoiCountStart
            self.accept()
        else:
            table = self.parent().findChild(QtWidgets.QTableWidget, "tableWidget_ROIs")
            table.setCurrentCell(0, 0)
            while table.rowCount() > 0:
                table.removeRow(table.currentRow())
            for row in range(self.CustomROIs.rowCount()):
                table.insertRow(table.currentRow() + 1)
                table.setItem(table.currentRow() + 1, 0, QtWidgets.QTableWidgetItem(f"{self.CustomROIs.item(row, 0).text()}"))
                table.setItem(table.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(f"{self.CustomROIs.item(row, 1).text()}"))
                table.setItem(table.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(f"{self.CustomROIs.item(row, 2).text()}"))
                table.setItem(table.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(f"{self.CustomROIs.item(row, 3).text()}"))
                table.setCurrentCell(table.currentRow() + 1, 0)
            self.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())