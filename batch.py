from PyQt6 import QtWidgets, uic
import sys

class BatchWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(BatchWindow, self).__init__(*args, **kwargs)
        uic.loadUi("batch.ui", self)
