import numpy as np
import pandas as pd
from matplotlib.lines import lineMarkers
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title
from numpy import polyfit

from peakdetect import simplePeakDetect
import math as math
# Sine wave generator + plot
    # parameters



dataFile1 = pd.read_csv("Data to Linearize/from .txt (example calibration data).csv")
dataFile2 = pd.read_csv("Data to Linearize/from Calibration Example and template.csv")
dataFile3 = pd.read_csv("Data to Linearize/from Big Data.csv")

T1 = dataFile1.get("Temp") # y is a panda Series of temperatures
V1 = dataFile1.get("Voltage") # y is a panda Series of voltages
T2 = dataFile2.get("Temp") # y is a panda Series of temperatures
V2 = dataFile2.get("Voltage") # y is a panda Series of voltages
T3 = dataFile3.get("Temp") # y is a panda Series of temperatures
V3 = dataFile3.get("Voltage") # y is a panda Series of voltages


# linearizing
x1 = 1 / T1
x2 = 1 / T2
x3 = 1 / T3
y1,y2,y3 = [], [], []
for value in V1: # y = ln V
    y1.append(math.log(value))
for value in V2: # y = ln V
    y2.append(math.log(value))
for value in V3: # y = ln V
    y3.append(math.log(value))

### Best fits of all data sets graphing
figure()
plot(x1, y1, marker=".", markersize=5, ls=" ", color="black")
plot(x2, y2, marker=".", markersize=5, ls=" ", color="red")
plot(x3, y3, marker=".", markersize=5, ls=" ", color="blue")

title("Best fits and linearization of 3 temp data sets")
xlabel("1/T")
ylabel("ln V")

m1, c1 = polyfit(x1, y1, 1) # get m and c from best fit, y = mx + c
m2, c2 = polyfit(x2, y2, 1)
m3, c3 = polyfit(x3, y3, 1)

bestfy1 = m1 * x1 + c1
bestfy2 = m2 * x2 + c2
bestfy3 = m3 * x3 + c3

plot(x1, bestfy1, ls=":", color="black")
plot(x2, bestfy2, ls=":", color="red")
plot(x3, bestfy3, ls=":", color="blue")

print("BLACK: m = " + str(m1) + ", c = "+ str(c1) )
print("RED: m = " + str(m2) + ", c = "+ str(c2))
print("BLUE: m = " + str(m3) + ", c = "+ str(c3))
print("BLACK is from example.txt file, RED is from calibration example and template, BLUE is from big data files")

### peak detection graphing

dataFile4 = pd.read_csv("sampleBigData/1200C Si APD open 1.csv")
y4 = dataFile4.get("Voltage") # y is a panda Series of voltages
lny4 = []
for value in y4:
    lny4.append(math.log(value))
lowlim = 0
prec = 0.0001
uplim = len(lny4)

x4 = np.arange(lowlim, uplim*prec, prec) # ndarray of x values
figure()
plot(x4, lny4, marker=".", markersize=5 , ls=" ")
title("Peak detection of 1 data set at temp = 1200 °C (not blanked yet)")
xlabel("Arbitrary time (s)")
ylabel("ln V")

#peak detection
peaks = simplePeakDetect(x4,lny4,10000)
plot(x4, peaks, marker="", markersize = 2)



### dampened sin wave to test peak detection
lowlim = 0
prec = 0.1
uplim = 100

x5 = np.arange(lowlim, uplim, prec) # ndarray of x value

y5Undamped = np.sin(x5) # corresponding sinx values
y5 = []
i = 0
for u in y5Undamped:
    if i < len(y5Undamped)/2:
        factor = np.exp(float(0.01)*x5[i])
        print(float(factor))
        y5.append(u*factor)

    else:
        factor = np.exp(float(-0.01) * x5[i])
        print(float(factor))
        y5.append(u * factor)
    i = i + 1

figure()
title("Peak Detection Test on Generated Dampened Wave")
xlabel("Time")
ylabel("Amplitude")
plot(x5, y5, marker=".", markersize=5 , ls=" ")
peaks = simplePeakDetect(x5,y5,5)
plot(x5, peaks, marker="", markersize = 2)

show()
