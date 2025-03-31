from calibration import findLinGraph
from matplotlib.lines import lineMarkers
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, axvline

myDataRcpT, myDataLnV = findLinGraph('Raw Data/Measurements26Feb/', 600, 1300, 100, 500, True)
#LouisDataRcpT, LouisDataLnV = findLinGraph('Raw Data/Louis Data/', 900, 1300, 100, 500, True)

figure()
xlabel(r"$\frac{1}{T}$ ($K^{-1}$)", size="12")
ylabel("ln V")
plot(myDataRcpT,myDataLnV,marker='.',label='Ammar\'s Data')
#plot(LouisDataRcpT,LouisDataLnV,marker='x',label='Louis\' Data')
grid()
axhline(0,color='black') # x = 0
axvline(0,color='black') # y = 0
legend()
show()