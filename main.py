from PyQt6 import QtWidgets, uic
import sys, os, pathlib

import PDA

try:
    from ctypes import windll
    myappid = 'SOLARIS.PolyX.PXDA'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

basedir = pathlib.Path(os.path.dirname(__file__))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(basedir / "main.ui", self)
        self.setWindowTitle('PolyX XRF Data Analyser')

        self.Calib  = None
        self.Sigma  = None

        # Single
        self.Single = self.tab_Single

        self.Single.doubleSpinBox_CalibrationGain.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))
        self.Single.doubleSpinBox_CalibrationZero.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))
        self.Single.doubleSpinBox_CalibrationNoise.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))
        self.Single.doubleSpinBox_CalibrationFano.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))

        # Batch
        self.Batch  = self.tab_Batch

        self.Batch.doubleSpinBox_CalibrationGain.valueChanged.connect (lambda value, mode = "Batch": self.setCalibration(value, mode))
        self.Batch.doubleSpinBox_CalibrationZero.valueChanged.connect (lambda value, mode = "Batch": self.setCalibration(value, mode))
        self.Batch.doubleSpinBox_CalibrationNoise.valueChanged.connect(lambda value, mode = "Batch": self.setCalibration(value, mode))
        self.Batch.doubleSpinBox_CalibrationFano.valueChanged.connect (lambda value, mode = "Batch": self.setCalibration(value, mode))

        # Stitch
        self.Stitch = self.tab_Stitch

    def setCalibration(self, value, mode):
        if mode == "Single": 
            child = self.Single
            child2 = self.Batch
        elif mode == "Batch": 
            child = self.Batch
            child2 = self.Single

        gain  = child.doubleSpinBox_CalibrationGain.value() / 1000
        zero  = child.doubleSpinBox_CalibrationZero.value() / 1000
        noise = child.doubleSpinBox_CalibrationNoise.value()
        fano  = child.doubleSpinBox_CalibrationFano.value()
        self.Calib, self.Sigma  = PDA.gen_calib(4096, gain, zero, noise, fano)

        child.pushButton_SpectraConfigEnergyAuto.setEnabled(True)
        child.doubleSpinBox_SpectraConfigEnergyStart.setEnabled(True)
        child.doubleSpinBox_SpectraConfigEnergyStop.setEnabled(True)

        child.doubleSpinBox_SpectraConfigEnergyStop.blockSignals(True)
        child.doubleSpinBox_SpectraConfigEnergyStop.setMaximum(self.Calib[-1] / 1000)
        child.doubleSpinBox_SpectraConfigEnergyStop.setValue(self.Calib[-1] / 1000)
        child.doubleSpinBox_SpectraConfigEnergyStop.blockSignals(False)

        child2.pushButton_SpectraConfigEnergyAuto.setEnabled(True)
        child2.doubleSpinBox_SpectraConfigEnergyStart.setEnabled(True)
        child2.doubleSpinBox_SpectraConfigEnergyStop.setEnabled(True)

        child2.doubleSpinBox_SpectraConfigEnergyStop.blockSignals(True)
        child2.doubleSpinBox_SpectraConfigEnergyStop.setMaximum(self.Calib[-1] / 1000)
        child2.doubleSpinBox_SpectraConfigEnergyStop.setValue(self.Calib[-1] / 1000)
        child2.doubleSpinBox_SpectraConfigEnergyStop.blockSignals(False)
        
        child.setCalibration(self.Calib, self.Sigma)
        child2.setCalibration(self.Calib, self.Sigma)

        child2.doubleSpinBox_CalibrationGain.blockSignals(True)
        child2.doubleSpinBox_CalibrationZero.blockSignals(True)
        child2.doubleSpinBox_CalibrationNoise.blockSignals(True)
        child2.doubleSpinBox_CalibrationFano.blockSignals(True)

        child2.doubleSpinBox_CalibrationGain.setValue(gain * 1000)
        child2.doubleSpinBox_CalibrationZero.setValue(zero * 1000)
        child2.doubleSpinBox_CalibrationNoise.setValue(noise)
        child2.doubleSpinBox_CalibrationFano.setValue(fano)

        child2.doubleSpinBox_CalibrationGain.blockSignals(False)
        child2.doubleSpinBox_CalibrationZero.blockSignals(False)
        child2.doubleSpinBox_CalibrationNoise.blockSignals(False)
        child2.doubleSpinBox_CalibrationFano.blockSignals(False)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())