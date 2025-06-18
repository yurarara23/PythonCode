import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import csv

rm = pyvisa.ResourceManager()

measurement_device_address = 'GPIB::9::INSTR'
measurement_device = rm.open_resource(measurement_device_address)

measurement_device.write(':MAIN:FUNC VOLT:DCV')
measurement_device.write(':VOLT:DCV:RANG 5')

power_supply_resource = 'ASRL10::INSTR'
power_supply = rm.open_resource(power_supply_resource)

power_supply.write('TRACK0')
power_supply.write('VSET1:0')
power_supply.write('ISET1:0')
power_supply.write('OUT1')
time.sleep(5)

time_data = []
voltage_data = []

start_time = time.time()

max_time = 100
measurement_interval = 0.1
supply_voltage = 1.0

plt.ion()
fig, ax = plt.subplots()
line_measurement, = ax.plot([], [], label='Measurement Voltage')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Voltage (V)')
ax.set_titile('Voltage Measurement Over Time')
ax.legend()
ax.grid(True)

power_supply.write('VSET1:1.0')
power_supply.write('ISET1:0.3')

while True:
    current_time = time.time() - start_time

    measurement_device.write(':MAIN:DATA?')
    response = measurement_device.read()

    try:
        voltage_str = responce.split(',')[3]
        voltage = float(voltage_str)
    except (IndexError, ValueError) as e:
        print(f"Error reading voltage: {e}")
        voltage = 0.0
    
    time.data.append(current_time)
    voltage_data.append(voltage)

    print(f"Time: {current_time:.3f} s, Voltage: {voltage:.3f} V")

    if current_time >= max_time or voltage >= 0.99 * supply_voltage:
        break

    line_measurement.set_xdata(time_data)
    line_measurement.set_ydata(voltage_data)

    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)

    time.sleep(0.01)

with open('例題5.1.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    if file.tell() == 0:
        writer.writerow(['Time (s)', 'Voltage (V)'])
    for t, v in zip(time_data, voltage_data):
        writer.writerow([t, v])

measurement_device.close()
power_supply.close()
rm.close()

plt.ioff()
plt.show()
