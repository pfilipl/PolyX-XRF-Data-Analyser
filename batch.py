from PyQt6 import QtWidgets, uic
import sys

import main, add_roi

class BatchWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(BatchWindow, self).__init__(parent)
        uic.loadUi("batch.ui", self)

        # Detectors
        self.DetectorsML                = self.pushButton_DetectorsML
        self.DetectorsBe                = self.pushButton_DetectorsBe
        self.DetectorsSum               = self.pushButton_DetectorsSum

        # Energy calibration
        self.Calib                      = None
        self.Sigma                      = None

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
        self.ExceptionsPath             = self.lineEdit_ExceptionsPath
        self.Paths                      = self.listWidget_Paths

        self.toolButton_ExperimentPathSearch.clicked.connect(self.ExperimentPathSearch_clicked)
        self.toolButton_ExceptionsPathSearch.clicked.connect(self.ExceptionsPathSearch_clicked)

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
        return

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
        return
    
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
    
    def ExperimentPathSearch_clicked(self):
        return
    
    def ExceptionsPathSearch_clicked(self):
        return
    
    def ResultsPathSearch_clicked(self):
        return
    
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