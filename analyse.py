from PyQt6 import QtWidgets, QtCore, uic, QtGui
import sys, os, numpy, itertools, subprocess, pathlib, h5py
import matplotlib.pyplot as plt

import main, PDA

basedir = pathlib.Path(os.path.dirname(__file__))

def OpenDirectory(path):
    try: os.startfile(path)
    except: subprocess.Popen(['xdg-open', path])

class Analyse(QtWidgets.QDialog):
    def __init__(self, parent = None, outputConfig = None, detectorsSDD1 = True, detectorsSDD2 = True, detectorsSum = False, batch = False):
        super(Analyse, self).__init__(parent)
        uic.loadUi(basedir / "analyse.ui", self)
        self.setWindowTitle('Choose output data')

        if batch: self.comboBox_Single.hide()
        else: self.comboBox_Batch.hide()

        if outputConfig is None:
            self.Output = {
                "DetectorsSDD1"     : detectorsSDD1,
                "DetectorsSDD2"     : detectorsSDD2,
                "DetectorsSum"      : detectorsSum,
                "Single"            : "Output type > Output",
                "Batch"             : "Experiment/Load > Map > Output type > Output",
                "NormTypeI0LT"      : True,
                "NormTypeI0"        : False,
                "NormTypeLT"        : False,
                "DispSelected"      : True,
                "DispSimpTitles"    : False,
                "DispTitles"        : True,
                "DispColorbars"     : True,
                "DispAxes"          : True,
                "DispChannelAxis"   : False,
                "DispGrid"          : False,
                "GenCsvs"           : False,
                "GenHDF5"           : False,
                "GenWiatrowska"     : False,
                "DiagRC"            : True,
                "DiagSum"           : True,
                "DiagMax"           : True,
                "DiagI0"            : True,
                "DiagLT"            : True,
                "DiagDT"            : True,
                "DiagRT"            : False,
                "DiagICR"           : False,
                "DiagOCR"           : False,
                "UNormPIN"          : True,
                "UNormTotal"        : True,
                "UNormROIs"         : True,
                "UNormTabular"      : False,
                "NormPIN"           : False,
                "NormTotal"         : True,
                "NormROIs"          : True,
                "NormTabular"       : False,
                "SpectraSumROIs"    : True,
                "SpectraMaxROIs"    : False,
                "SpectraSum"        : False,
                "SpectraMax"        : False
            }
        else:
            self.Output = outputConfig

        self.checkBox_DiagRC.checkStateChanged.connect(lambda state, mode = "DiagRC": self.CheckOutputs(state, mode))
        self.checkBox_DiagSum.checkStateChanged.connect(lambda state, mode = "DiagSum": self.CheckOutputs(state, mode))
        self.checkBox_DiagMax.checkStateChanged.connect(lambda state, mode = "DiagMax": self.CheckOutputs(state, mode))
        self.checkBox_DiagI0.checkStateChanged.connect(lambda state, mode = "DiagI0": self.CheckOutputs(state, mode))
        self.checkBox_DiagLT.checkStateChanged.connect(lambda state, mode = "DiagLT": self.CheckOutputs(state, mode))
        self.checkBox_DiagDT.checkStateChanged.connect(lambda state, mode = "DiagDT": self.CheckOutputs(state, mode))
        self.checkBox_DiagRT.checkStateChanged.connect(lambda state, mode = "DiagRT": self.CheckOutputs(state, mode))
        self.checkBox_DiagICR.checkStateChanged.connect(lambda state, mode = "DiagICR": self.CheckOutputs(state, mode))
        self.checkBox_DiagOCR.checkStateChanged.connect(lambda state, mode = "DiagOCR": self.CheckOutputs(state, mode))
        self.checkBox_UNormPIN.checkStateChanged.connect(lambda state, mode = "UNormPIN": self.CheckOutputs(state, mode))
        self.checkBox_UNormTotal.checkStateChanged.connect(lambda state, mode = "UNormTotal": self.CheckOutputs(state, mode))
        self.checkBox_UNormROIs.checkStateChanged.connect(lambda state, mode = "UNormROIs": self.CheckOutputs(state, mode))
        self.checkBox_UNormTabular.checkStateChanged.connect(lambda state, mode = "UNormTabular": self.CheckOutputs(state, mode))
        self.checkBox_NormPIN.checkStateChanged.connect(lambda state, mode = "NormPIN": self.CheckOutputs(state, mode))
        self.checkBox_NormTotal.checkStateChanged.connect(lambda state, mode = "NormTotal": self.CheckOutputs(state, mode))
        self.checkBox_NormROIs.checkStateChanged.connect(lambda state, mode = "NormROIs": self.CheckOutputs(state, mode))
        self.checkBox_NormTabular.checkStateChanged.connect(lambda state, mode = "NormTabular": self.CheckOutputs(state, mode))
        self.checkBox_SpectraSumROIs.checkStateChanged.connect(lambda state, mode = "SpectraSumROIs": self.CheckOutputs(state, mode))
        self.checkBox_SpectraMaxROIs.checkStateChanged.connect(lambda state, mode = "SpectraMaxROIs": self.CheckOutputs(state, mode))
        self.checkBox_SpectraSum.checkStateChanged.connect(lambda state, mode = "SpectraSum": self.CheckOutputs(state, mode))
        self.checkBox_SpectraMax.checkStateChanged.connect(lambda state, mode = "SpectraMax": self.CheckOutputs(state, mode))

        for name in self.Output.keys():
            if name.startswith("Detectors"):
                exec(f'self.pushButton_{name}.setChecked(self.Output["{name}"])')
            elif name in ["Single", "Batch"]:
                exec(f'self.comboBox_{name}.setCurrentIndex(self.comboBox_{name}.findText("{self.Output[name]}", QtCore.Qt.MatchFlag.MatchExactly))')
            else:
                exec(f'self.checkBox_{name}.setChecked(self.Output["{name}"])')

        self.checkBox_Diag.checkStateChanged.connect(lambda state, mode = "Diag": self.CheckOutputs(state, mode))
        self.checkBox_UNorm.checkStateChanged.connect(lambda state, mode = "UNorm": self.CheckOutputs(state, mode))
        self.checkBox_Norm.checkStateChanged.connect(lambda state, mode = "Norm": self.CheckOutputs(state, mode))
        self.checkBox_Spectra.checkStateChanged.connect(lambda state, mode = "Spectra": self.CheckOutputs(state, mode))
        self.checkBox_NormTotal.toggled.connect(self.NormTypeChanged)
        self.checkBox_NormROIs.toggled.connect(self.NormTypeChanged)
        self.checkBox_NormTabular.toggled.connect(self.NormTypeChanged)
        self.checkBox_NormTypeI0LT.toggled.connect(self.NormTypeChanged)
        self.checkBox_NormTypeI0.toggled.connect(self.NormTypeChanged)
        self.checkBox_NormTypeLT.toggled.connect(self.NormTypeChanged)
        self.checkBox_DispTitles.toggled.connect(lambda checked, mode = "Simp": self.TitlesChanged(checked, mode))        
        self.checkBox_DispSimpTitles.toggled.connect(lambda checked, mode = "": self.TitlesChanged(checked, mode))        
        self.buttonBox.clicked.connect(self.ButtonBox_clicked)

        self.label_Nesting.hide()
        self.comboBox_Single.hide()
        self.comboBox_Batch.hide()
        self.setFixedHeight(490)

    def CheckOutputs(self, state, mode):
        if mode in ["Diag", "UNorm", "Norm", "Spectra"]:
            if state != QtCore.Qt.CheckState.PartiallyChecked:
                for name in self.Output.keys():
                    if name.startswith(mode) and not name.startswith("NormType"):
                        exec(f'self.checkBox_{name}.blockSignals(True)')
                        exec(f'self.checkBox_{name}.setCheckState(QtCore.Qt.{state})')
                        exec(f'self.checkBox_{name}.blockSignals(False)')
            else:
                exec(f'self.checkBox_{mode}.setCheckState(QtCore.Qt.CheckState.Checked)')
        else:
            if mode.startswith(("Diag", "Norm")):
                tMode = mode[:4]
            elif mode.startswith("UNorm"):
                tMode = mode[:5]
            elif mode.startswith("Spectra"):
                tMode = mode[:7]
            flag = False
            exec(f'self.checkBox_{tMode}.blockSignals(True)')
            for name in self.Output.keys():
                if name.startswith(tMode) and name != mode and (not name.startswith("NormType")):
                    exec_code = f'''
if self.checkBox_{name}.checkState() != QtCore.Qt.{state}:
    if self.checkBox_{tMode}.checkState() != QtCore.Qt.CheckState.PartiallyChecked: 
        self.checkBox_{tMode}.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
    flag = True
                    '''
                    localdict = locals()
                    exec(exec_code, locals = localdict)
                    flag = localdict['flag']
                    if flag:
                        break
            exec(f'if not flag: self.checkBox_{tMode}.setCheckState(QtCore.Qt.{state})')
            exec(f'self.checkBox_{tMode}.blockSignals(False)')

    def NormTypeChanged(self, checked):
        output = self.checkBox_NormTotal.isChecked() or self.checkBox_NormROIs.isChecked() or self.checkBox_NormTabular.isChecked()
        normalization = self.checkBox_NormTypeI0LT.isChecked() or self.checkBox_NormTypeI0.isChecked() or self.checkBox_NormTypeLT.isChecked()
        if output and not normalization:
            self.checkBox_NormTypeI0LT.blockSignals(True)
            self.checkBox_NormTypeI0LT.setChecked(True)
            self.checkBox_NormTypeI0LT.blockSignals(False)

    def TitlesChanged(self, checked, mode):
        exec(f"if checked and self.checkBox_Disp{mode}Titles.isChecked(): self.checkBox_Disp{mode}Titles.setChecked(False)")

    def ButtonBox_clicked(self, button):
        if button.text() == "Cancel":
            self.reject()
        else:
            for name in self.Output.keys():
                if name[:9] == "Detectors":
                    exec(f'self.Output["{name}"] = self.pushButton_{name}.isChecked()')
                elif name in ["Single", "Batch"]:
                    exec(f'self.Output["{name}"] = self.comboBox_{name}.currentText()')
                else:
                    exec(f'self.Output["{name}"] = self.checkBox_{name}.isChecked()')
            self.accept()

