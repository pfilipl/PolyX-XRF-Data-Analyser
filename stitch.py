from PyQt6 import QtWidgets, uic
import sys

import main

class StitchWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(StitchWindow, self).__init__(parent)
        uic.loadUi("stitch.ui", self)

        # Top map
        self.TopMap             = self.widget_TopMap
        self.TopMapPath         = self.lineEdit_TopMapPath.text
        self.TopMapOffset       = self.spinBox_TopMapOffset.value()

        self.toolButton_TopMapPathSearch.clicked.connect(self.TopMapPathSearch_clicked)
        
        # Bottom map
        self.BottomMap          = self.widget_BottomMap
        self.BottomMapPath      = self.lineEdit_BottomMapPath.text
        self.BottomMapOffset    = self.spinBox_BottomMapOffset.value()

        self.toolButton_BottomMapPathSearch.clicked.connect(self.BottomMapPathSearch_clicked)

        # Results
        self.ResultPath         = self.lineEdit_ResultPath.text

        self.toolButton_ResultPathSearch.clicked.connect(self.ResultPathSearch_clicked)

        # Process
        self.StitchMaps         = self.pushButton_StitchMaps

        self.pushButton_StitchMaps.clicked.connect(self.StitchMaps_clicked)

        # Help
        self.Help               = self.label_Help
        self.HelpDescription    = self.label_HelpDescription
        
        self.Help.hide()
        self.HelpDescription.hide()

    def TopMapPathSearch_clicked(self):
        return

    def BottomMapPathSearch_clicked(self):
        return
    
    def ResultPathSearch_clicked(self):
        return
    
    def StitchMaps_clicked(self):
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())