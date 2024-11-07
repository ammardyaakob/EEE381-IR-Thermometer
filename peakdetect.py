
import matplotlib.pyplot as plt
import numpy as np

prec = 0.001

def simplePeakDetect(xArr: list, yArr : list):
    peakList = []
    bufferList=[]
    highestBuffPeak = 0
    threshold = 0
    count = 0  # if count > spec amount, peak is detected ( no other peak after 5 passes/intervals)

    for i in range(len(xArr)-1):
        if i > 0:
            if yArr[i-1] < yArr[i]:
                if yArr[i+1] < yArr[i]:
                    peakList.append(yArr[i])
    return peakList





