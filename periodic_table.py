from PyQt6 import QtWidgets, uic
import sys, xraylib, numpy

import main

# I wish I could make it like this (XRF parameters when button is hover)
class HoverableButton(QtWidgets.QPushButton):
    def __init__(self, parent = None):
        super(HoverableButton, self).__init__(parent)

    def enterEvent(self, event):
        self.parent().findChild(QtWidgets.QLabel, "label_ElementSymbol").setText(self.text())

        # self.ElementSymbol.setText(xraylib.AtomicNumberToSymbol(Z))
        # # self.ElementName    .setText(xraylib.(Z))
        
        # try: Ke = xraylib.EdgeEnergy(Z, xraylib.K_SHELL)
        # except: Ke = float("NaN")
        # self.ElementKedge.setText(f"{Ke:.3f}")
        # try: Le = xraylib.EdgeEnergy(Z, xraylib.L1_SHELL)
        # except: Le = float("NaN")
        # self.ElementLedge.setText(f"{Le:.3f}")
        # try: Me = xraylib.EdgeEnergy(Z, xraylib.M1_SHELL)
        # except: Me = float("NaN")
        # self.ElementMedge.setText(f"{Me:.3f}")

        # try: Ka = xraylib.LineEnergy(Z, xraylib.KA_LINE)
        # except: Ka = float("NaN")
        # self.ElementKalpha.setText(f"{Ka:.3f}")
        # try: Kb = xraylib.LineEnergy(Z, xraylib.KB_LINE)
        # except: Kb = float("NaN")
        # self.ElementKbeta.setText(f"{Kb:.3f}")
        # try: La = xraylib.LineEnergy(Z, xraylib.LA_LINE)
        # except: La = float("NaN")
        # self.ElementLalpha.setText(f"{La:.3f}")
        # try: Lb = xraylib.LineEnergy(Z, xraylib.LB_LINE)
        # except: Lb = float("NaN")
        # self.ElementLbeta.setText(f"{Lb:.3f}")
        # try: Ma = xraylib.LineEnergy(Z, xraylib.MA1_LINE)
        # except: Ma = float("NaN")
        # self.ElementM.setText(f"{Ma:.3f}")

    def leaveEvent(self, event):
        return

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
        self.ElementsChecked    = numpy.ones(119, numpy.bool_) * False

        for Z in range(1, 119):
            exec(f"self.Elements.append(self.pushButton_Element{Z})")
            self.Elements[Z - 1].clicked.connect(lambda checked, Z = Z: self.Element_clicked(checked, Z))
            self.Elements[Z - 1].pressed.connect(lambda Z = Z: self.Element_pressed(Z))
            self.Elements[Z - 1].released.connect(lambda Z = Z: self.Element_released(Z))

        # Other
        self.line               = None
        self.roi                = []
        self.calib              = None
        self.sigma              = None

    def setLine(self, line):
        self.line = line

    def getElementsChecked(self):
        return self.ElementsChecked
    
    def setElementsChecked(self, elementsChecked):
        self.ElementsChecked = elementsChecked
        for Z in range(1, 119):
            self.Elements[Z - 1].setChecked(self.ElementsChecked[Z - 1])

    def resetElementsChecked(self):
        for Z in range(1, 119):
            self.Elements[Z - 1].setChecked(False)
            self.ElementsChecked[Z - 1] = False

    def setRange(self, Z_start, Z_stop):
        for Z in range(1, 119):
            if Z >= Z_start and Z <= Z_stop:
                self.Elements[Z - 1].setEnabled(True)

    def Element_clicked(self, checked, Z):
        self.ElementsChecked[Z - 1] = self.Elements[Z - 1].isChecked()
        if checked:
            ROIs = self.parent().parent().parent().parent().findChild(QtWidgets.QTableWidget, "tableWidget_CustomROIs")
            ROIs.insertRow(ROIs.currentRow() + 1)
            ROIs.setItem(ROIs.currentRow() + 1, 0, QtWidgets.QTableWidgetItem(f"{self.Elements[Z - 1].text()}-{self.line}"))
            ROIs.setItem(ROIs.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(str(1000)))
            ROIs.setItem(ROIs.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(str(1500)))
            ROIs.setItem(ROIs.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(str(1.23)))
        else:
            print("BEEEEEEE")

    # def Element_pressed(self, Z):
    #     self.ElementSymbol.setText(xraylib.AtomicNumberToSymbol(Z))
    #     # self.ElementName    .setText(xraylib.(Z))
        
    #     try: Ke = xraylib.EdgeEnergy(Z, xraylib.K_SHELL)
    #     except: Ke = float("NaN")
    #     self.ElementKedge.setText(f"{Ke:.3f}")
    #     try: Le = xraylib.EdgeEnergy(Z, xraylib.L1_SHELL)
    #     except: Le = float("NaN")
    #     self.ElementLedge.setText(f"{Le:.3f}")
    #     try: Me = xraylib.EdgeEnergy(Z, xraylib.M1_SHELL)
    #     except: Me = float("NaN")
    #     self.ElementMedge.setText(f"{Me:.3f}")

    #     try: Ka = xraylib.LineEnergy(Z, xraylib.KA_LINE)
    #     except: Ka = float("NaN")
    #     self.ElementKalpha.setText(f"{Ka:.3f}")
    #     try: Kb = xraylib.LineEnergy(Z, xraylib.KB_LINE)
    #     except: Kb = float("NaN")
    #     self.ElementKbeta.setText(f"{Kb:.3f}")
    #     try: La = xraylib.LineEnergy(Z, xraylib.LA_LINE)
    #     except: La = float("NaN")
    #     self.ElementLalpha.setText(f"{La:.3f}")
    #     try: Lb = xraylib.LineEnergy(Z, xraylib.LB_LINE)
    #     except: Lb = float("NaN")
    #     self.ElementLbeta.setText(f"{Lb:.3f}")
    #     try: Ma = xraylib.LineEnergy(Z, xraylib.MA1_LINE)
    #     except: Ma = float("NaN")
    #     self.ElementM.setText(f"{Ma:.3f}")

    # def Element_released(self, Z):
    #     self.ElementSymbol.setText("")

    #     self.ElementKedge.setText("")
    #     self.ElementLedge.setText("")
    #     self.ElementMedge.setText("")
        
    #     self.ElementKalpha.setText("")
    #     self.ElementKbeta.setText("")
    #     self.ElementLalpha.setText("")
    #     self.ElementLbeta.setText("")
    #     self.ElementM.setText("")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())