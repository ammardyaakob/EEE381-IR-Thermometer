import statistics

import numpy as np
import pandas as pd
from matplotlib.lines import lineMarkers
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, \
    axvline, subplot, tight_layout
from numpy import polyfit

from averaging import simpleAvg
from calibration import findLinParams, voltToTemp, voltToEmis, emisComp
from peakdetect import simplePeakDetect
import math as math

m,c = findLinParams('Raw Data/Measurements26Feb/', 600, 1300, 100, 500, True)
N = 125
Fs = 1000

fig = figure(figsize=(9, 6))
ax = subplot(111)

folderStr = "Raw Data/Emissivity/"
chosenEmis = [1, 13, 8, 9]
emisArr =[]
for i in chosenEmis:
    filePath = folderStr + "E" + str(i) + ".csv"
    file = pd.read_csv(filePath)
    v = file.iloc[0:N, 1]
    emisArr.append(voltToEmis(v,m,c,True))
for i in range(len(chosenEmis)):
    filePath = folderStr+"E"+str(chosenEmis[i])+".csv"
    file = pd.read_csv(filePath)

    t = np.arange(0, N / Fs, 1 / Fs)
    v = file.iloc[0:N, 1]
    v = emisComp(v,emisArr[i])
    temp = voltToTemp(v, m, c, True)
    temp = simpleAvg(temp,250)
    plot(t * 100, temp, label="Emissivity = "+str((round(emisArr[i],3))))

title("Blackbody Temperatures with Emissivity Compensation and Averaging")
xlabel("Time (ms)")
ylabel("Temperature (°C)")

# Shrink current axis's height by 10% on the bottom
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.2,
                 box.width, box.height * 0.8])

# Put a legend below current axis
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.125),
          fancybox=True, shadow=True, ncol=5)

show()