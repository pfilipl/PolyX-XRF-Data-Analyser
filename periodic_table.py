from PyQt6 import QtCore, QtWidgets, uic
import sys, os, xraylib, numpy, pathlib

import main, PDA

basedir = pathlib.Path(os.path.dirname(__file__))

ElementNames = {
    "H" : "Hydrogen", "He" : "Helium", "Li" : "Lithium", "Be" : "Beryllium", "B" : "Boron", 
    "C" : "Carbon", "N" : "Nitrogen", "O" : "Oxygen", "F" : "Fluorine", "Ne" : "Neon", 
    "Na" : "Sodium", "Mg" : "Magnesium", "Al" : "Aluminium", "Si" : "Silicon", "P" : "Phosphorus", 
    "S" : "Sulfur", "Cl" : "Chlorine", "Ar" : "Argon", "K" : "Potassium", "Ca" : "Calcium", 
    "Sc" : "Scandium", "Ti" : "Titanium", "V" : "Vanadium", "Cr" : "Chromium", "Mn" : "Manganese", 
    "Fe" : "Iron", "Co" : "Cobalt", "Ni" : "Nickel", "Cu" : "Copper", "Zn" : "Zinc", "Ga" : "Gallium", 
    "Ge" : "Germanium", "As" : "Arsenic", "Se" : "Selenium", "Br" : "Bromine", "Kr" : "Krypton", 
    "Rb" : "Rubidium", "Sr" : "Strontium", "Y" : "Yttrium", "Zr" : "Zirconium", "Nb" : "Niobium", 
    "Mo" : "Molybdenum", "Tc" : "Technetium", "Ru" : "Ruthenium", "Rh" : "Rhodium", "Pd" : "Palladium", 
    "Ag" : "Silver", "Cd" : "Cadmium", "In" : "Indium", "Sn" : "Tin", "Sb" : "Antimony", 
    "Te" : "Tellurium", "I" : "Iodine", "Xe" : "Xenon", "Cs" : "Caesium", "Ba" : "Barium", 
    "La" : "Lanthanum", "Ce" : "Cerium", "Pr" : "Praseodymium", "Nd" : "Neodymium", "Pm" : "Promethium", 
    "Sm" : "Samarium", "Eu" : "Europium", "Gd" : "Gadolinium", "Tb" : "Terbium", "Dy" : "Dysprosium", 
    "Ho" : "Holmium", "Er" : "Erbium", "Tm" : "Thulium", "Yb" : "Ytterbium", "Lu" : "Lutetium", 
    "Hf" : "Hafnium", "Ta" : "Tantalum", "W" : "Tungsten", "Re" : "Rhenium", "Os" : "Osmium", 
    "Ir" : "Iridium", "Pt" : "Platinum", "Au" : "Gold", "Hg" : "Mercury", "Tl" : "Thallium", 
    "Pb" : "Lead", "Bi" : "Bismuth", "Po" : "Polonium", "At" : "Astatine", "Rn" : "Radon", 
    "Fr" : "Francium", "Ra" : "Radium", "Ac" : "Actinium", "Th" : "Thorium", "Pa" : "Protactinium", 
    "U" : "Uranium", "Np" : "Neptunium", "Pu" : "Plutonium", "Am" : "Americium", "Cm" : "Curium", 
    "Bk" : "Berkelium", "Cf" : "Californium", "Es" : "Einsteinium", "Fm" : "Fermium", 
    "Md" : "Mendelevium", "No" : "Nobelium", "Lr" : "Lawrencium", "Rf" : "Rutherfordium", 
    "Db" : "Dubnium", "Sg" : "Seaborgium", "Bh" : "Bohrium", "Hs" : "Hassium", "Mt" : "Meitnerium", 
    "Ds" : "Darmstadtium", "Rg" : "Roentgenium", "Cn" : "Copernicium", "Nh" : "Nihonium", 
    "Fl" : "Flerovium", "Mc" : "Moscovium", "Lv" : "Livermorium", "Ts" : "Tennessine", "Og" : "Oganesson"
}

