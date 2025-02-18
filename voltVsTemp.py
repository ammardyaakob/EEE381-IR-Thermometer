import numpy as np
import pandas as pd
from matplotlib.lines import lineMarkers
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, \
    axvline, subplot
from numpy import polyfit

from averaging import simpleAvg
from peakdetect import simplePeakDetect
import math as math

# output voltage vs temp of ingaas

m = -9441.80985771958
c = 10.84832678185014
dataFile1 = pd.read_csv("Data to Linearize/from .txt (example calibration data).csv")
T1 = dataFile1.get("Temp") # temperature of blackbody
V1 = dataFile1.get("Voltage") # y is a panda Series of voltages
outT = []

for v in V1:
    outT.append(m/(math.log(v) - c)) ## from equation T = m/(lnV - c)
figure()

subplot(2,1,1)
title("Output Voltage to Temperature Conversion")
plot(V1,outT,label="Interface Temperature",ls=":")
plot(V1,T1,label="Furnace Temperature",marker='.', ls ="")
xlabel("Output Voltage (V)")
ylabel("Temperature (K)")
legend()
subplot(2,1,2)
plot(V1, outT-T1,marker="x")
xlabel("Output Voltage (V)")
ylabel("Temperature Difference (K)")
legend()
show()