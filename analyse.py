from PyQt6 import QtWidgets, QtCore, uic, QtGui
import sys, os, numpy, itertools, subprocess, pathlib
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
                "GenCsvs"           : False,
                "GenWiatrowska"     : False,
                "DiagRC"            : True,
                "DiagSum"           : True,
                "DiagMax"           : True,
                "DiagI0"            : True,
                "DiagPIN"           : True,
                "DiagLT"            : True,
                "DiagDT"            : True,
                "DiagRT"            : False,
                "DiagICR"           : False,
                "DiagOCR"           : False,
                "UNormTotal"        : True,
                "UNormROIs"         : True,
                "UNormTabular"      : False,
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

        for name in self.Output.keys():
            if name[:9] == "Detectors":
                exec(f'self.pushButton_{name}.setChecked(self.Output["{name}"])')
            elif name in ["Single", "Batch"]:
                exec(f'self.comboBox_{name}.setCurrentIndex(self.comboBox_{name}.findText("{self.Output[name]}", QtCore.Qt.MatchFlag.MatchExactly))')
            else:
                exec(f'self.checkBox_{name}.setChecked(self.Output["{name}"])')

        self.checkBox_NormTotal.toggled.connect(self.NormTypeChanged)
        self.checkBox_NormROIs.toggled.connect(self.NormTypeChanged)
        self.checkBox_NormTabular.toggled.connect(self.NormTypeChanged)
        self.checkBox_NormTypeI0LT.toggled.connect(self.NormTypeChanged)
        self.checkBox_NormTypeI0.toggled.connect(self.NormTypeChanged)
        self.checkBox_NormTypeLT.toggled.connect(self.NormTypeChanged)
        self.checkBox_DispTitles.toggled.connect(lambda checked, mode = "Simp": self.TitlesChanged(checked, mode))        
        self.checkBox_DispSimpTitles.toggled.connect(lambda checked, mode = "": self.TitlesChanged(checked, mode))        
        self.buttonBox.clicked.connect(self.ButtonBox_clicked)

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
    elif nestingType == "W"     : outputPath = str(resultPath) + str(os.sep) + "Wiatrowska" + str(os.sep) + path.stem + str(os.sep)
    return outputPath

