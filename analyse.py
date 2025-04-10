from PyQt6 import QtWidgets, uic
import sys

import main

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
                "DiagTotal"         : True,
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
                "SpectraTotalROIs"  : True,
                "SpectraMaxROIs"    : False,
                "SpectraTotal"      : False,
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

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())