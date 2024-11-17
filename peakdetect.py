
import matplotlib.pyplot as plt
import numpy as np



def simplePeakDetect(xArr: list, yArr : list, holdParameter):
    # holdParameter determines how many data points a
    # high peak should sustain, unless a higher peak is found.

    peakList = []
    newPeak = yArr[0]
    hold = holdParameter

    for i in range(len(xArr)-1):
        if i > 0 and yArr[i-1] < yArr[i] and yArr[i+1] < yArr[i]:
            if yArr[i] > newPeak:
                newPeak = yArr[i]
                peakList.append(newPeak)
                hold = holdParameter
            elif hold > 0:
                hold = hold - 1
                peakList.append(newPeak)
            else:
                newPeak = yArr[i]
                peakList.append(newPeak)
                hold = holdParameter
        else:
            peakList.append(newPeak)
            hold = hold - 1
    peakList.append(newPeak) # add 1 more datapoint to make sure peak array is same size as X array
    return peakList





