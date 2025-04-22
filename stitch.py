from PyQt6 import QtWidgets, QtGui, QtCore, uic
import sys, matplotlib, numpy, pathlib, os, scipy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
matplotlib.use('QtAgg')

import main, PDA

class MatData():
    def __init__(self, path, parent = None):
        self.Path = path
        self.NumberOfFiles = len([name for name in path.iterdir() if (name.is_file() and name.suffix == ".mat" and name.stem[:5] != "PolyX")]) - 1 # 1 header + 2 snapshoty
        self.Data = []
        if self.NumberOfFiles > 0:
            for i in range(0, self.NumberOfFiles):
                self.Data.append(scipy.io.loadmat(f"{path.as_posix()}/{path.stem}_{i+1:04}.mat"))
        self.Head = scipy.io.loadmat(f"{path.as_posix()}/{path.stem}_HEADER.mat")

class MatplotlibCanvas(FigureCanvasQTAgg):
    def __init__(self, parent = None):
        self.Figure = matplotlib.figure.Figure(layout = "compressed", dpi = 100)
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

        # Map
        self.Map                = self.widget_Map
        self.MapCanvas          = MatplotlibCanvas(self.Map)
        self.MapToolbar         = NavigationToolbar2QT(self.MapCanvas, self.Map)
        self.TopMap             = None
        self.BottomMap          = None
        
        self.MapCanvas.setStyleSheet("background-color:transparent;")
        topLayout = QtWidgets.QVBoxLayout()
        topLayout.addWidget(self.MapToolbar)
        topLayout.addWidget(self.MapCanvas)
        self.Map.setLayout(topLayout)

        # Maps paths and offsets
        self.TopMapSumSignal    = None
        self.TopMapPath         = self.lineEdit_TopMapPath
        self.TopMapOffset       = self.spinBox_TopMapOffset
        self.BottomMapSumSignal = None
        self.BottomMapPath      = self.lineEdit_BottomMapPath
        self.BottomMapOffset    = self.spinBox_BottomMapOffset

        self.TopMapPath.editingFinished.connect(lambda mode = "top": self.LoadMap(mode))
        self.toolButton_TopMapPathSearch.clicked.connect(self.TopMapPathSearch_clicked)
        self.TopMapOffset.valueChanged.connect(lambda value, mode = "top": self.ReloadMap(value, mode))
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
        canvas = self.MapCanvas
        if mode == "top":
            path = pathlib.Path(self.TopMapPath.text())
            offset = self.TopMapOffset
        elif mode == "bottom":
            path = pathlib.Path(self.BottomMapPath.text())
            offset = self.BottomMapOffset
        try:
            head, Data, ICR, OCR, RT, LT, DT, PIN, I0, RC, ROI = PDA.data_load(path)
        except:
            if path == "":
                QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map from empty path.")
            else:
                QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map from path:\n{path}")
        else:
            if mode == "top":
                self.TopMap = MatData(path)
                sumSignal = numpy.sum(Data[2], axis=2)
                offset.setMaximum(Data[2].shape[1] - 1)
                printBottom = False if self.BottomMapSumSignal is None else True
                canvas.Axes.cla()
                imgTop = canvas.Axes.imshow(sumSignal.transpose(), extent = [-0.5, sumSignal.shape[0] - 0.5, -0.5, sumSignal.shape[1] - 0.5], origin = 'upper', cmap = 'viridis', aspect = 'equal')
                if printBottom:
                    imgBottom = canvas.Axes.imshow(self.BottomMapSumSignal.transpose(), extent = [-0.5, self.BottomMapSumSignal.shape[0] - 0.5, -self.BottomMapSumSignal.shape[1] + 0.5, -0.5], origin = 'upper', cmap = 'viridis', aspect = 'equal')
                    canvas.Axes.set_xlim([0, max(sumSignal.shape[0], self.BottomMapSumSignal.shape[0])])
                    canvas.Axes.set_ylim([-self.BottomMapSumSignal.shape[1], sumSignal.shape[1]])
                    imgBottom.set_clim([max(numpy.min(sumSignal), numpy.min(self.BottomMapSumSignal)), min(numpy.max(sumSignal), numpy.max(self.BottomMapSumSignal))])
                    imgTop.set_clim([max(numpy.min(sumSignal), numpy.min(self.BottomMapSumSignal)), min(numpy.max(sumSignal), numpy.max(self.BottomMapSumSignal))])
                self.TopMapSumSignal = sumSignal
                self.TopMapOffset.setValue(0)
                if not self.TopMapOffset.isEnabled(): self.TopMapOffset.setEnabled(True)
            elif mode == "bottom":
                self.BottomMap = MatData(path)
                sumSignal = numpy.sum(Data[2], axis=2)
                offset.setMaximum(Data[2].shape[1] - 1)
                printTop = False if self.TopMapSumSignal is None else True
                canvas.Axes.cla()
                imgBottom = canvas.Axes.imshow(sumSignal.transpose(), extent = [-0.5, sumSignal.shape[0] - 0.5, -sumSignal.shape[1] + 0.5, 0.5], origin = 'upper', cmap = 'viridis', aspect = 'equal')
                if printTop:
                    imgTop = canvas.Axes.imshow(self.TopMapSumSignal.transpose(), extent = [-0.5, self.TopMapSumSignal.shape[0] - 0.5, -0.5, self.TopMapSumSignal.shape[1] - 0.5], origin = 'upper', cmap = 'viridis', aspect = 'equal')
                    canvas.Axes.set_xlim([0, max(sumSignal.shape[0], self.TopMapSumSignal.shape[0])])
                    canvas.Axes.set_ylim([-sumSignal.shape[1], self.TopMapSumSignal.shape[1]])
                    imgTop.set_clim([max(numpy.min(sumSignal), numpy.min(self.TopMapSumSignal)), min(numpy.max(sumSignal), numpy.max(self.TopMapSumSignal))])
                    imgBottom.set_clim([max(numpy.min(sumSignal), numpy.min(self.TopMapSumSignal)), min(numpy.max(sumSignal), numpy.max(self.TopMapSumSignal))])
                self.BottomMapSumSignal = sumSignal
                self.BottomMapOffset.setValue(0)
                if not self.BottomMapOffset.isEnabled(): self.BottomMapOffset.setEnabled(True)
            canvas.Axes.format_coord = lambda x, y: f'x = {round(x)} px, z = {round(y)} px'
            canvas.draw()
        if not self.StitchMaps.isEnabled(): self.StitchMaps.setEnabled(True)
        QtGui.QGuiApplication.restoreOverrideCursor()

    def ReloadMap(self, value, mode):
        canvas = self.MapCanvas
        if mode == "top":
            sumSignal = self.TopMapSumSignal
            printBottom = False if self.BottomMapSumSignal is None else True
            canvas.Axes.cla()
            if value:
                imgTop = canvas.Axes.imshow(sumSignal[:, :-value].transpose(), extent = [-0.5, sumSignal[:, :-value].shape[0] - 0.5, -0.5, sumSignal[:, :-value].shape[1] - 0.5], origin = 'upper', cmap = 'viridis', aspect = 'equal')
            else:
                imgTop = canvas.Axes.imshow(sumSignal.transpose(), extent = [-0.5, sumSignal.shape[0] - 0.5, -0.5, sumSignal.shape[1] - 0.5], origin = 'upper', cmap = 'viridis', aspect = 'equal')
            if printBottom:
                if self.BottomMapOffset.value():
                    imgBottom = canvas.Axes.imshow(self.BottomMapSumSignal[:, self.BottomMapOffset.value():].transpose(), extent = [-0.5, self.BottomMapSumSignal[:, self.BottomMapOffset.value():].shape[0] - 0.5, -self.BottomMapSumSignal[:, self.BottomMapOffset.value():].shape[1] + 0.5, -0.5], origin = 'upper', cmap = 'viridis', aspect = 'equal')
                else:
                    imgBottom = canvas.Axes.imshow(self.BottomMapSumSignal.transpose(), extent = [-0.5, self.BottomMapSumSignal.shape[0] - 0.5, -self.BottomMapSumSignal.shape[1] + 0.5, -0.5], origin = 'upper', cmap = 'viridis', aspect = 'equal')
                if value:
                    canvas.Axes.set_xlim([0, max(sumSignal[:, :-value].shape[0], self.BottomMapSumSignal.shape[0])])
                    canvas.Axes.set_ylim([-self.BottomMapSumSignal[:, self.BottomMapOffset.value():].shape[1] if self.BottomMapOffset.value() else -self.BottomMapSumSignal.shape[1], sumSignal[:, :-value].shape[1]])
                    imgBottom.set_clim([max(numpy.min(sumSignal[:, :-value]), numpy.min(self.BottomMapSumSignal)), min(numpy.max(sumSignal[:, :-value]), numpy.max(self.BottomMapSumSignal))])
                    imgTop.set_clim([max(numpy.min(sumSignal[:, :-value]), numpy.min(self.BottomMapSumSignal)), min(numpy.max(sumSignal[:, :-value]), numpy.max(self.BottomMapSumSignal))])
                else:
                    canvas.Axes.set_xlim([0, max(sumSignal.shape[0], self.BottomMapSumSignal.shape[0])])
                    canvas.Axes.set_ylim([-self.BottomMapSumSignal[:, self.BottomMapOffset.value():].shape[1] if self.BottomMapOffset.value() else -self.BottomMapSumSignal.shape[1], sumSignal.shape[1]])
                    imgBottom.set_clim([max(numpy.min(sumSignal), numpy.min(self.BottomMapSumSignal)), min(numpy.max(sumSignal), numpy.max(self.BottomMapSumSignal))])
                    imgTop.set_clim([max(numpy.min(sumSignal), numpy.min(self.BottomMapSumSignal)), min(numpy.max(sumSignal), numpy.max(self.BottomMapSumSignal))])
        elif mode == "bottom":
            sumSignal = self.BottomMapSumSignal
            printTop = False if self.TopMapSumSignal is None else True
            canvas.Axes.cla()
            imgBottom = canvas.Axes.imshow(sumSignal[:, value:].transpose(), extent = [-0.5, sumSignal[:, value:].shape[0] - 0.5, -sumSignal[:, value:].shape[1] + 0.5, 0.5], origin = 'upper', cmap = 'viridis', aspect = 'equal')
            if printTop:
                if self.TopMapOffset.value():
                    imgTop = canvas.Axes.imshow(self.TopMapSumSignal[:, :-self.TopMapOffset.value()].transpose(), extent = [-0.5, self.TopMapSumSignal[:, :-self.TopMapOffset.value()].shape[0] - 0.5, -0.5, self.TopMapSumSignal[:, :-self.TopMapOffset.value()].shape[1] - 0.5], origin = 'upper', cmap = 'viridis', aspect = 'equal')
                else:    
                    imgTop = canvas.Axes.imshow(self.TopMapSumSignal.transpose(), extent = [-0.5, self.TopMapSumSignal.shape[0] - 0.5, -0.5, self.TopMapSumSignal.shape[1] - 0.5], origin = 'upper', cmap = 'viridis', aspect = 'equal')
                canvas.Axes.set_xlim([0, max(sumSignal[:, value:].shape[0], self.TopMapSumSignal.shape[0])])
                canvas.Axes.set_ylim([-sumSignal[:, value:].shape[1], self.TopMapSumSignal[:, :-self.TopMapOffset.value()].shape[1] if self.TopMapOffset.value() else self.TopMapSumSignal.shape[1]])
                imgTop.set_clim([max(numpy.min(sumSignal[:, value:]), numpy.min(self.TopMapSumSignal)), min(numpy.max(sumSignal[:, value:]), numpy.max(self.TopMapSumSignal))])
                imgBottom.set_clim([max(numpy.min(sumSignal[:, value:]), numpy.min(self.TopMapSumSignal)), min(numpy.max(sumSignal[:, value:]), numpy.max(self.TopMapSumSignal))])
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
        resultPath = pathlib.Path(self.ResultPath.text())
        if not resultPath.is_dir():
            if resultPath == pathlib.Path():
                QtWidgets.QMessageBox.warning(self, "Stitch", f"It is impossible to save output files on an empty path.")
            else:
                QtWidgets.QMessageBox.warning(self, "Stitch", f"It is impossible to save output files on the path:\n{resultPath}")
        else:
            QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
            if self.TopMap is not None and self.BottomMap is not None and self.TopMap.Head["XscanPulses"] != self.BottomMap.Head["XscanPulses"]:
                QtWidgets.QMessageBox.warning(self, "Stitch", f'It is impossible to stitch maps of various X dimensions ({self.TopMap.Head["XscanPulses"][0][0]} vs {self.BottomMap.Head["XscanPulses"][0][0]}).')
            elif self.TopMap is not None and self.BottomMap is None:
                dataName = resultPath.stem
                self.TopMap = MatData(pathlib.Path(self.TopMapPath.text()))
                head = self.TopMap.Head.copy()
                head["Zendpos"] = head["Zpositions"][0, self.TopMap.NumberOfFiles - self.TopMapOffset.value() - 1]
                head["Znpoints"] = self.TopMap.NumberOfFiles - self.TopMapOffset.value()
                head["Zpositions"] = head["Zpositions"][0, :self.TopMap.NumberOfFiles - self.TopMapOffset.value()]
                scipy.io.savemat(f"{resultPath}/{dataName}_HEADER.mat", head)
                for i in range(self.TopMap.NumberOfFiles - self.TopMapOffset.value()):
                    scipy.io.savemat(f"{resultPath}/{dataName}_{i+1:04}.mat", self.TopMap.Data[i])
            elif self.BottomMap is not None and self.TopMap is None:
                dataName = resultPath.stem
                self.BottomMap = MatData(pathlib.Path(self.BottomMapPath.text())) # why do I have to do this?!
                head = self.BottomMap.Head.copy()
                head["Zstartpos"] = head["Zpositions"][0, self.BottomMapOffset.value()]
                head["Znpoints"] = self.BottomMap.NumberOfFiles - self.BottomMapOffset.value()
                head["Zpositions"] = head["Zpositions"][0, self.BottomMapOffset.value():]
                scipy.io.savemat(f"{resultPath}/{dataName}_HEADER.mat", head)
                for i in range(self.BottomMapOffset.value(), self.BottomMap.NumberOfFiles):
                    data = self.BottomMap.Data[i].copy()
                    if self.BottomMapOffset.value() % 2 == 1:
                        data["dane1line"][0, :, :]  = data["dane1line"][0, :, :][::-1]
                        data["dane1line"][1, :, :]  = data["dane1line"][1, :, :][::-1]
                        data["stats1line"][0, :, 2] = data["stats1line"][0, :, 2][::-1]
                        data["stats1line"][1, :, 2] = data["stats1line"][1, :, 2][::-1]
                        data["stats1line"][0, :, 3] = data["stats1line"][0, :, 3][::-1]
                        data["stats1line"][1, :, 3] = data["stats1line"][1, :, 3][::-1]
                        data["stats1line"][0, :, 0] = data["stats1line"][0, :, 0][::-1]
                        data["stats1line"][1, :, 0] = data["stats1line"][1, :, 0][::-1]
                        data["stats1line"][0, :, 1] = data["stats1line"][0, :, 1][::-1]
                        data["stats1line"][1, :, 1] = data["stats1line"][1, :, 1][::-1]
                        data["PIN_map"][i, :]       = data["PIN_map"][i, :][::-1]
                        data["I0_map"][i, :]        = data["I0_map"][i, :][::-1]
                    scipy.io.savemat(f"{resultPath}/{dataName}_{i-self.BottomMapOffset.value()+1:04}.mat", data)
            else:
                print(resultPath)
            QtGui.QGuiApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.information(self, "Stitch", f"Stitching completed!")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())