import numpy as np
from contourpy.util.data import simple
from matplotlib.pyplot import xlabel, ylabel, plot, figure, show, title, legend, grid, axhline, axline, axvspan, axvline

from peakdetect import simplePeakDetect

# Parameters
start_time = 0
end_time = 10
sampling_rate = 1000  # samples per second

# Generate time array
num_samples = (end_time - start_time) * sampling_rate + 1
time = np.linspace(start_time, end_time, num=num_samples)

# Generate voltage array
voltage = np.zeros_like(time)

# Set specific voltage values at given times
pulse_times = [2, 4, 7]
pulse_values = [10, 50, 100]

for t, v in zip(pulse_times, pulse_values):
    # Find the index closest to the pulse time
    index = np.argmin(np.abs(time - t))
    voltage[index] = v

peaks = simplePeakDetect(time,voltage,5)
plot(time,voltage)
plot(time, peaks)
xlabel("Time (s)")
ylabel("Voltage (V)")
title("Generated Data with Pulses")
show()

# The complete lists are in 'time' and 'voltage' variables