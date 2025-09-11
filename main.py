from PyQt6 import QtWidgets, uic
import sys, os, pathlib, matplotlib
from scipy import io as sio, optimize as so
matplotlib.use('QtAgg')

import PDA

try:
    from ctypes import windll
    myappid = 'SOLARIS.PolyX.PXDA.0911'
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

        danteCalib = sio.loadmat(basedir / "_dante_Ecallibration.mat") # path to _dante_Ecallibration file
        danteCalibOpt, _ = so.curve_fit(lambda x, a, b: a * x + b, danteCalib['callibration_table'][:, 0], danteCalib['callibration_table'][:, 1])
        self.Single.doubleSpinBox_CalibrationGain.setValue(danteCalibOpt[0])
        self.Single.doubleSpinBox_CalibrationZero.setValue(danteCalibOpt[1])
        self.Single.doubleSpinBox_CalibrationNoise.setValue(140)
        self.Single.doubleSpinBox_CalibrationFano.setValue(0.006)

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

        # Set default energy calibration
        self.setCalibration(None, "Single")

    def setCalibration(self, value, mode):
        if mode == "Single": 
            child = self.Single
            child2 = self.Batch
        elif mode == "Batch": 
            child = self.Batch
            child2 = self.Single

        if value is not None:
            child.label_CalibrationCheck.hide()
            child2.label_CalibrationCheck.hide()

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
        child.doubleSpinBox_SpectraConfigEnergyStop.setValue(self.Single.monoE / 1000 if self.Single.monoE is not None else self.Calib[-1] / 1000) # widma do energii mono
        child.doubleSpinBox_SpectraConfigEnergyStop.blockSignals(False)

        child2.pushButton_SpectraConfigEnergyAuto.setEnabled(True)
        child2.doubleSpinBox_SpectraConfigEnergyStart.setEnabled(True)
        child2.doubleSpinBox_SpectraConfigEnergyStop.setEnabled(True)

        child2.doubleSpinBox_SpectraConfigEnergyStop.blockSignals(True)
        child2.doubleSpinBox_SpectraConfigEnergyStop.setMaximum(self.Calib[-1] / 1000)
        child2.doubleSpinBox_SpectraConfigEnergyStop.setValue(self.Single.monoE / 1000 if self.Single.monoE is not None else self.Calib[-1] / 1000) # widma do energii mono
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