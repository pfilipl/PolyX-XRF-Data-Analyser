from PyQt6 import QtWidgets, uic
import sys

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

        self.pushButton_ROIsImport.clicked.connect(self.ROIsImport_clicked)
        self.pushButton_ROIsAdd.clicked.connect(self.ROIsAdd_clicked)
        self.pushButton_ROIsSave.clicked.connect(self.ROIsSave_clicked)
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
        self.DetectorsML        = self.pushButton_DetectorsML
        self.DetectorsBe        = self.pushButton_DetectorsBe
        self.DetectorsSum       = self.pushButton_DetectorsSum

        # Energy calibration
        self.Calib              = None
        self.Sigma              = None

        # Process
        self.Progress           = self.progressBar_Progress
        self.ReloadMap          = self.pushButton_ReloadMap
        self.AnalyseMap         = self.pushButton_AnalyseMap

        self.pushButton_ReloadMap.clicked.connect(self.ReloadMap_clicked)
        self.pushButton_ImportConfig.clicked.connect(self.ImportConfig_clicked)
        self.pushButton_SaveConfig.clicked.connect(self.SaveConfig_clicked)
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
    
    def MapPathSearch_clicked(self):
        return
    
    def ResultsPathSearch_clicked(self):
        return
    
    def ReloadMap_clicked(self):
        return
    
    def ImportConfig_clicked(self):
        return
    
    def SaveConfig_clicked(self):
        return
    
    def AnalyseMap_clicked(self):
        return
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())