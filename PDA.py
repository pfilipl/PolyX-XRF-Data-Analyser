import math
import scipy.integrate as integrate
import scipy.stats as stats
import scipy.io as sio
import scipy.signal as sig
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.patches import Rectangle
import matplotlib.lines as lines
import matplotlib.scale as scale
import xraylib as xrl
import os

detectors = {
    0 : "Be",
    1 : "ML3",
    2 : "Be+ML3"
}

Energies = []
for i in range(1, 107):
    try: 
        ka = xrl.LineEnergy(i, xrl.KA_LINE) 
    except: 
        ka = 0
    try: 
        kb = xrl.LineEnergy(i, xrl.KB_LINE)
    except: 
        kb = 0
    try: 
        la = xrl.LineEnergy(i, xrl.LA_LINE)
    except: 
        la = 0
    try: 
        lb = xrl.LineEnergy(i, xrl.LB_LINE)
    except: 
        lb = 0
    Energies.append((xrl.AtomicNumberToSymbol(i), ka, kb, la, lb))
Energies = np.array(Energies, dtype = [('symbol', 'U2'), ('Ka', 'f8'), ('Kb', 'f8'), ('La', 'f8'), ('Lb', 'f8')])

# ZAŁADOWANIE FUNKCJI

# dzielenie spektrów prez siebie
# <- s1     - ndarray,  tablica 3-wymiarowa (X, Z, ch)
# <- s2     - ndarray,  tablica 3-wymiarowa (X, Z, ch)
# ->        - ndarray,  tablica 3-wymiarowa (X, Z, ch)
def div_spectrum(s1, s2):
    # sprawdzenie zgodności wymiarów
    if s1.shape == s2.shape:
        s = []
        for i in range(s1.shape[2]):
            # zabezpieczenie przed dzieleniem przez 0
            s.append(np.nan_to_num(s1[:, :, i] / s2[:, :, i], False, 0, 0, 0))
        return np.array(s).transpose((1, 2, 0))
    else:
        print("Array shapes are not equal!")
        return None

# sprawdzenie pozycji względem wymiarów mapy
# <- pos    - ndarray,      tablica dwuwymiarowa zawierająca współrzędne bezwzględne punktów ()(X, Z)
# <- shape  - list(list),   wymiary mapy (X, Z)
def check_pos(pos, shape):
    # sprawdzenie zgodności wymiarów
    if pos.shape[1] == len(shape):
        for i in range(pos.shape[0]):
            for j in range(pos.shape[1]):
                if pos[i, j] >= 0 and pos[i, j] < shape[j]:
                    continue
                # zmiana współrzędnych punktów, które były poza granicami mapy
                pos[i, j] = 0 if pos[i, j] < 0 else shape[j] - 1
    else:
        print("Invalid dimensions!")

# konwersja punktów o współrzędnych rzeczywistych na punkty o współrzędnych bezwzględnych
# <- rpos   - list(list)/ndarray,   lista lub tablica punktów o współrzędnych rzeczywistych w mm ()(X, Z)
# <- head   - dataframe,            struktura zawierająca informacje o zestawie danych eksperymentalnych
# ->        - list,                 lista punktów ()(X, Z)
def real_pos(rpos, head):
    # konwersja listy na tablicę
    if isinstance(rpos, list):
        rpos = np.array(rpos)
    # wyznaczenie rzeczywistych granic mapy
    xmin = min(head["Xpositions"][0, :])
    xmax = max(head["Xpositions"][0, :])
    zmin = min(head["Zpositions"][0, :])
    zmax = max(head["Zpositions"][0, :])
    # sprawdzenie czy punkty o współrzędnych rzeczywistych są w granicach mapy
    for i in range(rpos.shape[0]):
        if rpos[i, 0] < xmin or rpos[i, 0] > xmax or rpos[i, 1] < zmin or rpos[i, 1] > zmax:
            print("Invalid real positions!")
            return None
    pos = []
    # wyznaczenie współrzędnych bezwzględnych
    for i in range(rpos.shape[0]):
        x = (np.abs(head["Xpositions"][0, :] - rpos[i, 0])).argmin()
        z = (np.abs(head["Zpositions"][0, :] - rpos[i, 1])).argmin()
        pos.append([x, z])
    return pos

# wyznaczenie kalibracji energetycznej oraz rozmiarów pików XRF
# <- N  - int,      liczba kanałów detektora
# <- a  - float,    stała kierunkowa kalibracji energetycznej [keV/ch]
# <- b  - float,    stała swobodna kalibracji energetycznej [keV]
# <- n  - float,    stała określająca zaszumienie spektrum [eV]
# <- f  - float,    czynnik Fano [eV]
# ->    - ndarray,  tablica energii przypadających dla danego kanału [eV]
# ->    - ndarray,  tablica dyspersji pików przypadających dla danego kanału [eV]
def gen_calib(N, a, b, n, f):
    calib = []
    sigma = []
    for i in range(1, N):
        # kalibracja energetyczna
        E = (i * a + b) * 1000  # [ch * keV/ch + keV] -> [eV]
        # kalibracja dyspersji pików
        try:
            s = math.sqrt(n * n / 2.3548 / 2.3548 + 3.85 * f * E)   # [sqrt(eV * eV + eV * eV)]
        except:
            s = float("NaN")
        calib.append(E)
        sigma.append(s)
    return np.array(calib), np.array(sigma)