NestingTypes = {
    "Output type > Experiment/Load > Map > Output"  : "OtLMO",
    "Experiment/Load > Output type > Map > Output"  : "LOtMO",
    "Experiment/Load > Map > Output type > Output"  : "LMOtO",
    "Experiment/Load > Map > Output"                : "LMO",
    "Output type > Map > Output"                    : "OtMO",
    "Map > Output type > Output"                    : "MOtO",
    "Map > Output"                                  : "MO",
    "Output type > Output"                          : "OtO",
    "Output"                                        : "O"
}

def generateOutputPath(path, resultPath, nestingType, outputType):
    if nestingType   == "OtLMO" : outputPath = str(resultPath) + str(os.sep) + outputType + str(os.sep) + path.parents[0].stem + str(os.sep) + path.stem + str(os.sep)
    elif nestingType == "LOtMO" : outputPath = str(resultPath) + str(os.sep) + path.parents[0].stem + str(os.sep) + outputType + str(os.sep) + path.stem + str(os.sep)
    elif nestingType == "LMOtO" : outputPath = str(resultPath) + str(os.sep) + path.parents[0].stem + str(os.sep) + path.stem + str(os.sep) + outputType + str(os.sep)
    elif nestingType == "LMO"   : outputPath = str(resultPath) + str(os.sep) + path.parents[0].stem + str(os.sep) + path.stem + str(os.sep)
    elif nestingType == "OtMO"  : outputPath = str(resultPath) + str(os.sep) + outputType + str(os.sep) + path.stem + str(os.sep)
    elif nestingType == "MOtO"  : outputPath = str(resultPath) + str(os.sep) + path.stem + str(os.sep) + outputType + str(os.sep)
    elif nestingType == "MO"    : outputPath = str(resultPath) + str(os.sep) + path.stem + str(os.sep)
    elif nestingType == "OtO"   : outputPath = str(resultPath) + str(os.sep) + outputType + str(os.sep)
    elif nestingType == "O"     : outputPath = str(resultPath) + str(os.sep)
    elif nestingType == "W"     : outputPath = str(resultPath) + str(os.sep) + "SliceQuant" + str(os.sep) + path.stem + str(os.sep)
    return outputPath

