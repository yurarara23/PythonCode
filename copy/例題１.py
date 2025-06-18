import numpy as np
import matplotlib.pyplot as plt
import csv
import time

def get_sine_wave_data(phase_shift):
    x = np.linspace(0, 4 * np.pi, 1000)
    y = np.sin(x + phase_shift)
    return x, y 

plt.ion()
fig, ax = plt.subplots()
frequencies, amplitudes = get_sine_wave_data(0)
line, = ax.plot(frequencies, amplitudes)

ax.set_xlabel('Time')
ax.set_ylabel('Amplitude')  
ax.set_title('Sine Wave')
ax.set_ylim(-1.5, 1.5)

phase_shift = 0

while True:
    frequencies, amplitudes = get_sine_wave_data(phase_shift)

    line.set_xdata(frequencies)
    line.set_ydata(amplitudes)
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.1)

    with open('例題1.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Frequencies(Hz)','Voltage(V)'])
        for f, v in zip(frequencies, amplitudes):
            writer.writerow([f, v])

    phase_shift += 0.1
    time.sleep(0.1)
