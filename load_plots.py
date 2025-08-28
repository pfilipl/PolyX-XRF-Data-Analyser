from PyQt6 import QtWidgets
import matplotlib.patches
import sys, xraylib, matplotlib, numpy, scipy, math

import main, PDA

def setTicks(secAxes, axes, newTicks, maximum, mode, precision = 2):
    if mode == "X":
        lim = axes.get_xlim()
        lim = [max(0, lim[0]), min(lim[1], maximum - 1)]
        axes.set_xlim(lim)
        X = numpy.linspace(lim[0], lim[1], len(axes.get_xticks()) - 2).astype(int)
        secAxes.set_xticks(X)
        secAxes.set_xticklabels(numpy.round(newTicks[X], precision))
    elif mode == "Y":
        lim = axes.get_ylim()
        lim = [min(lim[0], maximum - 1), max(0, lim[1])]
        axes.set_ylim(lim)
        Y = numpy.linspace(lim[0], lim[1], len(axes.get_yticks()) - 2).astype(int)
        secAxes.set_yticks(Y)
        secAxes.set_yticklabels(numpy.round(newTicks[Y], precision))

def MapData(widget, tab, detector = 2, pos = [[0, 0], [1000, 1000]], importLoad = False, Vmin = None, Vmax = None, Aspect = 'equal', Cmap = 'viridis', Norm = None, clabel = "Counts [cps]"):
    map = tab.Canvas
    head = widget.Data["head"]
    if detector == 2:
        data = widget.Data["Data"][0] + tab.RoiFactor * widget.Data["Data"][1]
    else:
        data = widget.Data["Data"][detector]
    roiStart = tab.RoiStart
    roiStop = tab.RoiStop

    sumSignal = numpy.sum(data[:, :, roiStart:roiStop], axis=2)
    if Norm is not None:
        I0 = Norm[0]
        LT = Norm[1]
        sumSignal = sumSignal / I0 / (LT[detector] * 1e-6)

    if map.ColorBar: map.ColorBar.remove()
    map.Axes.cla()
    imgMap = map.Axes.imshow(sumSignal.transpose(), origin = 'upper', cmap = Cmap, aspect = Aspect, vmin = Vmin, vmax = Vmax)
    map.Axes.get_xaxis().set_visible(False)
    map.Axes.get_yaxis().set_visible(False)
    # map.Axes.invert_xaxis()

    map.Axes2x = map.Axes.secondary_xaxis('bottom')
    map.Axes2x.set_xlabel("X [mm]")
    map.Axes2x.callbacks.connect("xlim_changed", lambda secAxes: setTicks(secAxes, map.Axes, head["Xpositions"][0, :], len(head["Xpositions"][0, :]), "X", 3))

    map.Axes2y = map.Axes.secondary_yaxis('left')
    map.Axes2y.set_ylabel("Z [mm]")
    map.Axes2y.callbacks.connect("ylim_changed", lambda secAxes: setTicks(secAxes, map.Axes, head["Zpositions"][0, :], len(head["Zpositions"][0, :]), "Y", 3))

    map.Axes.format_coord = lambda x, y: f'x = {head["Xpositions"][0, round(x)]:.3f} mm, z = {head["Zpositions"][0, round(y)]:.3f} mm'

    map.ColorBar = map.figure.colorbar(imgMap)
    map.ColorBar.set_ticks(numpy.linspace(max(numpy.min(sumSignal), Vmin) if Vmin is not None else numpy.min(sumSignal), min(numpy.max(sumSignal), Vmax) if Vmax is not None else numpy.max(sumSignal), len(map.ColorBar.get_ticks()) - 2))
    if clabel: map.ColorBar.set_label(clabel)

    if (widget.AreaChanged or widget.PointChanged) and not importLoad:
        if isinstance(pos, list):
            pos = numpy.array(pos)
        PDA.check_pos(pos, [data.shape[0], data.shape[1]])
        if pos.shape[0] == 1:
            x0 = pos[0, 0]
            z0 = pos[0, 1]
            # map.Axes.add_patch(matplotlib.patches.Rectangle((x0 - 1, z0 - 1), 2, 2, linewidth = 1, linestyle = '--', edgecolor = 'r', facecolor = 'none'))
            h = 0.05 * (map.Axes.get_xlim()[1] - map.Axes.get_xlim()[0])
            v = 0.05 * (map.Axes.get_ylim()[1] - map.Axes.get_ylim()[0])
            map.Axes.add_artist(matplotlib.lines.Line2D([x0 - h, x0 + h], [z0, z0], linewidth = 1, linestyle = '--', color = 'r'))
            map.Axes.add_artist(matplotlib.lines.Line2D([x0, x0], [z0 - v, z0 + v], linewidth = 1, linestyle = '--', color = 'r'))
        elif pos.shape[0] == 2:
            x0 = min(pos[0, 0], pos[1, 0])
            z0 = min(pos[0, 1], pos[1, 1])
            x1 = max(pos[0, 0], pos[1, 0])
            z1 = max(pos[0, 1], pos[1, 1])
            map.Axes.add_patch(matplotlib.patches.Rectangle((x0 - 1, z0 - 1), x1 - x0 + 2, z1 - z0 + 2, linewidth = 1, linestyle = '--', edgecolor = 'r', facecolor = 'none'))
        else:
            print("Invalid pos!")
                
    map.draw()

