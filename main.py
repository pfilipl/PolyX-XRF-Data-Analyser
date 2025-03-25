from PyQt6 import QtWidgets, uic
import sys

import PDA

CALIB_NBINS = 4096

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi("main.ui", self)
        self.setWindowTitle('PolyX Data Analyser')

        self.Calib              = None
        self.Sigma              = None

        # Single
        self.Single             = self.tab_Single

        self.Single.doubleSpinBox_CalibrationGain.valueChanged.connect(self.setCalibrationSingle)
        self.Single.doubleSpinBox_CalibrationZero.valueChanged.connect(self.setCalibrationSingle)
        self.Single.doubleSpinBox_CalibrationNoise.valueChanged.connect(self.setCalibrationSingle)
        self.Single.doubleSpinBox_CalibrationFano.valueChanged.connect(self.setCalibrationSingle)

        # Batch
        self.Batch              = self.tab_Batch

        self.Batch.doubleSpinBox_CalibrationGain.valueChanged.connect(self.setCalibrationBatch)
        self.Batch.doubleSpinBox_CalibrationZero.valueChanged.connect(self.setCalibrationBatch)
        self.Batch.doubleSpinBox_CalibrationNoise.valueChanged.connect(self.setCalibrationBatch)
        self.Batch.doubleSpinBox_CalibrationFano.valueChanged.connect(self.setCalibrationBatch)

        # Stitch
        self.Stitch             = self.tab_Stitch

    def setCalibrationSingle(self):
        gain = self.Single.doubleSpinBox_CalibrationGain.value()
        zero = self.Single.doubleSpinBox_CalibrationZero.value()
        noise = self.Single.doubleSpinBox_CalibrationNoise.value()
        fano = self.Single.doubleSpinBox_CalibrationFano.value()
        self.Calib, self.Sigma  = PDA.gen_calib(CALIB_NBINS, gain, zero, noise, fano)

        self.Single.setCalibration(self.Calib, self.Sigma)
        self.Batch.setCalibration(self.Calib, self.Sigma)

        self.Batch.doubleSpinBox_CalibrationGain.blockSignals(True)
        self.Batch.doubleSpinBox_CalibrationZero.blockSignals(True)
        self.Batch.doubleSpinBox_CalibrationNoise.blockSignals(True)
        self.Batch.doubleSpinBox_CalibrationFano.blockSignals(True)

        self.Batch.doubleSpinBox_CalibrationGain.setValue(gain)
        self.Batch.doubleSpinBox_CalibrationZero.setValue(zero)
        self.Batch.doubleSpinBox_CalibrationNoise.setValue(noise)
        self.Batch.doubleSpinBox_CalibrationFano.setValue(fano)

        self.Batch.doubleSpinBox_CalibrationGain.blockSignals(False)
        self.Batch.doubleSpinBox_CalibrationZero.blockSignals(False)
        self.Batch.doubleSpinBox_CalibrationNoise.blockSignals(False)
        self.Batch.doubleSpinBox_CalibrationFano.blockSignals(False)

    def setCalibrationBatch(self):
        gain = self.Batch.doubleSpinBox_CalibrationGain.value()
        zero = self.Batch.doubleSpinBox_CalibrationZero.value()
        noise = self.Batch.doubleSpinBox_CalibrationNoise.value()
        fano = self.Batch.doubleSpinBox_CalibrationFano.value()
        self.Calib, self.Sigma  = PDA.gen_calib(CALIB_NBINS, gain, zero, noise, fano)

        self.Batch.setCalibration(self.Calib, self.Sigma)
        self.Single.setCalibration(self.Calib, self.Sigma)

        self.Single.doubleSpinBox_CalibrationGain.blockSignals(True)
        self.Single.doubleSpinBox_CalibrationZero.blockSignals(True)
        self.Single.doubleSpinBox_CalibrationNoise.blockSignals(True)
        self.Single.doubleSpinBox_CalibrationFano.blockSignals(True)

        self.Single.doubleSpinBox_CalibrationGain.setValue(gain)
        self.Single.doubleSpinBox_CalibrationZero.setValue(zero)
        self.Single.doubleSpinBox_CalibrationNoise.setValue(noise)
        self.Single.doubleSpinBox_CalibrationFano.setValue(fano)

        self.Single.doubleSpinBox_CalibrationGain.blockSignals(False)
        self.Single.doubleSpinBox_CalibrationZero.blockSignals(False)
        self.Single.doubleSpinBox_CalibrationNoise.blockSignals(False)
        self.Single.doubleSpinBox_CalibrationFano.blockSignals(False)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())