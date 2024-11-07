import matplotlib.pyplot as plt
import numpy as np

from peakdetect import simplePeakDetect, prec
import math as math
# Sine wave generator + plot
    # parameters
lowlim = 0
uplim = 100

x = np.arange(lowlim, uplim, prec) # ndarray of x values
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

peaks = simplePeakDetect(x,y)
print(peaks)
plt.figure()
plt.plot(x, y)
plt.figure()
plt.plot(np.arange(0,len(peaks),), peaks, marker=".")
plt.show()
