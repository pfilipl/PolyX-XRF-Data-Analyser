from PyQt6 import QtWidgets, uic
import sys, os

import main, add_roi

class BatchWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(BatchWindow, self).__init__(parent)
        uic.loadUi("batch.ui", self)

        # Detectors
        self.DetectorsBe                = self.pushButton_DetectorsBe
        self.DetectorsML                = self.pushButton_DetectorsML
        self.DetectorsSum               = self.pushButton_DetectorsSum

        # Energy calibration
        self.Calib                      = None
        self.Sigma                      = None

        self.CalibrationGain            = self.doubleSpinBox_CalibrationGain
        self.CalibrationZero            = self.doubleSpinBox_CalibrationZero
        self.CalibrationNoise           = self.doubleSpinBox_CalibrationNoise
        self.CalibrationFano            = self.doubleSpinBox_CalibrationFano

        # Maps configuration
        self.MapsConfigValuesAuto        = self.pushButton_MapsConfigValuesAuto
        self.MapsConfigValuesStart       = self.doubleSpinBox_MapsConfigValuesStart
        self.MapsConfigValuesStop        = self.doubleSpinBox_MapsConfigValuesStop
        self.MapsConfigAspectAuto        = self.pushButton_MapsConfigAspectAuto
        self.MapsConfigAspectValue       = self.doubleSpinBox_MapsConfigAspectValue
        self.MapsConfigColormapDefault   = self.pushButton_MapsConfigColormapDefault
        self.MapsConfigColormapValue     = self.lineEdit_MapsConfigColormapValue

        self.toolButton_MapsConfigColormapSearch.clicked.connect(self.MapsConfigColormapSearch_clicked)
        
        # Spectra configuration
        self.SpectraConfigEnergyAuto    = self.pushButton_SpectraConfigEnergyAuto
        self.SpectraConfigEnergyStart   = self.doubleSpinBox_SpectraConfigEnergyStart
        self.SpectraConfigEnergyStop    = self.doubleSpinBox_SpectraConfigEnergyStop
        self.SpectraConfigAspectAuto    = self.pushButton_SpectraConfigAspectAuto
        self.SpectraConfigAspectValue   = self.doubleSpinBox_SpectraConfigAspectValue

        # Regions of interest (ROIs)
        self.ROIs                       = self.tableWidget_ROIs
        self.ROIsDefault                = self.pushButton_ROIsDefault
        self.RoiCount                   = 0

        self.pushButton_ROIsImport.clicked.connect(lambda checked, fileName = None: self.ROIsImport_clicked(checked, fileName))
        self.pushButton_ROIsAdd.clicked.connect(self.ROIsAdd_clicked)
        self.pushButton_ROIsSave.clicked.connect(lambda checked, fileName = None, mode = 'w': self.ROIsSave_clicked(checked, fileName, mode))
        self.pushButton_ROIsDelete.clicked.connect(self.ROIsDelete_clicked)
        self.pushButton_ROIsDeleteAll.clicked.connect(self.ROIsDeleteAll_clicked)

        # Experiment / Load
        self.ExperimentPath             = self.lineEdit_ExperimentPath
        self.MapsNesting2               = self.radioButton_MapsNesting2
        self.MapsNesting3               = self.radioButton_MapsNesting3
        self.PathsList                  = self.listWidget_PathsList
        self.Paths                      = None

        self.ExperimentPath.editingFinished.connect(self.LoadExperiment)
        self.toolButton_ExperimentPathSearch.clicked.connect(self.ExperimentPathSearch_clicked)
        self.MapsNesting2.clicked.connect(self.LoadExperiment)
        self.MapsNesting3.clicked.connect(self.LoadExperiment)
        self.pushButton_PathsListExcept.clicked.connect(self.PathsListExcept_clicked)
        self.pushButton_PathsListReload.clicked.connect(self.LoadExperiment)

        # Results
        self.ResultsPath                = self.lineEdit_ResultsPath
        self.ResultsNested              = self.checkBox_ResultsNested

        self.toolButton_ResultsPathSearch.clicked.connect(self.ResultsPathSearch_clicked)

        # Process
        self.Progress                   = self.progressBar_Progress
        self.AnalyseMaps                = self.pushButton_AnalyseMaps

        self.pushButton_ImportConfig.clicked.connect(lambda checked, fileName = None: self.ImportConfig_clicked(checked, fileName))
        self.pushButton_SaveConfig.clicked.connect(lambda checked, fileName = None: self.SaveConfig_clicked(checked, fileName))
        self.pushButton_AnalyseMaps.clicked.connect(self.AnalyseMaps_clicked)

        # Help
        self.Help                       = self.label_Help
        self.HelpDescription            = self.label_HelpDescription
        
        self.Help.hide()
        self.HelpDescription.hide()

    def setCalibration(self, calib, sigma):
        self.Calib = calib
        self.Sigma = sigma

    def MapsConfigColormapSearch_clicked(self):
        return
    
    def ROIsImport_clicked(self, checked, fileName):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import ROIs config", self.ResultsPath.text(), "PDA Files(*.PDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:
            self.ROIsDeleteAll_clicked()
            self.ROIsDefault.setChecked(False)
            self.ROIs.setCurrentCell(0, 0)
            read = False
            file = open(fileName, "r")
            for line in file:
                if line[0] != "\n" and line[0:2] == "##":
                    read = True if line == "## ROIs\n" else False
                if read and line[0] not in ["#", "\n"]:
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
            table.setItem(table.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 1).text()}"))
            table.setItem(table.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 2).text()}"))
            table.setItem(table.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 3).text()}"))
            table.setCurrentCell(table.currentRow() + 1, 0)
        if addroi.exec():
            self.RoiCount = addroi.RoiCount
        
    def ROIsSave_clicked(self, checked, fileName, mode):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save ROIs config", self.ResultsPath.text(), "PDA Files(*.PDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:
            file = open(fileName, mode)
            fileContent = "## ROIs\n# Name\t Start channel\t Stop channel\t Sum factor\n"
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
    
    def PathsListExcept_clicked(self):
        for item in self.PathsList.selectedItems():
            self.PathsList.takeItem(self.PathsList.row(item))
        self.Paths = []
        experimentPath = self.ExperimentPath.text()
        for row in range(self.PathsList.count()):
            self.Paths.append(f"{experimentPath}{self.PathsList.item(row).text()}")

    def LoadExperiment(self):
        self.Paths = []
        self.PathsList.clear()
        experimentPath = self.ExperimentPath.text()
        if experimentPath != self.ResultsPath.text():
            for mainPath in os.listdir(experimentPath):
                if mainPath != self.ResultsPath and os.path.isdir(os.path.join(experimentPath, mainPath)):
                    if self.MapsNesting2.isChecked():
                        self.PathsList.insertItem(self.PathsList.currentRow() + 1, QtWidgets.QListWidgetItem(f"/{mainPath}"))
                        self.PathsList.setCurrentRow(self.PathsList.currentRow() + 1)
                        self.Paths.append(f"{os.path.join(experimentPath, mainPath)}")
                    elif self.MapsNesting3.isChecked():
                        for path in os.listdir(os.path.join(experimentPath, mainPath)):
                            if path != self.ResultsPath.text() and os.path.isdir(os.path.join(experimentPath, mainPath, path)):
                                self.PathsList.insertItem(self.PathsList.currentRow() + 1, QtWidgets.QListWidgetItem(f"/{mainPath}/{path}"))
                                self.PathsList.setCurrentRow(self.PathsList.currentRow() + 1)
                                self.Paths.append(f"{os.path.join(experimentPath, mainPath, path)}")

    def ExperimentPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Map path", self.ExperimentPath.text())
        if path:
            self.ExperimentPath.setText(path)
            self.LoadExperiment()
    
    def PathsSave(self, fileName, mode):
        file = open(fileName, mode)
        fileContent = "## Paths\n"
        for path in self.Paths:
            fileContent += f"\n{path}"
        file.write(fileContent)
        file.close()

    def PathsImport(self, fileName):
        self.PathsList.clear()
        self.Paths = []
        read = False
        file = open(fileName, "r")
        for line in file:
            if line[0] != "\n" and line[0:2] == "##":
                read = True if line == "## Paths\n" else False
            if read and line[0] not in ["#", "\n"]:
                self.PathsList.insertItem(self.PathsList.currentRow() + 1, QtWidgets.QListWidgetItem(f'/{line.split("/")[-1][:-1]}'))
                self.PathsList.setCurrentRow(self.PathsList.currentRow() + 1)
                self.Paths.append(line)

    def ResultsPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Map path", self.ResultsPath.text())
        if path:
            self.ResultsPath.setText(path)
            self.LoadExperiment()

    def ImportConfig_clicked(self, checked, fileName):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Batch config", self.ResultsPath.text(), "PDA Files(*.PDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:
            read = False
            file = open(fileName, "r")
            for line in file:
                if line[0] != "\n" and line[0:2] == "##":
                    read = True if line in ["## General configuration\n", "## Batch configuration\n"] else False
                if read and line[0] not in ["#", "\n"]:
                    data = line.split()
                    variableName = data[0]
                    property = data[1]
                    value = None
                    if len(data) > 2:
                        value = " ".join(data[2:])
                    if property == "Text": exec(f'self.{variableName}.set{property}("{value if value else ""}")')
                    else: exec(f'self.{variableName}.set{property}({value})')
            file.close()
            self.ROIsImport_clicked(False, fileName)
            self.PathsImport(fileName)
    
    def SaveConfig_clicked(self, checked, fileName):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Batch config", self.ResultsPath.text(), "PDA Files(*.PDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:
            file = open(fileName, 'w')
            fileContent = "## General configuration\n# Element name\tProperty\tValue"

            fileContent += f"\n\nDetectorsBe\tChecked\t{self.DetectorsBe.isChecked()}"
            fileContent += f"\nDetectorsML\tChecked\t{self.DetectorsML.isChecked()}"
            fileContent += f"\nDetectorsSum\tChecked\t{self.DetectorsSum.isChecked()}"

            fileContent += f"\n\nCalibrationGain\tValue\t{self.CalibrationGain.value()}"
            fileContent += f"\nCalibrationZero\tValue\t{self.CalibrationZero.value()}"
            fileContent += f"\nCalibrationNoise\tValue\t{self.CalibrationNoise.value()}"
            fileContent += f"\nCalibrationFano\tValue\t{self.CalibrationFano.value()}"

            fileContent += f"\n\nROIsDefault\tChecked\t{self.ROIsDefault.isChecked()}"

            fileContent += f"\n\nResultsPath\tText\t{self.ResultsPath.text()}"

            fileContent += "\n\n# -----\n\n## Batch configuration\n# Element name\tProperty\tValue"            

            fileContent += f"\n\nMapsConfigValuesAuto\tChecked\t{self.MapsConfigValuesAuto.isChecked()}"
            fileContent += f"\nMapsConfigValuesStart\tValue\t{self.MapsConfigValuesStart.value()}"
            fileContent += f"\nMapsConfigValuesStop\tValue\t{self.MapsConfigValuesStop.value()}"
            fileContent += f"\nMapsConfigAspectAuto\tChecked\t{self.MapsConfigAspectAuto.isChecked()}"
            fileContent += f"\nMapsConfigAspectValue\tValue\t{self.MapsConfigAspectValue.value()}"
            fileContent += f"\nMapsConfigColormapDefault\tChecked\t{self.MapsConfigColormapDefault.isChecked()}"
            fileContent += f"\nMapsConfigColormapValue\tText\t{self.MapsConfigColormapValue.text()}"

            fileContent += f"\n\nSpectraConfigEnergyAuto\tChecked\t{self.SpectraConfigEnergyAuto.isChecked()}"
            fileContent += f"\nSpectraConfigEnergyStart\tValue\t{self.SpectraConfigEnergyStart.value()}"
            fileContent += f"\nSpectraConfigEnergyStop\tValue\t{self.SpectraConfigEnergyStop.value()}"
            fileContent += f"\nSpectraConfigAspectAuto\tChecked\t{self.SpectraConfigAspectAuto.isChecked()}"
            fileContent += f"\nSpectraConfigAspectValue\tValue\t{self.SpectraConfigAspectValue.value()}"

            fileContent += f"\n\nExperimentPath\tText\t{self.ExperimentPath.text()}"
            fileContent += f"\nMapsNesting2\tChecked\t{self.MapsNesting2.isChecked()}"
            fileContent += f"\nMapsNesting3\tChecked\t{self.MapsNesting3.isChecked()}"
            
            fileContent += f"\n\nResultsNested\tChecked\t{self.ResultsNested.isChecked()}"

            file.write(fileContent + "\n\n# -----\n\n")
            file.close()

            self.ROIsSave_clicked(False, fileName, 'a')
            
            file = open(fileName, 'a')
            file.write("\n\n# -----\n\n")
            file.close()

            self.PathsSave(fileName, 'a')
    
    def AnalyseMaps_clicked(self):
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())