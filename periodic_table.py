from PyQt6 import QtWidgets, uic
import sys

import main

class Dictionary:
    def __init__(self):
        self.dictionary = {}

    def add_entry(self, name, description):
        self.dictionary[name] = description

    def get_entry(self, name):
        return self.dictionary.get(name)

class PeriodicTable(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(PeriodicTable, self).__init__(parent)
        uic.loadUi("periodic_table.ui", self)

        # Element info
        self.ElementSymbol      = self.label_ElementSymbol
        self.ElementName        = self.label_ElementName
        self.ElementKedge       = self.label_ElementKedge
        self.ElementKalpha      = self.label_ElementKalpha
        self.ElementKbeta       = self.label_ElementKbeta
        self.ElementLedge       = self.label_ElementLedge
        self.ElementLalpha      = self.label_ElementLalpha
        self.ElementLbeta       = self.label_ElementLbeta
        self.ElementMedge       = self.label_ElementMedge
        self.ElementM           = self.label_ElementM

        # Elements
        self.Elements           = []
        self.ElementsChecked    = []

        for Z in range(1, 119):
            exec(f"self.Elements.append(self.pushButton_Element{Z})")
            self.ElementsChecked.append(self.Elements[Z - 1].isChecked())
            self.Elements[Z - 1].clicked.connect(lambda checked, Z = Z: self.Element_clicked(Z))

    def Element_clicked(self, Z):
        self.ElementsChecked[Z - 1] = self.Elements[Z - 1].isChecked()

    def setRange(self, Z_start, Z_stop):
        for Z in range(1, 119):
            if Z >= Z_start and Z <= Z_stop:
                self.Elements[Z - 1].setEnabled(True)
    
    # def mousePressEvent(self, e):
    #     print(e.button)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())