# załadowanie zestawu danych eksperymentalnych
# <- path       - string,           ścieżka do zestawu danych
# (<-) variant  - string,           wariant załadunku dancyh ("fast" - podstawowy, "all" - zawierający ilorazy spektrów)
# -> head       - dataframe,        
# -> Data       - list(ndarray),     
# -> ICR        - list(ndarray),    
# -> OCR        - list(ndarray),    
# -> RT         - list(ndarray),    
# -> LT         - list(ndarray),    
# -> DT         - list(ndarray),    
# -> PIN        - list(ndarray),    
# -> I0         - list(ndarray),    
# -> RC         - list,             
# -> ROI        - list(list),       
def data_load(path, variant = "fast"):
    dataname = path.split("/")[-1]
    Data1 = []
    Data2 = []
    ICR1 = []
    ICR2 = []
    OCR1 = []
    OCR2 = []
    RT1 = []
    RT2 = []
    LT1 = []
    LT2 = []
    DT1 = []
    DT2 = []
    PIN = []
    I0 = []
    RC = []
    number_of_files = len([name for name in os.listdir(path) if (os.path.isfile(os.path.join(path, name)) and os.path.splitext(name)[-1].lower() == ".mat" and os.path.splitext(name)[0][:5] != "PolyX")]) - 1 # 1 header + 2 snapshoty
    if number_of_files > 0:
        for i in range(0, number_of_files):
            mat = sio.loadmat(f"{path}/{dataname}_{i+1:04}.mat")
            data1 = mat["dane1line"][0, :, :]
            data2 = mat["dane1line"][1, :, :]
            icr1 = mat["stats1line"][0, :, 2]
            icr2 = mat["stats1line"][1, :, 2]
            ocr1 = mat["stats1line"][0, :, 3]
            ocr2 = mat["stats1line"][1, :, 3]
            rt1 = mat["stats1line"][0, :, 0]
            rt2 = mat["stats1line"][1, :, 0]
            lt1 = mat["stats1line"][0, :, 1]
            lt2 = mat["stats1line"][1, :, 1]
            dt1 = (1 - ocr1 / icr1) * 100
            dt2 = (1 - ocr2 / icr2) * 100
            pin = mat["PIN_map"][i, :]
            i0 = mat["I0_map"][i, :]
            Data1.append(data1) if i % 2 == 0 else Data1.append(data1[::-1])     # [z, x, c]
            Data2.append(data2) if i % 2 == 0 else Data2.append(data2[::-1])     # [z, x, c]
            ICR1.append(icr1) if i % 2 == 0 else ICR1.append(icr1[::-1])
            ICR2.append(icr2) if i % 2 == 0 else ICR2.append(icr2[::-1])
            OCR1.append(ocr1) if i % 2 == 0 else OCR1.append(ocr1[::-1])
            OCR2.append(ocr2) if i % 2 == 0 else OCR2.append(ocr2[::-1])
            RT1.append(rt1) if i % 2 == 0 else RT1.append(rt1[::-1])
            RT2.append(rt2) if i % 2 == 0 else RT2.append(rt2[::-1])
            LT1.append(lt1) if i % 2 == 0 else LT1.append(lt1[::-1])
            LT2.append(lt2) if i % 2 == 0 else LT2.append(lt2[::-1])
            DT1.append(dt1) if i % 2 == 0 else DT1.append(dt1[::-1])
            DT2.append(dt2) if i % 2 == 0 else DT2.append(dt2[::-1])
            PIN.append(pin) if i % 2 == 0 else PIN.append(pin[::-1])
            I0.append(i0) if i % 2 == 0 else I0.append(i0[::-1])
            RC.extend(mat["srcurrent"][0])
        Data1 = np.array(Data1).transpose((1, 0, 2))    # [x, z, c]
        Data2 = np.array(Data2).transpose((1, 0, 2))    # [x, z, c]
        ICR1 = np.array(ICR1).transpose()
        ICR2 = np.array(ICR2).transpose()
        OCR1 = np.array(OCR1).transpose()
        OCR2 = np.array(OCR2).transpose()
        RT1 = np.array(RT1).transpose()
        RT2 = np.array(RT2).transpose()
        LT1 = np.array(LT1).transpose()
        LT2 = np.array(LT2).transpose()
        DT1 = np.array(DT1).transpose()
        DT2 = np.array(DT2).transpose()
        PIN = np.array(PIN).transpose()
        I0 = np.array(I0).transpose()

    ROI = []
    head = sio.loadmat(f"{path}/{dataname}_HEADER.mat")
    try:
        for i in range(head["roi_listbins"].shape[0]):
            ROI.append([head["roi_listbins"][i, 1][0], head["roi_listbins"][i, 2][0][0], head["roi_listbins"][i, 3][0][0]])
    except:
        try:
            for i in range(head["roi_table"].shape[0]):
                ROI.append([head["roi_table"][i, 0][0], head["roi_table"][i, 1][0][0], head["roi_table"][i, 2][0][0]])
        except:
            print("ROIs are not defined!")

    # mat = sio.loadmat(f"{path}/{dataname}_{number_of_files:04}.mat")
    # PIN = mat["PIN_map"].transpose()    # [x, z]
    # I0 = mat["I0_map"].transpose()      # [x, z]

    if number_of_files > 0:
        if variant == "all":
            Data = [Data1, Data2, Data1 + Data2, div_spectrum(Data1, Data2), div_spectrum(Data2, Data1)]
            ICR = [ICR1, ICR2, ICR1 + ICR2, ICR1 + ICR2, ICR1 + ICR2]    
            OCR = [OCR1, OCR2, OCR1 + OCR2, OCR1 + OCR2, OCR1 + OCR2]    
            RT = [RT1, RT2, RT1 + RT2, RT1 + RT2, RT1 + RT2]
            LT = [LT1, LT2, LT1 + LT2, LT1 + LT2, LT1 + LT2]
            DT = [DT1, DT2, np.mean([DT1, DT2], axis = 0), np.mean([DT1, DT2], axis = 0), np.mean([DT1, DT2], axis = 0)]
        else:
            Data = [Data1, Data2, Data1 + Data2]
            ICR = [ICR1, ICR2, ICR1 + ICR2]    
            OCR = [OCR1, OCR2, OCR1 + OCR2]    
            RT = [RT1, RT2, RT1 + RT2]
            LT = [LT1, LT2, LT1 + LT2]
            DT = [DT1, DT2, np.mean([DT1, DT2], axis = 0)]
        return [head, Data, ICR, OCR, RT, LT, DT, PIN, I0, RC, ROI]
    
    return [[], [], [], [], [], [], [], [], [], [], []]

def add_ROI(ROI, name, calib = None, sigma = None, s = 1, width = None, element = None, line = None, i_start = None, i_stop = None):
    if width is None and element is None and line is None and i_start is not None and i_stop is not None:
        ROI.append([name, i_start, i_stop])
    elif i_start is None and i_stop is None:
        if element is None:
            try: 
                element = xrl.SymbolToAtomicNumber(name.split("-")[-2])
            except:
                print("Unknown element symbol!")
        else:
            element = xrl.SymbolToAtomicNumber(element)
        if line is None:
            line = name.split("-")[-1]
            if line == "Ka":
                line = xrl.KA_LINE
            elif line == "Kb":
                line = xrl.KB_LINE
            elif line == "La":
                line = xrl.LA_LINE
            elif line == "Lb":
                line = xrl.LB_LINE
            elif line == "M":
                line = xrl.MA1_LINE
            else:
                print("Unknown line symbol!")
    if line is not None:
        E = xrl.LineEnergy(element, line) * 1000
        idx = (np.abs(calib - E)).argmin()
        sigma_width = math.floor((s * sigma[idx]) / 2 + 1)
        if width is None or width < sigma_width:
            width = sigma_width
        ROI.append([name, idx - width, idx + width])

