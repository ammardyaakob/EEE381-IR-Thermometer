import math

import matplotlib.pyplot as plt
import numpy as np



def simplePeakDetect(xArr: list, yArr : list, timeConstant):
    #time constant is the time it takes (in seconds) for signal to degrade to 36.8% of its original value.
    #original peak = last peak found in the signal
    #set inital values of last peak time, last peak voltage and current value. signal will degrade according to the last peak and time.
    peakList = []
    peakList.append(yArr[0])
    currVal = yArr[0]
    lastPeakVoltage = yArr[0]
    lastPeakTime = xArr[0]
    for i in range(len(xArr)-1):
        i=i+1
        degraded = currVal * math.exp((-(xArr[i] - xArr[i-1])) / (timeConstant)) # degraded signal according to time constant
        if yArr[i] >= degraded:
            currVal = yArr[i]
            lastPeakVoltage = yArr[i]
            lastPeakTime = xArr[i]
        else:
            currVal = degraded
        peakList.append(currVal)

    return peakList





