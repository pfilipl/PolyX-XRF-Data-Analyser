from PyQt6 import QtWidgets, QtGui, QtCore, uic
import sys, os, time, pathlib

import main, add_roi, analyse, PDA

basedir = pathlib.Path(os.path.dirname(__file__))

class BatchWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(BatchWindow, self).__init__(parent)
        uic.loadUi(basedir / "batch.ui", self)

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
        self.MapsConfigValuesAuto       = self.pushButton_MapsConfigValuesAuto
        self.MapsConfigValuesStart      = self.doubleSpinBox_MapsConfigValuesStart
        self.MapsConfigValuesStop       = self.doubleSpinBox_MapsConfigValuesStop
        self.MapsConfigAspectAuto       = self.pushButton_MapsConfigAspectAuto
        self.MapsConfigAspectValue      = self.doubleSpinBox_MapsConfigAspectValue
        self.MapsConfigColormap         = self.comboBox_MapsConfigColormap

        self.MapsConfigValuesStart.valueChanged.connect(self.MapsConfigValue_changed)
        self.MapsConfigValuesStop.valueChanged.connect(self.MapsConfigValue_changed)
        self.MapsConfigAspectValue.valueChanged.connect(self.MapsConfigAspect_changed)
        
        # Spectra configuration
        self.SpectraConfigEnergyAuto    = self.pushButton_SpectraConfigEnergyAuto
        self.SpectraConfigEnergyStart   = self.doubleSpinBox_SpectraConfigEnergyStart
        self.SpectraConfigEnergyStop    = self.doubleSpinBox_SpectraConfigEnergyStop
        self.SpectraConfigAspectAuto    = self.pushButton_SpectraConfigAspectAuto
        self.SpectraConfigAspectValue   = self.doubleSpinBox_SpectraConfigAspectValue

        self.SpectraConfigEnergyStart.valueChanged.connect(self.SpectraConfigEnergy_changed)
        self.SpectraConfigEnergyStop.valueChanged.connect(self.SpectraConfigEnergy_changed)
        self.SpectraConfigAspectValue.valueChanged.connect(self.SpectraConfigAspect_changed)

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

        self.toolButton_ResultsPathSearch.clicked.connect(self.ResultsPathSearch_clicked)

        # Process
        self.Progress                   = self.progressBar_Progress
        self.Analyse                    = self.pushButton_Analyse
        self.OutputConfig               = None

        self.pushButton_ImportConfig.clicked.connect(lambda checked, fileName = None: self.ImportConfig_clicked(checked, fileName))
        self.pushButton_SaveConfig.clicked.connect(lambda checked, fileName = None: self.SaveConfig_clicked(checked, fileName))
        self.pushButton_Analyse.clicked.connect(self.Analyse_clicked)

        # Help
        self.Help                       = self.label_Help
        self.HelpDescription            = self.label_HelpDescription
        
        self.Help.hide()
        self.HelpDescription.hide()

        self.pushButton_ResetAll.clicked.connect(self.ResetAll_clicked)

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
            fileContent = "## ROIs\n# Name\t Start channel\t Stop channel\t Sum factor [ML3.3/Be]\n"
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
        if self.ROIsDefault.isChecked(): self.ROIsDefault.setChecked(False)
    
    def ROIsDeleteAll_clicked(self):
        self.ROIs.setCurrentCell(0, 0)
        while self.ROIs.rowCount() > 0:
            self.ROIs.removeRow(self.ROIs.currentRow())
        if self.ROIsDefault.isChecked(): self.ROIsDefault.setChecked(False)
    
    def MapsConfigValue_changed(self):
        if self.MapsConfigValuesAuto.isChecked(): self.MapsConfigValuesAuto.setChecked(False)

    def MapsConfigAspect_changed(self):
        if self.MapsConfigAspectAuto.isChecked(): self.MapsConfigAspectAuto.setChecked(False)

    def SpectraConfigEnergy_changed(self):
        if self.SpectraConfigEnergyAuto.isChecked(): self.SpectraConfigEnergyAuto.setChecked(False)
        
    def SpectraConfigAspect_changed(self):
        if self.SpectraConfigAspectAuto.isChecked(): self.SpectraConfigAspectAuto.setChecked(False)

    def PathsListExcept_clicked(self):
        for item in self.PathsList.selectedItems():
            self.PathsList.takeItem(self.PathsList.row(item))
        self.Paths = []
        experimentPath = pathlib.Path(self.ExperimentPath.text())
        for row in range(self.PathsList.count()):
            self.Paths.append(experimentPath / self.PathsList.item(row).text())

    def LoadExperiment(self):
        self.Paths = []
        self.PathsList.clear()
        experimentPath = pathlib.Path(self.ExperimentPath.text())
        resultsPath = pathlib.Path(self.ResultsPath.text())
        if experimentPath != resultsPath:
            for mainPath in experimentPath.iterdir():
                if mainPath != resultsPath and mainPath.is_dir():
                    if self.MapsNesting2.isChecked():
                        self.PathsList.insertItem(self.PathsList.currentRow() + 1, QtWidgets.QListWidgetItem(f"{str(mainPath).split(os.sep)[-1]}"))
                        self.PathsList.setCurrentRow(self.PathsList.currentRow() + 1)
                        self.Paths.append(experimentPath / mainPath)
                    elif self.MapsNesting3.isChecked():
                        for path in mainPath.iterdir():
                            if path != resultsPath and path.is_dir():
                                self.PathsList.insertItem(self.PathsList.currentRow() + 1, QtWidgets.QListWidgetItem(f"{str(mainPath).split(os.sep)[-1]}{os.sep}{str(path).split(os.sep)[-1]}"))
                                self.PathsList.setCurrentRow(self.PathsList.currentRow() + 1)
                                self.Paths.append(experimentPath / mainPath / path)
        if len(self.Paths): self.Analyse.setEnabled(True)
        else: self.Analyse.setEnabled(False)

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
        file.write(fileContent + "\n")
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
                path = pathlib.Path(line[:-1])
                if path.parents[0] == pathlib.Path(self.ExperimentPath.text()):
                    self.MapsNesting2.setChecked(True)
                    self.PathsList.insertItem(self.PathsList.currentRow() + 1, QtWidgets.QListWidgetItem(f'{str(path).split(os.sep)[-1]}'))
                elif path.parents[1] == pathlib.Path(self.ExperimentPath.text()):
                    self.MapsNesting3.setChecked(True)
                    self.PathsList.insertItem(self.PathsList.currentRow() + 1, QtWidgets.QListWidgetItem(f'{str(path.parent).split(os.sep)[-1]}{os.sep}{str(path).split(os.sep)[-1]}'))
                self.PathsList.setCurrentRow(self.PathsList.currentRow() + 1)
                self.Paths.append(path)
        file.close()
        if len(self.Paths): self.Analyse.setEnabled(True)
        else: self.Analyse.setEnabled(False)

    def ResultsPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Map path", self.ResultsPath.text())
        if path:
            self.ResultsPath.setText(path)
            # self.LoadExperiment()

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
                    if property == "Text": 
                        if variableName == "MapsConfigColormap":
                            exec(f'self.comboBox_{variableName}.setCurrentIndex(self.comboBox_{variableName}.findText("{value}", QtCore.Qt.MatchFlag.MatchExactly))')
                        else:
                            exec(f'self.{variableName}.set{property}("{value if value else ""}")')
                    else: 
                        exec(f'self.{variableName}.set{property}({value})')
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

            if not self.MapsConfigValuesAuto.isChecked():
                fileContent += f"\n\nMapsConfigValuesStart\tValue\t{self.MapsConfigValuesStart.value()}"
                fileContent += f"\nMapsConfigValuesStop\tValue\t{self.MapsConfigValuesStop.value()}"
            if self.MapsConfigAspectAuto.isChecked():
                fileContent += f"\nMapsConfigAspectAuto\tChecked\tTrue"
            else: fileContent += f"\nMapsConfigAspectValue\tValue\t{self.MapsConfigAspectValue.value()}"
            fileContent += f"\nMapsConfigColormap\tText\t{self.MapsConfigColormap.currentText()}"

            if not self.SpectraConfigEnergyAuto.isChecked():
                fileContent += f"\n\nSpectraConfigEnergyStart\tValue\t{self.SpectraConfigEnergyStart.value()}"
                fileContent += f"\nSpectraConfigEnergyStop\tValue\t{self.SpectraConfigEnergyStop.value()}"
            if self.SpectraConfigAspectAuto.isChecked():
                fileContent += f"\nSpectraConfigAspectAuto\tChecked\tTrue"
            else: fileContent += f"\nSpectraConfigAspectValue\tValue\t{self.SpectraConfigAspectValue.value()}"

            fileContent += f"\n\nResultsPath\tText\t{self.ResultsPath.text()}"

            fileContent += "\n\n# -----\n\n## Batch configuration\n# Element name\tProperty\tValue"            

            fileContent += f"\n\nExperimentPath\tText\t{self.ExperimentPath.text()}"
            fileContent += f'\nMapsNesting{"2" if self.MapsNesting2.isChecked() else "3"}\tChecked\tTrue'

            file.write(fileContent + "\n\n# -----\n\n")
            file.close()

            self.ROIsSave_clicked(False, fileName, 'a')
            
            file = open(fileName, 'a')
            file.write("\n\n# -----\n\n")
            file.close()

            self.PathsSave(fileName, 'a')
    
    def Analyse_clicked(self):
        resultsPath = self.ResultsPath.text()
        if not os.path.isdir(resultsPath):
            if resultsPath == "":
                QtWidgets.QMessageBox.warning(self, "Analyse", f"It is impossible to save output files on an empty path.")
            else:
                QtWidgets.QMessageBox.warning(self, "Analyse", f"It is impossible to save output files on the path:\n{resultsPath}")
        else:
            outputConfig = analyse.Analyse(self, self.OutputConfig, self.DetectorsBe.isChecked(), self.DetectorsML.isChecked(), self.DetectorsSum.isChecked(), True)
            if outputConfig.exec():
                self.OutputConfig = outputConfig.Output
                self.Progress.setValue(0)
                self.Progress.setMaximum((len(self.OutputConfig.keys()) - 15) * len(self.Paths)) # 3 detectors buttons + 2 nesting combos + 3 normalization types + 5 display setting + 2 generates
                QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
                for path in self.Paths:
                    try:
                        head, Data, ICR, OCR, RT, LT, DT, PIN, I0, RC, ROI = PDA.data_load(path)
                    except:
                        if path == "":
                            QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map from empty path.")
                        else:
                            QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map from path:\n{path}")
                    else:
                        tempData = {"head" : head, "Data" : Data, "ICR" : ICR, "OCR" : OCR, "RT" : RT, "LT" : LT, "DT" : DT, "PIN" : PIN, "I0" : I0, "RC" : RC, "ROI" : ROI}
                    
                    if self.ROIsDefault.isChecked(): ROI = tempData["ROI"]
                    else:
                        ROI = []
                        for row in range(self.ROIs.rowCount()):
                            ROI.append([self.ROIs.item(row, 0).text(), int(self.ROIs.item(row, 1).text()), int(self.ROIs.item(row, 2).text()), float(self.ROIs.item(row, 3).text())])
                    POS = None
                    vMin = None if self.MapsConfigValuesAuto.isChecked() else self.MapsConfigValuesStart.value()
                    vMax = None if self.MapsConfigValuesAuto.isChecked() else self.MapsConfigValuesStop.value()
                    mapAspect = 'auto' if self.MapsConfigAspectAuto.isChecked() else self.MapsConfigAspectValue.value()
                    if self.Calib is not None:
                        eMin = 0.0 if self.SpectraConfigEnergyAuto.isChecked() else self.SpectraConfigEnergyStart.value()
                        eMax = None if self.SpectraConfigEnergyAuto.isChecked() else self.SpectraConfigEnergyStop.value()
                    else:
                        eMin = 0.0
                        eMax = None
                    spectraAspect = 'auto' if self.SpectraConfigAspectAuto.isChecked() else self.SpectraConfigAspectValue.value()
                    cMap = self.MapsConfigColormap.currentText()
                    detectors = []
                    nestingType = None
                    display = {}
                    normType = []
                    for name in self.OutputConfig.keys():
                        if name[:2] in ["De", "Si", "Ba", "Ge"]:
                            if name == "DetectorsBe" and self.OutputConfig[name]: detectors.append(1)
                            if name == "DetectorsML" and self.OutputConfig[name]: detectors.append(0)
                            if name == "DetectorsSum" and self.OutputConfig[name]: detectors.append(2)
                            if name == "Batch": nestingType = analyse.NestingTypes[self.OutputConfig[name]]
                            if name == "GenWiatrowska": wiatrowska = self.OutputConfig[name]
                            if name == "GenTiffs": tiffs = self.OutputConfig[name]
                            continue
                        if name[:4] == "Disp":
                            display.update({ name[4:] : self.OutputConfig[name]})
                            continue
                        if name[:8] == "NormType":
                            if self.OutputConfig[name]: normType.append(name[8:])
                            continue
                        if self.OutputConfig[name]:
                            exec(f'analyse.{name}(tempData, path, resultsPath, detectors, "{nestingType}", roi = ROI, pos = POS, calib = self.Calib, vmin = vMin, vmax = vMax, maspect = mapAspect, emin = eMin, emax = eMax, saspect = spectraAspect, cmap = cMap, normtype = normType, disp = display, tiffs = tiffs)')
                            if name == "NormROIs" and wiatrowska:
                                exec(f'analyse.{name}(tempData, path, resultsPath, detectors, "W", roi = ROI, pos = POS, calib = self.Calib, vmin = vMin, vmax = vMax, maspect = mapAspect, emin = eMin, emax = eMax, saspect = spectraAspect, cmap = cMap, normtype = ["I0LT"], disp = display, tiffs = tiffs)')
                        self.Progress.setValue(self.Progress.value() + 1)
                QtGui.QGuiApplication.restoreOverrideCursor()
                dialog = QtWidgets.QMessageBox.information(self, "Analyse", f"Analysis completed!", QtWidgets.QMessageBox.StandardButton.Open | QtWidgets.QMessageBox.StandardButton.Ok, QtWidgets.QMessageBox.StandardButton.Ok)
                if dialog == QtWidgets.QMessageBox.StandardButton.Open:
                    analyse.OpenDirectory(resultsPath)

    def ResetAll_clicked(self):
        if QtWidgets.QMessageBox.question(self, "Batch", f"Do you surely want to reset entire BATCH tab?") == QtWidgets.QMessageBox.StandardButton.Yes:
            parent = self.parent()
            self.setParent(None)
            idx = parent.parent().insertTab(1, BatchWindow(), "BATCH")
            parent.parent().setCurrentIndex(idx)

            parent.parent().parent().parent().Batch = parent.parent().currentWidget()
            parent.parent().parent().parent().Batch.doubleSpinBox_CalibrationGain.valueChanged.connect(lambda value, mode = "Batch": parent.parent().parent().parent().setCalibration(value, mode))
            parent.parent().parent().parent().Batch.doubleSpinBox_CalibrationZero.valueChanged.connect(lambda value, mode = "Batch": parent.parent().parent().parent().setCalibration(value, mode))
            parent.parent().parent().parent().Batch.doubleSpinBox_CalibrationNoise.valueChanged.connect(lambda value, mode = "Batch": parent.parent().parent().parent().setCalibration(value, mode))
            parent.parent().parent().parent().Batch.doubleSpinBox_CalibrationFano.valueChanged.connect(lambda value, mode = "Batch": parent.parent().parent().parent().setCalibration(value, mode))
            parent.parent().parent().parent().setCalibration(None, "Single")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())