def Data_plot(Data, head, title, detector = None, ROI = None, Cmap = 'viridis', pos = None, Vmin = None, Vmax = None, clabel = None, normalize = None, Origin = "lower", Aspect = 'auto'):
    Map = []
    Fig = []
    if normalize is not None:
        I0 = normalize[0]
        LT = normalize[1]
    for d in (range(len(Data)) if detector is None else detector):
        data = Data[d].copy()   # [x, z, c]
        if pos is not None:
            if isinstance(pos, list):
                pos = np.array(pos)
            check_pos(pos, [data.shape[0], data.shape[1]])
            if pos.shape[0] == 1:
                x0 = pos[0, 0]
                z0 = pos[0, 1]
            elif pos.shape[0] == 2:
                x0 = min(pos[0, 0], pos[1, 0])
                z0 = min(pos[0, 1], pos[1, 1])
                x1 = max(pos[0, 0], pos[1, 0])
                z1 = max(pos[0, 1], pos[1, 1])
            else:
                print("Invalid pos!")
                break
        if ROI != "max":
            if ROI is None or ROI == "sum":
                ROI = [['Total signal', 1, head["bins"][0, 0]]]
            for i in range(len(ROI)):
                fig = plt.figure(layout = 'compressed')
                ax1 = fig.add_subplot()
                sum_signal = np.sum(data[:, :, ROI[i][1]:ROI[i][2]], axis=2)
                if normalize is not None:
                    sum_signal = sum_signal / I0 / (LT[d] * 1e-6)
                    # sum_signal = sum_signal / I0 / (LT[d] / 1e3)
                # if normalized:
                #     max_signal = np.max(sum_signal)
                #     img = ax1.imshow(sum_signal/max_signal, origin=Origin)
                # else:
                img = ax1.imshow(sum_signal.transpose(), origin = Origin, cmap = Cmap, vmin = Vmin, vmax = Vmax)
                # img = ax1.imshow(sum_signal.transpose(), cmap = Cmap, vmin = Vmin, vmax = Vmax)
                cb = fig.colorbar(img)
                cb.set_ticks(np.linspace(max(np.min(sum_signal), Vmin) if Vmin is not None else np.min(sum_signal), min(np.max(sum_signal), Vmax) if Vmax is not None else np.max(sum_signal), len(cb.get_ticks()) - 2))
                if clabel:
                    cb.set_label(clabel)
                ax1.set_xticks(np.linspace(0, data.shape[0] - 1, len(ax1.get_xticks()) - 2))
                ax1.set_xticklabels(np.linspace(head["Xpositions"][0, 0], head["Xpositions"][0, -1], len(ax1.get_xticks())))
                ax1.set_xlabel("X [mm]")
                ax1.set_yticks(np.linspace(0, data.shape[1] - 1, len(ax1.get_yticks()) - 2))
                ax1.set_yticklabels(np.linspace(head["Zpositions"][0, 0], head["Zpositions"][0, -1], len(ax1.get_yticks())))
                ax1.set_ylabel("Z [mm]")
                if normalize is not None:
                    ax1.set_title(f"{title}\n SDD {detectors[d]}, ROI = {ROI[i][0]}, normalized")
                else:
                    ax1.set_title(f"{title}\n SDD {detectors[d]}, ROI = {ROI[i][0]}")
                if pos is not None:
                    if pos.shape[0] == 1:
                        ax1.add_patch(Rectangle((x0 - 1, z0 - 1), 3, 3, linewidth = 1, linestyle = '--', edgecolor = 'r', facecolor = 'none'))
                    elif pos.shape[0] == 2:
                        ax1.add_patch(Rectangle((x0 - 1, z0 - 1), x1 - x0 + 2, z1 - z0 + 2, linewidth = 1, linestyle = '--', edgecolor = 'r', facecolor = 'none'))
                    else:
                        print("Invalid pos!")
                        break
                ax1.set_aspect(Aspect)
                Map.append(sum_signal)
                Fig.append(fig)
        else:
            fig = plt.figure(layout = 'compressed')
            ax1 = fig.add_subplot()
            max_signal = np.max(data, axis=2)
            if normalize is not None:
                max_signal = max_signal / I0 / (LT[d] * 1e-6)
                # max_signal = max_signal / I0 / (LT[d] / 1e3)
            img = ax1.imshow(max_signal.transpose(), origin=Origin, cmap = Cmap, vmin = Vmin, vmax = Vmax)
            # img = ax1.imshow(max_signal.transpose(), cmap = Cmap, vmin = Vmin, vmax = Vmax)
            cb = fig.colorbar(img)
            cb.set_ticks(np.linspace(max(np.min(max_signal), Vmin) if Vmin is not None else np.min(max_signal), min(np.max(max_signal), Vmax) if Vmax is not None else np.max(max_signal), len(cb.get_ticks()) - 2))
            if clabel:
                cb.set_label(clabel)
            ax1.set_xticks(np.linspace(0, data.shape[0] - 1, len(ax1.get_xticks()) - 2))
            ax1.set_xticklabels(np.linspace(head["Xpositions"][0, 0], head["Xpositions"][0, -1], len(ax1.get_xticks())))
            ax1.set_xlabel("X [mm]")
            ax1.set_yticks(np.linspace(0, data.shape[1] - 1, len(ax1.get_yticks()) - 2))
            ax1.set_yticklabels(np.linspace(head["Zpositions"][0, 0], head["Zpositions"][0, -1], len(ax1.get_yticks())))
            ax1.set_ylabel("Z [mm]")
            if normalize is not None:
                ax1.set_title(f"{title}\n SDD {detectors[d]}, normalized")
            else:
                ax1.set_title(f"{title}\n SDD {detectors[d]}")
            if pos is not None:
                ax1.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, linewidth = 1, linestyle = '--', edgecolor = 'r', facecolor = 'none'))
            ax1.set_aspect(Aspect)
            Map.append(max_signal)
            Fig.append(fig)
    return Map, Fig

def Stats1D_plot(data, head, title, ylabel = None, Aspect = 'auto'):
    Fig = []
    fig = plt.figure(layout = 'compressed')
    ax1 = fig.add_subplot()
    if isinstance(data, list):
        data = np.array(data)
    img = ax1.plot(data, ".-")
    if ylabel:
        ax1.set_ylabel(ylabel)
    ax1.set_title(f"{title}")
    ax1.set_xticks(np.linspace(0, data.shape[0] - 1, len(ax1.get_xticks()) - 2))
    ax1.set_xticklabels(np.linspace(head["Zpositions"][0, 0], head["Zpositions"][0, -1], len(ax1.get_xticks())))
    ax1.set_xlabel("Z [mm]")
    # ax1.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax1.set_aspect(Aspect)
    Fig.append(fig)
    return Fig

