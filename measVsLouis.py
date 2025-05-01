from calibration import findLinGraph, findLinParams
from matplotlib.lines import lineMarkers
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, \
    axvline, xlim

myDataRcpT, myDataLnV = findLinGraph('Raw Data/Measurements26Feb/', 600, 1300, 100, 500, True)
LouisDataRcpT, LouisDataLnV = findLinGraph('Raw Data/Louis Data/', 900, 1300, 100, 500, True)
m,c = findLinParams('Raw Data/Measurements26Feb/', 600, 1300, 100, 500, True)
x = [0.0006,0.0012]
y = []
for val in x:
    y.append(m*val + c)

figure(figsize=(9,6))
xlabel(r"$\frac{1}{T}$ ($K^{-1}$)", size="12")
ylabel("ln V")
plot(myDataRcpT,myDataLnV,marker='.',label='Ammar\'s Data')
plot(x,y)
xlim(0.0006,0.0012)

plot(LouisDataRcpT,LouisDataLnV,marker='x',label='Louis\' Data')
grid()
axhline(0,color='black') # x = 0
axvline(0,color='black') # y = 0
legend()
show()