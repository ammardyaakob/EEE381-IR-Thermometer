import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import lineMarkers
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, axvline
from numpy import polyfit

from averaging import simpleAvg
from calibration import voltToTemp, findLinParams
from peakdetect import simplePeakDetect
import math as math

filePath =  "Raw Data/chopperSquare.csv"
file = pd.read_csv(filePath)

N = 125
Fs = 1000
t = np.arange(0, (N-1)/Fs, 1/Fs)
v = file.iloc[0:N-1, 1]
lifted = []
for data in v:
    if data < 0:
        lifted.append(0.0020)
    else:
        lifted.append(data)

m,c = findLinParams(folderStr="Raw Data/Measurements26Feb/",lowestTemp=700, highestTemp=1300,celsius=True,samples=500, increment=100)
temp = voltToTemp(lifted,m,c+1.38, True)

y = simplePeakDetect(t,temp,0.05)
fig = plt.figure(figsize=(9,6))
ax = fig.add_subplot(1, 1, 1)
title("Peak Detection of Chopper Wheel Measurement at 1000°C")
plot(t*100,temp,label = "Peak Detector On")
plot(t*100,y,label = "Peak Detector Off")
xlabel("Time (s)")
ylabel("Temperature (°C)")
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25),
          fancybox=True, shadow=True, ncol=2)

grid()
show()