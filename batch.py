from PyQt6 import QtWidgets, uic
import sys

import main, add_roi

class BatchWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(BatchWindow, self).__init__(parent)
        uic.loadUi("batch.ui", self)

        # Detectors
        self.DetectorsML                = self.pushButton_DetectorsML.isChecked()
        self.DetectorsBe                = self.pushButton_DetectorsBe.isChecked()
        self.DetectorsSum               = self.pushButton_DetectorsSum.isChecked()

        # Energy calibration
        self.Calib                      = None
        self.Sigma                      = None

        # Maps configuration
        self.MapConfigValuesAuto        = self.pushButton_MapsConfigValuesAuto.isChecked()
        self.MapConfigValuesStart       = self.doubleSpinBox_MapsConfigValuesStart.value()
        self.MapConfigValuesStop        = self.doubleSpinBox_MapsConfigValuesStop.value()
        self.MapConfigAspectAuto        = self.pushButton_MapsConfigAspectAuto.isChecked()
        self.MapConfigAspectValue       = self.doubleSpinBox_MapsConfigAspectValue.value()
        self.MapConfigColormapDefault   = self.pushButton_MapsConfigColormapDefault.isChecked()
        self.MapConfigColormapValue     = self.lineEdit_MapsConfigColormapValue.text

        self.toolButton_MapsConfigColormapSearch.clicked.connect(self.MapsConfigColormapSearch_clicked)
        
        # Spectra configuration
        self.SpectraConfigEnergyAuto    = self.pushButton_SpectraConfigEnergyAuto.isChecked()
        self.SpectraConfigEnergyStart   = self.doubleSpinBox_SpectraConfigEnergyStart.value()
        self.SpectraConfigEnergyStop    = self.doubleSpinBox_SpectraConfigEnergyStop.value()
        self.SpectraConfigAspectAuto    = self.pushButton_SpectraConfigAspectAuto.isChecked()
        self.SpectraConfigAspectValue   = self.doubleSpinBox_SpectraConfigAspectValue.value()

        # Regions of interest (ROIs)
        self.ROIs                       = self.tableWidget_ROIs
        self.ROIsDefault                = self.pushButton_ROIsDefault.isChecked()

        self.pushButton_ROIsImport.clicked.connect(self.ROIsImport_clicked)
        self.pushButton_ROIsAdd.clicked.connect(self.ROIsAdd_clicked)
        self.pushButton_ROIsSave.clicked.connect(self.ROIsSave_clicked)
        self.pushButton_ROIsDelete.clicked.connect(self.ROIsDelete_clicked)
        self.pushButton_ROIsDeleteAll.clicked.connect(self.ROIsDeleteAll_clicked)

        # Experiment / Load
        self.ExperimentPath             = self.lineEdit_ExperimentPath.text
        self.ExceptionsPath             = self.lineEdit_ExceptionsPath.text
        self.Paths                      = self.listWidget_Paths

        self.toolButton_ExperimentPathSearch.clicked.connect(self.ExperimentPathSearch_clicked)
        self.toolButton_ExceptionsPathSearch.clicked.connect(self.ExceptionsPathSearch_clicked)

        # Results
        self.ResultsPath                = self.lineEdit_ResultsPath.text
        self.ResultsNested              = self.checkBox_ResultsNested.isChecked()

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
        addroi = add_roi.AddRoi(self, self.Calib, self.Sigma)
        addroi.exec()
        
    def ROIsSave_clicked(self):
        return
    
    def ROIsDelete_clicked(self):
        return
    
    def ROIsDeleteAll_clicked(self):
        return
    
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