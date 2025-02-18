
import matplotlib.pyplot as plt
import numpy as np



def simplePeakDetect(xArr: list, yArr : list, holdParameter):
    # holdParameter determines how many data points a
    # high peak should sustain, unless a higher peak is found.

    peakList = []
    currPeak = yArr[0]
    hold = holdParameter

    for i in range(len(xArr)):
        peakList.append(currPeak)
        if yArr[i]> currPeak:
            currPeak = yArr[i]
        else:
            currPeak = currPeak - (holdParameter/1000)
    return peakList