class HoverableButton(QtWidgets.QPushButton):
    def __init__(self, parent = None):
        super(HoverableButton, self).__init__(parent)

    def enterEvent(self, event):
        self.parent().findChild(QtWidgets.QLabel, "label_ElementSymbol").setText(self.text())
        self.parent().findChild(QtWidgets.QLabel, "label_ElementName").setText(ElementNames[self.text()])
        
        try: Ke = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(self.text()), xraylib.K_SHELL)
        except: Ke = float("NaN")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementKedge").setText(f"{Ke:.3f}")
        try: L3e = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(self.text()), xraylib.L3_SHELL)
        except: L3e = float("NaN")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementL3edge").setText(f"{L3e:.3f}")
        try: L2e = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(self.text()), xraylib.L2_SHELL)
        except: L2e = float("NaN")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementL2edge").setText(f"{L2e:.3f}")
        try: Me = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(self.text()), xraylib.M5_SHELL)
        except: Me = float("NaN")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementMedge").setText(f"{Me:.3f}")

        try: Ka = xraylib.LineEnergy(xraylib.SymbolToAtomicNumber(self.text()), xraylib.KA_LINE)
        except: Ka = float("NaN")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementKalpha").setText(f"{Ka:.3f}")
        try: Kb = xraylib.LineEnergy(xraylib.SymbolToAtomicNumber(self.text()), xraylib.KB_LINE)
        except: Kb = float("NaN")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementKbeta").setText(f"{Kb:.3f}")
        try: La = xraylib.LineEnergy(xraylib.SymbolToAtomicNumber(self.text()), xraylib.LA_LINE)
        except: La = float("NaN")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementLalpha").setText(f"{La:.3f}")
        try: Lb = xraylib.LineEnergy(xraylib.SymbolToAtomicNumber(self.text()), xraylib.LB_LINE)
        except: Lb = float("NaN")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementLbeta").setText(f"{Lb:.3f}")
        try: M = xraylib.LineEnergy(xraylib.SymbolToAtomicNumber(self.text()), xraylib.MA1_LINE)
        except: M = float("NaN")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementM").setText(f"{M:.3f}")

    def leaveEvent(self, event):
        self.parent().findChild(QtWidgets.QLabel, "label_ElementSymbol").setText("")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementName").setText("")

        self.parent().findChild(QtWidgets.QLabel, "label_ElementKedge").setText("")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementL3edge").setText("")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementL2edge").setText("")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementMedge").setText("")

        self.parent().findChild(QtWidgets.QLabel, "label_ElementKalpha").setText("")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementKbeta").setText("")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementLalpha").setText("")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementLbeta").setText("")
        self.parent().findChild(QtWidgets.QLabel, "label_ElementM").setText("")

