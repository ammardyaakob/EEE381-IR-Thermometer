import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, \
    axvline, ticklabel_format, subplots

df = pd.read_excel("Graph Files/main.xlsx")
wavelength = df.loc[:,"Wavelength (µm)"]
t500 = df.loc[:,"500K"]
t700 = df.loc[:,"700K"]
t1000 = df.loc[:,"1000K"]
t2000 = df.loc[:,"2000K"]
t4000 = df.loc[:,"4000K"]
t5500 = df.loc[:,"5500K"]

maxWv= df.loc[0:5,"Max Wavelength"]
maxRad= df.loc[0:5,"radiance at max"]
print(maxWv)
print(maxRad)


fig = plt.figure(figsize=(9,6))
ax = fig.add_subplot(1, 1, 1)
title("Spectral Radiance at Different Temperatures")
ax.set_yscale('log')
ax.set_xscale('log')
plt.ylim(0.0001,10000)
plt.xlim(0.1,10)
plot(wavelength,t500,label="500K",marker=".")
plot(wavelength,t700,label="700K",marker=".")
plot(wavelength,t1000,label="1000K",marker=".")
plot(wavelength,t2000,label="2000K",marker=".")
plot(wavelength,t4000,label="4000K",marker=".")
plot(wavelength,t5500,label="5500K",marker=".")
plot(maxWv,maxRad)
xlabel("Wavelength (µm)")
ylabel("Spectral Radiance (Watts/cm-2 -sr-micron)")
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25),
          fancybox=True, shadow=True, ncol=6)
grid()
show()

