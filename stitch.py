from PyQt6 import QtWidgets, uic
import sys

class StitchWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(StitchWindow, self).__init__(*args, **kwargs)
        uic.loadUi("stitch.ui", self)