def PlotStats1D(widget, tab, dataName, ylabel = None, importLoad = False):
    plot = tab.Canvas
    head = widget.Data["head"]
    data = widget.Data[dataName]

    plot.Axes.cla()
    imgMap = plot.Axes.plot(data, ".-")
    plot.Axes.get_xaxis().set_visible(False)
    plot.Axes.get_yaxis().set_visible(True)
    plot.Axes.set_xlim([0, len(data)])
    if ylabel: plot.Axes.set_ylabel(ylabel)

    plot.Axes2x = plot.Axes.secondary_xaxis('bottom')
    plot.Axes2x.set_xlabel("Z [mm]")
    plot.Axes2x.callbacks.connect("xlim_changed", lambda secAxes: setTicks(secAxes, plot.Axes, head["Zpositions"][0, :], len(head["Zpositions"][0, :]), "X", 3))

    plot.Axes.format_coord = lambda x, y: f'z = {head["Zpositions"][0, round(x)]:.3f} mm, I = {y:.3f} mA'

    plot.draw()

def MapStats2D(widget, tab, dataName, detector = 2, clabel = None, importLoad = False, Vmin = None, Vmax = None, Aspect = 'equal', Cmap = 'viridis'):
    if detector != 2 or dataName == "I0": # do not draw statistic data for SDDSum
        map = tab.Canvas
        head = widget.Data["head"]
        Data = widget.Data[dataName]

        if isinstance(Data, list):
            data = Data[detector]
        else:
            data = Data

        if map.ColorBar: map.ColorBar.remove()
        map.Axes.cla()
        imgMap = map.Axes.imshow(data.transpose(), origin = 'upper', cmap = Cmap, aspect = Aspect, vmin = Vmin, vmax = Vmax)
        map.Axes.get_xaxis().set_visible(False)
        map.Axes.get_yaxis().set_visible(False)
        # map.Axes.invert_xaxis()

        map.Axes2x = map.Axes.secondary_xaxis('bottom')
        map.Axes2x.set_xlabel("X [mm]")
        map.Axes2x.callbacks.connect("xlim_changed", lambda secAxes: setTicks(secAxes, map.Axes, head["Xpositions"][0, :], len(head["Xpositions"][0, :]), "X", 3))

        map.Axes2y = map.Axes.secondary_yaxis('left')
        map.Axes2y.set_ylabel("Z [mm]")
        map.Axes2y.callbacks.connect("ylim_changed", lambda secAxes: setTicks(secAxes, map.Axes, head["Zpositions"][0, :], len(head["Zpositions"][0, :]), "Y", 3))

        map.Axes.format_coord = lambda x, y: f'x = {head["Xpositions"][0, round(x)]:.3f} mm, z = {head["Zpositions"][0, round(y)]:.3f} mm'

        map.ColorBar = map.figure.colorbar(imgMap)
        map.ColorBar.set_ticks(numpy.linspace(max(numpy.min(data), Vmin) if Vmin is not None else numpy.min(data), min(numpy.max(data), Vmax) if Vmax is not None else numpy.max(data), len(map.ColorBar.get_ticks()) - 2))
        if clabel: map.ColorBar.set_label(clabel)

        map.draw()

