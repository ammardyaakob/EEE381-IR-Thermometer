import numpy as np
import matplotlib.pyplot as plt

# Parameters
time = np.linspace(0, 100, 100)  # time from 0 to 100 seconds, 100 sample points
trueTemp = 1000  # Central temperature (in K)
noiseAmplitude = 20  # Amplitude of random noise

# noisy temp
noise = np.random.normal(0, noiseAmplitude, size=time.shape)
temperature = trueTemp + noise

plt.figure(figsize=(10, 5))
plt.plot(time, temperature, label='Temperature (with noise)', color='red', alpha=0.7)
plt.axhline(y=trueTemp, color='blue', linestyle='--', label='True Temperature (1000K)')
plt.title('Dummy Temperature vs Time Graph')
plt.xlabel('Time (s)')
plt.ylabel('Temperature (K)')
plt.legend()
plt.grid(True)
plt.show()