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
        self.MapConfigValuesAuto        = self.pushButton_MapsConfigValuesAuto
        self.MapConfigValuesStart       = self.doubleSpinBox_MapsConfigValuesStart
        self.MapConfigValuesStop        = self.doubleSpinBox_MapsConfigValuesStop
        self.MapConfigAspectAuto        = self.pushButton_MapsConfigAspectAuto
        self.MapConfigAspectValue       = self.doubleSpinBox_MapsConfigAspectValue
        self.MapConfigColormapDefault   = self.pushButton_MapsConfigColormapDefault
        self.MapConfigColormapValue     = self.lineEdit_MapsConfigColormapValue

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

        self.pushButton_ROIsImport.clicked.connect(self.ROIsImport_clicked)
        self.pushButton_ROIsAdd.clicked.connect(self.ROIsAdd_clicked)
        self.pushButton_ROIsSave.clicked.connect(self.ROIsSave_clicked)
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

        self.pushButton_ImportConfig.clicked.connect(self.ImportConfig_clicked)
        self.pushButton_SaveConfig.clicked.connect(self.SaveConfig_clicked)
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
    
    def ROIsImport_clicked(self):
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
            table.setItem(table.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 1).text()}"))
            table.setItem(table.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 2).text()}"))
            table.setItem(table.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 3).text()}"))
            table.setCurrentCell(table.currentRow() + 1, 0)
        if addroi.exec():
            self.RoiCount = addroi.RoiCount
        
    def ROIsSave_clicked(self):
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
                        self.Paths.append(os.path.join(experimentPath, mainPath))
                    elif self.MapsNesting3.isChecked():
                        for path in os.listdir(os.path.join(experimentPath, mainPath)):
                            if path != self.ResultsPath.text() and os.path.isdir(os.path.join(experimentPath, mainPath, path)):
                                self.PathsList.insertItem(self.PathsList.currentRow() + 1, QtWidgets.QListWidgetItem(f"/{mainPath}/{path}"))
                                self.PathsList.setCurrentRow(self.PathsList.currentRow() + 1)
                                self.Paths.append(os.path.join(experimentPath, mainPath, path))

    def ExperimentPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Map path", self.ExperimentPath.text())
        if path:
            self.ExperimentPath.setText(path)
            self.LoadExperiment()
    
    def ResultsPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Map path", self.ResultsPath.text())
        if path:
            self.ResultsPath.setText(path)
            self.LoadExperiment()
    
    def ImportConfig_clicked(self):
        return
    
    def SaveConfig_clicked(self):
        return
    
    def AnalyseMaps_clicked(self):
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())