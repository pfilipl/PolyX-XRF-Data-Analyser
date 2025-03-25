from PyQt6 import QtWidgets, uic
import sys

import PDA

CALIB_NBINS = 4096

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi("main.ui", self)
        self.setWindowTitle('PolyX Data Analyser')

        self.Single             = self.tab_Single
        self.Batch              = self.tab_Batch
        self.Stitch             = self.tab_Stitch

        self.CalibrationGain    = None
        self.CalibrationZero    = None
        self.CalibrationNoise   = None
        self.CalibrationFano    = None
        self.Calib              = None
        self.Sigma              = None

        CALIB_A     = 0.007016  # [keV/ch]
        CALIB_B     = -0.71138  # [keV]
        CALIB_NOISE = 142.61    # [eV]
        CALIB_FANO  = 0.06269   # [-]

        self.setCalibration(CALIB_A, CALIB_B, CALIB_NOISE, CALIB_FANO)

    def setCalibration(self, gain, zero, noise, fano):
        self.CalibrationGain    = gain
        self.CalibrationZero    = zero
        self.CalibrationNoise   = noise
        self.CalibrationFano    = fano
        self.Calib, self.Sigma  = PDA.gen_calib(CALIB_NBINS, gain, zero, noise, fano)

    def getCalibration(self):
        return self.CalibrationGain, self.CalibrationZero, self.CalibrationNoise, self.CalibrationFano, self.Calib, self.Sigma

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())