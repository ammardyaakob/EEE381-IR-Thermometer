import numpy as np
import pandas as pd
from matplotlib.lines import lineMarkers
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, axvline
from numpy import polyfit

from averaging import simpleAvg
from peakdetect import simplePeakDetect
import math as math

filePath =  "Raw Data/chopperSquare.csv"
file = pd.read_csv(filePath)

N = 125
Fs = 1000
t = np.arange(0, (N-1)/Fs, 1/Fs)
v = file.iloc[0:N-1, 1]



y = simplePeakDetect(t,v,8)

figure(figsize=(9,6))
title("Chopper Wheel Measurement at 1000°C")
plot(t*100,v)
plot(t*100,y)
xlabel("Time (ms)")
ylabel("Voltage (V)")
show()