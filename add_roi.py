from PyQt6 import QtWidgets, QtCore, uic
import sys, os, numpy, xraylib, math, pathlib

import main, single

basedir = pathlib.Path(os.path.dirname(__file__))

class AddRoi(QtWidgets.QDialog):
    def __init__(self, parent = None, calib = None, sigma = None, roiCount = 0, monoE = None, monoType = None):
        super(AddRoi, self).__init__(parent)
        uic.loadUi(basedir / "add_roi.ui", self)
        self.setWindowTitle('Add Regions of Interest (ROIs)')

        self.Calib                      = calib
        self.Sigma                      = sigma
        self.monoE                      = monoE
        self.monoType                   = monoType

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

        self.radioButton_CustomEnergy.toggled.connect(lambda checked: self.radioButton_CustomChannel.setChecked(not(checked)))
        self.radioButton_CustomEnergyLine.toggled.connect(lambda checked: self.radioButton_CustomEnergyRange.setChecked(not(checked)))
        self.radioButton_CustomEnergyRange.toggled.connect(lambda checked: self.radioButton_CustomEnergyLine.setChecked(not(checked)))
        self.radioButton_CustomEnergyWidth.toggled.connect(lambda checked: self.radioButton_CustomEnergySigmaWidth.setChecked(not(checked)))
        self.radioButton_CustomEnergySigmaWidth.toggled.connect(lambda checked: self.radioButton_CustomEnergyWidth.setChecked(not(checked)))
        
        self.CustomEnergyLine.valueChanged.connect(lambda value: self.radioButton_CustomEnergy.setChecked(True))
        self.CustomEnergyWidth.valueChanged.connect(lambda value: self.radioButton_CustomEnergy.setChecked(True))
        self.CustomEnergySigmaWidth.valueChanged.connect(lambda value: self.radioButton_CustomEnergy.setChecked(True))
        self.CustomEnergyStart.valueChanged.connect(lambda value: self.radioButton_CustomEnergy.setChecked(True))
        self.CustomEnergyStop.valueChanged.connect(lambda value: self.radioButton_CustomEnergy.setChecked(True))
        
        self.CustomEnergyLine.valueChanged.connect(lambda value: self.radioButton_CustomEnergyLine.setChecked(True))
        self.CustomEnergyWidth.valueChanged.connect(lambda value: self.radioButton_CustomEnergyLine.setChecked(True))
        self.CustomEnergySigmaWidth.valueChanged.connect(lambda value: self.radioButton_CustomEnergyLine.setChecked(True))
        self.CustomEnergyStart.valueChanged.connect(lambda value: self.radioButton_CustomEnergyRange.setChecked(True))
        self.CustomEnergyStop.valueChanged.connect(lambda value: self.radioButton_CustomEnergyRange.setChecked(True))

        self.CustomEnergyWidth.valueChanged.connect(lambda value: self.radioButton_CustomEnergyWidth.setChecked(True))
        self.CustomEnergySigmaWidth.valueChanged.connect(lambda value: self.radioButton_CustomEnergySigmaWidth.setChecked(True))
        
        # - Channel
        self.CustomLine                 = self.spinBox_CustomLine
        self.CustomWidth                = self.spinBox_CustomWidth
        self.CustomStart                = self.spinBox_CustomStart
        self.CustomStop                 = self.spinBox_CustomStop

        self.radioButton_CustomLine.toggled.connect(lambda checked: self.radioButton_CustomRange.setChecked(not(checked)))
        self.radioButton_CustomRange.toggled.connect(lambda checked: self.radioButton_CustomLine.setChecked(not(checked)))
        if self.Calib is not None: self.radioButton_CustomChannel.toggled.connect(lambda checked: self.radioButton_CustomEnergy.setChecked(not(checked)))
        else: self.radioButton_CustomChannel.toggled.connect(lambda checked: self.radioButton_CustomChannel.setChecked(True))

        self.CustomLine.valueChanged.connect(lambda value: self.radioButton_CustomChannel.setChecked(True))
        self.CustomWidth.valueChanged.connect(lambda value: self.radioButton_CustomChannel.setChecked(True))
        self.CustomStart.valueChanged.connect(lambda value: self.radioButton_CustomChannel.setChecked(True))
        self.CustomStop.valueChanged.connect(lambda value: self.radioButton_CustomChannel.setChecked(True))

        self.CustomLine.valueChanged.connect(lambda value: self.radioButton_CustomLine.setChecked(True))
        self.CustomWidth.valueChanged.connect(lambda value: self.radioButton_CustomLine.setChecked(True))
        self.CustomStart.valueChanged.connect(lambda value: self.radioButton_CustomRange.setChecked(True))
        self.CustomStop.valueChanged.connect(lambda value: self.radioButton_CustomRange.setChecked(True))

        # - Regions of interest (ROIs)
        self.CustomROIs                 = self.tableWidget_CustomROIs
        self.RoiCountStart              = roiCount
        self.RoiCount                   = roiCount

        self.CustomROIs.itemSelectionChanged.connect(self.SelectionChanged)
        self.pushButton_CustomAdd.clicked.connect(self.CustomAdd_clicked)
        self.pushButton_CustomDelete.clicked.connect(self.CustomDelete_clicked)
        self.pushButton_CustomDeleteAll.clicked.connect(self.CustomDeletaAll_clicked)

        # XRF lines
        self.XRFLines                   = self.tab_XRFLines
        self.XRFWarning                 = self.label_XRFWarning
        self.XRFSigmaWidth              = self.doubleSpinBox_XRFSigmaWidth
        self.XRFWidth                   = self.spinBox_XRFWidth

        self.radioButton_XRFWidth.toggled.connect(lambda checked: self.radioButton_XRFSigmaWidth.setChecked(not(checked)))
        self.radioButton_XRFSigmaWidth.toggled.connect(lambda checked: self.radioButton_XRFWidth.setChecked(not(checked)))

        self.XRFSigmaWidth.valueChanged.connect(lambda value: self.radioButton_XRFSigmaWidth.setChecked(True))
        self.XRFWidth.valueChanged.connect(lambda value: self.radioButton_XRFWidth.setChecked(True))

        self.Kalpha                     = self.tab_Kalpha
        self.Kbeta                      = self.tab_Kbeta
        self.Lalpha                     = self.tab_Lalpha
        self.Lbeta                      = self.tab_Lbeta
        self.M                          = self.tab_M

        if self.Calib is not None and self.Sigma is not None:
            self.CustomEnergyLine.setEnabled(True)
            self.CustomEnergyWidth.setEnabled(True)
            self.CustomEnergySigmaWidth.setEnabled(True)
            self.CustomEnergyStart.setEnabled(True)
            self.CustomEnergyStop.setEnabled(True)
            self.CustomWarning.hide()
            self.radioButton_CustomEnergy.setEnabled(True)
            self.radioButton_CustomEnergyLine.setEnabled(True)
            self.radioButton_CustomEnergyRange.setEnabled(True)
            self.radioButton_CustomEnergyWidth.setEnabled(True)
            self.radioButton_CustomEnergySigmaWidth.setEnabled(True)
            
            self.XRFLines.setEnabled(True)
            if self.monoE is not None:
                self.XRFWarning.show()
                self.XRFWarning.setText(f"Monochromator: {self.monoType}, E = {self.monoE:.0f} eV")
            else:
                self.XRFWarning.hide()

            self.Kalpha.setLine("Ka")
            self.Kbeta.setLine("Kb")
            self.Lalpha.setLine("La")
            self.Lbeta.setLine("Lb")
            self.M.setLine("M")

            self.Kalpha.setRoiCount(self.RoiCount)
            self.Kbeta.setRoiCount(self.RoiCount)
            self.Lalpha.setRoiCount(self.RoiCount)
            self.Lbeta.setRoiCount(self.RoiCount)
            self.M.setRoiCount(self.RoiCount)

            limitations = {
                "Ka"    : ["B", "Rf"],
                "Kb"    : ["Al", "Rf"],
                "La"    : ["Sc", "Rf"],
                "Lb"    : ["Al", "Cf"],
                "M"     : ["Ce", "Rf"]
            }
            if monoE is not None:
                findLimitK = True
                findLimitL = True
                findLimitM = True
                for Z in range(1, 119):
                    try:
                        if xraylib.EdgeEnergy(Z, xraylib.K_SHELL) > monoE / 1000 and findLimitK: 
                            limitations["Ka"][1] = xraylib.AtomicNumberToSymbol(Z - 1)
                            limitations["Kb"][1] = xraylib.AtomicNumberToSymbol(Z - 1)
                            findLimitK = False
                    finally:    
                        try:
                            if xraylib.EdgeEnergy(Z, xraylib.L1_SHELL) > monoE / 1000 and findLimitL: 
                                limitations["La"][1] = xraylib.AtomicNumberToSymbol(Z - 1)
                                limitations["Lb"][1] = xraylib.AtomicNumberToSymbol(Z - 1)
                                findLimitL = False
                        finally:
                            try:
                                if xraylib.EdgeEnergy(Z, xraylib.M1_SHELL) > monoE / 1000 and findLimitM: 
                                    limitations["M"][1] = xraylib.AtomicNumberToSymbol(Z - 1)
                                    findLimitM = False
                            except:
                                continue
            self.Kalpha.setRangeByName(limitations["Ka"][0], limitations["Ka"][1])
            self.Kbeta.setRangeByName(limitations["Kb"][0], limitations["Kb"][1])
            self.Lalpha.setRangeByName(limitations["La"][0], limitations["La"][1])
            self.Lbeta.setRangeByName(limitations["Lb"][0], limitations["Lb"][1])
            self.M.setRangeByName(limitations["M"][0], limitations["M"][1])

            self.Kalpha.setCalibration(self.Calib, self.Sigma)
            self.Kbeta.setCalibration(self.Calib, self.Sigma)
            self.Lalpha.setCalibration(self.Calib, self.Sigma)
            self.Lbeta.setCalibration(self.Calib, self.Sigma)
            self.M.setCalibration(self.Calib, self.Sigma)

        # Button box
        self.ButtonBox                  = self.buttonBox

        self.ButtonBox.clicked.connect(self.ButtonBox_clicked)

    # def setLastCustom(self, value, lastCustom):
    #     self.LastCustom = lastCustom

    def SelectionChanged(self):
        self.RoiCount = max(self.RoiCount, self.Kalpha.RoiCount, self.Kbeta.RoiCount, self.Lalpha.RoiCount, self.Lbeta.RoiCount, self.M.RoiCount)

    def CustomAdd_clicked(self):
        self.RoiCount += 1
        name = self.CustomName.text()
        if len(self.CustomROIs.findItems(name, QtCore.Qt.MatchFlag.MatchExactly)) > 0:
            name = f"{name}_{self.RoiCount}"

        # if self.LastCustom == "energy line":
        if self.radioButton_CustomEnergy.isChecked() and self.radioButton_CustomEnergyLine.isChecked():
            idx = (numpy.abs(self.Calib - self.CustomEnergyLine.value() * 1000)).argmin()
            sigma_width = math.floor((self.CustomEnergySigmaWidth.value() * self.Sigma[idx]) / 2 + 1)
            idx_minus = (numpy.abs(self.Calib - (self.CustomEnergyLine.value() * 1000 - self.CustomEnergyWidth.value() * 1000 / 2))).argmin()
            idx_plus = (numpy.abs(self.Calib - (self.CustomEnergyLine.value() * 1000 + self.CustomEnergyWidth.value() * 1000 / 2))).argmin()
            # width = max(sigma_width, idx - idx_minus, idx - idx_plus)
            width = sigma_width if self.radioButton_CustomEnergySigmaWidth.isChecked() else max(idx - idx_minus, idx - idx_plus)
            start = idx - width
            stop = idx + width
        # elif self.LastCustom == "energy range":
        elif self.radioButton_CustomEnergy.isChecked() and self.radioButton_CustomEnergyRange.isChecked():
            start = (numpy.abs(self.Calib - self.CustomEnergyStart.value() * 1000)).argmin()
            stop = (numpy.abs(self.Calib - self.CustomEnergyStop.value() * 1000)).argmin()
        # elif self.LastCustom == "channel line":
        elif self.radioButton_CustomChannel.isChecked() and self.radioButton_CustomLine.isChecked():
            idx = self.CustomLine.value()
            width = math.floor(self.CustomWidth.value() / 2)
            start = idx - width
            stop = idx + width
        # elif self.LastCustom == "channel range":
        elif self.radioButton_CustomChannel.isChecked() and self.radioButton_CustomRange.isChecked():
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
            table.blockSignals(True)
            table.setCurrentCell(0, 0)
            while table.rowCount() > 0:
                table.removeRow(table.currentRow())
            try:
                tabs = self.parent().findChild(QtWidgets.QTabWidget, "tabWidget")
                while tabs.count() > 13:
                    tabs.removeTab(13)
                singleParent = True
            except:
                signleParent = False
            for row in range(self.CustomROIs.rowCount()):
                table.insertRow(table.currentRow() + 1)
                table.setItem(table.currentRow() + 1, 0, QtWidgets.QTableWidgetItem(f"{self.CustomROIs.item(row, 0).text()}"))
                table.setItem(table.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(f"{self.CustomROIs.item(row, 1).text()}"))
                table.setItem(table.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(f"{self.CustomROIs.item(row, 2).text()}"))
                table.setItem(table.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(f"{self.CustomROIs.item(row, 3).text()}"))
                table.setCurrentCell(table.currentRow() + 1, 0)
                if singleParent:
                    i = tabs.addTab(single.PreviewTab(tabs.parent(), int(self.CustomROIs.item(row, 1).text()), int(self.CustomROIs.item(row, 2).text()), float(self.CustomROIs.item(row, 3).text())), self.CustomROIs.item(row, 0).text())
                    tabs.widget(i).Canvas.mpl_connect("button_press_event", lambda event, canvas = tabs.widget(i).Canvas: self.parent().MatplotlibButtonPressed(event, canvas))
                    tabs.widget(i).Canvas.mpl_connect("button_release_event", lambda event, canvas = tabs.widget(i).Canvas: self.parent().MatplotlibButtonReleased(event, canvas))
                    tabs.widget(i).Canvas.mpl_connect("motion_notify_event", lambda event, canvas = tabs.widget(i).Canvas: self.parent().MatplotlibMouseMotion(event, canvas))
            table.blockSignals(False)
            self.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())