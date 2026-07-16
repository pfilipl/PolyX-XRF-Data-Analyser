from PyQt6 import QtWidgets, uic
import sys, os, pathlib, matplotlib, numpy
from scipy import io as sio, optimize as so
matplotlib.use('QtAgg')

import PDA

try:
    from ctypes import windll
    myappid = 'SOLARIS.PolyX.PXDA.0.260324'
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

        danteCalib = sio.loadmat(basedir / "_dante_Ecallibration_SDD1.mat") # path to _dante_Ecallibration_SDD1 file
        danteCalib_2 = sio.loadmat(basedir / "_dante_Ecallibration_SDD2.mat") # path to _dante_Ecallibration_SDD2 file
        danteCalibOpt, _ = so.curve_fit(lambda x, a, b: a * x + b, danteCalib['callibration_table'][:, 0], danteCalib['callibration_table'][:, 1])
        danteCalibOpt_2, _ = so.curve_fit(lambda x, a, b: a * x + b, danteCalib_2['callibration_table'][:, 0], danteCalib_2['callibration_table'][:, 1])
        # danteCalibOpt_2, _ = so.curve_fit(lambda x, a, b: a * x + b, danteCalib_2['callibration_table'][:, 0], danteCalib_2['callibration_table'][:, 1]*1.2+200)
        self.Single.doubleSpinBox_CalibrationGain.setValue(danteCalibOpt[0])
        self.Single.doubleSpinBox_CalibrationZero.setValue(danteCalibOpt[1])
        self.Single.doubleSpinBox_CalibrationNoise.setValue(140)
        self.Single.doubleSpinBox_CalibrationFano.setValue(0.006)
        self.Single.doubleSpinBox_CalibrationGain_2.setValue(danteCalibOpt_2[0])
        self.Single.doubleSpinBox_CalibrationZero_2.setValue(danteCalibOpt_2[1])
        self.Single.doubleSpinBox_CalibrationNoise_2.setValue(140)
        self.Single.doubleSpinBox_CalibrationFano_2.setValue(0.006)

        self.Single.doubleSpinBox_CalibrationGain.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))
        self.Single.doubleSpinBox_CalibrationZero.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))
        self.Single.doubleSpinBox_CalibrationNoise.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))
        self.Single.doubleSpinBox_CalibrationFano.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))
        self.Single.doubleSpinBox_CalibrationGain_2.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))
        self.Single.doubleSpinBox_CalibrationZero_2.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))
        self.Single.doubleSpinBox_CalibrationNoise_2.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))
        self.Single.doubleSpinBox_CalibrationFano_2.valueChanged.connect(lambda value, mode = "Single": self.setCalibration(value, mode))

        # Batch
        self.Batch  = self.tab_Batch

        self.Batch.doubleSpinBox_CalibrationGain.valueChanged.connect(lambda value, mode = "Batch": self.setCalibration(value, mode))
        self.Batch.doubleSpinBox_CalibrationZero.valueChanged.connect(lambda value, mode = "Batch": self.setCalibration(value, mode))
        self.Batch.doubleSpinBox_CalibrationNoise.valueChanged.connect(lambda value, mode = "Batch": self.setCalibration(value, mode))
        self.Batch.doubleSpinBox_CalibrationFano.valueChanged.connect(lambda value, mode = "Batch": self.setCalibration(value, mode))
        self.Batch.doubleSpinBox_CalibrationGain_2.valueChanged.connect(lambda value, mode = "Batch": self.setCalibration(value, mode))
        self.Batch.doubleSpinBox_CalibrationZero_2.valueChanged.connect(lambda value, mode = "Batch": self.setCalibration(value, mode))
        self.Batch.doubleSpinBox_CalibrationNoise_2.valueChanged.connect(lambda value, mode = "Batch": self.setCalibration(value, mode))
        self.Batch.doubleSpinBox_CalibrationFano_2.valueChanged.connect(lambda value, mode = "Batch": self.setCalibration(value, mode))

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
        gain_2  = child.doubleSpinBox_CalibrationGain_2.value() / 1000
        zero_2  = child.doubleSpinBox_CalibrationZero_2.value() / 1000
        noise_2 = child.doubleSpinBox_CalibrationNoise_2.value()
        fano_2  = child.doubleSpinBox_CalibrationFano_2.value()
        calib, sigma  = PDA.gen_calib(4096, gain, zero, noise, fano)
        calib_2, sigma_2  = PDA.gen_calib(4096, gain_2, zero_2, noise_2, fano_2)
        self.Calib = numpy.concatenate([calib, calib_2])
        self.Sigma = numpy.concatenate([sigma, sigma_2])

        child.pushButton_SpectraConfigEnergyAuto.setEnabled(True)
        child.doubleSpinBox_SpectraConfigEnergyStart.setEnabled(True)
        child.doubleSpinBox_SpectraConfigEnergyStop.setEnabled(True)

        child.doubleSpinBox_SpectraConfigEnergyStop.blockSignals(True)
        child.doubleSpinBox_SpectraConfigEnergyStop.setMaximum(min(self.Calib[4096-1] / 1000, self.Calib[-1] / 1000))
        child.doubleSpinBox_SpectraConfigEnergyStop.setValue(self.Single.monoE / 1000 if self.Single.monoE is not None else min(self.Calib[4096-1] / 1000, self.Calib[-1] / 1000)) # widma do energii mono
        child.doubleSpinBox_SpectraConfigEnergyStop.blockSignals(False)

        child2.pushButton_SpectraConfigEnergyAuto.setEnabled(True)
        child2.doubleSpinBox_SpectraConfigEnergyStart.setEnabled(True)
        child2.doubleSpinBox_SpectraConfigEnergyStop.setEnabled(True)

        child2.doubleSpinBox_SpectraConfigEnergyStop.blockSignals(True)
        child2.doubleSpinBox_SpectraConfigEnergyStop.setMaximum(min(self.Calib[4096-1] / 1000, self.Calib[-1] / 1000))
        child2.doubleSpinBox_SpectraConfigEnergyStop.setValue(self.Single.monoE / 1000 if self.Single.monoE is not None else min(self.Calib[4096-1] / 1000, self.Calib[-1] / 1000)) # widma do energii mono
        child2.doubleSpinBox_SpectraConfigEnergyStop.blockSignals(False)
        
        child.setCalibration(self.Calib, self.Sigma)
        child2.setCalibration(self.Calib, self.Sigma)

        child2.doubleSpinBox_CalibrationGain.blockSignals(True)
        child2.doubleSpinBox_CalibrationZero.blockSignals(True)
        child2.doubleSpinBox_CalibrationNoise.blockSignals(True)
        child2.doubleSpinBox_CalibrationFano.blockSignals(True)
        child2.doubleSpinBox_CalibrationGain_2.blockSignals(True)
        child2.doubleSpinBox_CalibrationZero_2.blockSignals(True)
        child2.doubleSpinBox_CalibrationNoise_2.blockSignals(True)
        child2.doubleSpinBox_CalibrationFano_2.blockSignals(True)

        child2.doubleSpinBox_CalibrationGain.setValue(gain * 1000)
        child2.doubleSpinBox_CalibrationZero.setValue(zero * 1000)
        child2.doubleSpinBox_CalibrationNoise.setValue(noise)
        child2.doubleSpinBox_CalibrationFano.setValue(fano)
        child2.doubleSpinBox_CalibrationGain_2.setValue(gain_2 * 1000)
        child2.doubleSpinBox_CalibrationZero_2.setValue(zero_2 * 1000)
        child2.doubleSpinBox_CalibrationNoise_2.setValue(noise_2)
        child2.doubleSpinBox_CalibrationFano_2.setValue(fano_2)

        child2.doubleSpinBox_CalibrationGain.blockSignals(False)
        child2.doubleSpinBox_CalibrationZero.blockSignals(False)
        child2.doubleSpinBox_CalibrationNoise.blockSignals(False)
        child2.doubleSpinBox_CalibrationFano.blockSignals(False)
        child2.doubleSpinBox_CalibrationGain_2.blockSignals(False)
        child2.doubleSpinBox_CalibrationZero_2.blockSignals(False)
        child2.doubleSpinBox_CalibrationNoise_2.blockSignals(False)
        child2.doubleSpinBox_CalibrationFano_2.blockSignals(False)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())