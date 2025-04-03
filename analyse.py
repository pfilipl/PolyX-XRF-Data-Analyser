from PyQt6 import QtWidgets, uic
import sys

import main

class Analyse(QtWidgets.QDialog):
    def __init__(self, parent = None, outputConfig = None):
        super(Analyse, self).__init__(parent)
        uic.loadUi("analyse.ui", self)
        self.setWindowTitle('Choose output data')

        if outputConfig is None:
            self.Output = {
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
                "SpectraMax"        : False
            }
        else:
            self.Output = outputConfig

        for name in self.Output.keys():
            exec(f'self.checkBox_{name}.setChecked(self.Output["{name}"])')

        self.buttonBox.clicked.connect(self.ButtonBox_clicked)

    def ButtonBox_clicked(self, button):
        if button.text() == "Cancel":
            self.reject()
        else:
            for name in self.Output.keys():
                exec(f'self.Output["{name}"] = self.checkBox_{name}.isChecked()')
            self.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())