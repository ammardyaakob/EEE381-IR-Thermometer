import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import lineMarkers

from peakdetect import simplePeakDetect
import math as math
# Sine wave generator + plot
    # parameters


dataFile = pd.read_csv("sampleBigData/1200C Si APD open 1.csv")
y = dataFile.get("Voltage") # y is a panda Series of voltages
lowlim = 0
prec = 0.0001
uplim = len(y)

x = np.arange(lowlim, uplim*prec, prec) # ndarray of x values

'''
yUndamped = np.sin(x) # corresponding sinx values
y = []
i = 0
for u in yUndamped:
    if i < len(yUndamped)/2:
        factor = np.exp(float(0.01)*x[i])
        print(float(factor))
        y.append(u*factor)
        
    else:
        factor = np.exp(float(-0.01) * x[i])
        print(float(factor))
        y.append(u * factor)
    i = i + 1
'''





plt.figure()
plt.plot(x, y, marker=".", markersize=5 , ls=" ")

peaks = simplePeakDetect(x,y)
plt.plot(x, peaks, marker="", markersize = 2)

plt.show()
