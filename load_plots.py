from PyQt6 import QtWidgets
import sys, xraylib, matplotlib, numpy, scipy, math

import main, PDA

def MapData(widget, canvas, roiStart = 0, roiStop = 4096, pos = [[0, 0], [1000, 1000]], importLoad = False):
    map = canvas
    head = widget.Data["head"]
    Data = widget.Data["Data"]

    data = Data[2]
    sumSignal = numpy.sum(data[:, :, roiStart:roiStop], axis=2)
    if map.ColorBar: map.ColorBar.remove()
    map.Axes.cla()
    imgMap = map.Axes.imshow(sumSignal.transpose(), origin = 'upper', cmap = 'viridis', aspect = 'equal')
    map.Axes.get_xaxis().set_visible(False)
    map.Axes.get_yaxis().set_visible(False)

    map.Axes2x = map.Axes.secondary_xaxis('bottom', transform = map.Axes.transData)
    map.Axes2x.set_xticks(numpy.linspace(0, data.shape[0] - 1, len(map.Axes.get_xticks()) - 2))
    map.Axes2x.set_xticklabels(numpy.linspace(head["Xpositions"][0, 0], head["Xpositions"][0, -1], len(map.Axes2x.get_xticks())))
    map.Axes2x.set_xlabel("X [mm]")

    map.Axes2y = map.Axes.secondary_yaxis('left', transform = map.Axes.transData)
    map.Axes2y.set_yticks(numpy.linspace(0, data.shape[1] - 1, len(map.Axes.get_yticks()) - 2))
    map.Axes2y.set_yticklabels(numpy.linspace(head["Zpositions"][0, 0], head["Zpositions"][0, -1], len(map.Axes2y.get_yticks())))
    map.Axes2y.set_ylabel("Z [mm]")

    map.Axes.format_coord = lambda x, y: f'x = {head["Xpositions"][0, round(x)]:.3f} mm, z = {head["Zpositions"][0, round(y)]:.3f} mm'

    map.ColorBar = map.figure.colorbar(imgMap)
    map.ColorBar.set_ticks(numpy.linspace(numpy.min(sumSignal), numpy.max(sumSignal), len(map.ColorBar.get_ticks()) - 2))

    if (widget.AreaChanged or widget.PointChanged) and not importLoad:
        if isinstance(pos, list):
            pos = numpy.array(pos)
        PDA.check_pos(pos, [data.shape[0], data.shape[1]])
        if pos.shape[0] == 1:
            x0 = pos[0, 0]
            z0 = pos[0, 1]
            map.Axes.add_patch(matplotlib.patches.Rectangle((x0 - 1, z0 - 1), 2, 2, linewidth = 1, linestyle = '--', edgecolor = 'r', facecolor = 'none'))
        elif pos.shape[0] == 2:
            x0 = min(pos[0, 0], pos[1, 0])
            z0 = min(pos[0, 1], pos[1, 1])
            x1 = max(pos[0, 0], pos[1, 0])
            z1 = max(pos[0, 1], pos[1, 1])
            map.Axes.add_patch(matplotlib.patches.Rectangle((x0 - 1, z0 - 1), x1 - x0 + 2, z1 - z0 + 2, linewidth = 1, linestyle = '--', edgecolor = 'r', facecolor = 'none'))
        else:
            print("Invalid pos!")
                
    map.draw()

