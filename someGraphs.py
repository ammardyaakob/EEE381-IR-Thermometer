import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, \
    axvline, ticklabel_format, subplots

df = pd.read_excel("Graph Files/emi1.xlsx")
wavelength = df.loc[:,"Wavelength (µm)"]
e03 = df.loc[:,"ε=0.3"]
e05 = df.loc[:,"ε=0.5"]
e07 = df.loc[:,"ε=0.7"]
e10 = df.loc[:,"ε=1.0 "]


fig = plt.figure(figsize=(9,6))
ax = fig.add_subplot(1, 1, 1)
title("Spectral Radiance of different emissivities at T = 1200K")
ax.set_yscale('log')
plt.ylim(0.01,1.5)
plt.xlim(0.5,10)
plot(wavelength,e03,label="ε=0.3")
plot(wavelength,e05,label="ε=0.5")
plot(wavelength,e07,label="ε=0.7")
plot(wavelength,e10,label="ε=1.0")
xlabel("Wavelength (µm)")
ylabel("Spectral Radiance (Watts/cm-2 -sr-micron)")
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25),
          fancybox=True, shadow=True, ncol=5)
grid()
show()

