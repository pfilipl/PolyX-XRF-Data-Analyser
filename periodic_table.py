from PyQt6 import QtWidgets, uic
import sys, xraylib

import main

# I wish I could make it by this (XRF parameters when button is hover)
class HoverableButton(QtWidgets.QPushButton):
    def __init__(self, parent = None):
        super(HoverableButton, self).__init__(parent)
#         self.Entered    = False
#     def enterEvent(self, event):
#         self.Entered    = True
#         print("Entered")
#     def leaveEvent(self, event):
#         self.Entered    = False
#         print("Leaved")

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
            self.Elements[Z - 1].pressed.connect(lambda Z = Z: self.Element_pressed(Z))
            self.Elements[Z - 1].released.connect(lambda Z = Z: self.Element_released(Z))

    def Element_clicked(self, Z):
        self.ElementsChecked[Z - 1] = self.Elements[Z - 1].isChecked()

    def Element_pressed(self, Z):
        self.ElementSymbol.setText(xraylib.AtomicNumberToSymbol(Z))
        # self.ElementName    .setText(xraylib.(Z))
        
        try: Ke = xraylib.EdgeEnergy(Z, xraylib.K_SHELL)
        except: Ke = float("NaN")
        self.ElementKedge.setText(f"{Ke:.4f}")
        try: Le = xraylib.EdgeEnergy(Z, xraylib.L1_SHELL)
        except: Le = float("NaN")
        self.ElementLedge.setText(f"{Le:.4f}")
        try: Me = xraylib.EdgeEnergy(Z, xraylib.M1_SHELL)
        except: Me = float("NaN")
        self.ElementMedge.setText(f"{Me:.4f}")

        try: Ka = xraylib.LineEnergy(Z, xraylib.KA_LINE)
        except: Ka = float("NaN")
        self.ElementKalpha.setText(f"{Ka:.4f}")
        try: Kb = xraylib.LineEnergy(Z, xraylib.KB_LINE)
        except: Kb = float("NaN")
        self.ElementKbeta.setText(f"{Kb:.4f}")
        try: La = xraylib.LineEnergy(Z, xraylib.LA_LINE)
        except: La = float("NaN")
        self.ElementLalpha.setText(f"{La:.4f}")
        try: Lb = xraylib.LineEnergy(Z, xraylib.LB_LINE)
        except: Lb = float("NaN")
        self.ElementLbeta.setText(f"{Lb:.4f}")
        try: Ma = xraylib.LineEnergy(Z, xraylib.MA1_LINE)
        except: Ma = float("NaN")
        self.ElementM.setText(f"{Ma:.4f}")

    def Element_released(self, Z):
        self.ElementSymbol.setText("")

        self.ElementKedge.setText("")
        self.ElementLedge.setText("")
        self.ElementMedge.setText("")
        
        self.ElementKalpha.setText("")
        self.ElementKbeta.setText("")
        self.ElementLalpha.setText("")
        self.ElementLbeta.setText("")
        self.ElementM.setText("")

    def setRange(self, Z_start, Z_stop):
        for Z in range(1, 119):
            if Z >= Z_start and Z <= Z_stop:
                self.Elements[Z - 1].setEnabled(True)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())