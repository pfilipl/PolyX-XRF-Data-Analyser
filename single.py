from PyQt6 import QtWidgets, uic
import sys, xraylib

import main, add_roi

class SingleWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(SingleWindow, self).__init__(parent)
        uic.loadUi("single.ui", self)

        # Spectrum from map region
        self.AreaX1             = self.doubleSpinBox_AreaX1
        self.AreaZ1             = self.doubleSpinBox_AreaZ1
        self.AreaX2             = self.doubleSpinBox_AreaX2
        self.AreaZ2             = self.doubleSpinBox_AreaZ2
        self.PointX             = self.doubleSpinBox_PointX
        self.PointZ             = self.doubleSpinBox_PointZ

        self.pushButton_MarkPoint.clicked.connect(self.MarkPoint_clicked)
        self.pushButton_SelectArea.clicked.connect(self.SelectArea_clicked)

        # Regions of interest (ROIs)
        self.ROIs               = self.tableWidget_ROIs
        self.ROIsDefault        = self.pushButton_ROIsDefault
        self.RoiCount           = 0

        self.pushButton_ROIsImport.clicked.connect(lambda checked, fileName = None: self.ROIsImport_clicked(checked, fileName))
        self.pushButton_ROIsAdd.clicked.connect(self.ROIsAdd_clicked)
        self.pushButton_ROIsSave.clicked.connect(lambda checked, fileName = None: self.ROIsSave_clicked(checked, fileName))
        self.pushButton_ROIsDelete.clicked.connect(self.ROIsDelete_clicked)
        self.pushButton_ROIsDeleteAll.clicked.connect(self.ROIsDeleteAll_clicked)

        # Map & Spectrum
        self.Map                = self.tab_Map
        self.Spectrum           = self.tab_Spectrum

        # Map
        self.MapPath            = self.lineEdit_MapPath

        self.toolButton_MapPathSearch.clicked.connect(self.MapPathSearch_clicked)

        # Results
        self.ResultsPath        = self.lineEdit_ResultsPath

        self.toolButton_ResultsPathSearch.clicked.connect(self.ResultsPathSearch_clicked)

        # Detectors
        self.DetectorsBe        = self.pushButton_DetectorsBe
        self.DetectorsML        = self.pushButton_DetectorsML
        self.DetectorsSum       = self.pushButton_DetectorsSum

        # Energy calibration
        self.Calib              = None
        self.Sigma              = None

        self.CalibrationGain    = self.doubleSpinBox_CalibrationGain
        self.CalibrationZero    = self.doubleSpinBox_CalibrationZero
        self.CalibrationNoise   = self.doubleSpinBox_CalibrationNoise
        self.CalibrationFano    = self.doubleSpinBox_CalibrationFano

        # Process
        self.Progress           = self.progressBar_Progress
        self.ReloadMap          = self.pushButton_ReloadMap
        self.AnalyseMap         = self.pushButton_AnalyseMap

        self.pushButton_ReloadMap.clicked.connect(self.ReloadMap_clicked)
        self.pushButton_ImportConfig.clicked.connect(lambda clicked, fileName = None: self.ImportConfig_clicked(clicked, fileName))
        self.pushButton_SaveConfig.clicked.connect(lambda clicked, fileName = None: self.SaveConfig_clicked(clicked, fileName))
        self.pushButton_AnalyseMap.clicked.connect(self.AnalyseMap_clicked)

        # Help
        self.Help               = self.label_Help
        self.HelpDescription    = self.label_HelpDescription
        
        self.Help.hide()
        self.HelpDescription.hide()

    def setCalibration(self, calib, sigma):
        self.Calib = calib
        self.Sigma = sigma

    def MarkPoint_clicked(self):
        return

    def SelectArea_clicked(self):
        return

    def ROIsImport_clicked(self, checked, fileName):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import ROIs config", self.ResultsPath.text(), "Text files(*.dat *.txt);; All files(*)")
        if fileName:
            self.ROIs.setCurrentCell(0, 0)
            file = open(fileName, "r")
            for line in file:
                if line[0] != "#":
                    roi = line.split()
                    self.ROIs.insertRow(self.ROIs.currentRow() + 1)
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 0, QtWidgets.QTableWidgetItem(f"{roi[0]}"))
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(f"{roi[1]}"))
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(f"{roi[2]}"))
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(f"{roi[3]}"))
                    self.ROIs.setCurrentCell(self.ROIs.currentRow() + 1, 0)
            file.close()

    def ROIsAdd_clicked(self):
        self.ROIsDefault.setChecked(False)
        addroi = add_roi.AddRoi(self, self.Calib, self.Sigma, self.RoiCount)
        table = addroi.tableWidget_CustomROIs
        for row in range(self.ROIs.rowCount()):
            table.insertRow(table.currentRow() + 1)
            table.setItem(table.currentRow() + 1, 0, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 0).text()}"))
            try:
                name = self.ROIs.item(row, 0).text().split("-")
                if name[1] == "Ka": addroi.tab_Kalpha.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "Kb": addroi.tab_Kbeta.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "La": addroi.tab_Lalpha.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "Lb": addroi.tab_Lbeta.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "M": addroi.tab_M.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
            except:
                continue
            table.setItem(table.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 1).text()}"))
            table.setItem(table.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 2).text()}"))
            table.setItem(table.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 3).text()}"))
            table.setCurrentCell(table.currentRow() + 1, 0)
        if addroi.exec():
            self.RoiCount = addroi.RoiCount
        
    def ROIsSave_clicked(self, checked, fileName):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save ROIs config", self.ResultsPath.text(), "Text files(*.dat *.txt);; All files(*)")
        if fileName:
            file = open(fileName, 'w')
            fileContent = "# Name\t Start channel\t Stop channel\t Sum factor"
            for row in range(self.ROIs.rowCount()):
                fileContent += f"\n{self.ROIs.item(row, 0).text()}\t{self.ROIs.item(row, 1).text()}\t{self.ROIs.item(row, 2).text()}\t{self.ROIs.item(row, 3).text()}"
            file.write(fileContent)
            file.close()
    
    def ROIsDelete_clicked(self):
        rows = []
        for item in self.ROIs.selectedItems():
            rows.append(item.row())
        rows = list(set(rows))
        rows.sort(reverse = True)
        for row in rows:
            self.ROIs.removeRow(row)
    
    def ROIsDeleteAll_clicked(self):
        self.ROIs.setCurrentCell(0, 0)
        while self.ROIs.rowCount() > 0:
            self.ROIs.removeRow(self.ROIs.currentRow())
    
    def MapPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Map path", self.MapPath.text())
        if path:
            self.MapPath.setText(path)
    
    def ResultsPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Results path", self.ResultsPath.text())
        if path:
            self.ResultsPath.setText(path)
    
    def ReloadMap_clicked(self):
        return
    
    def ImportConfig_clicked(self, clicked, fileName):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Single config", self.ResultsPath.text(), "Text files(*.dat *.txt);; All files(*)")
        if fileName:
            file = open(fileName, "r")
            for line in file:
                if line[0] != "#":
                    data = line.split()
                    variableName = data[0]
                    property = data[1]
                    value = data[2]
                    if len(data) > 3:
                        value = " ".join(data[2:])
                    if variableName == "ROIsPath":
                        self.ROIsImport_clicked(False, value)
                    else:
                        if property == "Text": exec(f'self.{variableName}.set{property}("{value}")')
                        else: exec(f'self.{variableName}.set{property}({value})')
            file.close()
    
    def SaveConfig_clicked(self, clicked, fileName):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Single config", self.ResultsPath.text(), "Text files(*.dat *.txt);; All files(*)")
        if fileName:
            file = open(fileName, 'w')
            fileContent = "# Element name\tProperty\tValue"

            fileContent += f"\ndoubleSpinBox_AreaX1\tValue\t{self.AreaX1.value()}"
            fileContent += f"\ndoubleSpinBox_AreaZ1\tValue\t{self.AreaZ1.value()}"
            fileContent += f"\ndoubleSpinBox_AreaX2\tValue\t{self.AreaX2.value()}"
            fileContent += f"\ndoubleSpinBox_AreaZ2\tValue\t{self.AreaZ2.value()}"
            fileContent += f"\ndoubleSpinBox_PointX\tValue\t{self.PointX.value()}"
            fileContent += f"\ndoubleSpinBox_PointZ\tValue\t{self.PointZ.value()}"

            fileContent += f"\npushButton_ROIsDefault\tChecked\t{self.ROIsDefault.isChecked()}"
            fileContent += f'\nROIsPath\tPath\t{fileName.split(".", 1)[-2] + "_ROIs." + fileName.split(".", 1)[-1]}'
            self.ROIsSave_clicked(False, fileName.split('.', 1)[-2] + "_ROIs." + fileName.split('.', 1)[-1])

            fileContent += f"\nMapPath\tText\t{self.MapPath.text()}"
            fileContent += f"\nResultsPath\tText\t{self.ResultsPath.text()}"
            fileContent += f"\nResultsPath\tText\t{self.ResultsPath.text()}"

            fileContent += f"\npushButton_DetectorsBe\tChecked\t{self.DetectorsBe.isChecked()}"
            fileContent += f"\npushButton_DetectorsML\tChecked\t{self.DetectorsML.isChecked()}"
            fileContent += f"\npushButton_DetectorsSum\tChecked\t{self.DetectorsSum.isChecked()}"

            fileContent += f"\ndoubleSpinBox_CalibrationGain\tValue\t{self.CalibrationGain.value()}"
            fileContent += f"\ndoubleSpinBox_CalibrationZero\tValue\t{self.CalibrationZero.value()}"
            fileContent += f"\ndoubleSpinBox_CalibrationNoise\tValue\t{self.CalibrationNoise.value()}"
            fileContent += f"\ndoubleSpinBox_CalibrationFano\tValue\t{self.CalibrationFano.value()}"

            file.write(fileContent)
            file.close()
    
    def AnalyseMap_clicked(self):
        return
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())