from PyQt6 import QtWidgets, uic
import sys

import main, add_roi

class SingleWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(SingleWindow, self).__init__(parent)
        uic.loadUi("single.ui", self)

        # Spectrum from map region
        self.AreaX1 = self.doubleSpinBox_AreaX1.value()
        self.AreaZ1 = self.doubleSpinBox_AreaZ1.value()
        self.AreaX2 = self.doubleSpinBox_AreaX2.value()
        self.AreaZ2 = self.doubleSpinBox_AreaZ2.value()
        self.PointX = self.doubleSpinBox_PointX.value()
        self.PointZ = self.doubleSpinBox_PointZ.value()
        self.pushButton_MarkPoint.clicked.connect(self.MarkPoint_clicked)
        self.pushButton_SelectArea.clicked.connect(self.SelectArea_clicked)

        # Regions of interest (ROIs)
        self.ROIs = self.tableWidget_ROIs
        self.ROIsDefault = self.pushButton_ROIsDefault.isChecked()
        self.pushButton_ROIsImport.clicked.connect(self.ROIsImport_clicked)
        self.pushButton_ROIsAdd.clicked.connect(self.ROIsAdd_clicked)
        self.pushButton_ROIsSave.clicked.connect(self.ROIsSave_clicked)
        self.pushButton_ROIsDelete.clicked.connect(self.ROIsDelete_clicked)
        self.pushButton_ROIsDeleteAll.clicked.connect(self.ROIsDeleteAll_clicked)

        # Configuration Panel (on the right side)
        self.MapPath = self.lineEdit_MapPath.text
        self.toolButton_MapPathSearch.clicked.connect(self.MapPathSearch_clicked)
        self.ResultsPath = self.lineEdit_ResultsPath.text
        self.toolButton_ResultsPathSearch.clicked.connect(self.ResultsPathSearch_clicked)
        self.DetectorsBe = self.pushButton_DetectorsBe.isChecked()
        self.DetectorsML = self.pushButton_DetectorsML.isChecked()
        self.DetectorsSum = self.pushButton_DetectorsSum.isChecked()
        self.CalibrationGain = self.doubleSpinBox_CalibrationGain.value()
        self.CalibrationZero = self.doubleSpinBox_CalibrationZero.value()
        self.CalibrationNoise = self.doubleSpinBox_CalibrationNoise.value()
        self.CalibrationFano = self.doubleSpinBox_CalibrationFano.value()
        self.Progress = self.progressBar_Progress
        self.pushButton_ReloadMap.clicked.connect(self.ReloadMap_clicked)
        self.AnalyseMap = self.pushButton_AnalyseMap
        self.pushButton_AnalyseMap.clicked.connect(self.AnalyseMap_clicked)

        # Help section
        self.Help = self.label_Help
        self.Help.hide()
        self.HelpDescription = self.label_HelpDescription
        self.HelpDescription.hide()

    def MarkPoint_clicked(self):
        return

    def SelectArea_clicked(self):
        return

    def ROIsImport_clicked(self):
        return

    def ROIsAdd_clicked(self):
        addroi = add_roi.AddRoi(self)
        addroi.exec()
        
    def ROIsSave_clicked(self):
        return
    
    def ROIsDelete_clicked(self):
        return
    
    def ROIsDeleteAll_clicked(self):
        return
    
    def MapPathSearch_clicked(self):
        return
    
    def ResultsPathSearch_clicked(self):
        return
    
    def ReloadMap_clicked(self):
        return
    
    def AnalyseMap_clicked(self):
        return
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())