def Spectrum(widget, canvas, pos = [[0, 0], [1000, 1000]], Emin = 0.0, Emax = None, roi = None, peaks = True, startLoad = True, importLoad = False):
    spectrum = canvas
    head = widget.Data["head"]
    Data = widget.Data["Data"]
    ROI = widget.Data["ROI"]
    spectrum.Axes.cla()
    if widget.Calib is not None:
        cEmin = (numpy.abs(widget.Calib - Emin * 1000)).argmin() - 1
        if Emax is None:
            Emax = widget.Calib[-1] / 1000
            cEmax = head["bins"][0, 0] - 1
        else:
            cEmax = (numpy.abs(widget.Calib - Emax * 1000)).argmin() + 1
    if isinstance(pos, list):
        pos = numpy.array(pos)
    PDA.check_pos(pos, [Data[2].shape[0], Data[2].shape[1]])
    if pos.shape[0] == 1:
        x0 = pos[0, 0]
        z0 = pos[0, 1]
        x1 = pos[0, 0]
        z1 = pos[0, 1]
    elif pos.shape[0] == 2:
        x0 = min(pos[0, 0], pos[1, 0])
        z0 = min(pos[0, 1], pos[1, 1])
        x1 = max(pos[0, 0], pos[1, 0])
        z1 = max(pos[0, 1], pos[1, 1])
    for d in range(len(Data)):
        data = Data[d]
        if x1 > x0 and z1 > z0:
            sumData = data[x0:x1, z0:z1, :]
            sumData = numpy.sum(numpy.sum(sumData, axis = 0), axis = 0)
        elif x1 == x0 and z1 > z0:
            sumData = data[x0, z0:z1, :]
            sumData = numpy.sum(sumData, axis = 0)
        elif x1 > x0 and z1 == z0:
            sumData = data[x0:x1, z0, :]
            sumData = numpy.sum(sumData, axis = 0)
        else:
            sumData = data[x0, z0, :]
        imgSpectrum = spectrum.Axes.plot(sumData, label = PDA.detectors[d])
    spectrum.Axes.set_yscale('log')
    spectrum.Axes.get_xaxis().set_visible(True)
    spectrum.Axes.get_yaxis().set_visible(True)
    if (widget.AreaChanged or widget.PointChanged) and not (startLoad or importLoad):
        if pos.shape[0] == 1: spectrum.Axes.set_title(f"pos = [{widget.PointX.value()} mm, {widget.PointZ.value()} mm]")
        elif pos.shape[0] == 2: spectrum.Axes.set_title(f"pos = [[{widget.AreaX1.value()} mm, {widget.AreaZ1.value()} mm], [{widget.AreaX2.value()} mm, {widget.AreaZ2.value()} mm]]")

    if widget.Calib is not None:
        spectrum.Axes.set_ylim([1, numpy.max(numpy.sum(numpy.sum(data[x0:x1, z0:z1, cEmin:cEmax], axis = 0), axis = 0)) * 1.5])
    else:
        spectrum.Axes.set_ylim([1, numpy.max(sumData) * 1.5])

    if roi is None and widget.ROIsDefault.isChecked(): roi = ROI
    elif roi is None:
        roi = []
        for row in range(widget.ROIs.rowCount()):
            roi.append([widget.ROIs.item(row, 0).text(), int(widget.ROIs.item(row, 1).text()), int(widget.ROIs.item(row, 2).text()), float(widget.ROIs.item(row, 3).text())])

    if roi is not None:
        for i in range(len(roi)):
            if roi[i][0] != 'Total signal':
                spectrum.Axes.add_patch(matplotlib.patches.Rectangle((roi[i][1], 0), roi[i][2] - roi[i][1], 1, facecolor = 'r', alpha = 0.2, transform = spectrum.Axes.get_xaxis_transform()))
                if widget.Calib is not None:
                    if roi[i][1] + (roi[i][2] - roi[i][1]) / 2 > cEmin and roi[i][1] + (roi[i][2] - roi[i][1]) / 2 < cEmax:
                        spectrum.Axes.text(roi[i][1] + (roi[i][2] - roi[i][1]) / 2, 0.7, roi[i][0], ha = 'center', rotation = 'vertical', transform = spectrum.Axes.get_xaxis_transform())
                else:
                    spectrum.Axes.text(roi[i][1] + (roi[i][2] - roi[i][1]) / 2, 0.7, roi[i][0], ha = 'center', rotation = 'vertical', transform = spectrum.Axes.get_xaxis_transform())

    if peaks is not None:
        if isinstance(peaks, bool):
            if peaks:
                xP = scipy.signal.find_peaks(sumData, height = 1e-5 * numpy.max(sumData), width = 10)
                for xp in xP[0]:
                    if widget.Calib is not None:
                        if  xp > (numpy.abs(widget.Calib - 0)).argmin() + 50:
                            spectrum.Axes.add_artist(matplotlib.lines.Line2D([xp, xp], [0, sumData[xp]], 1.0, '-', 'C2'))
                            if xp > cEmin and xp < cEmax:
                                ka = PDA.Energies['symbol'][(numpy.abs(PDA.Energies['Ka'] - widget.Calib[xp] / 1000)).argmin()]
                                kb = PDA.Energies['symbol'][(numpy.abs(PDA.Energies['Kb'] - widget.Calib[xp] / 1000)).argmin()]
                                la = PDA.Energies['symbol'][(numpy.abs(PDA.Energies['La'] - widget.Calib[xp] / 1000)).argmin()]
                                lb = PDA.Energies['symbol'][(numpy.abs(PDA.Energies['Lb'] - widget.Calib[xp] / 1000)).argmin()]
                                spectrum.Axes.text(xp, 0.05, ka, ha = 'right', rotation = 'vertical', color = 'C4', transform = spectrum.Axes.get_xaxis_transform())
                                spectrum.Axes.text(xp, 0.12, kb, ha = 'right', rotation = 'vertical', color = 'C6', transform = spectrum.Axes.get_xaxis_transform())
                                spectrum.Axes.text(xp, 0.20, la, ha = 'right', rotation = 'vertical', color = 'C5', transform = spectrum.Axes.get_xaxis_transform())
                                spectrum.Axes.text(xp, 0.27, lb, ha = 'right', rotation = 'vertical', color = 'C7', transform = spectrum.Axes.get_xaxis_transform())
                    else:
                        spectrum.Axes.add_artist(matplotlib.lines.Line2D([xp, xp], [0, sumData[xp]], 1.0, '-', 'C2'))
                if widget.Calib is not None:
                    spectrum.Axes.text(0.05, 0.75, "Ka", ha = 'left', color = 'C4', transform = spectrum.Axes.transAxes)
                    spectrum.Axes.text(0.05, 0.80, "Kb", ha = 'left', color = 'C6', transform = spectrum.Axes.transAxes)
                    spectrum.Axes.text(0.05, 0.85, "La", ha = 'left', color = 'C5', transform = spectrum.Axes.transAxes)
                    spectrum.Axes.text(0.05, 0.90, "Lb", ha = 'left', color = 'C7', transform = spectrum.Axes.transAxes)
        elif widget.Calib is not None:
            for name in peaks:
                if name != 'Total signal':
                    try: 
                        element = xraylib.SymbolToAtomicNumber(name.split("-")[-2])
                    except:
                        print("Unknown element symbol!")
                        continue
                    line = name.split("-")[-1]
                    if line == "Ka":
                        line = xraylib.KA_LINE
                    elif line == "Kb":
                        line = xraylib.KB_LINE
                    elif line == "La":
                        line = xraylib.LA_LINE
                    elif line == "Lb":
                        line = xraylib.LB_LINE
                    else:
                        print("Unknown line symbol!")
                        continue
                    xp = (numpy.abs(widget.Calib - xraylib.LineEnergy(element, line) * 1000)).argmin()
                    spectrum.Axes.add_artist(matplotlib.lines.Line2D([xp, xp], [0, 0.5], 1.0, '-', 'red', transform = spectrum.Axes.get_xaxis_transform()))
                    if xp > cEmin and xp < cEmax:
                        spectrum.Axes.text(xp, 0.55, name, ha = 'center', rotation = 'vertical', color = 'red', transform = spectrum.Axes.get_xaxis_transform())
    
    spectrum.Axes.legend(loc = "upper right", ncols = len(Data), facecolor = "None", edgecolor = "None")
    
    if widget.Calib is None:
        spectrum.Axes.set_xlim([0, head["bins"][0, 0]])
        spectrum.Axes.set_xticks(range(0, head["bins"][0, 0] + 1, math.floor(head["bins"][0, 0]/4)))
        spectrum.Axes.set_xlabel("channel")
        spectrum.Axes.format_coord = lambda x, y: f'x = {x:d} ch, y = {y:.3e}'
    else:
        spectrum.Axes.get_xaxis().set_visible(False)
        spectrum.Axes2x = spectrum.Axes.secondary_xaxis('bottom', transform = spectrum.Axes.transData)
        spectrum.Axes.set_xlim([cEmin, cEmax])
        Eval = numpy.linspace(Emin * 1000, Emax * 1000, len(spectrum.Axes.get_xticks()) - 2)
        E = []
        for eval in Eval:
            E.append((numpy.abs(widget.Calib - eval)).argmin())
        spectrum.Axes2x.set_xticks(E)
        spectrum.Axes2x.set_xticklabels(numpy.abs(numpy.round(widget.Calib[E] / 1000, 2)))
        spectrum.Axes2x.set_xlabel("E [keV]")
        spectrum.Axes.format_coord = lambda x, y: f'E = {widget.Calib[round(x)] / 1000:.3f} keV, y = {y:.3e}'

    spectrum.draw()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())