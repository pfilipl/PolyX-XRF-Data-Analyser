from PyQt6 import QtWidgets, QtGui, QtCore, uic
import sys, xraylib, matplotlib, time, pathlib, numpy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
matplotlib.use('QtAgg')

import main, add_roi, PDA, analyse, load_plots

class MatplotlibCanvas(FigureCanvasQTAgg):
    def __init__(self, parent = None):
        self.Figure = matplotlib.figure.Figure(layout = 'compressed', dpi = 100)
        self.Axes = self.Figure.add_subplot(facecolor = "None")
        self.Axes.get_xaxis().set_visible(False)
        self.Axes.get_yaxis().set_visible(False)
        self.Axes.format_coord = lambda x, y: ""
        self.Figure.patch.set_facecolor("None")
        self.Axes2x = None
        self.Axes2y = None
        self.ColorBar = None
        super().__init__(self.Figure)

class PreviewTab(QtWidgets.QWidget):
    def __init__(self, parent = None, roiStart = 1, roiStop = 4096):
        super(PreviewTab, self).__init__(parent)
        self.Canvas = MatplotlibCanvas(self)
        self.Toolbar = NavigationToolbar2QT(self.Canvas, self)
        self.Canvas.setStyleSheet("background-color:transparent;")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.Canvas)
        layout.addWidget(self.Toolbar)
        self.setLayout(layout)
        self.RoiStart = roiStart
        self.RoiStop = roiStop

class SingleWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(SingleWindow, self).__init__(parent)
        uic.loadUi("single.ui", self)

        # Spectrum from map region
        self.MarkPoint          = self.pushButton_MarkPoint
        self.PointX             = self.doubleSpinBox_PointX
        self.PointZ             = self.doubleSpinBox_PointZ
        self.PointEnabled       = False
        self.PointChanged       = False
        
        self.SelectArea         = self.pushButton_SelectArea
        self.AreaX1             = self.doubleSpinBox_AreaX1
        self.AreaZ1             = self.doubleSpinBox_AreaZ1
        self.AreaX2             = self.doubleSpinBox_AreaX2
        self.AreaZ2             = self.doubleSpinBox_AreaZ2
        self.AreaEnabled        = False
        self.AreaChanged        = False
        
        self.LastChanged        = "Area"

        self.PointX.valueChanged.connect(lambda value, mode = "Point": self.RegionChanged(value, mode))
        self.PointZ.valueChanged.connect(lambda value, mode = "Point": self.RegionChanged(value, mode))
        self.AreaX1.valueChanged.connect(lambda value, mode = "Area": self.RegionChanged(value, mode))
        self.AreaZ1.valueChanged.connect(lambda value, mode = "Area": self.RegionChanged(value, mode))
        self.AreaX2.valueChanged.connect(lambda value, mode = "Area": self.RegionChanged(value, mode))
        self.AreaZ2.valueChanged.connect(lambda value, mode = "Area": self.RegionChanged(value, mode))

        self.MarkPoint.toggled.connect(self.MarkPoint_toggled)
        self.SelectArea.toggled.connect(self.SelectArea_toggled)

        # Regions of interest (ROIs)
        self.ROIs               = self.tableWidget_ROIs
        self.ROIsDefault        = self.pushButton_ROIsDefault
        self.RoiCount           = 0

        self.pushButton_ROIsImport.clicked.connect(lambda checked, fileName = None: self.ROIsImport_clicked(checked, fileName))
        self.pushButton_ROIsAdd.clicked.connect(self.ROIsAdd_clicked)
        self.pushButton_ROIsSave.clicked.connect(lambda checked, fileName = None, mode = 'w': self.ROIsSave_clicked(checked, fileName, mode))
        self.pushButton_ROIsDelete.clicked.connect(self.ROIsDelete_clicked)
        self.pushButton_ROIsDeleteAll.clicked.connect(self.ROIsDeleteAll_clicked)

        # Tabs
        self.TotalSignal        = self.tab_TotalSignal
        self.SumSpectrum        = self.tab_SumSpectrum
        self.MaxSpectrum        = self.tab_MaxSpectrum
        self.I0                 = self.tab_I0
        self.PIN                = self.tab_PIN
        self.DT                 = self.tab_DT
        self.RC                 = self.tab_RC

        self.Data               = None
        self.LastPressedX       = None
        self.LastPressedZ       = None
        self.LastReleasedX      = None
        self.LastReleasedZ      = None
        self.LastMotionX        = None
        self.LastMotionZ        = None
        self.Rectangle          = matplotlib.patches.Rectangle((0, 0), 0, 0, linewidth = 1, linestyle = '-', edgecolor = 'k')

        self.TotalSignal.Canvas.mpl_connect("button_press_event", lambda event, canvas = self.TotalSignal.Canvas: self.MatplotlibButtonPressed(event, canvas))
        self.TotalSignal.Canvas.mpl_connect("button_release_event", lambda event, canvas = self.TotalSignal.Canvas: self.MatplotlibButtonReleased(event, canvas))
        self.TotalSignal.Canvas.mpl_connect("motion_notify_event", lambda event, canvas = self.TotalSignal.Canvas: self.MatplotlibMouseMotion(event, canvas))

        # Map path
        self.MapPath            = self.lineEdit_MapPath

        self.MapPath.editingFinished.connect(self.LoadData)
        self.toolButton_MapPathSearch.clicked.connect(self.MapPathSearch_clicked)

        # Results
        self.ResultsPath        = self.lineEdit_ResultsPath

        self.toolButton_ResultsPathSearch.clicked.connect(self.ResultsPathSearch_clicked)

        # Detectors
        self.DetectorsBe        = self.pushButton_DetectorsBe
        self.DetectorsML        = self.pushButton_DetectorsML
        self.DetectorsSum       = self.pushButton_DetectorsSum
        self.LastDetector       = None
        self.CurrentDetector    = None

        self.DetectorsBe.clicked.connect(lambda checked, mode = "Be": self.DetectorChanged(checked, mode))
        self.DetectorsML.clicked.connect(lambda checked, mode = "ML": self.DetectorChanged(checked, mode))
        self.DetectorsSum.clicked.connect(lambda checked, mode = "Sum": self.DetectorChanged(checked, mode))

        # Energy calibration
        self.Calib              = None
        self.Sigma              = None
        self.monoE              = None

        self.CalibrationGain    = self.doubleSpinBox_CalibrationGain
        self.CalibrationZero    = self.doubleSpinBox_CalibrationZero
        self.CalibrationNoise   = self.doubleSpinBox_CalibrationNoise
        self.CalibrationFano    = self.doubleSpinBox_CalibrationFano

        # Process
        self.Progress           = self.progressBar_Progress
        self.Reload             = self.pushButton_Reload
        self.Analyse            = self.pushButton_Analyse
        self.OutputConfig       = None

        self.Reload.clicked.connect(self.Reload_clicked)
        self.pushButton_ImportConfig.clicked.connect(lambda clicked, fileName = None: self.ImportConfig_clicked(clicked, fileName))
        self.pushButton_SaveConfig.clicked.connect(lambda clicked, fileName = None: self.SaveConfig_clicked(clicked, fileName))
        self.Analyse.clicked.connect(self.Analyse_clicked)

        # Help
        self.Help               = self.label_Help
        self.HelpDescription    = self.label_HelpDescription
        
        self.Help.hide()
        self.HelpDescription.hide()

    def setCalibration(self, calib, sigma):
        self.Calib = calib
        self.Sigma = sigma

    def MatplotlibButtonPressed(self, event, canvas):
        if self.MarkPoint.isChecked() or self.SelectArea.isChecked():
            if event.inaxes == canvas.Axes:
                self.LastPressedX = event.xdata
                self.LastPressedZ = event.ydata
                self.Rectangle.set_facecolor('k')
                self.Rectangle.set_xy((self.LastPressedX, self.LastPressedZ))
                self.Rectangle.set_height(0.25)
                self.Rectangle.set_width(0.25)
                canvas.Axes.add_patch(self.Rectangle)
                canvas.draw()
                self.MarkPoint.setChecked(False)

    def MatplotlibButtonReleased(self, event, canvas):
        if self.SelectArea.isChecked():
            if event.inaxes == canvas.Axes:
                self.LastReleasedX = event.xdata
                self.LastReleasedZ = event.ydata
            else:
                self.LastReleasedX = self.LastMotionX
                self.LastReleasedZ = self.LastMotionZ
                self.LastMotionX = None
                self.LastMotionZ = None
            self.SelectArea.setChecked(False)

    def MatplotlibMouseMotion(self, event, canvas):
        if self.SelectArea.isChecked() and self.LastPressedX is not None and self.LastPressedZ is not None:
            if event.inaxes == canvas.Axes:
                self.LastMotionX = event.xdata
                self.LastMotionZ = event.ydata
                self.Rectangle.set_facecolor('none')
                self.Rectangle.set_height(self.LastMotionZ - self.Rectangle.get_y())
                self.Rectangle.set_width(self.LastMotionX - self.Rectangle.get_x())
                canvas.draw()

    def RegionChanged(self, value, mode):
        exec(f"self.{mode}Changed = True")
        exec(f'self.LastChanged = "{mode}"')

    def DetectorChanged(self, checked, mode):
        if checked:
            self.CurrentDetector = mode
            if self.LastDetector is None:
                self.LastDetector = mode
            for detector in ["Be", "ML", "Sum"]:
                if detector != mode:
                    exec(f'if self.Detectors{detector}.isChecked(): self.LastDetector = "{detector}"')
                    exec(f"self.Detectors{detector}.blockSignals(True)")
                    exec(f"self.Detectors{detector}.setChecked(False)")
                    exec(f"self.Detectors{detector}.blockSignals(False)")
        else:
            if self.LastDetector != mode:
                self.CurrentDetector = self.LastDetector
                exec(f"self.Detectors{self.LastDetector}.blockSignals(True)")
                exec(f"self.Detectors{self.LastDetector}.setChecked(True)")
                exec(f"self.Detectors{self.LastDetector}.blockSignals(False)")
            else:
                self.LastDetector = None
                self.CurrentDetector = None

    def LoadData(self, startLoad = True, importLoad = False):
        QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        path = pathlib.Path(self.MapPath.text())
        try:
            head, Data, ICR, OCR, RT, LT, DT, PIN, I0, RC, ROI = PDA.data_load(path)
        except:
            if path == pathlib.Path():
                QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map from empty path.")
            else:
                QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map from path:\n{path}")
        else:
            self.Data = {"head" : head, "Data" : Data, "ICR" : ICR, "OCR" : OCR, "RT" : RT, "LT" : LT, "DT" : DT, "PIN" : PIN, "I0" : I0, "RC" : RC, "ROI" : ROI}

            try:
                self.monoE = head["monoE"][0][0]
            except:
                self.monoE = None

            if self.ROIsDefault.isChecked():
                self.ROIsDeleteAll_clicked()
                for roi in ROI:
                    self.ROIs.insertRow(self.ROIs.currentRow() + 1)
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 0, QtWidgets.QTableWidgetItem(f"{roi[0]}"))
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(f"{roi[1]}"))
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(f"{roi[2]}"))
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(f"{roi[3]}"))
                    self.ROIs.setCurrentCell(self.ROIs.currentRow() + 1, 0)
                    i = self.tabWidget.addTab(PreviewTab(self, int(roi[1]), int(roi[2])), roi[0])
                    self.tabWidget.widget(i).Canvas.mpl_connect("button_press_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibButtonPressed(event, canvas))
                    self.tabWidget.widget(i).Canvas.mpl_connect("button_release_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibButtonReleased(event, canvas))
                    self.tabWidget.widget(i).Canvas.mpl_connect("motion_notify_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibMouseMotion(event, canvas))

            if self.CurrentDetector == "Be": det = 0
            elif self.CurrentDetector == "ML": det = 1
            else: det = 2
            load_plots.MapData(self, self.TotalSignal, det, importLoad = importLoad)
            load_plots.Spectrum(self, self.SumSpectrum, numpy.sum, det, startLoad = startLoad, importLoad = importLoad)
            load_plots.Spectrum(self, self.MaxSpectrum, numpy.max, det, startLoad = startLoad, importLoad = importLoad, peaks = None)
            load_plots.MapStats2D(self, self.I0, "I0", det, "I0 [V]", importLoad = importLoad)
            load_plots.MapStats2D(self, self.PIN, "PIN", det, "I1/PIN [V]", importLoad = importLoad)
            load_plots.MapStats2D(self, self.DT, "DT", det, "DT [%]", importLoad = importLoad)
            load_plots.PlotStats1D(self, self.RC, "RC", "I [mA]", importLoad = importLoad)
            for i in range(7, self.tabWidget.count()):
                load_plots.MapData(self, self.tabWidget.widget(i), det, importLoad = importLoad)

            if not self.Reload.isEnabled(): self.Reload.setEnabled(True)
            if not self.Analyse.isEnabled(): self.Analyse.setEnabled(True)
            if not self.PointEnabled:
                self.PointX.setEnabled(True)
                self.PointZ.setEnabled(True)
                self.PointEnabled = True
            if not self.AreaEnabled:
                self.AreaX1.setEnabled(True)
                self.AreaZ1.setEnabled(True)
                self.AreaX2.setEnabled(True)
                self.AreaZ2.setEnabled(True)
                self.AreaEnabled = True
            if not self.pushButton_MarkPoint.isEnabled(): self.pushButton_MarkPoint.setEnabled(True)
            if not self.pushButton_SelectArea.isEnabled(): self.pushButton_SelectArea.setEnabled(True)

            self.PointX.blockSignals(True)
            self.PointZ.blockSignals(True)
            self.AreaX1.blockSignals(True)
            self.AreaX2.blockSignals(True)
            self.AreaZ1.blockSignals(True)
            self.AreaZ2.blockSignals(True)

            self.PointX.setMinimum(min(head["Xpositions"][0, :]))
            self.PointZ.setMinimum(min(head["Zpositions"][0, :]))
            self.PointX.setMaximum(max(head["Xpositions"][0, :]))
            self.PointZ.setMaximum(max(head["Zpositions"][0, :]))

            self.AreaX1.setMinimum(min(head["Xpositions"][0, :]))
            self.AreaX2.setMinimum(min(head["Xpositions"][0, :]))
            self.AreaZ1.setMinimum(min(head["Zpositions"][0, :]))
            self.AreaZ2.setMinimum(min(head["Zpositions"][0, :]))
            self.AreaX1.setMaximum(max(head["Xpositions"][0, :]))
            self.AreaX2.setMaximum(max(head["Xpositions"][0, :]))
            self.AreaZ1.setMaximum(max(head["Zpositions"][0, :]))
            self.AreaZ2.setMaximum(max(head["Zpositions"][0, :]))

            if startLoad or not self.PointChanged:
                self.PointX.setValue(min(head["Xpositions"][0, :]))
                self.PointZ.setValue(min(head["Zpositions"][0, :]))
                
            if startLoad or not self.AreaChanged:
                self.AreaX1.setValue(min(head["Xpositions"][0, :]))
                self.AreaX2.setValue(max(head["Xpositions"][0, :]))
                self.AreaZ1.setValue(min(head["Zpositions"][0, :]))
                self.AreaZ2.setValue(max(head["Zpositions"][0, :]))

            self.PointX.blockSignals(False)
            self.PointZ.blockSignals(False)
            self.AreaX1.blockSignals(False)
            self.AreaX2.blockSignals(False)
            self.AreaZ1.blockSignals(False)
            self.AreaZ2.blockSignals(False)

        QtGui.QGuiApplication.restoreOverrideCursor()

    def ReloadData(self):
        QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        head = self.Data["head"]
        if self.ROIsDefault.isChecked(): ROI = self.Data["ROI"]
        else:
            ROI = []
            for row in range(self.ROIs.rowCount()):
                ROI.append([self.ROIs.item(row, 0).text(), int(self.ROIs.item(row, 1).text()), int(self.ROIs.item(row, 2).text()), float(self.ROIs.item(row, 3).text())])
        if self.AreaChanged or self.PointChanged:
            if self.LastChanged == "Area":
                POS = PDA.real_pos([[self.AreaX1.value(), self.AreaZ1.value()], [self.AreaX2.value(), self.AreaZ2.value()]], head)
            elif self.LastChanged == "Point":
                POS = PDA.real_pos([[self.PointX.value(), self.PointZ.value()]], head)
        else:
            POS = [[0, 0], [1000, 1000]]
        
        if self.CurrentDetector == "Be": det = 0
        elif self.CurrentDetector == "ML": det = 1
        else: det = 2
        load_plots.MapData(self, self.TotalSignal, det, pos = POS)
        load_plots.Spectrum(self, self.SumSpectrum, numpy.sum, det, pos = POS, roi = ROI, startLoad = False)
        load_plots.Spectrum(self, self.MaxSpectrum, numpy.max, det, pos = POS, roi = ROI, startLoad = False, peaks = None)
        load_plots.MapStats2D(self, self.I0, "I0", det, "I0 [V]")
        load_plots.MapStats2D(self, self.PIN, "PIN", det, "I1/PIN [V]")
        load_plots.MapStats2D(self, self.DT, "DT", det, "DT [%]")
        # load_plots.PlotStats1D(self, self.RC, "RC")
        for i in range(7, self.tabWidget.count()):
            load_plots.MapData(self, self.tabWidget.widget(i), det, pos = POS)
        QtGui.QGuiApplication.restoreOverrideCursor()

    def MarkPoint_toggled(self, checked):
        head = self.Data["head"]
        # QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.TotalSignal.Canvas.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        if not checked:
            if self.LastPressedX is not None and self.LastPressedZ is not None:
                self.PointX.setValue(head["Xpositions"][0, round(self.LastPressedX)])
                self.PointZ.setValue(head["Zpositions"][0, round(self.LastPressedZ)])
                self.LastPressedX = None
                self.LastPressedZ = None
                # QtGui.QGuiApplication.restoreOverrideCursor()
                self.TotalSignal.Canvas.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        else:
            if self.SelectArea.isChecked(): 
                self.SelectArea.blockSignals(True)
                self.SelectArea.setChecked(False)
                self.SelectArea.blockSignals(False)

    def SelectArea_toggled(self, checked):
        head = self.Data["head"]
        # QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.TotalSignal.Canvas.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        if not checked:
            if self.LastPressedX is not None and self.LastPressedZ is not None and self.LastReleasedX is not None and self.LastReleasedZ is not None:
                self.AreaX1.setValue(head["Xpositions"][0, round(self.LastPressedX)])
                self.AreaZ1.setValue(head["Zpositions"][0, round(self.LastPressedZ)])
                self.AreaX2.setValue(head["Xpositions"][0, round(self.LastReleasedX)])
                self.AreaZ2.setValue(head["Zpositions"][0, round(self.LastReleasedZ)])
                self.LastPressedX = None
                self.LastPressedZ = None
                self.LastReleasedX = None
                self.LastReleasedZ = None
                # QtGui.QGuiApplication.restoreOverrideCursor()
                self.TotalSignal.Canvas.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        else:
            if self.MarkPoint.isChecked(): 
                self.MarkPoint.blockSignals(True)
                self.MarkPoint.setChecked(False)
                self.MarkPoint.blockSignals(False)

    def ROIsImport_clicked(self, checked, fileName, changeROIsDefault = True):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import ROIs config", self.ResultsPath.text(), "PDA Files(*.PDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:
            self.ROIsDeleteAll_clicked()
            if changeROIsDefault: self.ROIsDefault.setChecked(False)
            self.ROIs.setCurrentCell(0, 0)
            while self.tabWidget.count() > 7:
                self.tabWidget.removeTab(7)

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
                    i = self.tabWidget.addTab(PreviewTab(self, int(roi[1]), int(roi[2])), roi[0])
                    self.tabWidget.widget(i).Canvas.mpl_connect("button_press_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibButtonPressed(event, canvas))
                    self.tabWidget.widget(i).Canvas.mpl_connect("button_release_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibButtonReleased(event, canvas))
                    self.tabWidget.widget(i).Canvas.mpl_connect("motion_notify_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibMouseMotion(event, canvas))
            file.close()

    def ROIsAdd_clicked(self):
        self.ROIsDefault.setChecked(False)
        addroi = add_roi.AddRoi(self, self.Calib, self.Sigma, self.RoiCount, self.monoE)
        table = addroi.tableWidget_CustomROIs
        for row in range(self.ROIs.rowCount()):
            table.insertRow(table.currentRow() + 1)
            table.setItem(table.currentRow() + 1, 0, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 0).text()}"))
            table.setItem(table.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 1).text()}"))
            table.setItem(table.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 2).text()}"))
            table.setItem(table.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 3).text()}"))
            table.setCurrentCell(table.currentRow() + 1, 0)
            try:
                name = self.ROIs.item(row, 0).text().split("-")
                if name[1] == "Ka": addroi.tab_Kalpha.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "Kb": addroi.tab_Kbeta.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "La": addroi.tab_Lalpha.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "Lb": addroi.tab_Lbeta.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "M": addroi.tab_M.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
            except:
                continue
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
            self.tabWidget.removeTab(7 + row)
            self.ROIs.removeRow(row)
    
    def ROIsDeleteAll_clicked(self):
        self.ROIs.setCurrentCell(0, 0)
        while self.ROIs.rowCount() > 0:
            self.ROIs.removeRow(self.ROIs.currentRow())
        while self.tabWidget.count() > 7:
                self.tabWidget.removeTab(7)
    
    def MapPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Map path", self.MapPath.text())
        if path:
            self.MapPath.blockSignals(True)
            self.MapPath.setText(path)
            self.MapPath.blockSignals(False)
            self.LoadData()
    
    def ResultsPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Results path", self.ResultsPath.text())
        if path:
            self.ResultsPath.setText(path)
    
    def Reload_clicked(self):
        self.ReloadData()
    
    def ImportConfig_clicked(self, clicked, fileName):
        self.PointChanged = False
        self.AreaChanged = False
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Single config", self.ResultsPath.text(), "PDA Files(*.PDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:

            self.PointX.blockSignals(True)
            self.PointZ.blockSignals(True)
            self.AreaX1.blockSignals(True)
            self.AreaX2.blockSignals(True)
            self.AreaZ1.blockSignals(True)
            self.AreaZ2.blockSignals(True)

            self.PointX.setMinimum(-100)
            self.PointZ.setMinimum(-100)
            self.PointX.setMaximum(100)
            self.PointZ.setMaximum(100)

            self.AreaX1.setMinimum(-100)
            self.AreaX2.setMinimum(-100)
            self.AreaZ1.setMinimum(-100)
            self.AreaZ2.setMinimum(-100)
            self.AreaX1.setMaximum(100)
            self.AreaX2.setMaximum(100)
            self.AreaZ1.setMaximum(100)
            self.AreaZ2.setMaximum(100)

            self.PointX.blockSignals(False)
            self.PointZ.blockSignals(False)
            self.AreaX1.blockSignals(False)
            self.AreaX2.blockSignals(False)
            self.AreaZ1.blockSignals(False)
            self.AreaZ2.blockSignals(False)

            read = False
            file = open(fileName, "r")
            for line in file:
                if line[0] != "\n" and line[0:2] == "##":
                    read = True if line in ["## General configuration\n", "## Single configuration\n"] else False
                if read and line[0] not in ["#", "\n"]:
                    data = line.split()
                    variableName = data[0]
                    property = data[1]
                    value = None
                    if len(data) > 2:
                        value = " ".join(data[2:])

                    if variableName[:9] == "Detectors":
                        if variableName[9:] == "Be": self.CurrentDetector = "Be"
                        elif variableName[9:] == "ML": self.CurrentDetector = "ML"
                        else: self.CurrentDetector = "Sum"

                    if variableName in ["MapPath"]:
                        exec(f'self.{variableName}.blockSignals(True)')
                    if property == "Text": 
                        exec(f'self.{variableName}.set{property}("{value if value else ""}")')
                    else: 
                        exec(f'self.{variableName}.set{property}({value})')
                    if variableName in ["MapPath"]:
                        exec(f'self.{variableName}.blockSignals(False)')
            file.close()
            self.ROIsImport_clicked(False, fileName, False)
            self.LoadData(startLoad = not (self.PointChanged or self.AreaChanged), importLoad = True)
            if self.PointChanged or self.AreaChanged: self.ReloadData()
    
    def SaveConfig_clicked(self, clicked, fileName):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Single config", self.ResultsPath.text(), "PDA Files(*.PDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:
            file = open(fileName, 'w')
            fileContent = "## General configuration\n# Element name\tProperty\tValue"

            fileContent += f"\n\nROIsDefault\tChecked\t{self.ROIsDefault.isChecked()}"

            fileContent += f'\n\nResultsPath\tText\t{self.ResultsPath.text() if self.ResultsPath.text() else ""}'

            if self.CurrentDetector is not None:
                fileContent += f"\n\nDetectors{self.CurrentDetector}\tChecked\tTrue"

            fileContent += f"\n\nCalibrationGain\tValue\t{self.CalibrationGain.value()}"
            fileContent += f"\nCalibrationZero\tValue\t{self.CalibrationZero.value()}"
            fileContent += f"\nCalibrationNoise\tValue\t{self.CalibrationNoise.value()}"
            fileContent += f"\nCalibrationFano\tValue\t{self.CalibrationFano.value()}"

            fileContent += "\n\n# -----\n\n## Single configuration\n# Element name\tProperty\tValue"

            if self.AreaChanged or self.PointChanged:
                if self.LastChanged == "Area":
                    fileContent += f"\n\nAreaX1\tValue\t{self.AreaX1.value()}"
                    fileContent += f"\nAreaZ1\tValue\t{self.AreaZ1.value()}"
                    fileContent += f"\nAreaX2\tValue\t{self.AreaX2.value()}"
                    fileContent += f"\nAreaZ2\tValue\t{self.AreaZ2.value()}"
                elif self.LastChanged == "Point":
                    fileContent += f"\nPointX\tValue\t{self.PointX.value()}"
                    fileContent += f"\nPointZ\tValue\t{self.PointZ.value()}"

            fileContent += f'\n\nMapPath\tText\t{self.MapPath.text() if self.MapPath.text() else ""}'

            file.write(fileContent + "\n\n# -----\n\n")
            file.close()

            self.ROIsSave_clicked(False, fileName, 'a')

    def Analyse_clicked(self):
        path = pathlib.Path(self.ResultsPath.text())
        if not path.is_dir():
            if path == pathlib.Path():
                QtWidgets.QMessageBox.warning(self, "Analyse", f"It is impossible to save output files from empty path.")
            else:
                QtWidgets.QMessageBox.warning(self, "Analyse", f"It is impossible to save output files from path:\n{path}")
        else:
            outputConfig = analyse.Analyse(self, self.OutputConfig)
            if outputConfig.exec():
                self.OutputConfig = outputConfig.Output
                self.Progress.setValue(0)
                self.Progress.setMaximum(len(self.OutputConfig.keys()))
                QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
                for name in self.OutputConfig.keys():
                    if self.OutputConfig[name]:
                        time.sleep(0.1)
                        # exec(f'analyse.{name}({self.Data}, {path})')
                    self.Progress.setValue(self.Progress.value() + 1)
                QtGui.QGuiApplication.restoreOverrideCursor()
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())