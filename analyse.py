from PyQt6 import QtWidgets, uic
import sys, os, numpy
import matplotlib.pyplot as plt

import main, PDA

class Analyse(QtWidgets.QDialog):
    def __init__(self, parent = None, outputConfig = None, detectorsBe = True, detectorsML = True, detectorsSum = False, batch = False):
        super(Analyse, self).__init__(parent)
        uic.loadUi("analyse.ui", self)
        self.setWindowTitle('Choose output data')

        if not batch:
            self.label_Nesting.hide()
            self.radioButton_ELMOtO.hide()
            self.radioButton_ELMO.hide()
            self.radioButton_ELOtMO.hide()
            self.radioButton_ELOtO.hide()
            self.setMinimumHeight(410)

        if outputConfig is None:
            self.Output = {
                "DetectorsBe"       : detectorsBe,
                "DetectorsML"       : detectorsML,
                "DetectorsSum"      : detectorsSum,
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
                "NormTotal"         : True,
                "NormROIs"          : True,
                "SpectraSumROIs"    : True,
                "SpectraMaxROIs"    : False,
                "SpectraSum"        : False,
                "SpectraMax"        : False,
                "ELMOtO"            : True,
                "ELMO"              : False,
                "ELOtMO"            : False,
                "ELOtO"             : False
            }
        else:
            self.Output = outputConfig

        for name in self.Output.keys():
            if name[:9] == "Detectors":
                exec(f'self.pushButton_{name}.setChecked(self.Output["{name}"])')
            elif name[:2] == "EL":
                exec(f'self.radioButton_{name}.setChecked(self.Output["{name}"])')
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
                elif name[:2] == "EL":
                    exec(f'self.Output["{name}"] = self.radioButton_{name}.isChecked()')
                else:
                    exec(f'self.Output["{name}"] = self.checkBox_{name}.isChecked()')
            self.accept()

def getOutputPath(path, resultPath, nestingType, outputType):
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

def DiagRC(Data, path, resultPath, detectors = None, nestingType = "OtO", origin = "upper", aspect = "equal"):
    head = Data["head"]
    RC = Data["RC"]
    dataName = path.stem
    outputPath = getOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Fig = PDA.Stats1D_plot(RC, head, "ring currert", "I [mA]")
    plt.close('all')
    PDA.print_Fig(Fig, outputPath + f"{dataName}_RC")

def DiagSum(Data, path, resultPath, detectors = None, nestingType = "OtO", origin = "upper", aspect = "equal"):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = getOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_check_plot(data, head, f"{dataName}: Sum Signal Check", log = True, func = numpy.sum)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_SumCheck")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_SumCheck")

def DiagMax(Data, path, resultPath, detectors = None, nestingType = "OtO", origin = "upper", aspect = "equal"):
    head = Data["head"]
    data = Data["Data"]
    dataName = path.stem
    outputPath = getOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Hist, Fig = PDA.Hist_check_plot(data, head, f"{dataName}: Max Signal Check", log = False, func = numpy.max)
    plt.close('all')
    PDA.print_Hist(Hist, outputPath + f"{dataName}_MaxCheck")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_MaxCheck")

def DiagI0(Data, path, resultPath, detectors = None, nestingType = "OtO", origin = "upper", aspect = "equal"):
    head = Data["head"]
    I0 = Data["I0"]
    dataName = path.stem
    outputPath = getOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(I0, head, f"{dataName}: I0 [V]", Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_I0")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_I0")

def DiagPIN(Data, path, resultPath, detectors = None, nestingType = "OtO", origin = "upper", aspect = "equal"):
    head = Data["head"]
    PIN = Data["PIN"]
    dataName = path.stem
    outputPath = getOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(PIN, head, f"{dataName}: I1/PIN [V]", Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_PIN")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_PIN")

def DiagLT(Data, path, resultPath, detectors = None, nestingType = "OtO", origin = "upper", aspect = "equal"):
    head = Data["head"]
    LT = Data["LT"]
    dataName = path.stem
    outputPath = getOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(list(map(lambda x: x / 1e3, LT)), head, f"{dataName}: Live Time [ms]", detectors, Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_LT")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_LT")

def DiagDT(Data, path, resultPath, detectors = None, nestingType = "OtO", origin = "upper", aspect = "equal"):
    head = Data["head"]
    DT = Data["DT"]
    dataName = path.stem
    outputPath = getOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(DT, head, f"{dataName}: Dead Time [%]", detectors, Vmax = None, Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_DT")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_DT")

def DiagRT(Data, path, resultPath, detectors = None, nestingType = "OtO", origin = "upper", aspect = "equal"):
    head = Data["head"]
    RT = Data["RT"]
    dataName = path.stem
    outputPath = getOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(list(map(lambda x: x / 1e3, RT)), head, f"{dataName}: Real Time [ms]", detectors, Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_RT")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_RT")

def DiagICR(Data, path, resultPath, detectors = None, nestingType = "OtO", origin = "upper", aspect = "equal"):
    head = Data["head"]
    ICR = Data["ICR"]
    dataName = path.stem
    outputPath = getOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(ICR, head, f"{dataName}: Input Count Rate", detectors, Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_ICR")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_ICR")

def DiagOCR(Data, path, resultPath, detectors = None, nestingType = "OtO", origin = "upper", aspect = "equal"):
    head = Data["head"]
    OCR = Data["OCR"]
    dataName = path.stem
    outputPath = getOutputPath(path, resultPath, nestingType, "DiagnosticData")
    os.makedirs(outputPath, exist_ok = True)
    Map, Fig = PDA.Stats2D_plot(OCR, head, f"{dataName}: Output Count Rate", detectors, Origin = origin, Aspect = aspect)
    plt.close('all')
    PDA.print_Map(Map, outputPath + f"{dataName}_OCR")
    PDA.print_Fig(Fig, outputPath + f"{dataName}_OCR")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())