def DiagRC(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    RC = Data["RC"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Fig = PDA.Stats1D_plot(RC, head, f"{dataName}: Ring Currert", "I [mA]", Disp = disp)
    plt.close('all')
    PDA.print_Fig(Fig, outputPath + f"{dataName}_RC")

def DiagSum(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_check_plot(data, head, f"{dataName}: Sum Signal Check", log = True, func = numpy.sum, Aspect = saspect, Disp = disp)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_SumCheck", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_SumCheck")

def DiagMax(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_check_plot(data, head, f"{dataName}: Max Signal Check", log = False, func = numpy.max, Aspect = saspect, Disp = disp)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_MaxCheck", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_MaxCheck")

def DiagI0(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    I0 = Data["I0"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(I0, head, f"{dataName}: I0 [V]", Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp)
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_I0")
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_I0")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_I0")

def DiagPIN(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    PIN = Data["PIN"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(PIN, head, f"{dataName}: I1 or PIN [V]", Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp)
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_PIN")
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_PIN")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_PIN")

def DiagLT(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    LT = Data["LT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(list(map(lambda x: x / 1e3, LT)), head, f"{dataName}: Live Time [ms]", detectors, Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp)
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_LT", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_LT", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_LT", detector = detectors)

def DiagDT(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    DT = Data["DT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(DT, head, f"{dataName}: Dead Time [%]", detectors, Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp)
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_DT", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_DT", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_DT", detector = detectors)

def DiagRT(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    RT = Data["RT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(list(map(lambda x: x / 1e3, RT)), head, f"{dataName}: Real Time [ms]", detectors, Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp)
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_RT", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_RT", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_RT", detector = detectors)

def DiagICR(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    ICR = Data["ICR"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(ICR, head, f"{dataName}: Input Count Rate [kcps]", detectors, Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp)
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_ICR", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_ICR", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_ICR", detector = detectors)

def DiagOCR(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    OCR = Data["OCR"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(OCR, head, f"{dataName}: Output Count Rate [kcps]", detectors, Origin = origin, Aspect = maspect, Cmap = cmap, Disp = disp)
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_OCR", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_OCR", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_OCR", detector = detectors)

def UNormTotal(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Unnormalized")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, Origin = origin, Aspect = maspect, pos = pos, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp)
    plt.close('all')
    PDA.print_Tiff(Map, outputPath + f"{dataName}_UNormTotal", detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_UNormTotal", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_UNormTotal", detector = detectors)

def UNormROIs(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Unnormalized")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, ROI = roi, Origin = origin, Aspect = maspect, pos = pos, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp)
    plt.close('all')
    try: name = numpy.array(roi)[:, 0]
    except: 
        QtWidgets.QMessageBox.warning(Parent, "Analyse", f"ROIs are incorrectly defined. It is impossible to make unnormalized ROIs maps.")
        name = None
    PDA.print_Tiff(Map, outputPath + f"{dataName}_UNormROIs", Name = name, detector = detectors)
    if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_UNormROIs", Name = name, detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_UNormROIs", Name = name, detector = detectors)

def UNormTabular(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Unnormalized")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, ROI = roi, Origin = origin, Aspect = maspect, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp)
    plt.close('all')
    PDA.print_stack_Map(Map, head, roi, outputPath + f"{dataName}_UNormTabular", detectors)

# def UNormRGB(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
#     head = Data["head"]
#     data = Data["Data"]
#     dataName = path.stem
#     outputPath = generateOutputPath(path, resultPath, nestingType, "Unnormalized")
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
#             PDA.print_Fig(stackFig, outputPath + f"{dataName}_UNormRGB", Name = [f"{sL[0]}_{sL[1]}_{sL[2]}"], detector = [d])
#         didx += 1

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
        elif nt == "LT":
            i0 = numpy.ones(I0.shape)
            norm = [i0, LT]
        else: norm = [I0, LT]
        dataName = path.stem
        outputPath = generateOutputPath(path, resultPath, nestingType, f"Normalized{nt}")
        os.makedirs(outputPath, exist_ok = True)
        Map, Fig = PDA.Data_plot(data, head, f"{dataName} (normalized {nt})", detectors, normalize = norm, Origin = origin, Aspect = maspect, pos = pos, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp)
        plt.close('all')
        PDA.print_Tiff(Map, outputPath + f"{dataName}_Norm{nt}Total", detector = detectors)
        if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_Norm{nt}Total", detector = detectors)
        PDA.print_Fig(Fig, outputPath + f"{dataName}_Norm{nt}Total", detector = detectors)

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
        elif nt == "LT":
            i0 = numpy.ones(I0.shape)
            norm = [i0, LT]
        else: norm = [I0, LT]
        dataName = path.stem
        outputPath = generateOutputPath(path, resultPath, nestingType, f"Normalized{nt}")
        os.makedirs(outputPath, exist_ok = True)
        Map, Fig = PDA.Data_plot(data, head, f"{dataName} (normalized {nt})", detectors, ROI = roi, normalize = norm, Origin = origin, Aspect = maspect, pos = pos, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp)
        plt.close('all')
        try: name = numpy.array(roi)[:, 0]
        except: 
            QtWidgets.QMessageBox.warning(Parent, "Analyse", f"ROIs are incorrectly defined. It is impossible to make normalized ROIs maps.")
            name = None
        PDA.print_Tiff(Map, outputPath + f"{dataName}_Norm{nt}ROIs", Name = name, detector = detectors)
        if nestingType != "W": 
            if csvs: PDA.print_Map(Map, outputPath + f"{dataName}_Norm{nt}ROIs", Name = name, detector = detectors)
            PDA.print_Fig(Fig, outputPath + f"{dataName}_Norm{nt}ROIs", Name = name, detector = detectors)

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
        elif nt == "LT":
            i0 = numpy.ones(I0.shape)
            norm = [i0, LT]
        else: norm = [I0, LT]
        dataName = path.stem
        outputPath = generateOutputPath(path, resultPath, nestingType, f"Normalized{nt}")
        os.makedirs(outputPath, exist_ok = True)
        Map, Fig = PDA.Data_plot(data, head, f"{dataName} (normalized {nt})", detectors, ROI = roi, normalize = norm, Origin = origin, Aspect = maspect, Vmin = vmin, Vmax = vmax, Cmap = cmap, Disp = disp)
        plt.close('all')
        PDA.print_stack_Map(Map, head, roi, outputPath + f"{dataName}_Norm{nt}Tabular", detectors)

def SpectraSumROIs(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    if disp["Selected"]:
        Hist, Fig = PDA.Hist_plot(data, head, f"{dataName} (extracted)", pos, calib, detectors, Emax = emax, ROI = roi, log = True, Aspect = saspect, Emin = emin, Disp = disp)
        plt.close('all')
        PDA.print_Hist(Hist, outputPath + f"{dataName}_ExtSumROIs", detector = detectors)
        PDA.print_Fig(Fig, outputPath + f"{dataName}_ExtSumROIs", detector = detectors)
    Hist, Fig = PDA.Hist_plot(data, head, f"{dataName}", None, calib, detectors, Emax = emax, ROI = roi, log = True, Aspect = saspect, Emin = emin, Disp = disp)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_SumROIs", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_SumROIs", detector = detectors)

def SpectraMaxROIs(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    if disp["Selected"]:
        Hist, Fig = PDA.Hist_max_plot(data, head, f"{dataName} (extracted)", calib, detectors, Emax = emax, ROI = roi, log = False, POS = pos, Aspect = saspect, Emin = emin, Disp = disp)
        plt.close('all')
        PDA.print_Hist(Hist, outputPath + f"{dataName}_ExtMaxROIs", detector = detectors)
        PDA.print_Fig(Fig, outputPath + f"{dataName}_ExtMaxROIs", detector = detectors)
    Hist, Fig = PDA.Hist_max_plot(data, head, f"{dataName}", calib, detectors, Emax = emax, ROI = roi, log = False, POS = None, Aspect = saspect, Emin = emin, Disp = disp)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_MaxROIs", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_MaxROIs", detector = detectors)

def SpectraSum(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    if disp["Selected"]:
        Hist, Fig = PDA.Hist_plot(data, head, f"{dataName} (extracted)", pos, calib, detectors, Emax = emax, ROI = None, log = True, Aspect = saspect, Emin = emin, Disp = disp)
        plt.close('all')
        PDA.print_Hist(Hist, outputPath + f"{dataName}_ExtSum", detector = detectors)
        PDA.print_Fig(Fig, outputPath + f"{dataName}_ExtSum", detector = detectors)
    Hist, Fig = PDA.Hist_plot(data, head, f"{dataName}", None, calib, detectors, Emax = emax, ROI = None, log = True, Aspect = saspect, Emin = emin, Disp = disp)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_Sum", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_Sum", detector = detectors)

def SpectraMax(Parent, Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "auto", roi = None, pos = None, calib = None, vmin = None, vmax = None, maspect = "equal", emin = 0.0, emax = None, saspect = "auto", cmap = "viridis", normtype = [], disp = None, csvs = False):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    if disp["Selected"]:
        Hist, Fig = PDA.Hist_max_plot(data, head, f"{dataName} (extracted)", calib, detectors, Emax = emax, ROI = None, log = False, POS = pos, Aspect = saspect, Emin = emin, Disp = disp)
        plt.close('all')
        PDA.print_Hist(Hist, outputPath + f"{dataName}_ExtMax", detector = detectors)
        PDA.print_Fig(Fig, outputPath + f"{dataName}_ExtMax", detector = detectors)
    Hist, Fig = PDA.Hist_max_plot(data, head, f"{dataName}", calib, detectors, Emax = emax, ROI = None, log = False, POS = None, Aspect = saspect, Emin = emin, Disp = disp)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_Max", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_Max", detector = detectors)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())