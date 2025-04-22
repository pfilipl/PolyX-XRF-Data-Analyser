from PyQt6 import QtWidgets, QtCore, uic
import sys, os, numpy, itertools, subprocess
import matplotlib.pyplot as plt

import main, PDA

def OpenDirectory(path):
    try: os.startfile(path)
    except: subprocess.Popen(['xdg-open', path])

class Analyse(QtWidgets.QDialog):
    def __init__(self, parent = None, outputConfig = None, detectorsBe = True, detectorsML = True, detectorsSum = False, batch = False):
        super(Analyse, self).__init__(parent)
        uic.loadUi("analyse.ui", self)
        self.setWindowTitle('Choose output data')

        if batch: self.comboBox_Single.hide()
        else: self.comboBox_Batch.hide()

        if outputConfig is None:
            self.Output = {
                "DetectorsBe"       : detectorsBe,
                "DetectorsML"       : detectorsML,
                "DetectorsSum"      : detectorsSum,
                "Single"            : "Output type > Output",
                "Batch"             : "Experiment/Load > Map > Output type > Output",
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

        self.buttonBox.clicked.connect(self.ButtonBox_clicked)

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
    return outputPath

def DiagRC(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    print(nestingType)
    head = Data["head"]
    RC = Data["RC"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Fig = PDA.Stats1D_plot(RC, head, "ring currert", "I [mA]")
    plt.close('all')
    PDA.print_Fig(Fig, outputPath + f"{dataName}_RC")

def DiagSum(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_check_plot(data, head, f"{dataName}: Sum Signal Check", log = True, func = numpy.sum)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_SumCheck", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_SumCheck")

def DiagMax(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_check_plot(data, head, f"{dataName}: Max Signal Check", log = False, func = numpy.max)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_MaxCheck", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_MaxCheck")

def DiagI0(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    I0 = Data["I0"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(I0, head, f"{dataName}: I0 [V]", Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_I0")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_I0")

def DiagPIN(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    PIN = Data["PIN"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(PIN, head, f"{dataName}: I1/PIN [V]", Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_PIN")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_PIN")

def DiagLT(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    LT = Data["LT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(list(map(lambda x: x / 1e3, LT)), head, f"{dataName}: Live Time [ms]", detectors, Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_LT", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_LT", detector = detectors)

def DiagDT(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    DT = Data["DT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(DT, head, f"{dataName}: Dead Time [%]", detectors, Vmax = None, Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_DT", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_DT", detector = detectors)

def DiagRT(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    RT = Data["RT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(list(map(lambda x: x / 1e3, RT)), head, f"{dataName}: Real Time [ms]", detectors, Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_RT", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_RT", detector = detectors)

def DiagICR(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    ICR = Data["ICR"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(ICR, head, f"{dataName}: Input Count Rate", detectors, Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_ICR", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_ICR", detector = detectors)

def DiagOCR(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    OCR = Data["OCR"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(OCR, head, f"{dataName}: Output Count Rate", detectors, Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_OCR", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_OCR", detector = detectors)

def UNormTotal(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Unnormalized")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, Origin = origin, Aspect = aspect, pos = pos)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_UNormTotal", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_UNormTotal", detector = detectors)

def UNormROIs(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Unnormalized")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, ROI = roi, Origin = origin, Aspect = aspect, pos = pos)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_UNormROIs", Name = numpy.array(roi)[:, 0], detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_UNormROIs", Name = numpy.array(roi)[:, 0], detector = detectors)

def UNormTabular(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Unnormalized")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, ROI = roi, Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_stack_Map(Map, head, roi, outputPath + f"{dataName}_UNormTabular", detectors)

# def UNormRGB(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
#     head = Data["head"]
#     data = Data["Data"]
#     dataName = path.stem
#     outputPath = generateOutputPath(path, resultPath, nestingType, "Unnormalized")
#     os.makedirs(outputPath, exist_ok = True)
#     Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, ROI = roi, Origin = origin, Aspect = aspect)
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

def NormTotal(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    I0 = Data["I0"]
    LT = Data["LT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Normalized")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, normalize = [I0, LT], Origin = origin, Aspect = aspect, pos = pos)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_NormTotal", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_NormTotal", detector = detectors)

def NormROIs(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    I0 = Data["I0"]
    LT = Data["LT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Normalized")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, ROI = roi, normalize = [I0, LT], Origin = origin, Aspect = aspect, pos = pos)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_NormROIs", Name = numpy.array(roi)[:, 0], detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_NormROIs", Name = numpy.array(roi)[:, 0], detector = detectors)

def NormTabular(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    I0 = Data["I0"]
    LT = Data["LT"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Normalized")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Data_plot(data, head, f"{dataName}", detectors, ROI = roi, normalize = [I0, LT], Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_stack_Map(Map, head, roi, outputPath + f"{dataName}_NormTabular", detectors)

def SpectraSumROIs(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_plot(data, head, f"{dataName}", pos, calib, detectors, Emax = 20, ROI = roi, log = True)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_SumROIs", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_SumROIs", detector = detectors)

def SpectraMaxROIs(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_max_plot(data, head, f"{dataName}", calib, detectors, Emax = 20, ROI = roi, log = False, POS = pos)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_MaxROIs", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_MaxROIs", detector = detectors)

def SpectraSum(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_plot(data, head, f"{dataName}", pos, calib, detectors, Emax = 20, ROI = None, log = True)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_Sum", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_Sum", detector = detectors)

def SpectraMax(Data, path, resultPath, detectors = [2], nestingType = "OtO", origin = "upper", aspect = "equal", roi = None, pos = None, calib = None):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = generateOutputPath(path, resultPath, nestingType, "Spectra")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_max_plot(data, head, f"{dataName}", calib, detectors, Emax = 20, ROI = None, log = False, POS = pos)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_Max", detector = detectors)
    PDA.print_Fig(Fig, outputPath + f"{dataName}_Max", detector = detectors)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())