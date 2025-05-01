from cProfile import label

import numpy as np
import pandas as pd
import glob
import os

from fontTools.misc.cython import returns
from numpy.ma.extras import average

from averaging import simpleAvg
from matplotlib.lines import lineMarkers
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, axvline
from numpy import polyfit
from listMath import listLn,listRcp

from averaging import simpleAvg
from listMath import listLn, listRcp
from peakdetect import simplePeakDetect
import math as math

#csv_files = glob.glob('Raw Data/Measurements26Feb/*.csv')

'''
for file in csv_files:
    df = pd.read_csv(file)
    avg = simpleAvg(df.loc[:,"Time"],df.loc[:,"Dev1/ai0"],500)
    print(os.path.basename(file)[:-4],avg[499]) # print file name and the average value, some decimal loss here because excel
'''


def findLinGraph(folderStr : str, lowestTemp, highestTemp, increment, samples, celsius:bool):
    # Returns calibrated 1/T and lnV arrays
 # PUT FOLDER DIRECTORY FROM PROJECT CONTEXT IN folderStr e.g 'Raw Data/Measurements26Feb/'
 # DATA FILES MUST BE [TEMP].csv AND BLOCKED DATA FILES MUST BE [TEMP]B.csv e.g. "1300.csv" and "1300B.csv" IN ONE FOLDER
    # samples is the amount of data points to take for the calibration
    #increment is the temperature step between each calibration measurement

    voltages = []
    temps = []

    for temperature in range(lowestTemp,highestTemp+1,increment):
        filePath = folderStr+'/'+str(temperature)+".csv" # string e.g "Raw Data/Measurements26Feb/1300.csv"
        filePathBlocked = folderStr+'/'+str(temperature)+"B.csv" # string e.g "Raw Data/Measurements26Feb/1300B.csv"

        # Read set of data and blocked data
        df = pd.read_csv(filePath)
        dfBlocked = pd.read_csv(filePathBlocked)

        # calculate the average of each set
        avg = average(df.loc[:samples, "Dev1/ai0"])
        avgBlocked = average(dfBlocked.loc[:samples, "Dev1/ai0"])
        print(temperature, avg-avgBlocked)
        voltages.append(avg-avgBlocked)

        if celsius:
            temps.append(temperature+273.15)
        else:
            temps.append(temperature)

    m, c = polyfit(listRcp(temps), listLn(voltages), 1)
    print("m =",m,"c =",c, "Mean Eff. Wavelength:", -(0.014388/m))
    return listRcp(temps),listLn(voltages)

def findLinParams(folderStr : str, lowestTemp : int, highestTemp: int, increment, samples, celsius:bool):
    # Returns m and C values of calibrated lnV against 1/T graph.
 # PUT FOLDER DIRECTORY FROM PROJECT CONTEXT IN folderStr e.g 'Raw Data/Measurements26Feb/'
 # DATA FILES MUST BE [TEMP].csv AND BLOCKED DATA FILES MUST BE [TEMP]B.csv e.g. "1300.csv" and "1300B.csv" IN ONE FOLDER

    voltages = []
    temps = []

    for temperature in range(lowestTemp,highestTemp+1,increment):
        filePath = folderStr+'/'+str(temperature)+".csv" # string e.g "Raw Data/Measurements26Feb/1300.csv"
        filePathBlocked = folderStr+'/'+str(temperature)+"B.csv" # string e.g "Raw Data/Measurements26Feb/1300B.csv"

        # Read set of data and blocked data
        df = pd.read_csv(filePath)
        dfBlocked = pd.read_csv(filePathBlocked)

        # calculate the average of each set
        avg = average(df.loc[:samples, "Dev1/ai0"])
        avgBlocked = average(dfBlocked.loc[:samples, "Dev1/ai0"])
        print(temperature, avg-avgBlocked)
        voltages.append(avg-avgBlocked)

        if celsius:
            temps.append(temperature+273.15)
        else:
            temps.append(temperature)


    m, c = polyfit(listRcp(temps), listLn(voltages), 1)
    print("m =",m,"c =",c, "Mean Eff. Wavelength:", -(0.014388/m))
    return m,c

def voltToTemp(vArr, m, c, celsius):
    temp = []
    if celsius:
        for i in range(len(vArr)):
            temp.append(m/(math.log(vArr[i]) - c) - 273.15) ## from equation T = m/(lnV - c)
    else:
        for i in range(len(vArr)):
            temp.append(m/(math.log(vArr[i]) - c)) ## from equation T = m/(lnV - c)
    return temp

def voltToEmis(vArr, m, c, celsius): #compares with emissivity 0 at T = 1300C
    emis = []
    for i in range(len(vArr)):
        emis.append(vArr[i]/1.67931706328) ## V/V0
    return average(emis)

def emisComp(vArr, emis):
    comped = []
    for v in vArr:
        comped.append(v/emis)
    return comped