def SpectrumCheck(widget, tab, func = numpy.sum, Emin = 0.0, Emax = None, log = False, Aspect = 'auto'):
    spectrum = tab.Canvas
    head = widget.Data["head"]
    spectrum.Axes.cla()
    if widget.Calib is not None:
        cEmin = (numpy.abs(widget.Calib - Emin * 1000)).argmin() - 1
        if Emax is None:
            Emax = widget.Calib[-1] / 1000
            cEmax = head["bins"][0, 0] - 1
        else:
            cEmax = (numpy.abs(widget.Calib - Emax * 1000)).argmin() + 1

    for d in [0, 1]:
        data = widget.Data["Data"][d]
        spectrum.Axes.plot(func(func(data, axis = 0), axis = 0), label = f"{PDA.detectors[d]}")
        spectrum.Axes.set_ylim([1 if log else 0, numpy.max([numpy.max(data) * 1.5 if log else numpy.max(data) * 1.05, spectrum.Axes.get_ylim()[1]], axis = 0)])
    spectrum.Axes.legend()
    if log:
        spectrum.Axes.set_yscale('log')
    spectrum.Axes.set_ylabel("Counts [cps]")

    if widget.Calib is None:
        spectrum.Axes.set_xlim([0, head["bins"][0, 0]])
        spectrum.Axes.set_xticks(range(0, head["bins"][0, 0] + 1, math.floor(head["bins"][0, 0]/4)))
        spectrum.Axes.set_xlabel("channel")
        spectrum.Axes.format_coord = lambda x, y: f'x = {x:d} ch, y = {y:.3e}'
    else:
        spectrum.Axes.get_xaxis().set_visible(False)
        spectrum.Axes.get_yaxis().set_visible(True)
        spectrum.Axes.set_xlim([cEmin, cEmax])
        spectrum.Axes2x = spectrum.Axes.secondary_xaxis('bottom')
        spectrum.Axes2x.set_xlabel("E [eV]")
        spectrum.Axes2x.callbacks.connect("xlim_changed", lambda secAxes: setTicks(secAxes, spectrum.Axes, widget.Calib, 4096, "X"))
        spectrum.Axes.format_coord = lambda x, y: f'E = {widget.Calib[round(x)]:.3f} eV, y = {y:.3e}'

    spectrum.Axes.set_aspect(Aspect)
    spectrum.draw()