def Stats2D_plot(Data, head, title, detector = None, Cmap = 'viridis', Vmin = None, Vmax = None, clabel = None, Origin = "lower", Aspect = 'auto'):
    Map = []
    Fig = []
    if isinstance(Data, list):
        for d in (range(len(Data)) if detector is None else detector):
            data = Data[d].copy()
            fig = plt.figure(layout = 'compressed')
            ax1 = fig.add_subplot()
            img = ax1.imshow(data.transpose(), origin=Origin, cmap = Cmap, vmin = Vmin, vmax = Vmax)
            # img = ax1.imshow(data.transpose(), cmap = Cmap, vmin = Vmin, vmax = Vmax)
            cb = fig.colorbar(img)
            cb.set_ticks(np.linspace(max(np.min(data), Vmin) if Vmin is not None else np.min(data), min(np.max(data), Vmax) if Vmax is not None else np.max(data), len(cb.get_ticks()) - 2))
            if clabel:
                cb.set_label(clabel)
            ax1.set_xticks(np.linspace(0, data.shape[0] - 1, len(ax1.get_xticks()) - 2))
            ax1.set_xticklabels(np.linspace(head["Xpositions"][0, 0], head["Xpositions"][0, -1], len(ax1.get_xticks())))
            ax1.set_xlabel("X [mm]")
            ax1.set_yticks(np.linspace(0, data.shape[1] - 1, len(ax1.get_yticks()) - 2))
            ax1.set_yticklabels(np.linspace(head["Zpositions"][0, 0], head["Zpositions"][0, -1], len(ax1.get_yticks())))
            ax1.set_ylabel("Z [mm]")
            ax1.set_title(f"{title}, SDD {detectors[d]}")
            ax1.set_aspect(Aspect)
            Map.append(data)
            Fig.append(fig)
    else:
        data = Data
        fig = plt.figure(layout = 'compressed')
        ax1 = fig.add_subplot()
        img = ax1.imshow(data.transpose(), origin=Origin, cmap = Cmap, vmin = Vmin, vmax = Vmax)
        # img = ax1.imshow(data.transpose(), cmap = Cmap, vmin = Vmin vmax = Vmax)
        cb = fig.colorbar(img)
        cb.set_ticks(np.linspace(max(np.min(data), Vmin) if Vmin is not None else np.min(data), min(np.max(data), Vmax) if Vmax is not None else np.max(data), len(cb.get_ticks()) - 2))
        if clabel:
            cb.set_label(clabel)
        ax1.set_xticks(np.linspace(0, data.shape[0] - 1, len(ax1.get_xticks()) - 2))
        ax1.set_xticklabels(np.linspace(head["Xpositions"][0, 0], head["Xpositions"][0, -1], len(ax1.get_xticks())))
        ax1.set_xlabel("X [mm]")
        ax1.set_yticks(np.linspace(0, data.shape[1] - 1, len(ax1.get_yticks()) - 2))
        ax1.set_yticklabels(np.linspace(head["Zpositions"][0, 0], head["Zpositions"][0, -1], len(ax1.get_yticks())))
        ax1.set_ylabel("Z [mm]")
        ax1.set_title(f"{title}")
        ax1.set_aspect(Aspect)
        Map.append(data)
        Fig.append(fig)
    return Map, Fig

def Hist_plot(Data, head, title, pos, calib = None, detector = None, log = False, ROI = None, Emin = 0.0, Emax = None, peaks = None, normalize = None, Aspect = 'auto'):
    if normalize is not None:
        I0 = normalize[0]
        LT = normalize[1]
    if pos is None:
        print("Invalid position!")
        return None
    else:
        Hist = []
        Fig = []
        for d in (range(len(Data)) if detector is None else detector):
            data = Data[d].copy()       # [x, z, c]
            if calib is not None:
                cEmin = (np.abs(calib - Emin * 1000)).argmin() - 1
                if Emax is None:
                    Emax = calib[-1] / 1000
                    cEmax = head["bins"][0, 0] - 1
                else:
                    cEmax = (np.abs(calib - Emax * 1000)).argmin() + 1
            if isinstance(pos, list):
                pos = np.array(pos)     # [[x0, z0], [x1, z1]]
            if pos.shape[0] == 1:
                fig = plt.figure(layout = 'compressed')
                ax1 = fig.add_subplot()
                check_pos(pos, [data.shape[0], data.shape[1]])
                x0 = pos[0, 0]
                z0 = pos[0, 1]
                if normalize is not None:
                    # img = ax1.plot(data[x0, z0, :] / np.max(data[x0, z0, :]) / I0[x0, z0] / (LT[d][x0, z0] * 1e-6) )
                    sum_data = data[x0, z0, :] / I0[x0, z0] / (LT[d][x0, z0] * 1e-6)
                else:
                    # img = ax1.plot(data[x0, z0, :] / np.max(data[x0, z0, :]))
                    sum_data = data[x0, z0, :]
                img = ax1.plot(sum_data)
                if calib is not None:
                    # ax1.set_ylim([1/np.max(data[x0, z0, cEmin:cEmax]) if log else 0, np.max(data[x0, z0, cEmin:cEmax]) / np.max(data[x0, z0, :])])
                    ax1.set_ylim([1 if log else 0, np.max(data[x0, z0, cEmin:cEmax]) * 1.5 if log else np.max(data[x0, z0, cEmin:cEmax]) * 1.05])
                else:
                    # ax1.set_ylim([1/np.max(data[x0, z0, :]) if log else 0, 1])
                    ax1.set_ylim([1 if log else 0, np.max(data[x0, z0, :]) * 1.5 if log else np.max(data[x0, z0, :]) * 1.05])
                x0r = np.round(head["Xpositions"][0, x0], 2)
                z0r = np.round(head["Zpositions"][0, z0], 2)
                if normalize is not None:
                    ax1.set_title(f"{title}\npos = [{x0r}, {z0r}], SDD {detectors[d]}, normalized")
                else:
                    ax1.set_title(f"{title}\npos = [{x0r}, {z0r}], SDD {detectors[d]}")
                hist = data[x0, z0, :]
                if ROI is not None:
                    for i in range(len(ROI)):
                        if ROI[i][0] != 'Total signal':
                            ax1.add_patch(Rectangle((ROI[i][1], 0), ROI[i][2] - ROI[i][1], 1, facecolor = 'r', alpha = 0.2, transform = ax1.get_xaxis_transform()))
                            if calib is not None:
                                if ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2 > cEmin and ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2 < cEmax:
                                    ax1.text(ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2, 0.7, ROI[i][0], ha = 'center', rotation = 'vertical', transform = ax1.get_xaxis_transform())
                            else:
                                ax1.text(ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2, 0.7, ROI[i][0], ha = 'center', rotation = 'vertical', transform = ax1.get_xaxis_transform())
                if peaks is not None:
                    if isinstance(peaks, bool):
                        if peaks:
                            xP = sig.find_peaks(sum_data, height = 1e-5 * np.max(sum_data), width = 5)
                            for xp in xP[0]:
                                if calib is not None:
                                    if  xp > (np.abs(calib - 0)).argmin() + 50:
                                        ax1.add_artist(lines.Line2D([xp, xp], [0, sum_data[xp]], 1.0, '-', 'C1'))
                                        if xp > cEmin and xp < cEmax:
                                            # ka_diff = Energies['Ka'][(np.abs(Energies['Ka'] - calib[xp] / 1000)).argmin()] - calib[xp] / 1000
                                            # kb_diff = Energies['Kb'][(np.abs(Energies['Kb'] - calib[xp] / 1000)).argmin()] - calib[xp] / 1000
                                            # la_diff = Energies['La'][(np.abs(Energies['La'] - calib[xp] / 1000)).argmin()] - calib[xp] / 1000
                                            # lb_diff = Energies['Lb'][(np.abs(Energies['Lb'] - calib[xp] / 1000)).argmin()] - calib[xp] / 1000
                                            # k = Energies['symbol'][(np.abs(Energies['Ka'] - calib[xp] / 1000)).argmin()] + "-Ka" if ka_diff < kb_diff else Energies['symbol'][(np.abs(Energies['Kb'] - calib[xp] / 1000)).argmin()] + "-Kb"
                                            # l = Energies['symbol'][(np.abs(Energies['La'] - calib[xp] / 1000)).argmin()] + "-La" if la_diff < lb_diff else Energies['symbol'][(np.abs(Energies['Kb'] - calib[xp] / 1000)).argmin()] + "-Lb"
                                            # ax1.text(xp, 0.05, k, ha = 'right', rotation = 'vertical', color = 'C1', transform = ax1.get_xaxis_transform())
                                            # ax1.text(xp, 0.20, l, ha = 'right', rotation = 'vertical', color = 'C4', transform = ax1.get_xaxis_transform())
                                            ka = Energies['symbol'][(np.abs(Energies['Ka'] - calib[xp] / 1000)).argmin()]
                                            kb = Energies['symbol'][(np.abs(Energies['Kb'] - calib[xp] / 1000)).argmin()]
                                            la = Energies['symbol'][(np.abs(Energies['La'] - calib[xp] / 1000)).argmin()]
                                            lb = Energies['symbol'][(np.abs(Energies['Lb'] - calib[xp] / 1000)).argmin()]
                                            ax1.text(xp, 0.05, ka, ha = 'right', rotation = 'vertical', color = 'C4', transform = ax1.get_xaxis_transform())
                                            ax1.text(xp, 0.12, kb, ha = 'right', rotation = 'vertical', color = 'C6', transform = ax1.get_xaxis_transform())
                                            ax1.text(xp, 0.20, la, ha = 'right', rotation = 'vertical', color = 'C5', transform = ax1.get_xaxis_transform())
                                            ax1.text(xp, 0.27, lb, ha = 'right', rotation = 'vertical', color = 'C7', transform = ax1.get_xaxis_transform())
                                else:
                                    ax1.add_artist(lines.Line2D([xp, xp], [0, sum_data[xp]], 1.0, '-', 'C2'))
                            if calib is not None:
                                ax1.text(0.95, 0.80, "Ka", ha = 'left', color = 'C4', transform = ax1.transAxes)
                                ax1.text(0.95, 0.85, "Kb", ha = 'left', color = 'C6', transform = ax1.transAxes)
                                ax1.text(0.95, 0.90, "La", ha = 'left', color = 'C5', transform = ax1.transAxes)
                                ax1.text(0.95, 0.95, "Lb", ha = 'left', color = 'C7', transform = ax1.transAxes)
                    elif calib is not None:
                        for name in peaks:
                            if name != 'Total signal':
                                try: 
                                    element = xrl.SymbolToAtomicNumber(name.split("-")[-2])
                                except:
                                    print("Unknown element symbol!")
                                    continue
                                line = name.split("-")[-1]
                                if line == "Ka":
                                    line = xrl.KA_LINE
                                elif line == "Kb":
                                    line = xrl.KB_LINE
                                elif line == "La":
                                    line = xrl.LA_LINE
                                elif line == "Lb":
                                    line = xrl.LB_LINE
                                else:
                                    print("Unknown line symbol!")
                                    continue
                                xp = (np.abs(calib - xrl.LineEnergy(element, line) * 1000)).argmin()
                                ax1.add_artist(lines.Line2D([xp, xp], [0, 0.5], 1.0, '-', 'red', transform = ax1.get_xaxis_transform()))
                                if xp > cEmin and xp < cEmax:
                                    ax1.text(xp, 0.55, name, ha = 'center', rotation = 'vertical', color = 'red', transform = ax1.get_xaxis_transform())
            elif pos.shape[0] == 2:
                check_pos(pos, [data.shape[0], data.shape[1]])
                x0 = min(pos[0, 0], pos[1, 0])
                z0 = min(pos[0, 1], pos[1, 1])
                x1 = max(pos[0, 0], pos[1, 0])
                z1 = max(pos[0, 1], pos[1, 1])
                fig = plt.figure(layout = 'compressed')
                ax1 = fig.add_subplot()
                if x1 > x0 and z1 > z0:
                    sum_data = data[x0:x1, z0:z1, :]
                    if normalize is not None:
                        i0 = I0[x0:x1, z0:z1]
                        lt = LT[d][x0:x1, z0:z1] * 1e-6
                        for ch in range(data.shape[2]):
                            sum_data[:, :, ch] = sum_data[:, :, ch] / i0 / lt
                    sum_data = np.sum(np.sum(sum_data, axis = 0), axis = 0)
                elif x1 == x0 and z1 > z0:
                    sum_data = data[x0, z0:z1, :]
                    if normalize is not None:
                        i0 = I0[x0, z0:z1]
                        lt = LT[d][x0, z0:z1] * 1e-6
                        for ch in range(data.shape[2]):
                            sum_data[:, ch] = sum_data[:, ch] / i0 / lt
                    sum_data = np.sum(sum_data, axis = 0)
                elif x1 > x0 and z1 == z0:
                    sum_data = data[x0:x1, z0, :]
                    if normalize is not None:
                        i0 = I0[x0:x1, z0]
                        lt = LT[d][x0:x1, z0] * 1e-6
                        for ch in range(data.shape[2]):
                            sum_data[:, ch] = sum_data[:, ch] / i0 / lt
                    sum_data = np.sum(sum_data, axis = 0)
                else:
                    sum_data = data[x0, z0, :]
                    if normalize is not None:
                        i0 = I0[x0, z0]
                        lt = LT[d][x0, z0] * 1e-6
                        sum_data = sum_data / i0 / lt
                # img = ax1.plot(sum_data / np.max(sum_data))
                img = ax1.plot(sum_data)
                if calib is not None:
                    # ax1.set_ylim([1/np.max(sum_data[cEmin:cEmax]) if log else 0, np.max(sum_data[cEmin:cEmax]) / np.max(sum_data)])
                    # ax1.set_ylim([1/np.max(sum_data) if log else 0, np.max(sum_data)])
                    ax1.set_ylim([1 if log else 0, np.max(np.sum(np.sum(data[x0:x1, z0:z1, cEmin:cEmax], axis = 0), axis = 0)) * 1.5 if log else np.max(np.sum(np.sum(data[x0:x1, z0:z1, cEmin:cEmax], axis = 0), axis = 0)) * 1.05])
                else:
                    # ax1.set_ylim([1/np.max(sum_data) if log else 0, 1])
                    ax1.set_ylim([1 if log else 0, np.max(sum_data) * 1.5 if log else np.max(sum_data) * 1.05])
                x0r = np.round(head["Xpositions"][0, x0], 2)
                z0r = np.round(head["Zpositions"][0, z0], 2)
                x1r = np.round(head["Xpositions"][0, x1], 2)
                z1r = np.round(head["Zpositions"][0, z1], 2)
                if normalize is not None:
                    ax1.set_title(f"{title}\npos = [[{x0r}, {z0r}], [{x1r}, {z1r}]]\n SDD {detectors[d]}, normalized")
                else:
                    ax1.set_title(f"{title}\npos = [[{x0r}, {z0r}], [{x1r}, {z1r}]], SDD {detectors[d]}")
                hist = sum_data
                if ROI is not None:
                    for i in range(len(ROI)):
                        if ROI[i][0] != 'Total signal':
                            ax1.add_patch(Rectangle((ROI[i][1], 0), ROI[i][2] - ROI[i][1], 1, facecolor = 'r', alpha = 0.2, transform = ax1.get_xaxis_transform()))
                            if calib is not None:
                                if ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2 > cEmin and ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2 < cEmax:
                                    ax1.text(ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2, 0.7, ROI[i][0], ha = 'center', rotation = 'vertical', transform = ax1.get_xaxis_transform())
                            else:
                                ax1.text(ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2, 0.7, ROI[i][0], ha = 'center', rotation = 'vertical', transform = ax1.get_xaxis_transform())
                if peaks is not None:
                    if isinstance(peaks, bool):
                        if peaks:
                            xP = sig.find_peaks(sum_data, height = 1e-5 * np.max(sum_data), width = 10)
                            for xp in xP[0]:
                                if calib is not None:
                                    if  xp > (np.abs(calib - 0)).argmin() + 50:
                                        ax1.add_artist(lines.Line2D([xp, xp], [0, sum_data[xp]], 1.0, '-', 'C1'))
                                        if xp > cEmin and xp < cEmax:
                                            # ka_diff = Energies['Ka'][(np.abs(Energies['Ka'] - calib[xp] / 1000)).argmin()] - calib[xp] / 1000
                                            # kb_diff = Energies['Kb'][(np.abs(Energies['Kb'] - calib[xp] / 1000)).argmin()] - calib[xp] / 1000
                                            # la_diff = Energies['La'][(np.abs(Energies['La'] - calib[xp] / 1000)).argmin()] - calib[xp] / 1000
                                            # lb_diff = Energies['Lb'][(np.abs(Energies['Lb'] - calib[xp] / 1000)).argmin()] - calib[xp] / 1000
                                            # k = Energies['symbol'][(np.abs(Energies['Ka'] - calib[xp] / 1000)).argmin()] + "-Ka" if ka_diff < kb_diff else Energies['symbol'][(np.abs(Energies['Kb'] - calib[xp] / 1000)).argmin()] + "-Kb"
                                            # l = Energies['symbol'][(np.abs(Energies['La'] - calib[xp] / 1000)).argmin()] + "-La" if la_diff < lb_diff else Energies['symbol'][(np.abs(Energies['Kb'] - calib[xp] / 1000)).argmin()] + "-Lb"
                                            # ax1.text(xp, 0.05, k, ha = 'right', rotation = 'vertical', color = 'C1', transform = ax1.get_xaxis_transform())
                                            # ax1.text(xp, 0.20, l, ha = 'right', rotation = 'vertical', color = 'C4', transform = ax1.get_xaxis_transform())
                                            ka = Energies['symbol'][(np.abs(Energies['Ka'] - calib[xp] / 1000)).argmin()]
                                            kb = Energies['symbol'][(np.abs(Energies['Kb'] - calib[xp] / 1000)).argmin()]
                                            la = Energies['symbol'][(np.abs(Energies['La'] - calib[xp] / 1000)).argmin()]
                                            lb = Energies['symbol'][(np.abs(Energies['Lb'] - calib[xp] / 1000)).argmin()]
                                            ax1.text(xp, 0.05, ka, ha = 'right', rotation = 'vertical', color = 'C4', transform = ax1.get_xaxis_transform())
                                            ax1.text(xp, 0.12, kb, ha = 'right', rotation = 'vertical', color = 'C6', transform = ax1.get_xaxis_transform())
                                            ax1.text(xp, 0.20, la, ha = 'right', rotation = 'vertical', color = 'C5', transform = ax1.get_xaxis_transform())
                                            ax1.text(xp, 0.27, lb, ha = 'right', rotation = 'vertical', color = 'C7', transform = ax1.get_xaxis_transform())
                                else:
                                    ax1.add_artist(lines.Line2D([xp, xp], [0, sum_data[xp]], 1.0, '-', 'C2'))
                            if calib is not None:
                                ax1.text(0.95, 0.80, "Ka", ha = 'left', color = 'C4', transform = ax1.transAxes)
                                ax1.text(0.95, 0.85, "Kb", ha = 'left', color = 'C6', transform = ax1.transAxes)
                                ax1.text(0.95, 0.90, "La", ha = 'left', color = 'C5', transform = ax1.transAxes)
                                ax1.text(0.95, 0.95, "Lb", ha = 'left', color = 'C7', transform = ax1.transAxes)
                    elif calib is not None:
                        for name in peaks:
                            if name != 'Total signal':
                                try: 
                                    element = xrl.SymbolToAtomicNumber(name.split("-")[-2])
                                except:
                                    print("Unknown element symbol!")
                                    continue
                                line = name.split("-")[-1]
                                if line == "Ka":
                                    line = xrl.KA_LINE
                                elif line == "Kb":
                                    line = xrl.KB_LINE
                                elif line == "La":
                                    line = xrl.LA_LINE
                                elif line == "Lb":
                                    line = xrl.LB_LINE
                                else:
                                    print("Unknown line symbol!")
                                    continue
                                xp = (np.abs(calib - xrl.LineEnergy(element, line) * 1000)).argmin()
                                ax1.add_artist(lines.Line2D([xp, xp], [0, 0.5], 1.0, '-', 'red', transform = ax1.get_xaxis_transform()))
                                if xp > cEmin and xp < cEmax:
                                    ax1.text(xp, 0.55, name, ha = 'center', rotation = 'vertical', color = 'red', transform = ax1.get_xaxis_transform())
            else:
                print("Invalid position!")
                break
            if log:
                ax1.set_yscale('log')
            if calib is None:
                ax1.set_xlim([0, head["bins"][0, 0]])
                ax1.set_xticks(range(0, head["bins"][0, 0] + 1, math.floor(head["bins"][0, 0]/4)))
                ax1.set_xlabel("channel")
            else:
                ax1.set_xlim([cEmin, cEmax])
                Eval = np.linspace(Emin * 1000, Emax * 1000, 7)
                E = []
                for eval in Eval:
                    E.append((np.abs(calib - eval)).argmin())
                ax1.set_xticks(E)
                ax1.set_xticklabels(np.abs(np.round(calib[E] / 1000, 2)))
                ax1.set_xlabel("E [keV]")
            ax1.set_aspect(Aspect)
            Hist.append(hist)
            Fig.append(fig)
        return Hist, Fig
    
