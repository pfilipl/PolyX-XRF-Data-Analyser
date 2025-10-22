from PyQt6 import QtWidgets, QtGui, QtCore, uic
import sys, os, xraylib, matplotlib, time, pathlib, numpy
import matplotlib.backends.backend_qtagg as backend
matplotlib.use('QtAgg')

import main, add_roi, PDA, analyse, load_plots

basedir = pathlib.Path(os.path.dirname(__file__))

class MatplotlibCanvas(backend.FigureCanvasQTAgg):
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
    def __init__(self, parent = None, roiStart = 1, roiStop = 4096, roiFactor = 1.0):
        super(PreviewTab, self).__init__(parent)
        self.Canvas = MatplotlibCanvas(self)
        self.Toolbar = backend.NavigationToolbar2QT(self.Canvas, self)
        self.Canvas.setStyleSheet("background-color:transparent;")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.Canvas)
        layout.addWidget(self.Toolbar)
        self.setLayout(layout)
        self.RoiStart = roiStart
        self.RoiStop = roiStop
        self.RoiFactor = roiFactor

class SingleWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(SingleWindow, self).__init__(parent)
        uic.loadUi(basedir / "single.ui", self)

        # Regions of interest (ROIs)
        self.ROIs               = self.tableWidget_ROIs
        self.ROIsDefault        = self.pushButton_ROIsDefault
        self.RoiCount           = 0

        self.ROIs.cellChanged.connect(self.ROIsChanged)
        self.pushButton_ROIsImport.clicked.connect(lambda checked, fileName = None: self.ROIsImport_clicked(checked, fileName))
        self.pushButton_ROIsAdd.clicked.connect(self.ROIsAdd_clicked)
        self.pushButton_ROIsSave.clicked.connect(lambda checked, fileName = None, mode = 'w': self.ROIsSave_clicked(checked, fileName, mode))
        self.pushButton_ROIsDelete.clicked.connect(self.ROIsDelete_clicked)
        self.pushButton_ROIsDeleteAll.clicked.connect(self.ROIsDeleteAll_clicked)

        # Maps configuration
        self.MapsConfigValuesAuto       = self.pushButton_MapsConfigValuesAuto
        self.MapsConfigValuesStart      = self.doubleSpinBox_MapsConfigValuesStart
        self.MapsConfigValuesStop       = self.doubleSpinBox_MapsConfigValuesStop
        self.MapsConfigAspectAuto       = self.pushButton_MapsConfigAspectAuto
        self.MapsConfigAspectValue      = self.doubleSpinBox_MapsConfigAspectValue
        self.MapsConfigColormap         = self.comboBox_MapsConfigColormap

        self.MapsConfigValuesAuto.toggled.connect(self.ConfigReload)
        self.MapsConfigValuesStart.valueChanged.connect(self.MapsConfigValue_changed)
        self.MapsConfigValuesStop.valueChanged.connect(self.MapsConfigValue_changed)
        self.MapsConfigAspectAuto.toggled.connect(self.ConfigReload)
        self.MapsConfigAspectValue.valueChanged.connect(self.MapsConfigAspect_changed)
        self.MapsConfigColormap.currentTextChanged.connect(self.ConfigReload)
        
        # Spectra configuration
        self.SpectraConfigEnergyAuto    = self.pushButton_SpectraConfigEnergyAuto
        self.SpectraConfigEnergyStart   = self.doubleSpinBox_SpectraConfigEnergyStart
        self.SpectraConfigEnergyStop    = self.doubleSpinBox_SpectraConfigEnergyStop
        self.SpectraConfigAspectAuto    = self.pushButton_SpectraConfigAspectAuto
        self.SpectraConfigAspectValue   = self.doubleSpinBox_SpectraConfigAspectValue
        self.SpectraConfigChannelAxis   = self.checkBox_SpectraConfigChannelAxis
        self.SpectraConfigGrid          = self.checkBox_SpectraConfigGrid

        self.SpectraConfigEnergyAuto.toggled.connect(self.ConfigReload)
        self.SpectraConfigEnergyStart.valueChanged.connect(self.SpectraConfigEnergy_changed)
        self.SpectraConfigEnergyStop.valueChanged.connect(self.SpectraConfigEnergy_changed)
        self.SpectraConfigAspectAuto.toggled.connect(self.ConfigReload)
        self.SpectraConfigAspectValue.valueChanged.connect(self.SpectraConfigAspect_changed)
        self.SpectraConfigChannelAxis.checkStateChanged.connect(self.ConfigReload)
        self.SpectraConfigGrid.checkStateChanged.connect(self.ConfigReload)

        # Tabs
        self.TotalSignal        = self.tab_TotalSignal
        self.SumCheckSpectrum   = self.tab_SumCheckSpectrum
        self.MaxCheckSpectrum   = self.tab_MaxCheckSpectrum
        self.SumSpectrum        = self.tab_SumSpectrum
        self.MaxSpectrum        = self.tab_MaxSpectrum
        self.ExtSumSpectrum     = self.tab_ExtSumSpectrum
        self.ExtMaxSpectrum     = self.tab_ExtMaxSpectrum
        self.I0                 = self.tab_I0
        self.PIN                = self.tab_PIN
        self.LT                 = self.tab_LT
        self.DT                 = self.tab_DT
        self.ICR                 = self.tab_ICR
        self.OCR                 = self.tab_OCR
        self.RC                 = self.tab_RC

        self.Data               = None
        self.LastPressedX       = None
        self.LastPressedZ       = None
        self.LastReleasedX      = None
        self.LastReleasedZ      = None
        self.LastMotionX        = None
        self.LastMotionZ        = None
        self.Rectangle          = matplotlib.patches.Rectangle((0, 0), 0, 0, linewidth = 1, linestyle = '-', edgecolor = 'r')
        self.HLine              = matplotlib.lines.Line2D([0, 0], [0, 0], linewidth = 1, linestyle = '-', color = 'r')
        self.VLine              = matplotlib.lines.Line2D([0, 0], [0, 0], linewidth = 1, linestyle = '-', color = 'r')
        self.SumLine            = matplotlib.lines.Line2D([0, 0], [0, 0], linewidth = 1, linestyle = '-', color = 'r')
        self.MaxLine            = matplotlib.lines.Line2D([0, 0], [0, 0], linewidth = 1, linestyle = '-', color = 'r')
        self.SumCheckLine       = matplotlib.lines.Line2D([0, 0], [0, 0], linewidth = 1, linestyle = '-', color = 'r')
        self.MaxCheckLine       = matplotlib.lines.Line2D([0, 0], [0, 0], linewidth = 1, linestyle = '-', color = 'r')
        self.ExtSumLine         = matplotlib.lines.Line2D([0, 0], [0, 0], linewidth = 1, linestyle = '-', color = 'r')
        self.ExtMaxLine         = matplotlib.lines.Line2D([0, 0], [0, 0], linewidth = 1, linestyle = '-', color = 'r')
        self.SumText            = matplotlib.text.Text(0, 0.95, "", color = 'r', verticalalignment = 'center', transform = self.SumSpectrum.Canvas.Axes.get_xaxis_transform())
        self.MaxText            = matplotlib.text.Text(0, 0.95, "", color = 'r', verticalalignment = 'center', transform = self.MaxSpectrum.Canvas.Axes.get_xaxis_transform())
        self.SumCheckText       = matplotlib.text.Text(0, 0.95, "", color = 'r', verticalalignment = 'center', transform = self.SumCheckSpectrum.Canvas.Axes.get_xaxis_transform())
        self.MaxCheckText       = matplotlib.text.Text(0, 0.95, "", color = 'r', verticalalignment = 'center', transform = self.MaxCheckSpectrum.Canvas.Axes.get_xaxis_transform())
        self.ExtSumText         = matplotlib.text.Text(0, 0.95, "", color = 'r', verticalalignment = 'center', transform = self.ExtSumSpectrum.Canvas.Axes.get_xaxis_transform())
        self.ExtMaxText         = matplotlib.text.Text(0, 0.95, "", color = 'r', verticalalignment = 'center', transform = self.ExtMaxSpectrum.Canvas.Axes.get_xaxis_transform())
    
        self.TotalSignal.Canvas.mpl_connect("button_press_event", lambda event, canvas = self.TotalSignal.Canvas: self.MatplotlibButtonPressed(event, canvas))
        self.TotalSignal.Canvas.mpl_connect("button_release_event", lambda event, canvas = self.TotalSignal.Canvas: self.MatplotlibButtonReleased(event, canvas))
        self.TotalSignal.Canvas.mpl_connect("motion_notify_event", lambda event, canvas = self.TotalSignal.Canvas: self.MatplotlibMouseMotion(event, canvas))
        self.SumSpectrum.Canvas.mpl_connect("button_press_event", lambda event, canvas = self.SumSpectrum.Canvas, mode = "sum": self.MatplotlibButtonPressedSpectrum(event, canvas, mode))
        self.MaxSpectrum.Canvas.mpl_connect("button_press_event", lambda event, canvas = self.MaxSpectrum.Canvas, mode = "max": self.MatplotlibButtonPressedSpectrum(event, canvas, mode))
        self.SumCheckSpectrum.Canvas.mpl_connect("button_press_event", lambda event, canvas = self.SumCheckSpectrum.Canvas, mode = "sumcheck": self.MatplotlibButtonPressedSpectrum(event, canvas, mode))
        self.MaxCheckSpectrum.Canvas.mpl_connect("button_press_event", lambda event, canvas = self.MaxCheckSpectrum.Canvas, mode = "maxcheck": self.MatplotlibButtonPressedSpectrum(event, canvas, mode))
        self.ExtSumSpectrum.Canvas.mpl_connect("button_press_event", lambda event, canvas = self.ExtSumSpectrum.Canvas, mode = "extsum": self.MatplotlibButtonPressedSpectrum(event, canvas, mode))
        self.ExtMaxSpectrum.Canvas.mpl_connect("button_press_event", lambda event, canvas = self.ExtMaxSpectrum.Canvas, mode = "extmax": self.MatplotlibButtonPressedSpectrum(event, canvas, mode))

        self.tabWidget.setTabEnabled(5, False)
        self.tabWidget.setTabEnabled(6, False)
        self.tabWidget.setTabEnabled(8, False)
        self.tabWidget.setTabEnabled(9, False)
        self.tabWidget.setTabEnabled(10, False)
        self.tabWidget.setTabEnabled(11, False)
        self.tabWidget.setTabEnabled(12, False)

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
        self.ClearSelection     = self.pushButton_ClearSelection

        self.PointX.valueChanged.connect(lambda value, mode = "Point": self.RegionChanged(value, mode))
        self.PointZ.valueChanged.connect(lambda value, mode = "Point": self.RegionChanged(value, mode))
        self.AreaX1.valueChanged.connect(lambda value, mode = "Area": self.RegionChanged(value, mode))
        self.AreaZ1.valueChanged.connect(lambda value, mode = "Area": self.RegionChanged(value, mode))
        self.AreaX2.valueChanged.connect(lambda value, mode = "Area": self.RegionChanged(value, mode))
        self.AreaZ2.valueChanged.connect(lambda value, mode = "Area": self.RegionChanged(value, mode))

        self.MarkPoint.toggled.connect(self.MarkPoint_toggled)
        self.SelectArea.toggled.connect(self.SelectArea_toggled)
        self.ClearSelection.clicked.connect(self.ClearSelection_clicked)

        # Map path
        self.MapPath            = self.lineEdit_MapPath

        self.MapPath.editingFinished.connect(self.LoadData)
        self.toolButton_MapPathSearch.clicked.connect(self.MapPathSearch_clicked)

        # Results
        self.ResultsPath        = self.lineEdit_ResultsPath

        self.toolButton_ResultsPathSearch.clicked.connect(self.ResultsPathSearch_clicked)

        # Detectors
        self.DetectorsSDD1      = self.pushButton_DetectorsSDD1
        self.DetectorsSDD2      = self.pushButton_DetectorsSDD2
        self.DetectorsSum       = self.pushButton_DetectorsSum
        self.LastDetector       = None
        self.CurrentDetector    = None

        self.DetectorsSDD1.clicked.connect(lambda checked, mode = "SDD1": self.DetectorChanged(checked, mode))
        self.DetectorsSDD2.clicked.connect(lambda checked, mode = "SDD2": self.DetectorChanged(checked, mode))
        self.DetectorsSum.clicked.connect(lambda checked, mode = "Sum": self.DetectorChanged(checked, mode))

        # Energy calibration
        self.Calib              = None
        self.Sigma              = None
        self.monoE              = None
        self.monoType           = None

        self.CalibrationGain    = self.doubleSpinBox_CalibrationGain
        self.CalibrationZero    = self.doubleSpinBox_CalibrationZero
        self.CalibrationNoise   = self.doubleSpinBox_CalibrationNoise
        self.CalibrationFano    = self.doubleSpinBox_CalibrationFano

        # Normalization
        self.NormType           = None

        self.radioButton_NormTypeNone.clicked.connect(lambda checked, mode = None: self.NormTypeChanged(mode))
        self.radioButton_NormTypeI0LT.clicked.connect(lambda checked, mode = "I0LT": self.NormTypeChanged(mode))
        self.radioButton_NormTypeI0.clicked.connect(lambda checked, mode = "I0": self.NormTypeChanged(mode))
        self.radioButton_NormTypeLT.clicked.connect(lambda checked, mode = "LT": self.NormTypeChanged(mode))

        # Process
        self.Progress           = self.progressBar_Progress
        self.Reload             = self.pushButton_Reload
        self.AutoReload         = self.pushButton_AutoReload
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

        self.pushButton_ResetAll.clicked.connect(self.ResetAll_clicked)

    def setCalibration(self, calib, sigma):
        self.Calib = calib
        self.Sigma = sigma

    def MatplotlibButtonPressedSpectrum(self, event, canvas, mode):
        if mode == "sum":
            line = self.SumLine
            text = self.SumText
        elif mode == "max":
            line = self.MaxLine
            text = self.MaxText
        elif mode == "sumcheck":
            line = self.SumCheckLine
            text = self.SumCheckText
        elif mode == "maxcheck":
            line = self.MaxCheckLine
            text = self.MaxCheckText
        elif mode == "extsum":
            line = self.ExtSumLine
            text = self.ExtSumText
        elif mode == "extmax":
            line = self.ExtMaxLine
            text = self.ExtMaxText
        if event.inaxes == canvas.Axes:
            line.set(xdata = [event.xdata, event.xdata], ydata = [1e-10, 1e20])
            canvas.Axes.add_artist(line)
            if self.Calib is not None:
                text.set(x = event.xdata, text = f" E = {self.Calib[round(event.xdata)]:.3f} eV ", horizontalalignment = 'right' if event.xdata > canvas.Axes.get_xlim()[1] * 0.8 else 'left')
                canvas.Axes.add_artist(text)
            canvas.draw()

    def MatplotlibButtonPressed(self, event, canvas):
        if self.MarkPoint.isChecked() or self.SelectArea.isChecked():
            if event.inaxes == canvas.Axes:
                self.LastPressedX = event.xdata
                self.LastPressedZ = event.ydata
                if self.SelectArea.isChecked():
                    self.Rectangle.set_visible(True)
                    self.HLine.set_visible(False)
                    self.VLine.set_visible(False)
                    self.Rectangle.set_facecolor('r')
                    self.Rectangle.set_xy((self.LastPressedX, self.LastPressedZ))
                    self.Rectangle.set_height(0.25)
                    self.Rectangle.set_width(0.25)
                    canvas.Axes.add_patch(self.Rectangle)
                else:
                    self.Rectangle.set_visible(False)
                    self.HLine.set_visible(True)
                    self.VLine.set_visible(True)
                    h = 0.05 * (canvas.Axes.get_xlim()[1] - canvas.Axes.get_xlim()[0])
                    v = 0.05 * (canvas.Axes.get_ylim()[1] - canvas.Axes.get_ylim()[0])
                    self.HLine.set(xdata = [self.LastPressedX - h, self.LastPressedX + h], ydata = [self.LastPressedZ, self.LastPressedZ])
                    self.VLine.set(xdata = [self.LastPressedX, self.LastPressedX], ydata = [self.LastPressedZ - v, self.LastPressedZ + v])
                    canvas.Axes.add_artist(self.HLine)
                    canvas.Axes.add_artist(self.VLine)
                    self.AreaChanged = False
                    self.PointChanged = True
                    self.tabWidget.setTabEnabled(5, True)
                    self.tabWidget.setTabEnabled(6, True)
                canvas.draw()
                self.MarkPoint.setChecked(False)
            if not self.SelectArea.isChecked():
                if self.AutoReload.isChecked(): self.Reload_clicked()

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
            self.PointChanged = False
            self.AreaChanged = True
            self.tabWidget.setTabEnabled(5, True)
            self.tabWidget.setTabEnabled(6, True)
            if self.AutoReload.isChecked(): self.Reload_clicked()

    def MatplotlibMouseMotion(self, event, canvas):
        if self.SelectArea.isChecked() and self.LastPressedX is not None and self.LastPressedZ is not None:
            if event.inaxes == canvas.Axes:
                self.LastMotionX = event.xdata
                self.LastMotionZ = event.ydata
                self.Rectangle.set_facecolor('none')
                self.Rectangle.set_height(self.LastMotionZ - self.Rectangle.get_y())
                self.Rectangle.set_width(self.LastMotionX - self.Rectangle.get_x())
                canvas.draw()

    def DetectorChanged(self, checked, mode):
        if checked:
            self.CurrentDetector = mode
            if self.LastDetector is None:
                self.LastDetector = mode
            for detector in ["SDD1", "SDD2", "Sum"]:
                if detector != mode:
                    exec(f'if self.Detectors{detector}.isChecked(): self.LastDetector = "{detector}"')
                    exec(f"self.Detectors{detector}.blockSignals(True)")
                    exec(f"self.Detectors{detector}.setChecked(False)")
                    exec(f"self.Detectors{detector}.blockSignals(False)")
        else:
            if self.LastDetector != mode:
                self.CurrentDetector = self.LastDetector
                if self.LastDetector is not None:
                    exec(f"self.Detectors{self.LastDetector}.blockSignals(True)")
                    exec(f"self.Detectors{self.LastDetector}.setChecked(True)")
                    exec(f"self.Detectors{self.LastDetector}.blockSignals(False)")
            else:
                self.LastDetector = None
                self.CurrentDetector = None
        if self.CurrentDetector in ["SDD1", "SDD2"]:
            self.tabWidget.setTabEnabled(8, True)
            self.tabWidget.setTabEnabled(9, True)
            self.tabWidget.setTabEnabled(10, True)
            self.tabWidget.setTabEnabled(11, True)
            self.tabWidget.setTabEnabled(12, True)
            self.radioButton_NormTypeI0LT.setEnabled(True)
            self.radioButton_NormTypeLT.setEnabled(True)
        else:
            self.tabWidget.setTabEnabled(8, False)
            self.tabWidget.setTabEnabled(9, False)
            self.tabWidget.setTabEnabled(10, False)
            self.tabWidget.setTabEnabled(11, False)
            self.tabWidget.setTabEnabled(12, False)
            self.radioButton_NormTypeI0LT.setEnabled(False)
            self.radioButton_NormTypeLT.setEnabled(False)
        if self.AutoReload.isChecked(): self.Reload_clicked()

    def NormTypeChanged(self, mode = None):
        self.NormType = mode
        if self.AutoReload.isChecked(): self.Reload_clicked()

    def ConfigReload(self, variable):
        if self.AutoReload.isChecked(): self.Reload_clicked()

    def ROIsChanged(self):
        table = self.ROIs
        tabs = self.tabWidget
        while tabs.count() > 14:
            tabs.removeTab(14)
        for row in range(table.rowCount()):
            i = tabs.addTab(PreviewTab(self, int(table.item(row, 1).text()), int(table.item(row, 2).text()), float(table.item(row, 3).text())), table.item(row, 0).text())
            tabs.widget(i).Canvas.mpl_connect("button_press_event", lambda event, canvas = tabs.widget(i).Canvas: self.parent().MatplotlibButtonPressed(event, canvas))
            tabs.widget(i).Canvas.mpl_connect("button_release_event", lambda event, canvas = tabs.widget(i).Canvas: self.parent().MatplotlibButtonReleased(event, canvas))
            tabs.widget(i).Canvas.mpl_connect("motion_notify_event", lambda event, canvas = tabs.widget(i).Canvas: self.parent().MatplotlibMouseMotion(event, canvas))
        
    def LoadData(self, startLoad = True, importLoad = False):
        QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        path = pathlib.Path(self.MapPath.text())
        try:
            head, Data, ICR, OCR, RT, LT, DT, PIN, I0, RC, ROI = PDA.data_load(path)
        except:
            if path == pathlib.Path():
                if not importLoad: QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map from empty path.")
            else:
                QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map from path:\n{path}")
        else:
            self.Data = {"head" : head, "Data" : Data, "ICR" : ICR, "OCR" : OCR, "RT" : RT, "LT" : LT, "DT" : DT, "PIN" : PIN, "I0" : I0, "RC" : RC, "ROI" : ROI}

            try:
                self.monoE = head["monoE"][0][0]
                self.SpectraConfigEnergyStop.blockSignals(True)
                self.SpectraConfigEnergyStop.setValue(self.monoE / 1000 + 1) # widma do energii mono
                self.SpectraConfigEnergyStop.blockSignals(False)
            except:
                self.monoE = None

            try:
                self.monoType = head["monotype"][0]
            except:
                self.monoType = None

            if self.ROIsDefault.isChecked():
                self.ROIs.blockSignals(True)
                self.ROIsDeleteAll_clicked()
                for roi in ROI:
                    self.ROIs.insertRow(self.ROIs.currentRow() + 1)
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 0, QtWidgets.QTableWidgetItem(f"{roi[0]}"))
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(f"{roi[1]}"))
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(f"{roi[2]}"))
                    self.ROIs.setItem(self.ROIs.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(f"{roi[3]}"))
                    self.ROIs.setCurrentCell(self.ROIs.currentRow() + 1, 0)
                    i = self.tabWidget.addTab(PreviewTab(self, int(roi[1]), int(roi[2]), float(roi[3])), roi[0])
                    self.tabWidget.widget(i).Canvas.mpl_connect("button_press_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibButtonPressed(event, canvas))
                    self.tabWidget.widget(i).Canvas.mpl_connect("button_release_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibButtonReleased(event, canvas))
                    self.tabWidget.widget(i).Canvas.mpl_connect("motion_notify_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibMouseMotion(event, canvas))
                self.ROIs.blockSignals(False)

            self.MapsConfigValuesStop.blockSignals(True)
            self.MapsConfigValuesStop.setMaximum(numpy.max(numpy.sum(Data[2], axis = 2)))
            if not self.MapsConfigValuesAuto.isChecked():
                self.MapsConfigValuesStop.setValue(numpy.max(numpy.sum(Data[2], axis = 2)))
            self.MapsConfigValuesStop.blockSignals(False)

            vMin = None if self.MapsConfigValuesAuto.isChecked() else self.MapsConfigValuesStart.value()
            vMax = None if self.MapsConfigValuesAuto.isChecked() else self.MapsConfigValuesStop.value()
            mapAspect = 'auto' if self.MapsConfigAspectAuto.isChecked() else self.MapsConfigAspectValue.value()
            if self.Calib is not None:
                eMin = 0.0 if self.SpectraConfigEnergyAuto.isChecked() else self.SpectraConfigEnergyStart.value()
                eMax = self.monoE / 1000 + 1 if self.SpectraConfigEnergyAuto.isChecked() and self.monoE is not None else self.SpectraConfigEnergyStop.value() # widma do energii mono
            else:
                eMin = 0.0
                eMax = None
            spectraAspect = 'auto' if self.SpectraConfigAspectAuto.isChecked() else self.SpectraConfigAspectValue.value()
            cMap = self.MapsConfigColormap.currentText()

            if startLoad:
                if self.CurrentDetector is not None:
                    exec(f'self.Detectors{self.CurrentDetector}.setChecked(True)')
                    exec(f'self.DetectorChanged(True, self.CurrentDetector)')
                else:
                    self.DetectorsSum.click()

            clabel = "Counts [c"
            if self.NormType is None: 
                norm = None
                clabel = clabel + "]"
            elif self.NormType == "I0":
                lt = numpy.ones(self.Data["LT"][0].shape) * 1e6
                lt = [lt, lt, lt]
                norm = [self.Data["I0"], lt]
                clabel = clabel + "/V]"
            elif self.NormType == "LT":
                i0 = numpy.ones(self.Data["I0"].shape)
                norm = [i0, self.Data["LT"]]
                clabel = clabel + "ps]"
            else: 
                norm = [self.Data["I0"], self.Data["LT"]]
                clabel = clabel + "ps/V]"

            if self.CurrentDetector == "SDD1": det = 0
            elif self.CurrentDetector == "SDD2": det = 1
            else: det = 2
            load_plots.MapData(self, self.TotalSignal, det, importLoad = importLoad, Vmin = vMin, Vmax = vMax, Aspect = mapAspect, Cmap = cMap, Norm = norm, Clabel = clabel)
            load_plots.SpectrumCheck(self, self.SumCheckSpectrum, numpy.sum, Emin = eMin, Emax = eMax, log = True, Aspect = spectraAspect, ChannelAxis = self.SpectraConfigChannelAxis.isChecked(), Grid = self.SpectraConfigGrid.isChecked())
            load_plots.SpectrumCheck(self, self.MaxCheckSpectrum, numpy.max, Emin = eMin, Emax = eMax, log = False, Aspect = spectraAspect, ChannelAxis = self.SpectraConfigChannelAxis.isChecked(), Grid = self.SpectraConfigGrid.isChecked())
            load_plots.Spectrum(self, self.SumSpectrum, numpy.sum, det, startLoad = startLoad, importLoad = importLoad, Emin = eMin, Emax = eMax, Aspect = spectraAspect, ChannelAxis = self.SpectraConfigChannelAxis.isChecked(), Grid = self.SpectraConfigGrid.isChecked())
            load_plots.Spectrum(self, self.MaxSpectrum, numpy.max, det, startLoad = startLoad, importLoad = importLoad, peaks = None, Emin = eMin, Emax = eMax, Aspect = spectraAspect, ChannelAxis = self.SpectraConfigChannelAxis.isChecked(), Grid = self.SpectraConfigGrid.isChecked())
            load_plots.MapStats2D(self, self.I0, "I0", det, "I0 [V]", importLoad = importLoad, Aspect = mapAspect, Cmap = cMap)
            load_plots.MapStats2D(self, self.PIN, "PIN", det, "PIN [V]", importLoad = importLoad, Aspect = mapAspect, Cmap = cMap)
            load_plots.MapStats2D(self, self.LT, "LT", det, "LT [ms]", importLoad = importLoad, Aspect = mapAspect, Cmap = cMap, coefficient = 1e-3)
            load_plots.MapStats2D(self, self.DT, "DT", det, "DT [%]", importLoad = importLoad, Aspect = mapAspect, Cmap = cMap)
            load_plots.MapStats2D(self, self.ICR, "ICR", det, "ICR [kcps]", importLoad = importLoad, Aspect = mapAspect, Cmap = cMap)
            load_plots.MapStats2D(self, self.OCR, "OCR", det, "OCR [kcps]", importLoad = importLoad, Aspect = mapAspect, Cmap = cMap)
            load_plots.PlotStats1D(self, self.RC, "RC", "I [mA]", importLoad = importLoad)
            for i in range(14, self.tabWidget.count()):
                load_plots.MapData(self, self.tabWidget.widget(i), det, importLoad = importLoad, Vmin = vMin, Vmax = vMax, Aspect = mapAspect, Cmap = cMap, Norm = norm, Clabel = clabel)

            if not self.Reload.isEnabled(): 
                self.Reload.setEnabled(True)
                self.AutoReload.setEnabled(True)
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
            if not self.MarkPoint.isEnabled(): self.pushButton_MarkPoint.setEnabled(True)
            if not self.SelectArea.isEnabled(): self.pushButton_SelectArea.setEnabled(True)
            if not self.ClearSelection.isEnabled(): self.pushButton_ClearSelection.setEnabled(True)

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

            if startLoad:
                self.PointChanged = False
                self.AreaChanged = False

                try:
                    self.label_Help.setText("Map info:")
                    self.label_Help.show()
                    info = f'map size: \t {numpy.round(head["Xpositions"][0, -1] - head["Xpositions"][0, 0], 3)} x {numpy.round(head["Zpositions"][0, -1] - head["Zpositions"][0, 0], 3)} mm ({len(head["Xpositions"][0, :])} x {len(head["Zpositions"][0, :])} px)'
                    info += f'\npixel size: \t {numpy.round(head["Xpositions"][0, 1] * 1000 - head["Xpositions"][0, 0] * 1000, 3)} x {numpy.round(head["Zpositions"][0, 1] * 1000 - head["Zpositions"][0, 0] * 1000, 3)} um'
                    info += f'\ntime per pixel: \t {numpy.round(head["dt"][0, 0] * 1000, 3)} ms'
                    info += f'\ntotal acquisition time: \t {numpy.round(len(head["Xpositions"][0, :]) * len(head["Zpositions"][0, :]) * head["dt"][0, 0], 3)} s ({numpy.round(len(head["Xpositions"][0, :]) * len(head["Zpositions"][0, :]) * head["dt"][0, 0] / 3600, 3)} h)'
                    # info += f'\nmeasurement time: \t {} s'
                    self.label_HelpDescription.setText(info)
                    self.label_HelpDescription.show()
                except:
                    self.label_Help.hide()
                    self.label_HelpDescription.hide()

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
        
        vMin = None if self.MapsConfigValuesAuto.isChecked() else self.MapsConfigValuesStart.value()
        vMax = None if self.MapsConfigValuesAuto.isChecked() else self.MapsConfigValuesStop.value()
        mapAspect = 'auto' if self.MapsConfigAspectAuto.isChecked() else self.MapsConfigAspectValue.value()
        if self.Calib is not None:
            eMin = 0.0 if self.SpectraConfigEnergyAuto.isChecked() else self.SpectraConfigEnergyStart.value()
            eMax = self.monoE / 1000 + 1 if self.SpectraConfigEnergyAuto.isChecked() and self.monoE is not None else self.SpectraConfigEnergyStop.value() # widma do energii mono
        else:
            eMin = 0.0
            eMax = None
        spectraAspect = 'auto' if self.SpectraConfigAspectAuto.isChecked() else self.SpectraConfigAspectValue.value()
        cMap = self.MapsConfigColormap.currentText()

        clabel = "Counts [c"
        if self.NormType is None: 
            norm = None
            clabel = clabel + "]"
        elif self.NormType == "I0":
            lt = numpy.ones(self.Data["LT"][0].shape) * 1e6
            lt = [lt, lt, lt]
            norm = [self.Data["I0"], lt]
            clabel = clabel + "/V]"
        elif self.NormType == "LT":
            i0 = numpy.ones(self.Data["I0"].shape)
            norm = [i0, self.Data["LT"]]
            clabel = clabel + "ps]"
        else: 
            norm = [self.Data["I0"], self.Data["LT"]]
            clabel = clabel + "ps/V]"

        if self.CurrentDetector == "SDD1": det = 0
        elif self.CurrentDetector == "SDD2": det = 1
        else: det = 2
        load_plots.MapData(self, self.TotalSignal, det, pos = POS, Vmin = vMin, Vmax = vMax, Aspect = mapAspect, Cmap = cMap, Norm = norm, Clabel = clabel)
        load_plots.SpectrumCheck(self, self.SumCheckSpectrum, numpy.sum, Emin = eMin, Emax = eMax, log = True, Aspect = spectraAspect, ChannelAxis = self.SpectraConfigChannelAxis.isChecked(), Grid = self.SpectraConfigGrid.isChecked())
        load_plots.SpectrumCheck(self, self.MaxCheckSpectrum, numpy.max, Emin = eMin, Emax = eMax, log = False, Aspect = spectraAspect, ChannelAxis = self.SpectraConfigChannelAxis.isChecked(), Grid = self.SpectraConfigGrid.isChecked())
        load_plots.Spectrum(self, self.SumSpectrum, numpy.sum, det, pos = None, roi = ROI, startLoad = True, Emin = eMin, Emax = eMax, Aspect = spectraAspect, ChannelAxis = self.SpectraConfigChannelAxis.isChecked(), Grid = self.SpectraConfigGrid.isChecked())
        load_plots.Spectrum(self, self.MaxSpectrum, numpy.max, det, pos = None, roi = ROI, startLoad = True, peaks = None, Emin = eMin, Emax = eMax, Aspect = spectraAspect, ChannelAxis = self.SpectraConfigChannelAxis.isChecked(), Grid = self.SpectraConfigGrid.isChecked())
        load_plots.Spectrum(self, self.ExtSumSpectrum, numpy.sum, det, pos = POS, roi = ROI, startLoad = False, Emin = eMin, Emax = eMax, Aspect = spectraAspect, ChannelAxis = self.SpectraConfigChannelAxis.isChecked(), Grid = self.SpectraConfigGrid.isChecked())
        load_plots.Spectrum(self, self.ExtMaxSpectrum, numpy.max, det, pos = POS, roi = ROI, startLoad = False, peaks = None, Emin = eMin, Emax = eMax, Aspect = spectraAspect, ChannelAxis = self.SpectraConfigChannelAxis.isChecked(), Grid = self.SpectraConfigGrid.isChecked())
        load_plots.MapStats2D(self, self.I0, "I0", det, "I0 [V]", Aspect = mapAspect, Cmap = cMap)
        load_plots.MapStats2D(self, self.PIN, "PIN", det, "PIN [V]", Aspect = mapAspect, Cmap = cMap)
        load_plots.MapStats2D(self, self.LT, "LT", det, "LT [ms]", Aspect = mapAspect, Cmap = cMap, coefficient = 1e-3)
        load_plots.MapStats2D(self, self.DT, "DT", det, "DT [%]", Aspect = mapAspect, Cmap = cMap)
        load_plots.MapStats2D(self, self.ICR, "ICR", det, "ICR [kcps]", Aspect = mapAspect, Cmap = cMap)
        load_plots.MapStats2D(self, self.OCR, "OCR", det, "OCR [kcps]", Aspect = mapAspect, Cmap = cMap)
        # load_plots.PlotStats1D(self, self.RC, "RC")
        for i in range(14, self.tabWidget.count()):
            load_plots.MapData(self, self.tabWidget.widget(i), det, pos = POS, Vmin = vMin, Vmax = vMax, Aspect = mapAspect, Cmap = cMap, Norm = norm, Clabel = clabel)
        QtGui.QGuiApplication.restoreOverrideCursor()

    def MapsConfigValue_changed(self):
        if self.MapsConfigValuesAuto.isChecked(): self.MapsConfigValuesAuto.setChecked(False)
        if self.AutoReload.isChecked(): self.Reload_clicked()

    def MapsConfigAspect_changed(self):
        if self.MapsConfigAspectAuto.isChecked(): self.MapsConfigAspectAuto.setChecked(False)
        if self.AutoReload.isChecked(): self.Reload_clicked()

    def SpectraConfigEnergy_changed(self):
        if self.SpectraConfigEnergyAuto.isChecked(): self.SpectraConfigEnergyAuto.setChecked(False)
        if self.AutoReload.isChecked(): self.Reload_clicked()
        
    def SpectraConfigAspect_changed(self):
        if self.SpectraConfigAspectAuto.isChecked(): self.SpectraConfigAspectAuto.setChecked(False)
        if self.AutoReload.isChecked(): self.Reload_clicked()

    def ROIsImport_clicked(self, checked, fileName, changeROIsDefault = True):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import ROIs config", self.ResultsPath.text(), "PXDA Files(*.PXDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:
            self.ROIsDeleteAll_clicked()
            if changeROIsDefault: self.ROIsDefault.setChecked(False)
            self.ROIs.blockSignals(True)
            self.ROIs.setCurrentCell(0, 0)
            while self.tabWidget.count() > 14:
                self.tabWidget.removeTab(14)

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
                    i = self.tabWidget.addTab(PreviewTab(self, int(roi[1]), int(roi[2]), float(roi[3])), roi[0])
                    self.tabWidget.widget(i).Canvas.mpl_connect("button_press_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibButtonPressed(event, canvas))
                    self.tabWidget.widget(i).Canvas.mpl_connect("button_release_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibButtonReleased(event, canvas))
                    self.tabWidget.widget(i).Canvas.mpl_connect("motion_notify_event", lambda event, canvas = self.tabWidget.widget(i).Canvas: self.MatplotlibMouseMotion(event, canvas))
            file.close()
            self.ROIs.blockSignals(False)
            if self.AutoReload.isChecked(): self.Reload_clicked()

    def ROIsAdd_clicked(self):
        self.ROIsDefault.setChecked(False)
        addroi = add_roi.AddRoi(self, self.Calib, self.Sigma, self.RoiCount, self.monoE, self.monoType)
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
            if self.AutoReload.isChecked(): self.Reload_clicked()
        
    def ROIsSave_clicked(self, checked, fileName, mode):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save ROIs config", self.ResultsPath.text(), "PXDA Files(*.PXDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:
            file = open(fileName, mode)
            fileContent = "## ROIs\n# Name\t Start channel\t Stop channel\t Sum factor [SDD1/SDD2]\n"
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
            self.tabWidget.removeTab(14 + row)
            self.ROIs.removeRow(row)
        if self.ROIsDefault.isChecked(): self.ROIsDefault.setChecked(False)
    
    def ROIsDeleteAll_clicked(self):
        self.ROIs.setCurrentCell(0, 0)
        while self.ROIs.rowCount() > 0:
            self.ROIs.removeRow(self.ROIs.currentRow())
        while self.tabWidget.count() > 14:
                self.tabWidget.removeTab(14)
        if self.ROIsDefault.isChecked(): self.ROIsDefault.setChecked(False)
    
    def RegionChanged(self, value, mode):
        exec(f"self.{mode}Changed = True")
        exec(f'self.LastChanged = "{mode}"')

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

    def ClearSelection_clicked(self):
        head = self.Data["head"]
        self.Rectangle.set_visible(False)
        self.HLine.set_visible(False)
        self.VLine.set_visible(False)
        self.TotalSignal.Canvas.draw()
        self.SumSpectrum.Canvas.draw()
        self.MaxSpectrum.Canvas.draw()
        for i in range(14, self.tabWidget.count()):
            self.tabWidget.widget(i).Canvas.draw()
        
        self.PointX.blockSignals(True)
        self.PointZ.blockSignals(True)
        self.AreaX1.blockSignals(True)
        self.AreaX2.blockSignals(True)
        self.AreaZ1.blockSignals(True)
        self.AreaZ2.blockSignals(True)

        self.PointX.setValue(min(head["Xpositions"][0, :]))
        self.PointZ.setValue(min(head["Zpositions"][0, :]))
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

        if self.MarkPoint.isChecked(): 
            self.MarkPoint.blockSignals(True)
            self.MarkPoint.setChecked(False)
            self.MarkPoint.blockSignals(False)
        if self.SelectArea.isChecked(): 
            self.SelectArea.blockSignals(True)
            self.SelectArea.setChecked(False)
            self.SelectArea.blockSignals(False)
        self.PointChanged = False
        self.AreaChanged = False

        self.tabWidget.setTabEnabled(5, False)
        self.tabWidget.setTabEnabled(6, False)
        if self.AutoReload.isChecked(): self.Reload_clicked()
    
    def MapPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Map path", self.MapPath.text())
        if path:
            self.MapPath.blockSignals(True)
            self.ResultsPath.blockSignals(True)
            self.MapPath.setText(path)
            self.ResultsPath.setText(path)
            self.MapPath.blockSignals(False)
            self.ResultsPath.blockSignals(False)
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
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Single config", self.ResultsPath.text(), "PXDA Files(*.PXDAconfig);; Text files(*.dat *.txt);; All files(*)")
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
                        if variableName[9:] == "SDD1": self.CurrentDetector = "SDD1"
                        elif variableName[9:] == "SDD2": self.CurrentDetector = "SDD2"
                        else: self.CurrentDetector = "Sum"

                    if variableName in ["MapPath"]:
                        exec(f'self.{variableName}.blockSignals(True)')
                    if property == "Text": 
                        if variableName == "MapsConfigColormap":
                            exec(f'self.comboBox_{variableName}.setCurrentIndex(self.comboBox_{variableName}.findText("{value}", QtCore.Qt.MatchFlag.MatchExactly))')
                        else:
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
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Single config", self.ResultsPath.text(), "PXDA Files(*.PXDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:
            file = open(fileName, 'w')
            fileContent = "## General configuration\n# Element name\tProperty\tValue"

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
            if self.SpectraConfigChannelAxis.isChecked():
                fileContent += f"\nSpectraConfigChannelAxis\tChecked\tTrue"
            if self.SpectraConfigGrid.isChecked():
                fileContent += f"\nSpectraConfigGrid\tChecked\tTrue"

            # fileContent += f'\n\nResultsPath\tText\t{self.ResultsPath.text() if self.ResultsPath.text() else ""}'

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

            # fileContent += f'\n\nMapPath\tText\t{self.MapPath.text() if self.MapPath.text() else ""}'

            file.write(fileContent + "\n\n# -----\n\n")
            file.close()

            self.ROIsSave_clicked(False, fileName, 'a')

    def Analyse_clicked(self):
        resultsPath = pathlib.Path(self.ResultsPath.text())
        if not resultsPath.is_dir():
            QtWidgets.QMessageBox.warning(self, "Analyse", f"It is impossible to save output files on the path:\n{resultsPath}")
        elif resultsPath == pathlib.Path():
            QtWidgets.QMessageBox.warning(self, "Analyse", f"It is impossible to save output files on an empty path.")
        else:
            outputConfig = analyse.Analyse(self, self.OutputConfig, self.DetectorsSDD1.isChecked(), self.DetectorsSDD2.isChecked(), self.DetectorsSum.isChecked(), False)
            if outputConfig.exec():
                self.OutputConfig = outputConfig.Output
                self.Progress.setValue(0)
                self.Progress.setMaximum(len(self.OutputConfig.keys()) - 17) # 3 detectors buttons + 2 nesting combos + 3 normalization types + 7 display setting + 2 generates
                QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
                if self.ROIsDefault.isChecked(): ROI = self.Data["ROI"]
                else:
                    ROI = []
                    for row in range(self.ROIs.rowCount()):
                        ROI.append([self.ROIs.item(row, 0).text(), int(self.ROIs.item(row, 1).text()), int(self.ROIs.item(row, 2).text()), float(self.ROIs.item(row, 3).text())])
                if self.AreaChanged or self.PointChanged:
                    if self.LastChanged == "Area":
                        POS = PDA.real_pos([[self.AreaX1.value(), self.AreaZ1.value()], [self.AreaX2.value(), self.AreaZ2.value()]], self.Data["head"])
                    elif self.LastChanged == "Point":
                        POS = PDA.real_pos([[self.PointX.value(), self.PointZ.value()]], self.Data["head"])
                else:
                    POS = None
                vMin = None if self.MapsConfigValuesAuto.isChecked() else self.MapsConfigValuesStart.value()
                vMax = None if self.MapsConfigValuesAuto.isChecked() else self.MapsConfigValuesStop.value()
                mapAspect = 'auto' if self.MapsConfigAspectAuto.isChecked() else self.MapsConfigAspectValue.value()
                if self.Calib is not None:
                    eMin = 0.0 if self.SpectraConfigEnergyAuto.isChecked() else self.SpectraConfigEnergyStart.value()
                    eMax = self.monoE / 1000 + 1 if self.SpectraConfigEnergyAuto.isChecked() and self.monoE is not None else self.SpectraConfigEnergyStop.value() # widma do energii mono
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
                        if name == "DetectorsSDD1" and self.OutputConfig[name]: detectors.append(0)
                        if name == "DetectorsSDD2" and self.OutputConfig[name]: detectors.append(1)
                        if name == "DetectorsSum" and self.OutputConfig[name]: detectors.append(2)
                        if name == "Single": nestingType = analyse.NestingTypes[self.OutputConfig[name]]
                        if name == "GenWiatrowska": wiatrowska = self.OutputConfig[name]
                        if name == "GenHDF5": hdf5 = self.OutputConfig[name]
                        if name == "GenCsvs": csvs = self.OutputConfig[name]
                        continue
                    if name[:4] == "Disp":
                        display.update({ name[4:] : self.OutputConfig[name]})
                        continue
                    if name[:8] == "NormType":
                        if self.OutputConfig[name]: normType.append(name[8:])
                        continue
                    if self.OutputConfig[name]:
                        exec(f'analyse.{name}(self, self.Data, pathlib.Path(self.MapPath.text()), resultsPath, detectors, "{nestingType}", roi = ROI, pos = POS, calib = self.Calib, vmin = vMin, vmax = vMax, maspect = mapAspect, emin = eMin, emax = eMax, saspect = spectraAspect, cmap = cMap, normtype = normType, disp = display, csvs = csvs)')
                        if name == "NormROIs" and wiatrowska:
                            exec(f'analyse.{name}(self, self.Data, pathlib.Path(self.MapPath.text()), resultsPath, detectors, "W", roi = ROI, pos = POS, calib = self.Calib, vmin = vMin, vmax = vMax, maspect = mapAspect, emin = eMin, emax = eMax, saspect = spectraAspect, cmap = cMap, normtype = ["I0LT"], disp = display, csvs = csvs)')
                    self.Progress.setValue(self.Progress.value() + 1)
                if hdf5:
                    exec(f'analyse.HDF5(self, self.Data, pathlib.Path(self.MapPath.text()), resultsPath)')
                self.Progress.setValue(self.Progress.value() + 1)
                QtGui.QGuiApplication.restoreOverrideCursor()
                
                dialog = QtWidgets.QMessageBox(self)
                dialog.setIcon(QtWidgets.QMessageBox.Icon.Information)
                dialog.setWindowTitle("Analyse")
                dialog.setText(f"Analysis completed!")
                dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Open | QtWidgets.QMessageBox.StandardButton.Ok)
                button = dialog.button(QtWidgets.QMessageBox.StandardButton.Open)
                button.setText("Open folder")
                button.setMinimumWidth(100)
                dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Ok)
                dialog.exec()
                if dialog.clickedButton() == button:
                # dialog = QtWidgets.QMessageBox.information(self, "Analyse", f"Analysis completed!", QtWidgets.QMessageBox.StandardButton.Open | QtWidgets.QMessageBox.StandardButton.Ok, QtWidgets.QMessageBox.StandardButton.Ok)
                # if dialog == QtWidgets.QMessageBox.StandardButton.Open:
                    analyse.OpenDirectory(pathlib.Path(str(resultsPath) + str(os.sep) + "PXDA_Export"))

    def ResetAll_clicked(self):
        if QtWidgets.QMessageBox.question(self, "Single", f"Do you surely want to reset entire SINGLE tab?") == QtWidgets.QMessageBox.StandardButton.Yes:
            parent = self.parent()
            self.setParent(None)
            idx = parent.parent().insertTab(0, SingleWindow(), "SINGLE")
            parent.parent().setCurrentIndex(idx)

            parent.parent().parent().parent().Single = parent.parent().currentWidget()
            parent.parent().parent().parent().Single.doubleSpinBox_CalibrationGain.valueChanged.connect(lambda value, mode = "Single": parent.parent().parent().parent().setCalibration(value, mode))
            parent.parent().parent().parent().Single.doubleSpinBox_CalibrationZero.valueChanged.connect(lambda value, mode = "Single": parent.parent().parent().parent().setCalibration(value, mode))
            parent.parent().parent().parent().Single.doubleSpinBox_CalibrationNoise.valueChanged.connect(lambda value, mode = "Single": parent.parent().parent().parent().setCalibration(value, mode))
            parent.parent().parent().parent().Single.doubleSpinBox_CalibrationFano.valueChanged.connect(lambda value, mode = "Single": parent.parent().parent().parent().setCalibration(value, mode))
            parent.parent().parent().parent().setCalibration(None, "Batch")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())