def Spectrum(widget, tab, func = numpy.sum, detector = 2, pos = [[0, 0], [1000, 1000]], Emin = 0.0, Emax = None, roi = None, peaks = True, startLoad = True, importLoad = False, Aspect = 'auto'):
    spectrum = tab.Canvas
    head = widget.Data["head"]
    data = widget.Data["Data"][detector]
    ROI = widget.Data["ROI"]
    spectrum.Axes.cla()
    if widget.Calib is not None:
        cEmin = (numpy.abs(widget.Calib - Emin * 1000)).argmin() - 1
        if Emax is None:
            Emax = widget.Calib[-1] / 1000
            cEmax = head["bins"][0, 0] - 1
        else:
            cEmax = (numpy.abs(widget.Calib - Emax * 1000)).argmin() + 1
    if pos is None:
        pos = [[0, 0], [1000, 1000]]
    if isinstance(pos, list):
        pos = numpy.array(pos)
    PDA.check_pos(pos, [data.shape[0], data.shape[1]])
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
        
    if x1 > x0 and z1 > z0:
        sumData = data[x0:x1, z0:z1, :]
        sumData = func(func(sumData, axis = 0), axis = 0)
    elif x1 == x0 and z1 > z0:
        sumData = data[x0, z0:z1, :]
        sumData = func(sumData, axis = 0)
    elif x1 > x0 and z1 == z0:
        sumData = data[x0:x1, z0, :]
        sumData = func(sumData, axis = 0)
    else:
        sumData = data[x0, z0, :]
    imgSpectrum = spectrum.Axes.plot(sumData)

    if func == numpy.sum and not widget.PointChanged: spectrum.Axes.set_yscale('log')
    spectrum.Axes.set_ylabel("Counts [cps]")
    spectrum.Axes.get_xaxis().set_visible(True)
    spectrum.Axes.get_yaxis().set_visible(True)
    if (widget.AreaChanged or widget.PointChanged) and not (startLoad or importLoad):
        if pos.shape[0] == 1: spectrum.Axes.set_title(f"pos = [{widget.PointX.value()} mm, {widget.PointZ.value()} mm]")
        elif pos.shape[0] == 2: spectrum.Axes.set_title(f"pos = [[{widget.AreaX1.value()} mm, {widget.AreaZ1.value()} mm], [{widget.AreaX2.value()} mm, {widget.AreaZ2.value()} mm]]" + r", area = {0} $\times$ {1} px$^2$".format(x1 - x0, z1 - z0))

    if widget.Calib is not None:
        if func == numpy.sum: spectrum.Axes.set_ylim([1, numpy.max(sumData[cEmin:cEmax]) * 1.5])
        else: spectrum.Axes.set_ylim([0, numpy.max(sumData[cEmin:cEmax]) * 1.05])
    else:
        if func == numpy.sum: spectrum.Axes.set_ylim([1, numpy.max(sumData) * 1.5])
        else: spectrum.Axes.set_ylim([0, numpy.max(sumData) * 1.05])

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
                        spectrum.Axes.text(roi[i][1] + (roi[i][2] - roi[i][1]) / 2, 0.7, roi[i][0], ha = 'center', rotation = 'vertical', transform = spectrum.Axes.get_xaxis_transform(), clip_on = True)
                else:
                    spectrum.Axes.text(roi[i][1] + (roi[i][2] - roi[i][1]) / 2, 0.7, roi[i][0], ha = 'center', rotation = 'vertical', transform = spectrum.Axes.get_xaxis_transform(), clip_on = True)

    if peaks is not None:
        if isinstance(peaks, bool):
            if peaks:
                xP = scipy.signal.find_peaks(sumData, height = 1e-5 * numpy.max(sumData), width = 10)
                for xp in xP[0]:
                    if widget.Calib is not None:
                        if ((widget.monoE is not None) and xp > (numpy.abs(widget.Calib - 0)).argmin() + 50 and xp < (numpy.abs(widget.Calib - widget.monoE)).argmin()) or widget.monoE is None and xp > (numpy.abs(widget.Calib - 0)).argmin() + 50:
                            spectrum.Axes.add_artist(matplotlib.lines.Line2D([xp, xp], [0, sumData[xp]], linewidth=1.0, linestyle='-', color='C1'))
                            ts = False * numpy.ones((5, 1))
                            kadifft = numpy.abs(PDA.Energies['Ka'] - widget.Calib[xp] / 1000)
                            kbdifft = numpy.abs(PDA.Energies['Kb'] - widget.Calib[xp] / 1000)
                            ladifft = numpy.abs(PDA.Energies['La'] - widget.Calib[xp] / 1000)
                            lbdifft = numpy.abs(PDA.Energies['Lb'] - widget.Calib[xp] / 1000)
                            mdifft  = numpy.abs(PDA.Energies['M']  - widget.Calib[xp] / 1000)
                            ka = PDA.Energies['symbol'][kadifft.argmin()]
                            kb = PDA.Energies['symbol'][kbdifft.argmin()]
                            la = PDA.Energies['symbol'][ladifft.argmin()]
                            lb = PDA.Energies['symbol'][lbdifft.argmin()]
                            m  = PDA.Energies['symbol'][mdifft.argmin()]
                            ts[numpy.array([min(kadifft), min(kbdifft), min(ladifft), min(lbdifft), min(mdifft)]).argmin()] = True
                            spectrum.Axes.text(xp, 0.05, ka, weight = 'bold' if ts[0] else 'normal', ha = 'right', rotation = 'vertical', color = 'C4', transform = spectrum.Axes.get_xaxis_transform(), clip_on = True)
                            spectrum.Axes.text(xp, 0.12, kb, weight = 'bold' if ts[1] else 'normal', ha = 'right', rotation = 'vertical', color = 'C6', transform = spectrum.Axes.get_xaxis_transform(), clip_on = True)
                            spectrum.Axes.text(xp, 0.20, la, weight = 'bold' if ts[2] else 'normal', ha = 'right', rotation = 'vertical', color = 'C5', transform = spectrum.Axes.get_xaxis_transform(), clip_on = True)
                            spectrum.Axes.text(xp, 0.27, lb, weight = 'bold' if ts[3] else 'normal', ha = 'right', rotation = 'vertical', color = 'C7', transform = spectrum.Axes.get_xaxis_transform(), clip_on = True)
                            spectrum.Axes.text(xp, 0.35, m,  weight = 'bold' if ts[4] else 'normal', ha = 'right', rotation = 'vertical', color = 'C8', transform = spectrum.Axes.get_xaxis_transform(), clip_on = True)
                    else:
                        spectrum.Axes.add_artist(matplotlib.lines.Line2D([xp, xp], [0, sumData[xp]], linewidth=1.0, linestyle='-', color='C2'))
                if widget.Calib is not None:
                    spectrum.Axes.text(0.05, 0.70, "Ka", ha = 'left', color = 'C4', transform = spectrum.Axes.transAxes, clip_on = True)
                    spectrum.Axes.text(0.05, 0.75, "Kb", ha = 'left', color = 'C6', transform = spectrum.Axes.transAxes, clip_on = True)
                    spectrum.Axes.text(0.05, 0.80, "La", ha = 'left', color = 'C5', transform = spectrum.Axes.transAxes, clip_on = True)
                    spectrum.Axes.text(0.05, 0.85, "Lb", ha = 'left', color = 'C7', transform = spectrum.Axes.transAxes, clip_on = True)
                    spectrum.Axes.text(0.05, 0.90, "M",  ha = 'left', color = 'C8', transform = spectrum.Axes.transAxes, clip_on = True)
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
                    elif line == "M":
                        line = xraylib.MA1_LINE
                    else:
                        print("Unknown line symbol!")
                        continue
                    xp = (numpy.abs(widget.Calib - xraylib.LineEnergy(element, line) * 1000)).argmin()
                    spectrum.Axes.add_artist(matplotlib.lines.Line2D([xp, xp], [0, 0.5], 1.0, '-', 'red', transform = spectrum.Axes.get_xaxis_transform()))
                    if xp > cEmin and xp < cEmax:
                        spectrum.Axes.text(xp, 0.55, name, ha = 'center', rotation = 'vertical', color = 'red', transform = spectrum.Axes.get_xaxis_transform(), clip_on = True)
    
    if widget.Calib is None:
        spectrum.Axes.set_xlim([0, head["bins"][0, 0]])
        spectrum.Axes.set_xticks(range(0, head["bins"][0, 0] + 1, math.floor(head["bins"][0, 0]/4)))
        spectrum.Axes.set_xlabel("channel")
        spectrum.Axes.format_coord = lambda x, y: f'x = {x:d} ch, y = {y:.3e}'
    else:
        spectrum.Axes.get_xaxis().set_visible(False)
        spectrum.Axes2x = spectrum.Axes.secondary_xaxis('bottom')
        spectrum.Axes.set_xlim([cEmin, cEmax])
        spectrum.Axes2x.set_xlabel("E [eV]")
        spectrum.Axes2x.callbacks.connect("xlim_changed", lambda secAxes: setTicks(secAxes, spectrum.Axes, widget.Calib, 4096, "X"))
        spectrum.Axes.format_coord = lambda x, y: f'E = {widget.Calib[round(x)]:.3f} eV, y = {y:.3e}'

    spectrum.Axes.set_aspect(Aspect)
    spectrum.draw()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec())