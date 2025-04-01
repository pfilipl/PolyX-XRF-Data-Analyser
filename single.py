from PyQt6 import QtWidgets, uic
import sys, xraylib, matplotlib, numpy, scipy, math
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
matplotlib.use('QtAgg')

import main, add_roi, PDA

class MatplotlibCanvas(FigureCanvasQTAgg):
    def __init__(self, parent = None):
        self.Figure = matplotlib.figure.Figure(layout = 'compressed', dpi = 100)
        self.Axes = self.Figure.add_subplot(facecolor = "None")
        self.Axes.get_xaxis().set_visible(False)
        self.Axes.get_yaxis().set_visible(False)
        self.Figure.patch.set_facecolor("None")
        self.Axes2x = None
        self.Axes2y = None
        self.ColorBar = None
        super().__init__(self.Figure)

class RectangleDrawer:
    def __init__(self, rectangle):
        self.Rectangle = rectangle
        self.X = rectangle.get_x()
        self.Y = rectangle.get_y()
        self.CanvasID = rectangle.figure.canvas.mpl_connect('motion_notify_event', self)

    def __call__(self, event):
        if event.inaxes == self.Rectangle.axes:
            self.Rectangle.set_height(event.ydata - self.Y)
            self.Rectangle.set_width(event.xdata - self.X)
            self.Rectangle.figure.canvas.draw()

class SingleWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(SingleWindow, self).__init__(parent)
        uic.loadUi("single.ui", self)

        # Spectrum from map region
        self.SelectArea         = self.pushButton_SelectArea
        self.AreaX1             = self.doubleSpinBox_AreaX1
        self.AreaZ1             = self.doubleSpinBox_AreaZ1
        self.AreaX2             = self.doubleSpinBox_AreaX2
        self.AreaZ2             = self.doubleSpinBox_AreaZ2
        self.AreaEnabled        = False
        self.AreaChanged        = False
        self.MarkPoint          = self.pushButton_MarkPoint
        self.PointX             = self.doubleSpinBox_PointX
        self.PointZ             = self.doubleSpinBox_PointZ
        self.PointEnabled       = False
        self.PointChanged       = False
        self.LastChanged        = "area"

        self.AreaX1.valueChanged.connect(lambda value, mode = "area": self.Changed(value, mode))
        self.AreaZ1.valueChanged.connect(lambda value, mode = "area": self.Changed(value, mode))
        self.AreaX2.valueChanged.connect(lambda value, mode = "area": self.Changed(value, mode))
        self.AreaZ2.valueChanged.connect(lambda value, mode = "area": self.Changed(value, mode))
        self.PointX.valueChanged.connect(lambda value, mode = "point": self.Changed(value, mode))
        self.PointZ.valueChanged.connect(lambda value, mode = "point": self.Changed(value, mode))

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

        # Map & Spectrum
        self.Map                = self.tab_Map
        self.MapCanvas          = MatplotlibCanvas(self.Map)
        self.MapToolbar         = NavigationToolbar2QT(self.MapCanvas, self.Map)
        self.MapSumSignal       = None
        self.Spectrum           = self.tab_Spectrum
        self.SpectrumCanvas     = MatplotlibCanvas(self.Spectrum)
        self.SpectrumToolbar    = NavigationToolbar2QT(self.SpectrumCanvas, self.Spectrum)
        # self.SpectrumSumSignal  = None
        self.Head               = None
        self.LastPressedX       = None
        self.LastPressedZ       = None
        self.LastReleasedX      = None
        self.LastReleasedZ      = None
        self.LastMotionX        = None
        self.LastMotionZ        = None
        self.Rectangle          = matplotlib.patches.Rectangle((0, 0), 0, 0, linewidth = 1, linestyle = '-', edgecolor = 'r', facecolor = 'none')

        self.MapCanvas.setStyleSheet("background-color:transparent;")
        mapLayout = QtWidgets.QVBoxLayout()
        mapLayout.addWidget(self.MapCanvas)
        mapLayout.addWidget(self.MapToolbar)
        self.Map.setLayout(mapLayout)
        self.MapCanvas.mpl_connect("button_press_event", self.MatplotlibButtonPressed)
        self.MapCanvas.mpl_connect("button_release_event", self.MatplotlibButtonReleased)
        self.MapCanvas.mpl_connect("motion_notify_event", self.MatplotlibMouseMotion)

        self.SpectrumCanvas.setStyleSheet("background-color:transparent;")
        spectrumLayout = QtWidgets.QVBoxLayout()
        spectrumLayout.addWidget(self.SpectrumCanvas)
        spectrumLayout.addWidget(self.SpectrumToolbar)
        self.Spectrum.setLayout(spectrumLayout)

        # Map path
        self.MapPath            = self.lineEdit_MapPath

        self.MapPath.editingFinished.connect(self.Load)
        self.toolButton_MapPathSearch.clicked.connect(self.MapPathSearch_clicked)

        # Results
        self.ResultsPath        = self.lineEdit_ResultsPath

        self.toolButton_ResultsPathSearch.clicked.connect(self.ResultsPathSearch_clicked)

        # Detectors
        self.DetectorsBe        = self.pushButton_DetectorsBe
        self.DetectorsML        = self.pushButton_DetectorsML
        self.DetectorsSum       = self.pushButton_DetectorsSum

        # Energy calibration
        self.Calib              = None
        self.Sigma              = None

        self.CalibrationGain    = self.doubleSpinBox_CalibrationGain
        self.CalibrationZero    = self.doubleSpinBox_CalibrationZero
        self.CalibrationNoise   = self.doubleSpinBox_CalibrationNoise
        self.CalibrationFano    = self.doubleSpinBox_CalibrationFano

        # Process
        self.Progress           = self.progressBar_Progress
        self.ReloadMap          = self.pushButton_ReloadMap
        self.AnalyseMap         = self.pushButton_AnalyseMap

        self.pushButton_ReloadMap.clicked.connect(self.ReloadMap_clicked)
        self.pushButton_ImportConfig.clicked.connect(lambda clicked, fileName = None: self.ImportConfig_clicked(clicked, fileName))
        self.pushButton_SaveConfig.clicked.connect(lambda clicked, fileName = None: self.SaveConfig_clicked(clicked, fileName))
        self.pushButton_AnalyseMap.clicked.connect(self.AnalyseMap_clicked)

        # Help
        self.Help               = self.label_Help
        self.HelpDescription    = self.label_HelpDescription
        
        self.Help.hide()
        self.HelpDescription.hide()

    def setCalibration(self, calib, sigma):
        self.Calib = calib
        self.Sigma = sigma

    def MatplotlibButtonPressed(self, event):
        if self.MarkPoint.isChecked() or self.SelectArea.isChecked():
            if event.inaxes == self.MapCanvas.Axes:
                self.LastPressedX = event.xdata
                self.LastPressedZ = event.ydata
                self.Rectangle.set_xy((self.LastPressedX - 1, self.LastPressedZ - 1))
                self.Rectangle.set_height(3)
                self.Rectangle.set_width(3)
                self.MapCanvas.Axes.add_patch(self.Rectangle)
                self.MapCanvas.draw()
                self.MarkPoint.setChecked(False)

    def MatplotlibButtonReleased(self, event):
        if self.SelectArea.isChecked():
            if event.inaxes == self.MapCanvas.Axes:
                self.LastReleasedX = event.xdata
                self.LastReleasedZ = event.ydata
            else:
                self.LastReleasedX = self.LastMotionX
                self.LastReleasedZ = self.LastMotionZ
                self.LastMotionX = None
                self.LastMotionZ = None
            # self.Rectangle.set_height(self.LastReleasedZ + 1 - self.Rectangle.get_y())
            # self.Rectangle.set_width(self.LastReleasedX + 1 - self.Rectangle.get_x())
            # self.MapCanvas.draw()
            self.SelectArea.setChecked(False)

    def MatplotlibMouseMotion(self, event):
        if self.SelectArea.isChecked() and self.LastPressedX is not None and self.LastPressedZ is not None:
            if event.inaxes == self.MapCanvas.Axes:
                self.LastMotionX = event.xdata
                self.LastMotionZ = event.ydata
                self.Rectangle.set_height(self.LastMotionZ + 1 - self.Rectangle.get_y())
                self.Rectangle.set_width(self.LastMotionX + 1 - self.Rectangle.get_x())
                self.MapCanvas.draw()

    def Changed(self, value, mode):
        if mode == "area":
            self.AreaChanged = True
            self.LastChanged = "area"
        elif mode == "point":
            self.PointChanged = True
            self.LastChanged = "point"

    def Load(self, roiStart = 0, roiStop = 4096, pos = [[0, 0], [1000, 1000]], Emin = 0.0, Emax = None, roi = None, peaks = True, startLoad = True):
        map = self.MapCanvas
        spectrum = self.SpectrumCanvas
        path = self.MapPath.text()

        try:
            head, Data, ICR, OCR, RT, LT, DT, PIN, I0, RC, ROI = PDA.data_load(path)
        except:
            if path == "":
                QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map under the empty path.")
            else:
                QtWidgets.QMessageBox.warning(self, "Map loading", f"It is impossible to load the map under the path:\n{path}")
        else:
            self.Head = head
            data = Data[2]
            sumSignal = numpy.sum(data[:, :, roiStart:roiStop], axis=2)
            self.MapSumSignal = sumSignal
            if map.ColorBar: map.ColorBar.remove()
            map.Axes.cla()
            imgMap = map.Axes.imshow(sumSignal.transpose(), origin = 'upper', cmap = 'viridis', aspect = 'equal')
            map.Axes.get_xaxis().set_visible(False)
            map.Axes.get_yaxis().set_visible(False)

            map.Axes2x = map.Axes.secondary_xaxis('bottom', transform = map.Axes.transData)
            map.Axes2x.set_xticks(numpy.linspace(0, data.shape[0] - 1, len(map.Axes.get_xticks()) - 2))
            map.Axes2x.set_xticklabels(numpy.linspace(head["Xpositions"][0, 0], head["Xpositions"][0, -1], len(map.Axes2x.get_xticks())))
            map.Axes2x.set_xlabel("X [mm]")

            map.Axes2y = map.Axes.secondary_yaxis('left', transform = map.Axes.transData)
            map.Axes2y.set_yticks(numpy.linspace(0, data.shape[1] - 1, len(map.Axes.get_yticks()) - 2))
            map.Axes2y.set_yticklabels(numpy.linspace(head["Zpositions"][0, 0], head["Zpositions"][0, -1], len(map.Axes2y.get_yticks())))
            map.Axes2y.set_ylabel("Z [mm]")

            map.ColorBar = map.figure.colorbar(imgMap)
            map.ColorBar.set_ticks(numpy.linspace(numpy.min(sumSignal), numpy.max(sumSignal), len(map.ColorBar.get_ticks()) - 2))
            
            if self.AreaChanged or self.PointChanged:
                if isinstance(pos, list):
                    pos = numpy.array(pos)
                PDA.check_pos(pos, [data.shape[0], data.shape[1]])
                if pos.shape[0] == 1:
                    x0 = pos[0, 0]
                    z0 = pos[0, 1]
                    map.Axes.add_patch(matplotlib.patches.Rectangle((x0 - 1, z0 - 1), 3, 3, linewidth = 1, linestyle = '--', edgecolor = 'r', facecolor = 'none'))
                elif pos.shape[0] == 2:
                    x0 = min(pos[0, 0], pos[1, 0])
                    z0 = min(pos[0, 1], pos[1, 1])
                    x1 = max(pos[0, 0], pos[1, 0])
                    z1 = max(pos[0, 1], pos[1, 1])
                    map.Axes.add_patch(matplotlib.patches.Rectangle((x0 - 1, z0 - 1), x1 - x0 + 2, z1 - z0 + 2, linewidth = 1, linestyle = '--', edgecolor = 'r', facecolor = 'none'))
                else:
                    print("Invalid pos!")
                        
            map.draw()

            spectrum.Axes.cla()
            if self.Calib is not None:
                cEmin = (numpy.abs(self.Calib - Emin * 1000)).argmin() - 1
                if Emax is None:
                    Emax = self.Calib[-1] / 1000
                    cEmax = head["bins"][0, 0] - 1
                else:
                    cEmax = (numpy.abs(self.Calib - Emax * 1000)).argmin() + 1
            if isinstance(pos, list):
                pos = numpy.array(pos)
            PDA.check_pos(pos, [data.shape[0], data.shape[1]])
            if pos.shape[0] == 1:
                x0 = pos[0, 0]
                z0 = pos[0, 1]
                x1 = pos[0, 0]
                z1 = pos[0, 1]
            elif pos.shape[0] == 2:
                x0 = min(pos[0, 0], pos[1, 0])
                z0 = min(pos[0, 1], pos[1, 1])
                x1 = max(pos[0, 0], pos[1, 0])
                z1 = max(pos[0, 1], pos[1, 1])
            for d in range(len(Data)):
                data = Data[d]
                if x1 > x0 and z1 > z0:
                    sumData = data[x0:x1, z0:z1, :]
                    sumData = numpy.sum(numpy.sum(sumData, axis = 0), axis = 0)
                elif x1 == x0 and z1 > z0:
                    sumData = data[x0, z0:z1, :]
                    sumData = numpy.sum(sumData, axis = 0)
                elif x1 > x0 and z1 == z0:
                    sumData = data[x0:x1, z0, :]
                    sumData = numpy.sum(sumData, axis = 0)
                else:
                    sumData = data[x0, z0, :]
                imgSpectrum = spectrum.Axes.plot(sumData, label = PDA.detectors[d])
            spectrum.Axes.set_yscale('log')
            spectrum.Axes.get_xaxis().set_visible(True)
            spectrum.Axes.get_yaxis().set_visible(True)
            if self.AreaChanged or self.PointChanged:
                if pos.shape[0] == 1: spectrum.Axes.set_title(f"pos = [{self.PointX.value()} mm, {self.PointZ.value()} mm]")
                elif pos.shape[0] == 2: spectrum.Axes.set_title(f"pos = [[{self.AreaX1.value()} mm, {self.AreaZ1.value()} mm], [{self.AreaX2.value()} mm, {self.AreaZ2.value()} mm]]")

            if self.Calib is not None:
                spectrum.Axes.set_ylim([1, numpy.max(numpy.sum(numpy.sum(data[x0:x1, z0:z1, cEmin:cEmax], axis = 0), axis = 0)) * 1.5])
            else:
                spectrum.Axes.set_ylim([1, numpy.max(sumData) * 1.5])

            if roi is None and self.ROIsDefault.isChecked(): roi = ROI
            elif roi is None:
                roi = []
                for row in range(self.ROIs.rowCount()):
                    roi.append([self.ROIs.item(row, 0).text(), int(self.ROIs.item(row, 1).text()), int(self.ROIs.item(row, 2).text()), float(self.ROIs.item(row, 3).text())])

            if roi is not None:
                for i in range(len(roi)):
                    if roi[i][0] != 'Total signal':
                        spectrum.Axes.add_patch(matplotlib.patches.Rectangle((roi[i][1], 0), roi[i][2] - roi[i][1], 1, facecolor = 'r', alpha = 0.2, transform = spectrum.Axes.get_xaxis_transform()))
                        if self.Calib is not None:
                            if roi[i][1] + (roi[i][2] - roi[i][1]) / 2 > cEmin and roi[i][1] + (roi[i][2] - roi[i][1]) / 2 < cEmax:
                                spectrum.Axes.text(roi[i][1] + (roi[i][2] - roi[i][1]) / 2, 0.7, roi[i][0], ha = 'center', rotation = 'vertical', transform = spectrum.Axes.get_xaxis_transform())
                        else:
                            spectrum.Axes.text(roi[i][1] + (roi[i][2] - roi[i][1]) / 2, 0.7, roi[i][0], ha = 'center', rotation = 'vertical', transform = spectrum.Axes.get_xaxis_transform())

            if peaks is not None:
                if isinstance(peaks, bool):
                    if peaks:
                        xP = scipy.signal.find_peaks(sumData, height = 1e-5 * numpy.max(sumData), width = 10)
                        for xp in xP[0]:
                            if self.Calib is not None:
                                if  xp > (numpy.abs(self.Calib - 0)).argmin() + 50:
                                    spectrum.Axes.add_artist(matplotlib.lines.Line2D([xp, xp], [0, sumData[xp]], 1.0, '-', 'C2'))
                                    if xp > cEmin and xp < cEmax:
                                        ka = PDA.Energies['symbol'][(numpy.abs(PDA.Energies['Ka'] - self.Calib[xp] / 1000)).argmin()]
                                        kb = PDA.Energies['symbol'][(numpy.abs(PDA.Energies['Kb'] - self.Calib[xp] / 1000)).argmin()]
                                        la = PDA.Energies['symbol'][(numpy.abs(PDA.Energies['La'] - self.Calib[xp] / 1000)).argmin()]
                                        lb = PDA.Energies['symbol'][(numpy.abs(PDA.Energies['Lb'] - self.Calib[xp] / 1000)).argmin()]
                                        spectrum.Axes.text(xp, 0.05, ka, ha = 'right', rotation = 'vertical', color = 'C4', transform = spectrum.Axes.get_xaxis_transform())
                                        spectrum.Axes.text(xp, 0.12, kb, ha = 'right', rotation = 'vertical', color = 'C6', transform = spectrum.Axes.get_xaxis_transform())
                                        spectrum.Axes.text(xp, 0.20, la, ha = 'right', rotation = 'vertical', color = 'C5', transform = spectrum.Axes.get_xaxis_transform())
                                        spectrum.Axes.text(xp, 0.27, lb, ha = 'right', rotation = 'vertical', color = 'C7', transform = spectrum.Axes.get_xaxis_transform())
                            else:
                                spectrum.Axes.add_artist(matplotlib.lines.Line2D([xp, xp], [0, sumData[xp]], 1.0, '-', 'C2'))
                        if self.Calib is not None:
                            spectrum.Axes.text(0.05, 0.75, "Ka", ha = 'left', color = 'C4', transform = spectrum.Axes.transAxes)
                            spectrum.Axes.text(0.05, 0.80, "Kb", ha = 'left', color = 'C6', transform = spectrum.Axes.transAxes)
                            spectrum.Axes.text(0.05, 0.85, "La", ha = 'left', color = 'C5', transform = spectrum.Axes.transAxes)
                            spectrum.Axes.text(0.05, 0.90, "Lb", ha = 'left', color = 'C7', transform = spectrum.Axes.transAxes)
                elif self.Calib is not None:
                    for name in peaks:
                        if name != 'Total signal':
                            try: 
                                element = xraylib.SymbolToAtomicNumber(name.split("-")[-2])
                            except:
                                print("Unknown element symbol!")
                                continue
                            line = name.split("-")[-1]
                            if line == "Ka":
                                line = xraylib.KA_LINE
                            elif line == "Kb":
                                line = xraylib.KB_LINE
                            elif line == "La":
                                line = xraylib.LA_LINE
                            elif line == "Lb":
                                line = xraylib.LB_LINE
                            else:
                                print("Unknown line symbol!")
                                continue
                            xp = (numpy.abs(self.Calib - xraylib.LineEnergy(element, line) * 1000)).argmin()
                            spectrum.Axes.add_artist(matplotlib.lines.Line2D([xp, xp], [0, 0.5], 1.0, '-', 'red', transform = spectrum.Axes.get_xaxis_transform()))
                            if xp > cEmin and xp < cEmax:
                                spectrum.Axes.text(xp, 0.55, name, ha = 'center', rotation = 'vertical', color = 'red', transform = spectrum.Axes.get_xaxis_transform())
            
            spectrum.Axes.legend(loc = "upper right", ncols = len(Data), facecolor = "None", edgecolor = "None")
            
            if self.Calib is None:
                spectrum.Axes.set_xlim([0, head["bins"][0, 0]])
                spectrum.Axes.set_xticks(range(0, head["bins"][0, 0] + 1, math.floor(head["bins"][0, 0]/4)))
                spectrum.Axes.set_xlabel("channel")
            else:
                spectrum.Axes.get_xaxis().set_visible(False)
                spectrum.Axes2x = spectrum.Axes.secondary_xaxis('bottom', transform = spectrum.Axes.transData)
                spectrum.Axes.set_xlim([cEmin, cEmax])
                Eval = numpy.linspace(Emin * 1000, Emax * 1000, len(spectrum.Axes.get_xticks()) - 2)
                E = []
                for eval in Eval:
                    E.append((numpy.abs(self.Calib - eval)).argmin())
                spectrum.Axes2x.set_xticks(E)
                spectrum.Axes2x.set_xticklabels(numpy.abs(numpy.round(self.Calib[E] / 1000, 2)))
                spectrum.Axes2x.set_xlabel("E [keV]")

            spectrum.draw()

            self.AreaX1.setMinimum(min(head["Xpositions"][0, :]))
            self.AreaX2.setMinimum(min(head["Xpositions"][0, :]))
            self.AreaZ1.setMinimum(min(head["Zpositions"][0, :]))
            self.AreaZ2.setMinimum(min(head["Zpositions"][0, :]))

            self.AreaX1.setMaximum(max(head["Xpositions"][0, :]))
            self.AreaX2.setMaximum(max(head["Xpositions"][0, :]))
            self.AreaZ1.setMaximum(max(head["Zpositions"][0, :]))
            self.AreaZ2.setMaximum(max(head["Zpositions"][0, :]))

            if self.AreaEnabled:
                if self.AreaX1.value() != min(head["Xpositions"][0, :]): self.Changed(None, "area")
                if self.AreaX2.value() != max(head["Xpositions"][0, :]): self.Changed(None, "area")
                if self.AreaZ1.value() != min(head["Zpositions"][0, :]): self.Changed(None, "area")
                if self.AreaZ2.value() != max(head["Zpositions"][0, :]): self.Changed(None, "area")
            
            if not self.AreaChanged or startLoad:
                self.AreaX1.blockSignals(True)
                self.AreaX2.blockSignals(True)
                self.AreaZ1.blockSignals(True)
                self.AreaZ2.blockSignals(True)

                self.AreaX1.setValue(min(head["Xpositions"][0, :]))
                self.AreaX2.setValue(max(head["Xpositions"][0, :]))
                self.AreaZ1.setValue(min(head["Zpositions"][0, :]))
                self.AreaZ2.setValue(max(head["Zpositions"][0, :]))

                self.AreaX1.blockSignals(False)
                self.AreaX2.blockSignals(False)
                self.AreaZ1.blockSignals(False)
                self.AreaZ2.blockSignals(False)

            self.PointX.setMinimum(min(head["Xpositions"][0, :]))
            self.PointZ.setMinimum(min(head["Zpositions"][0, :]))

            self.PointX.setMaximum(max(head["Xpositions"][0, :]))
            self.PointZ.setMaximum(max(head["Zpositions"][0, :]))

            if self.PointEnabled:
                if self.PointX.value() != min(head["Xpositions"][0, :]): self.Changed(None, "point")
                if self.PointZ.value() != min(head["Zpositions"][0, :]): self.Changed(None, "point")

            if not self.PointChanged or startLoad:
                self.PointX.blockSignals(True)
                self.PointZ.blockSignals(True)

                self.PointX.setValue(min(head["Xpositions"][0, :]))
                self.PointZ.setValue(min(head["Zpositions"][0, :]))

                self.PointX.blockSignals(False)
                self.PointZ.blockSignals(False)

            if not self.ReloadMap.isEnabled(): self.ReloadMap.setEnabled(True)
            if not self.AreaEnabled:
                self.AreaX1.setEnabled(True)
                self.AreaZ1.setEnabled(True)
                self.AreaX2.setEnabled(True)
                self.AreaZ2.setEnabled(True)
                self.AreaEnabled = True
            if not self.PointEnabled:
                self.PointX.setEnabled(True)
                self.PointZ.setEnabled(True)
                self.PointEnabled = True
            if not self.pushButton_MarkPoint.isEnabled(): self.pushButton_MarkPoint.setEnabled(True)
            if not self.pushButton_SelectArea.isEnabled(): self.pushButton_SelectArea.setEnabled(True)
    
    def Reload(self):
        if self.ROIsDefault.isChecked(): ROI = None
        else:
            ROI = []
            for row in range(self.ROIs.rowCount()):
                ROI.append([self.ROIs.item(row, 0).text(), int(self.ROIs.item(row, 1).text()), int(self.ROIs.item(row, 2).text()), float(self.ROIs.item(row, 3).text())])
        if self.AreaChanged or self.PointChanged:
            if self.LastChanged == "area":
                POS = PDA.real_pos([[self.AreaX1.value(), self.AreaZ1.value()], [self.AreaX2.value(), self.AreaZ2.value()]], self.Head)
            elif self.LastChanged == "point":
                POS = PDA.real_pos([[self.PointX.value(), self.PointZ.value()]], self.Head)
        else:
            POS = [[0, 0], [1000, 1000]]
        
        self.Load(0, 4096, POS, roi = ROI, startLoad = False)
    
    def MarkPoint_toggled(self, checked):
        if not checked:
            if self.LastPressedX is not None and self.LastPressedZ is not None:
                self.PointX.setValue(self.Head["Xpositions"][0, round(self.LastPressedX)])
                self.PointZ.setValue(self.Head["Zpositions"][0, round(self.LastPressedZ)])
                self.LastPressedX = None
                self.LastPressedZ = None
        else:
            if self.SelectArea.isChecked(): 
                self.SelectArea.blockSignals(True)
                self.SelectArea.setChecked(False)
                self.SelectArea.blockSignals(False)

    def SelectArea_toggled(self, checked):
        if not checked:
            if self.LastPressedX is not None and self.LastPressedZ is not None and self.LastReleasedX is not None and self.LastReleasedZ is not None:
                self.AreaX1.setValue(self.Head["Xpositions"][0, round(self.LastPressedX)])
                self.AreaZ1.setValue(self.Head["Zpositions"][0, round(self.LastPressedZ)])
                self.AreaX2.setValue(self.Head["Xpositions"][0, round(self.LastReleasedX)])
                self.AreaZ2.setValue(self.Head["Zpositions"][0, round(self.LastReleasedZ)])
                self.LastPressedX = None
                self.LastPressedZ = None
                self.LastReleasedX = None
                self.LastReleasedZ = None
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
        self.Load()

    def ROIsAdd_clicked(self):
        self.ROIsDefault.setChecked(False)
        addroi = add_roi.AddRoi(self, self.Calib, self.Sigma, self.RoiCount)
        table = addroi.tableWidget_CustomROIs
        for row in range(self.ROIs.rowCount()):
            table.insertRow(table.currentRow() + 1)
            table.setItem(table.currentRow() + 1, 0, QtWidgets.QTableWidgetItem(f"{self.ROIs.item(row, 0).text()}"))
            try:
                name = self.ROIs.item(row, 0).text().split("-")
                if name[1] == "Ka": addroi.tab_Kalpha.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "Kb": addroi.tab_Kbeta.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "La": addroi.tab_Lalpha.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "Lb": addroi.tab_Lbeta.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
                elif name[1] == "M": addroi.tab_M.setElementChecked(xraylib.SymbolToAtomicNumber(name[0]), True)
            except:
                continue
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
            self.ROIs.removeRow(row)
    
    def ROIsDeleteAll_clicked(self):
        self.ROIs.setCurrentCell(0, 0)
        while self.ROIs.rowCount() > 0:
            self.ROIs.removeRow(self.ROIs.currentRow())
    
    def MapPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Map path", self.MapPath.text())
        if path:
            self.MapPath.blockSignals(True)
            self.MapPath.setText(path)
            self.MapPath.blockSignals(False)
            self.Load()
    
    def ResultsPathSearch_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Results path", self.ResultsPath.text())
        if path:
            self.ResultsPath.setText(path)
    
    def ReloadMap_clicked(self):
        self.Reload()
    
    def ImportConfig_clicked(self, clicked, fileName):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Single config", self.ResultsPath.text(), "PDA Files(*.PDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:
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

                    if variableName in ["MapPath", "AreaX1", "AreaX2", "AreaZ1", "AreaZ2", "PointX", "PointZ"]:
                        exec(f'self.{variableName}.blockSignals(True)')
                    if property == "Text": 
                        exec(f'self.{variableName}.set{property}("{value if value else ""}")')
                    else: 
                        exec(f'self.{variableName}.set{property}({value})')
                    if variableName in ["MapPath", "AreaX1", "AreaX2", "AreaZ1", "AreaZ2", "PointX", "PointZ"]:
                        exec(f'self.{variableName}.blockSignals(False)')
            file.close()
            self.ROIsImport_clicked(False, fileName, False)
            self.Reload()
    
    def SaveConfig_clicked(self, clicked, fileName):
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Single config", self.ResultsPath.text(), "PDA Files(*.PDAconfig);; Text files(*.dat *.txt);; All files(*)")
        if fileName:
            file = open(fileName, 'w')
            fileContent = "## General configuration\n# Element name\tProperty\tValue"

            fileContent += f"\n\nROIsDefault\tChecked\t{self.ROIsDefault.isChecked()}"

            fileContent += f'\n\nResultsPath\tText\t{self.ResultsPath.text() if self.ResultsPath.text() else ""}'

            fileContent += f"\n\nDetectorsBe\tChecked\t{self.DetectorsBe.isChecked()}"
            fileContent += f"\nDetectorsML\tChecked\t{self.DetectorsML.isChecked()}"
            fileContent += f"\nDetectorsSum\tChecked\t{self.DetectorsSum.isChecked()}"

            fileContent += f"\n\nCalibrationGain\tValue\t{self.CalibrationGain.value()}"
            fileContent += f"\nCalibrationZero\tValue\t{self.CalibrationZero.value()}"
            fileContent += f"\nCalibrationNoise\tValue\t{self.CalibrationNoise.value()}"
            fileContent += f"\nCalibrationFano\tValue\t{self.CalibrationFano.value()}"

            fileContent += "\n\n# -----\n\n## Single configuration\n# Element name\tProperty\tValue"

            if self.AreaChanged:
                fileContent += f"\n\nAreaX1\tValue\t{self.AreaX1.value()}"
                fileContent += f"\nAreaZ1\tValue\t{self.AreaZ1.value()}"
                fileContent += f"\nAreaX2\tValue\t{self.AreaX2.value()}"
                fileContent += f"\nAreaZ2\tValue\t{self.AreaZ2.value()}"
            if self.PointChanged:
                fileContent += f"\nPointX\tValue\t{self.PointX.value()}"
                fileContent += f"\nPointZ\tValue\t{self.PointZ.value()}"

            fileContent += f'\n\nMapPath\tText\t{self.MapPath.text() if self.MapPath.text() else ""}'

            file.write(fileContent + "\n\n# -----\n\n")
            file.close()

            self.ROIsSave_clicked(False, fileName, 'a')

    def AnalyseMap_clicked(self):
        return
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())