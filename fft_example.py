import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

print("hello")

# s0, set up the sampling rate and sample spacing
sample_rate = 500  # sampling frequency, Hz
T = 1. / sample_rate  # sampling interval in seconds 
x = np.linspace(.0, 1., sample_rate, endpoint=False)


# s1, create a signal
freq = 5  # frequency of the example signal, in Hz
y = np.sin(freq * 2 * np.pi * x)  # example signal

# s2, perform fft
yf = np.fft.fft(y)

# s3, calculate the frequencies
xf = np.fft.fftfreq(sample_rate, T)

# s4, plot the results
fig, ax = plt.subplots(2, 1, figsize=(10, 6))

ax[0].plot(x, y)
ax[0].set_xlabel('Time [s]')
ax[0].set_ylabel('Signal amplitude')
ax[0].set_title('Signal')

data = pd.DataFrame({'Frequency': xf, 'Power': np.abs(yf)})
# use kde estimation for the frequency distribution, with line plot
sns.lineplot(x='Frequency', y='Power', data=data, ax=ax[1])

ax[1].set_xlabel('Frequency [Hz]')
ax[1].set_ylabel('Power')
ax[1].set_title('Power spectrum')
ax[1].set_xlim(0, 10)

plt.tight_layout()
plt.show()


print(x)