def Hist_max_plot(Data, head, title, calib = None, detector = None, log = False, ROI = None, Emin = 0.0, Emax = None, peaks = None, Aspect = 'auto'):
    Hist = []
    Fig = []
    for d in (range(len(Data)) if detector is None else detector):
        data = Data[d].copy()       # [x, z, c]
        if calib is not None:
            cEmin = (np.abs(calib - Emin * 1000)).argmin() - 1
            if Emax is None:
                Emax = calib[-1] / 1000
                cEmax = head["bins"][0, 0] - 1
            else:
                cEmax = (np.abs(calib - Emax * 1000)).argmin() + 1
        fig = plt.figure(layout = 'compressed')
        ax1 = fig.add_subplot()
        max_data = np.max(np.max(data, axis = 0), axis = 0)
        # img = ax1.plot(max_data / np.max(max_data))
        img = ax1.plot(max_data)
        if calib is not None:
            # ax1.set_ylim([1/np.max(sum_data[cEmin:cEmax]) if log else 0, np.max(sum_data[cEmin:cEmax]) / np.max(sum_data)])
            # ax1.set_ylim([1/np.max(sum_data) if log else 0, np.max(sum_data)])
            ax1.set_ylim([1 if log else 0, np.max(np.max(np.max(data[:, :, cEmin:cEmax], axis = 0), axis = 0)) * 1.5 if log else np.max(np.max(np.max(data[:, :, cEmin:cEmax], axis = 0), axis = 0)) * 1.05])
        else:
            # ax1.set_ylim([1/np.max(sum_data) if log else 0, 1])
            ax1.set_ylim([1 if log else 0, np.max(max_data) * 1.5 if log else np.max(max_data) * 1.05])
        ax1.set_title(f"{title}, SDD {detectors[d]}")
        hist = max_data
        if ROI is not None:
            for i in range(len(ROI)):
                if ROI[i][0] != 'Total signal':
                    ax1.add_patch(Rectangle((ROI[i][1], 0), ROI[i][2] - ROI[i][1], 1, facecolor = 'r', alpha = 0.2, transform = ax1.get_xaxis_transform()))
                    if calib is not None:
                        if ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2 > cEmin and ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2 < cEmax:
                            ax1.text(ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2, 0.7, ROI[i][0], ha = 'center', rotation = 'vertical', transform = ax1.get_xaxis_transform())
                    else:
                        ax1.text(ROI[i][1] + (ROI[i][2] - ROI[i][1]) / 2, 0.7, ROI[i][0], ha = 'center', rotation = 'vertical', transform = ax1.get_xaxis_transform())
        if peaks is not None:
            if isinstance(peaks, bool):
                if peaks:
                    xP = sig.find_peaks(max_data, height = 0.01 * np.max(max_data), width = 10)
                    for xp in xP[0]:
                        if calib is not None and xp > (np.abs(calib - Emin * 1000)).argmin() + 10:
                            ax1.add_artist(lines.Line2D([xp, xp], [0, max_data[xp] / np.max(max_data)], 1.0, '-', 'C2'))
                        else:
                            ax1.add_artist(lines.Line2D([xp, xp], [0, max_data[xp] / np.max(max_data)], 1.0, '-', 'C2'))
            elif calib is not None:
                for name in peaks:
                    if name != 'Total signal':
                        try: 
                            element = xrl.SymbolToAtomicNumber(name.split("-")[-2])
                        except:
                            print("Unknown element symbol!")
                            continue
                        line = name.split("-")[-1]
                        if line == "Ka":
                            line = xrl.KA_LINE
                        elif line == "Kb":
                            line = xrl.KB_LINE
                        elif line == "La":
                            line = xrl.LA_LINE
                        elif line == "Lb":
                            line = xrl.LB_LINE
                        else:
                            print("Unknown line symbol!")
                            continue
                        xp = (np.abs(calib - xrl.LineEnergy(element, line) * 1000)).argmin()
                        ax1.add_artist(lines.Line2D([xp, xp], [0, 0.5], 1.0, '-', 'red', transform = ax1.get_xaxis_transform()))
                        if xp > cEmin and xp < cEmax:
                            ax1.text(xp, 0.55, name, ha = 'center', rotation = 'vertical', color = 'red', transform = ax1.get_xaxis_transform())
        if log:
            ax1.set_yscale('log')
        if calib is None:
            ax1.set_xlim([0, head["bins"][0, 0]])
            ax1.set_xticks(range(0, head["bins"][0, 0] + 1, math.floor(head["bins"][0, 0]/4)))
            ax1.set_xlabel("channel")
        else:
            ax1.set_xlim([cEmin, cEmax])
            Eval = np.linspace(Emin * 1000, Emax * 1000, 7)
            E = []
            for eval in Eval:
                E.append((np.abs(calib - eval)).argmin())
            ax1.set_xticks(E)
            ax1.set_xticklabels(np.abs(np.round(calib[E] / 1000, 2)))
            ax1.set_xlabel("E [keV]")
        ax1.set_aspect(Aspect)
        Hist.append(hist)
        Fig.append(fig)
    return Hist, Fig
    
