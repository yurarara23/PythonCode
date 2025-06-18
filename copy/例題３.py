import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import csv

def get_voltage(fq):
    function_generator.write(f"FREQ {fq}")
    time.sleep(2)
    mesurement_deevice.write("MEAS:VOLT?")
    response = mesurement_deevice.read()

    try:
        voltage_str = response.split(',')[3]
        voltage = float(voltage_str)
    except (IndexError, ValueError) as e:
        print(f"Error parsing voltage response: {e}")
        voltage = 0.0

    return voltage

rm = pyvisa.ResourceManager()
function_generator_address = 'GPIB::2::INSTR'
funciton_generator = rm.open_resource(function_generator_address)

function_generator.write(":FUNC SIN")
function_generator.write("VOLT 2")   
function_generator.write("FREQ 100")
function_generator.write("OUTP ON")

measurement_device_address = 'GPIB::9::INSTR'
measurement_device = rm.open_resource(measurement_device_address)
measurement_device.timeout = 5000

measurement_device.write("MAIN:FUNC ACV")
measurement_device.write("MAIN:MEAS?")

time.sleep(0.1)

frequencies = np.logspace(2, 5, 31)
voltages = []

plt.ion()
fig, ax = plt.subplots()
line, = ax.semilogx(frequencies, [0] * len(frequencies), 'o-')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Voltage (V)')
ax.set_title('Voltage vs Frequency')

for freq in frequencies:
    voltage = get_voltage(freq)
    print(f"Frequency: {freq} Hz, Voltage: {voltage} V")
    voltage.append(voltage)

    line.set_ydata(voltages)
    line.set_xdata(frequencies[:len(voltages)])
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)

    with open('例題3.csv', 'a', newline='') as csvfile:
        if file.tell() == 0:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Frequency (Hz)', 'Voltage (V)'])
        for f,v in zip(frequencies, voltages):
            csvwriter.writerow([f, v])


measurement_device.clse()
function_generator.close()
rm.close()

plt.ioff()
plt.show()