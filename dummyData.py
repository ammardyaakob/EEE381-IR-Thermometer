### dampened sin wave dummy data to test time functions
import numpy as np
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend

from averaging import simpleAvg
from peakdetect import simplePeakDetect

temp = []
trueTemp = []

# parameters
lowlim = 0
samples = 1000
uplim = 500
noiseAmplitude = 0.5
centralTemp = 800
addedTemp = 5
# time fx parameters
avgHold = 250
peakHold = 50


x5 = np.linspace(lowlim, uplim, samples)  # time from 0 to 100 seconds, 100 sample points # ndarray of x value

y5Undamped = np.sin(0.1*x5) #  sin x wave values

#waveform bending
i = 0
for u in y5Undamped:
    if i < len(y5Undamped)/2:
        dampFactor = np.exp(float(0.01) * x5[i])
        trueTemp.append(u * dampFactor + centralTemp)

    else:
        dampFactor = np.exp(float(-0.01) * x5[i])
        trueTemp.append(100 * u * dampFactor + centralTemp + addedTemp)
    i = i + 1

# add noise
noise = np.random.normal(0, noiseAmplitude, size=x5.shape)
for i in range(len(trueTemp)):
    temp.append(trueTemp[i] + noise[i])

# plot graph
figure()
title("Peak Detection Test on Generated Wave")
xlabel("Time")
ylabel("Temperature")
plot(x5, temp, marker=".", markersize=5, ls="")

# peak detect
peaks = simplePeakDetect(x5, temp, peakHold)
plot(x5, peaks, marker="", markersize = 2)

#plot graph 2
figure()
title("Averaging Test on Generated Wave")
xlabel("Time")
ylabel("Temperature")
plot(x5, temp, marker=".", markersize=5, ls="")

# average
avgs = simpleAvg(x5, temp, avgHold)
plot(x5, avgs, marker="", markersize = 2, ls="--", linewidth="3")

show()