class PeriodicTable(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(PeriodicTable, self).__init__(parent)
        uic.loadUi(basedir / "periodic_table.ui", self)

        # Elements info
        self.ElementKedge       = self.label_ElementKedge
        self.ElementL3edge      = self.label_ElementL3edge
        self.ElementL2edge      = self.label_ElementL2edge
        self.ElementMedge       = self.label_ElementMedge

        self.KedgeLabel         = self.label_KedgeLabel
        self.L3edgeLabel        = self.label_L3edgeLabel
        self.L2edgeLabel        = self.label_L2edgeLabel
        self.MedgeLabel         = self.label_MedgeLabel

        self.KedgeUnit          = self.label_KedgeUnit
        self.L3edgeUnit         = self.label_L3edgeUnit
        self.L2edgeUnit         = self.label_L2edgeUnit
        self.MedgeUnit          = self.label_MedgeUnit

        self.ElementKalpha      = self.label_ElementKalpha
        self.ElementKbeta       = self.label_ElementKbeta
        self.ElementLalpha      = self.label_ElementLalpha
        self.ElementLbeta       = self.label_ElementLbeta
        self.ElementM           = self.label_ElementM  

        self.KalphaLabel        = self.label_KalphaLabel
        self.KbetaLabel         = self.label_KbetaLabel
        self.LalphaLabel        = self.label_LalphaLabel
        self.LbetaLabel         = self.label_LbetaLabel
        self.MLabel             = self.label_MLabel

        self.KalphaUnit         = self.label_KalphaUnit
        self.KbetaUnit          = self.label_KbetaUnit
        self.LalphaUnit         = self.label_LalphaUnit
        self.LbetaUnit          = self.label_LbetaUnit
        self.MUnit              = self.label_MUnit

        # Elements
        self.Elements           = []
        self.ElementsChecked    = numpy.ones(119, numpy.bool_) * False

        for Z in range(1, 119):
            exec(f"self.Elements.append(self.pushButton_Element{Z})")
            self.Elements[Z - 1].clicked.connect(lambda checked, Z = Z: self.Element_clicked(checked, Z))

        # Other
        self.RoiCount           = 0
        self.line               = None
        self.calib              = None
        self.sigma              = None
        
    # Setters
    def setRoiCount(self, roiCount):
        self.RoiCount = roiCount

    def setLine(self, line):
        self.line = line
        if self.line == "Ka":
            self.ElementKedge.setEnabled(True)
            self.KedgeLabel.setEnabled(True)
            self.KedgeUnit.setEnabled(True)
            self.ElementKalpha.setEnabled(True)
            self.KalphaLabel.setEnabled(True)
            self.KalphaUnit.setEnabled(True)
        elif self.line == "Kb":
            self.ElementKedge.setEnabled(True)
            self.KedgeLabel.setEnabled(True)
            self.KedgeUnit.setEnabled(True)
            self.ElementKbeta.setEnabled(True)
            self.KbetaLabel.setEnabled(True)
            self.KbetaUnit.setEnabled(True)
        elif self.line == "La":
            self.ElementL3edge.setEnabled(True)
            self.L3edgeLabel.setEnabled(True)
            self.L3edgeUnit.setEnabled(True)
            self.ElementLalpha.setEnabled(True)
            self.LalphaLabel.setEnabled(True)
            self.LalphaUnit.setEnabled(True)
        elif self.line == "Lb":
            self.ElementL2edge.setEnabled(True)
            self.L2edgeLabel.setEnabled(True)
            self.L2edgeUnit.setEnabled(True)
            self.ElementLbeta.setEnabled(True)
            self.LbetaLabel.setEnabled(True)
            self.LbetaUnit.setEnabled(True)
        elif self.line == "M":
            self.ElementMedge.setEnabled(True)
            self.MedgeLabel.setEnabled(True)
            self.MedgeUnit.setEnabled(True)
            self.ElementM.setEnabled(True)
            self.MLabel.setEnabled(True)
            self.MUnit.setEnabled(True)

    def setCalibration(self, calib, sigma):
        self.calib = calib
        self.sigma = sigma

    def setElementChecked(self, Z, state):
        self.Elements[Z - 1].setChecked(state)
        self.ElementsChecked[Z - 1] = state

    def setElementsChecked(self, elementsChecked):
        self.ElementsChecked = elementsChecked
        for Z in range(1, 119):
            self.Elements[Z - 1].setChecked(self.ElementsChecked[Z - 1])
    
    def setRange(self, Z_start, Z_stop):
        for Z in range(1, 119):
            if Z >= Z_start and Z <= Z_stop:
                self.Elements[Z - 1].setEnabled(True)

    def setRangeByName(self, startName, stopName):
        try:
            Z_start = xraylib.SymbolToAtomicNumber(startName)
            Z_stop = xraylib.SymbolToAtomicNumber(stopName)
        except:
            print("Wrong element name!")
        else:
            self.setRange(Z_start, Z_stop)

    # Resetters
    def resetElementsChecked(self):
        for Z in range(1, 119):
            self.Elements[Z - 1].setChecked(False)
            self.ElementsChecked[Z - 1] = False

    # Getters
    def getElementsChecked(self):
        return self.ElementsChecked

    # Slots
    def Element_clicked(self, checked, Z):
        ROIs = self.parent().parent().parent().parent().findChild(QtWidgets.QTableWidget, "tableWidget_CustomROIs")
        self.ElementsChecked[Z - 1] = self.Elements[Z - 1].isChecked()
        self.RoiCount += 1
        name = f"{self.Elements[Z - 1].text()}-{self.line}"
        if len(ROIs.findItems(name, QtCore.Qt.MatchFlag.MatchExactly)) > 0:
            name = f"{name}_{self.RoiCount}"

        if checked:
            roi = []
            sigmaWidth = self.parent().parent().parent().findChild(QtWidgets.QDoubleSpinBox, "doubleSpinBox_XRFSigmaWidth").value()
            Width = self.parent().parent().parent().findChild(QtWidgets.QSpinBox, "spinBox_XRFWidth").value()
            PDA.add_ROI(roi, f"{self.Elements[Z - 1].text()}-{self.line}", self.calib, self.sigma, sigmaWidth, Width)
            ROIs.insertRow(ROIs.currentRow() + 1)
            ROIs.setItem(ROIs.currentRow() + 1, 0, QtWidgets.QTableWidgetItem(f"{name}"))
            ROIs.setItem(ROIs.currentRow() + 1, 1, QtWidgets.QTableWidgetItem(str(int(roi[-1][1]))))
            ROIs.setItem(ROIs.currentRow() + 1, 2, QtWidgets.QTableWidgetItem(str(int(roi[-1][2]))))
            ROIs.setItem(ROIs.currentRow() + 1, 3, QtWidgets.QTableWidgetItem(str(PDA.SDD1toSDD2ratio)))
            ROIs.setItem(ROIs.currentRow() + 1, 4, QtWidgets.QTableWidgetItem(str(max(roi[-1][3], 1))))
            ROIs.setItem(ROIs.currentRow() + 1, 5, QtWidgets.QTableWidgetItem(str(min(roi[-1][4], 4096))))
            ROIs.setItem(ROIs.currentRow() + 1, 6, QtWidgets.QTableWidgetItem(str(max(roi[-1][5], 1))))
            ROIs.setItem(ROIs.currentRow() + 1, 7, QtWidgets.QTableWidgetItem(str(min(roi[-1][6], 4096)))) 
            ROIs.setCurrentCell(ROIs.currentRow() + 1, 0)
        else:
            for item in ROIs.findItems(f"{self.Elements[Z - 1].text()}-{self.line}", QtCore.Qt.MatchFlag.MatchExactly):
                ROIs.removeRow(item.row())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())