from cProfile import label

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from click import style
from matplotlib.lines import lineMarkers
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, \
    axvline, ticklabel_format, subplots
from numpy import polyfit
from numpy.ma.extras import apply_over_axes

from averaging import simpleAvg
from peakdetect import simplePeakDetect
import math as math

# Sine wave generator + plot
# parameters


dataFile1 = pd.read_csv("Data to Linearize/from .txt (example calibration data).csv")
dataFile2 = pd.read_csv("Data to Linearize/from Calibration Example and template.csv")
dataFile3 = pd.read_csv("Data to Linearize/from Big Data.csv")

T1 = dataFile1.get("Temp")  # y is a panda Series of temperatures
V1 = dataFile1.get("Voltage")  # y is a panda Series of voltages
T2 = dataFile2.get("Temp")  # y is a panda Series of temperatures
V2 = dataFile2.get("Voltage")  # y is a panda Series of voltages
T3 = dataFile3.iloc[2:8, 0]  # y is a panda Series of temperatures
V3 = dataFile3.iloc[2:8, 1]  # y is a panda Series of voltages
print(V3)

# linearizing
x1 = 1 / T1
x2 = 1 / T2
x3 = 1 / T3
y1, y2, y3 = [], [], []
for value in V1:  # y = ln V
    y1.append(math.log(value))
for value in V2:  # y = ln V
    y2.append(math.log(value))
for value in V3:  # y = ln V
    y3.append(math.log(value))

### Best fits of all data sets graphing
figure(figsize=(9,6))
plot(x1, y1, marker=".", markersize=5, ls=" ", color="black")
plot(x2, y2, marker=".", markersize=5, ls=" ", color="red")
plot(x3, y3, marker=".", markersize=5, ls=" ", color="blue")

title("Linearisation of Voltage to Temperature of Different Photodiodes")
xlabel(r"$\frac{1}{T}$ ($K^{-1}$)", size="12")
ylabel("ln V")

m1, c1 = polyfit(x1, y1, 1)  # get m and c from best fit, y = mx + c
m2, c2 = polyfit(x2, y2, 1)
m3, c3 = polyfit(x3, y3, 1)

bestfy1 = m1 * x1 + c1
bestfy2 = m2 * x2 + c2
bestfy3 = m3 * x3 + c3

plot(x1, bestfy1, ls=":", color="black", label="InGaAs Photodiode")
plot(x2, bestfy2, ls=":", color="red", label="Si Photodiode")
plot(x3, bestfy3, ls=":", color="blue", label="Si Avalanche Photodiode")

legend()
grid()
axhline(0, color='black')  # x = 0
axvline(0, color='black')  # y = 0

print("BLACK: m = " + str(m1) + ", c = " + str(c1))
print("RED: m = " + str(m2) + ", c = " + str(c2))
print("BLUE: m = " + str(m3) + ", c = " + str(c3))
print(
    "BLACK is from example.txt file (InGaAs), RED is from calibration example and template (Si), BLUE is from big data files (Si APD)")

### convert voltage to temperature using calibration parameters

# from blue line in graph above, m = -15404.425383931075, c = 10.876797484015087
m4 = m3
c4 = c3

# remove blanked value
blankedBlue = 0.001508862
dataFile4 = pd.read_csv("sampleBigData/1200C Si APD open 1.csv")
v4 = dataFile4.get("Voltage")  # v4 is a panda Series of voltages from Si APD
lnv4 = []  # get lnV values
for value in v4:
    lnv4.append(math.log(value - blankedBlue))

# range of time to use in us
micro = 0.000001
lowlim = 0
prec = 0.01  # interval
uplim = 1

#convert volt to temp
x4 = np.arange(lowlim, uplim, prec)  # ndarray of x values, mimicking the time
print((uplim - lowlim) / prec)
temp4 = []
for i in range(int((uplim - lowlim) / prec)):
    temp4.append((m3 / (lnv4[i] - c3)) - 273.15)  ## from equation T = m/(lnV - c)

### peak detection graphing

figure(figsize=(9,6))
plot(x4, temp4, marker=".", markersize=5, ls="-")
title("Peak detection of 1 data set at temp = 1200 °C (not blanked yet), Time constant = 1000s")
xlabel("Time (s)")
ylabel("Temperature (K)")

# peak detection
peaks = simplePeakDetect(x4, temp4, 1000)
plot(x4, peaks, marker="", markersize=2)

# Temperature

fig, ax = subplots(figsize=(9, 6))

ax.plot(x4, temp4, marker=".", markersize=5, ls="-", linewidth="2", label='Calibrated Measurement', color="black")
ax.set_title("Si APD measurements of a blackbody furnace at T = 1200 °C")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Temperature (°C)")
ax.ticklabel_format(axis='y',style='')

# line at T = 1473.15 K
l4 = []
for value in x4:
    l4.append(1473.15)
# plot(x4, l4, marker=" ", markersize=5, ls="-", linewidth='4',label='Blackbody Temperature')

averages10 = simpleAvg(temp4, 20)
averages5 = simpleAvg(temp4, 5)
averages50 = simpleAvg(temp4, 50)

ax.plot(x4, averages10, marker="", markersize=3, ls="-", linewidth='1.5', label='Averaging: 10 data points', color="red")
ax.plot(x4, averages5, marker="", markersize=3, ls="-", linewidth='1.5', label='Averaging: 5 data points', color="green")
ax.plot(x4, averages50, marker="", markersize=3, ls="-", linewidth='1.5', label='Averaging: 50 data points',
     color="magenta")
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25),
          fancybox=True, shadow=True, ncol=2)
plt.ylim(1199,1201)
grid()
show()