def DiagRC(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    RC = Data["RC"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "StatisticData")
    os.makedirs(outputPath, exist_ok = True)
    Fig = PDA.Stats1D_plot(RC, head, f"{dataName}: Ring Currert", "I [mA]", Disp = disp)
    plt.close('all')
    PDA.print_Fig(Fig, outputPath + f"{dataName}_RingCurrent")

def DiagSum(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "StatisticData")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_check_plot(data, head, f"{dataName}: Sum Spectra", log = True, func = numpy.sum, Aspect = saspect, Disp = disp, Calib = calib, Emin = emin, Emax = emax)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_SumSpectra", detector = detectors, Calib = calib)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_SumSpectra")

def DiagMax(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "StatisticData")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_check_plot(data, head, f"{dataName}: Max Spectra", log = False, func = numpy.max, Aspect = saspect, Disp = disp, Calib = calib, Emin = emin, Emax = emax)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_MaxSpectra", detector = detectors, Calib = calib)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_MaxSpectra")

def DiagI0(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    I0 = Data["I0"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "StatisticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(I0, head, f"{dataName}: Incident radiation", Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp, clabel = "I0 [V]")
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_IonizationChamber0VoltageMap")
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_IonizationChamber0VoltageMap")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_IonizationChamber0VoltageMap")

def DiagLT(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    LT = Data["LT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "StatisticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(list(map(lambda x: x / 1e3, LT)), head, f"{dataName}: Live Time", detectors, Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp, clabel = "LT [ms]")
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_LiveTimeMap", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_LiveTimeMap", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_LiveTimeMap", detector = detectors)

def DiagDT(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    DT = Data["DT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "StatisticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(DT, head, f"{dataName}: Dead Time", detectors, Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp, clabel = "DT [%]")
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_DeadTimeMap", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_DeadTimeMap", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_DeadTimeMap", detector = detectors)

def DiagRT(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    RT = Data["RT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "StatisticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(list(map(lambda x: x / 1e3, RT)), head, f"{dataName}: Real Time", detectors, Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp, clabel = "RT [ms]")
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_RealTimeMap", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_RealTimeMap", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_RealTimeMap", detector = detectors)

def DiagICR(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    ICR = Data["ICR"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "StatisticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(ICR, head, f"{dataName}: Input Count Rate", detectors, Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp, clabel = "ICR [kcps]")
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_ICRMap", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_ICRMap", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_ICRMap", detector = detectors)

def DiagOCR(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    OCR = Data["OCR"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "StatisticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(OCR, head, f"{dataName}: Output Count Rate", detectors, Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp, clabel = "OCR [kcps]")
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_OCRMap", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_OCRMap", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_OCRMap", detector = detectors)

def UNormPIN(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    PIN = Data["PIN"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "RawData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(PIN, head, f"{dataName}: Transmission", Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp, clabel = "PIN [V]")
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_TransmissionMap")
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_TransmissionMap")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_TransmissionMap")

def UNormTotal(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "RawData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, Origin = origin, Aspect = maspect, pos = pos, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp)
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_RawTotalSignalMap", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_RawTotalSignalMap", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_RawTotalSignalMap", detector = detectors)

def UNormROIs(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "RawData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, ROI = roi, Origin = origin, Aspect = maspect, pos = pos, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp)
    plt.close('all')
    try: name = numpy.array(roi)[:, 0]
    except: 
        QtWidgets.QMessageBox.warning(Parent, "Analyse", f"ROIs are incorrectly defined. It is impossible to make unnormalized ROIs maps.")
        name = None
    PDA.print_Tiff(Map, outputPath + f"{dataName}_RawROIsSignalMap", Name = name, detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_RawROIsSignalMap", Name = name, detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_RawROIsSignalMap", Name = name, detector = detectors)

def UNormTabular(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "RawData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, ROI = roi, Origin = origin, Aspect = maspect, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp)
    plt.close('all')
    PDA.print_stack_Map(Map, head, roi, outputPath + f"{dataName}_RawROIsSignalTabularData", detectors, Norm = False)

# def UNormRGB(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
#     head = Data["head"]
#     data = Data["Data"]
#     dataName = path.stem
#     outputPath = generateOutputPath(path, resultPath, nestingType, "RawData")
#     os.makedirs(outputPath, exist_ok = True)
#     Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, ROI = roi, Origin = origin, Aspect = maspect, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp)
#     plt.close('all')
#     # stackLabels = list(itertools.permutations(numpy.array(roi)[:, 0], 3))
#     stackLabels = list(itertools.combinations(numpy.array(roi)[:, 0], 3))
#     didx = 0
#     for d in detectors:
#         # stackData = list(itertools.permutations(Map[didx * len(detectors):didx * len(detectors) + len(roi)], 3))
#         stackData = list(itertools.combinations(Map[didx * len(detectors):didx * len(detectors) + len(roi)], 3))
#         for i in range(len(stackData)):
#             sD = stackData[i]
#             sL = stackLabels[i]
#             stackFig = PDA.stack_Map(sD, head, f"{dataName}", sL, lightmode = False, Origin = origin)
#             PDA.print_Fig(stackFig, outputPath + f"{dataName}_RawRGBMap", Name = [f"{sL[0]}_{sL[1]}_{sL[2]}"], detector = [d])
#         didx += 1

def NormPIN(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    PIN = Data["PIN"]
    I0 = Data["I0"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "NormalizedI0")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(PIN / I0, head, f"{dataName}: Transmission (normalized to I0)", Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp, clabel = "PIN [-]")
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_NormalizedI0TransmissionMap")
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_NormalizedI0TransmissionMap")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_NormalizedI0TransmissionMap")

def NormTotal(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    I0 = Data["I0"]
    LT = Data["LT"]
    for nt in normtype:
        if nt == "I0":
            lt = numpy.ones(LT[0].shape) * 1e6
            lt = [lt, lt, lt]
            norm = [I0, lt]
            label = "c/V"
        elif nt == "LT":
            i0 = numpy.ones(I0.shape)
            norm = [i0, LT]
            label = "cps"
        else: 
            norm = [I0, LT]
            label = "cps/V"
        clabel = f"Counts [{label}]"
        dataName = path.stem
        outputPath = generateOutputPath(path, resultPath, nestingType, f"Normalized{nt}")
        os.makedirs(outputPath, exist_ok = True)
        Map, Fig = PDA.Data_plot(data, head, f"{dataName} (normalized to {nt})", detectors[:-1] if nt in ["LT", "I0LT"] and 2 in detectors else detectors, normalize = norm, Origin = origin, Aspect = maspect, pos = pos, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp, Clabel = clabel)
        plt.close('all')
        PDA.print_Tiff(Map, outputPath + f"{dataName}_Normalized{nt}TotalSignalMap", detector = detectors)
        if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_Normalized{nt}TotalSignalMap", detector = detectors)
        PDA.print_Fig(Fig, outputPath + f"{dataName}_Normalized{nt}TotalSignalMap", detector = detectors)

def NormROIs(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    I0 = Data["I0"]
    LT = Data["LT"]
    for nt in normtype:
        if nt == "I0":
            lt = numpy.ones(LT[0].shape) * 1e6
            lt = [lt, lt, lt]
            norm = [I0, lt]
            label = "c/V"
        elif nt == "LT":
            i0 = numpy.ones(I0.shape)
            norm = [i0, LT]
            label = "cps"
        else: 
            norm = [I0, LT]
            label = "cps/V"
        clabel = f"Counts [{label}]"
        dataName = path.stem
        outputPath = generateOutputPath(path, resultPath, nestingType, f"Normalized{nt}")
        os.makedirs(outputPath, exist_ok = True)
        Map, Fig = PDA.Data_plot(data, head, f"{dataName} (normalized to {nt})", detectors[:-1] if nt in ["LT", "I0LT"] and 2 in detectors else detectors, ROI = roi, normalize = norm, Origin = origin, Aspect = maspect, pos = pos, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp, Clabel = clabel)
        plt.close('all')
        try: name = numpy.array(roi)[:, 0]
        except: 
            QtWidgets.QMessageBox.warning(Parent, "Analyse", f"ROIs are incorrectly defined. It is impossible to make normalized ROIs maps.")
            name = None
        PDA.print_Tiff(Map, outputPath + f"{dataName}_Normalized{nt}ROIsSignalMap", Name = name, detector = detectors)
        if nestingType != "W": 
            if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_Normalized{nt}ROIsSignalMap", Name = name, detector = detectors)
            PDA.print_Fig(Fig, outputPath + f"{dataName}_Normalized{nt}ROIsSignalMap", Name = name, detector = detectors)

def NormTabular(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    I0 = Data["I0"]
    LT = Data["LT"]
    for nt in normtype:
        if nt == "I0":
            lt = numpy.ones(LT[0].shape) * 1e6
            lt = [lt, lt, lt]
            norm = [I0, lt]
            label = "c/V"
        elif nt == "LT":
            i0 = numpy.ones(I0.shape)
            norm = [i0, LT]
            label = "cps"
        else: 
            norm = [I0, LT]
            label = "cps/V"
        clabel = f"Counts [{label}]"
        dataName = path.stem
        outputPath = generateOutputPath(path, resultPath, nestingType, f"Normalized{nt}")
        os.makedirs(outputPath, exist_ok = True)
        Map, Fig = PDA.Data_plot(data, head, f"{dataName} (normalized to {nt})", detectors[:-1] if nt in ["LT", "I0LT"] and 2 in detectors else detectors, ROI = roi, normalize = norm, Origin = origin, Aspect = maspect, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp, Clabel = clabel)
        plt.close('all')
        PDA.print_stack_Map(Map, head, roi, outputPath + f"{dataName}_Normalized{nt}ROIsSignalTabularData", detectors[:-1] if nt in ["LT", "I0LT"] and 2 in detectors else detectors, Norm = True, Label = label)

def SpectraSumROIs(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    if disp["Selected"] and (Parent.PointChanged or Parent.AreaChanged):
        Hist, Fig = PDA.Hist_plot(data, head, f"{dataName} (extracted)", pos, calib, detectors, Emax = emax, ROI = roi, log = True, Aspect = saspect, Emin = emin, Disp = disp)
        plt.close('all')
        PDA.print_Hist(Hist, outputPath + f"{dataName}_ExtractedSumROIsSpectrum", detector = detectors, Calib = calib)
        PDA.print_Fig(Fig, outputPath + f"{dataName}_ExtractedSumROIsSpectrum", detector = detectors)
    Hist, Fig = PDA.Hist_plot(data, head, f"{dataName}", None, calib, detectors, Emax = emax, ROI = roi, log = True, Aspect = saspect, Emin = emin, Disp = disp)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_SumROIsSpectrum", detector = detectors, Calib = calib)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_SumROIsSpectrum", detector = detectors)

def SpectraMaxROIs(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    if disp["Selected"] and (Parent.PointChanged or Parent.AreaChanged):
        Hist, Fig = PDA.Hist_max_plot(data, head, f"{dataName} (extracted)", calib, detectors, Emax = emax, ROI = roi, log = False, POS = pos, Aspect = saspect, Emin = emin, Disp = disp)
        plt.close('all')
        PDA.print_Hist(Hist, outputPath + f"{dataName}_ExtractedMaxROIsSpectrum", detector = detectors, Calib = calib)
        PDA.print_Fig(Fig, outputPath + f"{dataName}_ExtractedMaxROIsSpectrum", detector = detectors)
    Hist, Fig = PDA.Hist_max_plot(data, head, f"{dataName}", calib, detectors, Emax = emax, ROI = roi, log = False, POS = None, Aspect = saspect, Emin = emin, Disp = disp)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_MaxROIsSpectrum", detector = detectors, Calib = calib)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_MaxROIsSpectrum", detector = detectors)

def SpectraSum(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    if disp["Selected"] and (Parent.PointChanged or Parent.AreaChanged):
        Hist, Fig = PDA.Hist_plot(data, head, f"{dataName} (extracted)", pos, calib, detectors, Emax = emax, ROI = None, log = True, Aspect = saspect, Emin = emin, Disp = disp)
        plt.close('all')
        PDA.print_Hist(Hist, outputPath + f"{dataName}_ExtractedSumSpectrum", detector = detectors, Calib = calib)
        PDA.print_Fig(Fig, outputPath + f"{dataName}_ExtractedSumSpectrum", detector = detectors)
    Hist, Fig = PDA.Hist_plot(data, head, f"{dataName}", None, calib, detectors, Emax = emax, ROI = None, log = True, Aspect = saspect, Emin = emin, Disp = disp)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_SumSpectrum", detector = detectors, Calib = calib)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_SumSpectrum", detector = detectors)

def SpectraMax(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    if disp["Selected"] and (Parent.PointChanged or Parent.AreaChanged):
        Hist, Fig = PDA.Hist_max_plot(data, head, f"{dataName} (extracted)", calib, detectors, Emax = emax, ROI = None, log = False, POS = pos, Aspect = saspect, Emin = emin, Disp = disp)
        plt.close('all')
        PDA.print_Hist(Hist, outputPath + f"{dataName}_ExtractedMaxSpectrum", detector = detectors, Calib = calib)
        PDA.print_Fig(Fig, outputPath + f"{dataName}_ExtractedMaxSpectrum", detector = detectors)
    Hist, Fig = PDA.Hist_max_plot(data, head, f"{dataName}", calib, detectors, Emax = emax, ROI = None, log = False, POS = None, Aspect = saspect, Emin = emin, Disp = disp)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_MaxSpectrum", detector = detectors, Calib = calib)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_MaxSpectrum", detector = detectors)

def HDF5(Parent, Data, path, resultPath):
    dataName = path.stem
    outputPath = str(resultPath) + str(os.sep)
    with h5py.File(outputPath + f"{dataName}.h5", "w") as file:
        grp_header = file.create_group("header")
        grp_header.create_dataset("TimeStep", data = Data["head"]["dt"])
        grp_header.create_dataset("Boards", data = Data["head"]["boards"])
        grp_header.create_dataset("BinsNo", data = Data["head"]["bins"])
        
        grp_roi = grp_header.create_group("ROI")
        try:
            ds_ROInames = grp_roi.create_dataset("ROInames", shape = (Data["head"]["roi_listbins"].shape[0], ), dtype = h5py.string_dtype())
            ds_ROInames = Data["head"]["roi_listbins"][:, 1]
            grp_roi.create_dataset("ROIstartChannel", data = Data["head"]["roi_listbins"][:, 2].astype(int))
            grp_roi.create_dataset("ROIstopChannel", data = Data["head"]["roi_listbins"][:, 3].astype(int))
        except:
            ds_ROInames = grp_roi.create_dataset("ROInames", shape = (Data["head"]["roi_table"].shape[0], ), dtype = h5py.string_dtype())
            ds_ROInames = Data["head"]["roi_table"][:, 0]
            grp_roi.create_dataset("ROIstartChannel", data = Data["head"]["roi_table"][:, 1].astype(int))
            grp_roi.create_dataset("ROIstopChannel", data = Data["head"]["roi_table"][:, 2].astype(int))
        
        grp_beam = grp_header.create_group("beam")
        try:
            grp_beam.create_dataset("MonoE", data = Data["head"]["monoE"])
            ds_monoType = grp_beam.create_dataset("MonoType", shape = (1, ),dtype = h5py.string_dtype())
            ds_monoType = Data["head"]["monotype"]
        except:
            grp_beam.attrs["monochromatization"] = "no data"
        try:
            grp_beam.create_dataset("TotalAttenuation", data = Data["head"]["TOTALatten"])
            grp_beam.create_dataset("FrontEndAttenuation", data = Data["head"]["FEatten"])
            grp_beam.create_dataset("BeamLineAttenuation", data = Data["head"]["BLatten"])
        except:
            grp_beam.attrs["attenuation"] = "no data"
        try:
            grp_beam.create_dataset("Slit1VetricalGap", data = Data["head"]["s1vg"])
            grp_beam.create_dataset("Slit2VetricalGap", data = Data["head"]["s2vg"])
            grp_beam.create_dataset("Slit3VetricalGap", data = Data["head"]["s3vg"])
            grp_beam.create_dataset("Slit1HorizontalGap", data = Data["head"]["s1hg"])
            grp_beam.create_dataset("Slit2HorizontalGap", data = Data["head"]["s2hg"])
            grp_beam.create_dataset("Slit3HorizontalGap", data = Data["head"]["s3hg"])
        except:
            grp_beam.attrs["slits"] = "no data"
        try:
            ds_I0amp = grp_beam.create_dataset("I0amplification", shape = (1, ),dtype = h5py.string_dtype())
            ds_I0amp = Data["head"]["pamps"]["pamp"]["sens"][0]
            ds_PINamp = grp_beam.create_dataset("PINamplification", shape = (1, ),dtype = h5py.string_dtype())
            ds_PINamp = Data["head"]["femto"]["gain"]
        except:
            grp_beam.attrs["I0andPINsignalAmplification"] = "no data"
        
        grp_position = grp_header.create_group("positions")      
        grp_position.create_dataset("ZscanVel", data = Data["head"]["Zvelocity"])
        grp_position.create_dataset("ZscanStart", data = Data["head"]["Zstartpos"])
        try:
            grp_position.create_dataset("ZscanStep", data = Data["head"]["ZscanStep"])
        except:
            grp_position.attrs["ZscanStep"] = "no data"
        grp_position.create_dataset("ZscanPositions", data = Data["head"]["Zpositions"])
        grp_position.create_dataset("ZscanPoints", data = Data["head"]["Znpoints"])
        grp_position.create_dataset("ZscanStop", data = Data["head"]["Zendpos"])
        grp_position.create_dataset("XscanVel", data = Data["head"]["XscanVel"])
        grp_position.create_dataset("XscanStop", data = Data["head"]["XscanStop"])
        grp_position.create_dataset("XscanStep", data = Data["head"]["XscanStep"])
        grp_position.create_dataset("XscanStart", data = Data["head"]["XscanStart"])
        grp_position.create_dataset("XscanRange", data = Data["head"]["XscanRange"])
        grp_position.create_dataset("XscanPulses", data = Data["head"]["XscanPulses"])
        grp_position.create_dataset("XscanPositions", data = Data["head"]["Xpositions"])

        grp_data = file.create_group("data")
        grp_data.create_dataset("PINmap", data = Data["PIN"].transpose())
        grp_data.create_dataset("I0map", data = Data["I0"].transpose())
        grp_data.create_dataset("StorageRingCurrent", data = Data["RC"])
        
        grp_sdd1 = grp_data.create_group("SDD1")
        grp_sdd1.create_dataset("SpectralData", data = Data["Data"][0].transpose(1, 0, 2))
        grp_sdd1.create_dataset("ICR", data = Data["ICR"][0].transpose())
        grp_sdd1.create_dataset("OCR", data = Data["OCR"][0].transpose())
        grp_sdd1.create_dataset("RealTime", data = Data["RT"][0].transpose())
        grp_sdd1.create_dataset("LiveTime", data = Data["LT"][0].transpose())
        grp_sdd1.create_dataset("DeadTime", data = Data["DT"][0].transpose())
        
        grp_sdd1 = grp_data.create_group("SDD2")
        grp_sdd1.create_dataset("SpectralData", data = Data["Data"][1].transpose(1, 0, 2))
        grp_sdd1.create_dataset("ICR", data = Data["ICR"][1].transpose())
        grp_sdd1.create_dataset("OCR", data = Data["OCR"][1].transpose())
        grp_sdd1.create_dataset("RealTime", data = Data["RT"][1].transpose())
        grp_sdd1.create_dataset("LiveTime", data = Data["LT"][1].transpose())
        grp_sdd1.create_dataset("DeadTime", data = Data["DT"][1].transpose())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())