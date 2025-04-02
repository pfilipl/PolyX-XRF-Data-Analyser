from PyQt6 import QtWidgets, QtGui, QtCore, uic
import sys, matplotlib, numpy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
matplotlib.use('QtAgg')

import main, PDA

class MatplotlibCanvas(FigureCanvasQTAgg):
    def __init__(self, parent = None):
        self.Figure = matplotlib.figure.Figure(layout = 'compressed', dpi = 100)
        self.Axes = self.Figure.add_subplot(facecolor = "None")
        self.Axes.get_xaxis().set_visible(False)
        self.Axes.get_yaxis().set_visible(False)
        self.Axes.format_coord = lambda x, y: ""
        self.Figure.patch.set_facecolor("None")
        super().__init__(self.Figure)

class StitchWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(StitchWindow, self).__init__(parent)
        uic.loadUi("stitch.ui", self)

        # Top map
        self.TopMap             = self.widget_TopMap
        self.TopMapCanvas       = MatplotlibCanvas(self.TopMap)
        self.TopMapToolbar      = NavigationToolbar2QT(self.TopMapCanvas, self.TopMap)
        self.TopMapSumSignal    = None
        self.TopMapPath         = self.lineEdit_TopMapPath
        self.TopMapOffset       = self.spinBox_TopMapOffset

        self.TopMapCanvas.setStyleSheet("background-color:transparent;")
        topLayout = QtWidgets.QVBoxLayout()
        topLayout.addWidget(self.TopMapToolbar)
        topLayout.addWidget(self.TopMapCanvas)
        self.TopMap.setLayout(topLayout)

        self.TopMapPath.editingFinished.connect(lambda mode = "top": self.LoadMap(mode))
        self.toolButton_TopMapPathSearch.clicked.connect(self.TopMapPathSearch_clicked)
        self.TopMapOffset.valueChanged.connect(lambda value, mode = "top": self.ReloadMap(value, mode))
        
        # Bottom map
        self.BottomMap          = self.widget_BottomMap
        self.BottomMapCanvas    = MatplotlibCanvas(self.BottomMap)
        self.BottomMapToolbar   = NavigationToolbar2QT(self.BottomMapCanvas, self.BottomMap)
        self.BottomMapSumSignal = None
        self.BottomMapPath      = self.lineEdit_BottomMapPath
        self.BottomMapOffset    = self.spinBox_BottomMapOffset

        self.BottomMapCanvas.setStyleSheet("background-color:transparent;")
        bottomLayout = QtWidgets.QVBoxLayout()
        bottomLayout.addWidget(self.BottomMapCanvas)
        bottomLayout.addWidget(self.BottomMapToolbar)
        self.BottomMap.setLayout(bottomLayout)

        self.BottomMapPath.editingFinished.connect(lambda mode = "bottom": self.LoadMap(mode))
        self.toolButton_BottomMapPathSearch.clicked.connect(self.BottomMapPathSearch_clicked)
        self.BottomMapOffset.valueChanged.connect(lambda value, mode = "bottom": self.ReloadMap(value, mode))

        # Results
        self.ResultPath         = self.lineEdit_ResultPath

        self.toolButton_ResultPathSearch.clicked.connect(self.ResultPathSearch_clicked)

        # Process
        self.StitchMaps         = self.pushButton_StitchMaps

        self.pushButton_StitchMaps.clicked.connect(self.StitchMaps_clicked)

        # Help
        self.Help               = self.label_Help
        self.HelpDescription    = self.label_HelpDescription
        
        self.Help.hide()
        self.HelpDescription.hide()

    def LoadMap(self, mode):
        QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        if mode == "top":
            canvas = self.TopMapCanvas
            path = self.TopMapPath.text()
            offset = self.TopMapOffset
        elif mode == "bottom":
            canvas = self.BottomMapCanvas
            path = self.BottomMapPath.text()
            offset = self.BottomMapOffset

        try:
            head, Data, ICR, OCR, RT, LT, DT, PIN, I0, RC, ROI = PDA.data_load(path)
        except:
            if path == "":
                QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map under the empty path.")
            else:
                QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map under the path:\n{path}")
        else:
            sumSignal = numpy.sum(Data[2], axis=2)
            canvas.Axes.cla()
            canvas.Axes.imshow(sumSignal.transpose(), origin = 'upper', cmap = 'viridis', aspect = 'equal')
            canvas.Axes.format_coord = lambda x, y: f'x = {round(x)} px, z = {round(y)} px'
            canvas.draw()

            offset.setMaximum(Data[2].shape[1] - 1)

            if mode == "top":
                self.TopMapSumSignal = sumSignal
                if not self.TopMapOffset.isEnabled(): self.TopMapOffset.setEnabled(True)
            elif mode == "bottom":
                self.BottomMapSumSignal = sumSignal
                if not self.BottomMapOffset.isEnabled(): self.BottomMapOffset.setEnabled(True)

        QtGui.QGuiApplication.restoreOverrideCursor()

    def ReloadMap(self, value, mode):
        if mode == "top":
            canvas = self.TopMapCanvas
            sumSignal = self.TopMapSumSignal
            canvas.Axes.cla()
            if value:
                canvas.Axes.imshow(sumSignal[:, :-value].transpose(), origin = 'upper', cmap = 'viridis', aspect = 'equal')
            else:
                canvas.Axes.imshow(sumSignal.transpose(), origin = 'upper', cmap = 'viridis', aspect = 'equal')
        elif mode == "bottom":
            canvas = self.BottomMapCanvas
            sumSignal = self.BottomMapSumSignal
            canvas.Axes.cla()
            canvas.Axes.imshow(sumSignal[:, value:].transpose(), origin = 'upper', cmap = 'viridis', aspect = 'equal')
        canvas.draw()

    def TopMapPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Top Map path", self.TopMapPath.text())
        if path:
            self.TopMapPath.blockSignals(True)
            self.TopMapPath.setText(path)
            self.TopMapPath.blockSignals(False)
            self.LoadMap("top")

    def BottomMapPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Bottom Map path", self.BottomMapPath.text())
        if path:
            self.BottomMapPath.blockSignals(True)
            self.BottomMapPath.setText(path)
            self.BottomMapPath.blockSignals(False)
            self.LoadMap("bottom")
    
    def ResultPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Result path", self.ResultPath.text())
        if path:
            self.ResultPath.setText(path)
    
    def StitchMaps_clicked(self):
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())