def Hist_check_plot(Data, head, title, detector = [0, 1], log = False, func = np.sum, Aspect = 'auto'):
    Hist = []
    Fig = []
    fig = plt.figure(layout = 'compressed')
    ax1 = fig.add_subplot()
    for d in (range(len(Data)) if detector is None else detector):
        data = func(func(Data[d], axis = 0), axis = 0)
        ax1.plot(data, label = f"SDD {detectors[d]}")
        ax1.set_ylim([1 if log else 0, np.max([np.max(data) * 1.5 if log else np.max(data) * 1.05, ax1.get_ylim()[1]], axis = 0)])
        Hist.append(data)
    ax1.legend()
    ax1.set_title(f"{title}")
    if log:
        ax1.set_yscale('log')
    ax1.set_xlim([0, head["bins"][0, 0]])
    ax1.set_xticks(range(0, head["bins"][0, 0] + 1, math.floor(head["bins"][0, 0]/4)))
    ax1.set_xlabel("channel")
    ax1.set_aspect(Aspect)
    Fig.append(fig)
    return Hist, Fig

def print_Hist(Hist, filename, Name = None):
    for h in range(len(Hist)):
        if Name is not None:
            if len(Hist) > len(Name):
                file = open(filename + f"_{Name[h % len(Name)]}_{h // len(Name)}.csv", "w")
            else:
                file = open(filename + f"_{Name[h]}.csv" if len(Hist) > 1 else filename + ".csv", "w")
        else:
            file = open(filename + f"_{h}.csv" if len(Hist) > 1 else filename + ".csv", "w")
        for i in Hist[h]:
            file.write(f"{i}\n")
        file.close()

