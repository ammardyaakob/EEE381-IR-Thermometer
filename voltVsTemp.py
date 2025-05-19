import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import lineMarkers
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, \
    axvline, subplot, subplots
from numpy import polyfit

from averaging import simpleAvg
from calibration import findLinParams, findLinGraph
from peakdetect import simplePeakDetect
import math as math

# output voltage vs temp of ingaas
rcpT, lnV = findLinGraph('Raw Data/Measurements26Feb/', 900, 1300, 100, 500, True)
m,c = findLinParams('Raw Data/Measurements26Feb/', 1000, 1300, 100, 500, True)
dataFile1 = pd.read_csv("Data to Linearize/from .txt (example calibration data).csv")
V1 = []
T1 = []
for a in lnV:
    V1.append(math.exp(a))
for a in rcpT:
    T1.append((1 / a)-273.15)

outT = []


for v in V1:
    outT.append((m/(math.log(v) - c))-273.15) ## from equation T = m/(lnV - c)
figure()

tempDiff = []

for a in range(len(T1)):
    tempDiff.append(outT[a]-T1[a])
print(tempDiff)

subplot(2,1,1)
title("Interface Reading and Furnace Setting Comparison")
plot(outT,V1,label="Interface Reading",ls=":")
plot(T1,V1,label="Furnace Setting",marker='.', ls ="")
ylabel("Voltage (V)")
xlabel("Temperature (°C)")
legend()
grid()
plt.xticks(np.arange(900, 1301, 100))

subplot(2,1,2)
plot(T1,tempDiff,marker="x")
xlabel("Target Temperature (°C)")
ylabel("Temperature Difference (°C)")
plt.xticks(np.arange(900, 1301, 100))
plt.yticks(np.arange(-3, 3.1, 1))
grid()
show()

