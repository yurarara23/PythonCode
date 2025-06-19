import numpy as np
import matplotlib.pyplot as plt
import csv
import pyvisa
import time

R = 5100
C = 1e-8
v_in_peak = 1
v_in_RMS = v_in_peak / np.sqrt(2)

def calculate_voltage(frequency):
    omega = 2 * np.pi * frequency
    H = 1 / np.sqrt(1 + (omega * R * C) ** 2)
    return v_in_RMS * H


def get_voltage(fq):
    function_generator.write(f"FREQ {fq}")
    time.sleep(2)
    measurement_device.write("MEAS:VOLT?")
    response = measurement_device.read()

    try:
        voltage_str = response.split(',')[3]
        voltage = float(voltage_str)
    except (IndexError, ValueError) as e:
        print(f"Error parsing voltage response: {e}")
        voltage = 0.0

    return voltage

rm = pyvisa.ResourceManager()
function_generator_address = 'GPIB::2::INSTR'  
measurement_device_address = 'GPIB::9::INSTR'

function_generator = rm.open_resource(function_generator_address)
measurement_device = rm.open_resource(measurement_device_address)
measurement_device.timeout = 5000

function_generator.write(":FUNC SIN")
function_generator.write(":VOLT 2")
function_generator.write(":FREQ 100")
function_generator.write(":OUTP ON")

measurement_device.write(":MAIN:FUNC ACV")
time.sleep(0.1)

frequencies = np.logspace(2, 5, 31)
voltages = []
theoretical_voltages = []

plt.ion()
fig, ax = plt.subplots() 
line_measured, = ax.semilogx([],[], 'o-', label='Measured Voltage')
line_theoretical, = ax.semilogx([],[], 'x-', label='Theoretical Voltage')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Voltage (V)')
ax.set_title('Voltage vs Frequency')
ax.grid(True, which='both', linestyle=':')
ax.legend()

for freq in frequencies:
    voltage = get_voltage(freq)
    voltages.append(voltage) 
    theoretical_voltage = calculate_voltage(freq)
    theoretical_voltages.append(theoretical_voltage)

    line_measured.set_data(frequencies[:len(voltages)], voltages)
    line_theoretical.set_data(frequencies[:len(theoretical_voltages)], theoretical_voltages)
    
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)

with open('例題4.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Frequency (Hz)', 'Measured Voltage (V)', 'Theoretical Voltage (V)'])
    for f, v, t in zip(frequencies, voltages, theoretical_voltages):
        csvwriter.writerow([f, v, t])


measurement_device.close()
function_generator.close()
rm.close()

plt.ioff()
plt.show()
       