def print_Fig(Fig, filename, Name = None, dpi = 300, ext = ".png"):
    for f in range(len(Fig)):
        if Name is not None:
            if len(Fig) > len(Name):
                Fig[f].savefig(filename + f"_{Name[f % len(Name)]}_{f // len(Name)}" + ext, dpi = dpi)
            else:
                Fig[f].savefig(filename + f"_{Name[f]}" + ext if len(Fig) > 1 else filename + ext, dpi = dpi)
        else:
            Fig[f].savefig(filename + f"_{f}" + ext if len(Fig) > 1 else filename + ext, dpi = dpi)

def print_Map(Map, filename, Name = None):
    for m in range(len(Map)):
        if Name is not None:
            if len(Map) > len(Name):
                file = open(filename + f"_{Name[m % len(Name)]}_{m // len(Name)}.csv", 'w')
            else:
                file = open(filename + f"_{Name[m]}.csv" if len(Map) > 1 else filename + ".csv", 'w')
        else:
            file = open(filename + f"_{m}.csv" if len(Map) > 1 else filename + ".csv", 'w')
        for j in range(Map[m].shape[1]):
            if j != 0:
                file.write("\n")
            for i in range(Map[m].shape[0]):
                file.write(f"{Map[m][i, j]}" if i == 0 else f",{Map[m][i, j]}")
        file.close()

# def print_stack_Map(Map, head, ROI, filename):
#     file = open(filename + ".csv", 'w')
#     file.write("X,Z,real_X,real_Z")
#     for k in range(len(ROI)):
#         file.write(f",{ROI[k][0]}")
#     for i in range(Map[0].shape[0]):
#         file.write("\n")
#         for j in range(Map[0].shape[1]):
#             file.write(f"{i},{j},{head["Xpositions"][0, i]},{head["Zpositions"][0, j]}")
#             for k in range(len(ROI)):
#                 file.write(f",{Map[k][i, j]}")
#     file.close()

def stack_Map(Map, head, title, Label = None, lightmode = False, Origin = "lower", Aspect = 'auto'):
    if len(Map) > 3:
        print("Too many maps to stack!")
        return
    Fig = []
    fig = plt.figure(layout = 'compressed')
    ax1 = fig.add_subplot()
    data = []
    for m in range(3):
        if len(Map) < m + 1:
            if lightmode:
                data.append(np.ones(shape = data[0].shape))
            else:
                data.append(np.zeros(shape = data[0].shape))
        else:
            if lightmode:
                data.append(1 - Map[m] / np.max(Map[m]))
            else:
                data.append(Map[m] / np.max(Map[m]))
    data = np.array(data).transpose(1, 2, 0)
    ax1.imshow(data.transpose(1, 0, 2), origin=Origin)
    X = list(range(0, data.shape[0] + 1, math.floor(data.shape[0]/6) if math.floor(data.shape[0]/6) > 0 else 1))
    if data.shape[0] % 6 == 0:
        X[-1] -= 1
    Z = list(range(0, data.shape[0] + 1, math.floor(data.shape[0]/6) if math.floor(data.shape[0]/6) > 0 else 1))
    if data.shape[1] % 6 == 0:
        Z[-1] -= 1
    ax1.set_xlabel("X [mm]")
    ax1.set_ylabel("Z [mm]")
    if Label is not None:
        if lightmode:
            colors = "(C, M, Y)"
        else:
            colors = "(R, G, B)"
        if len(Map) == 3:
            ax1.set_title(f"{title}\n {colors}=({Label[0]}, {Label[1]}, {Label[2]})")
        elif len(Map) == 2:
            ax1.set_title(f"{title}\n {colors}=({Label[0]}, {Label[1]}, 0.0)")
        else:
            ax1.set_title(f"{title}\n {colors}=({Label[0]}, 0.0, 0.0)")
    else:
        ax1.set_title(f"{title}")
    ax1.set_xticks(X)
    ax1.set_yticks(Z)
    ax1.set_xticklabels(np.round(head["Xpositions"][0, X], 2))
    ax1.set_yticklabels(np.round(head["Zpositions"][0, Z], 2))
    ax1.set_aspect(Aspect)
    Fig.append(fig)
    return Fig

def print_stack_Map(Map, head, ROI, filename):
    file = open(filename + ".csv", 'w')
    file.write("X,Z,real_X,real_Z")
    for k in range(len(ROI)):
        file.write(f",{ROI[k][0]}")
    for i in range(Map[0].shape[0]):
        for j in range(Map[0].shape[1]):
            file.write("\n")
            file.write(f'{i},{j},{head["Xpositions"][0, i]},{head["Zpositions"][0, j]}')
            for k in range(len(ROI)):
                file.write(f",{Map[k][i, j]}")
    file.close()