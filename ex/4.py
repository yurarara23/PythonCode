import numpy as np
import matplotlib.pyplot as plt
import csv
import pyvisa
import time

R = 5100
C = 1e-8
vin_peak = 1
vin_rms = vin_peak / np.sqrt(2)

def calc_voltage(freq):
    omega = 2 * np.pi * freq
    H = 1 / np.sqrt(1 + (omega * R * C) ** 2)
    return vin_rms * H

def get_voltage(freq):
    fg.write(f"FREQ {freq}")
    time.sleep(2)

    meter.write("MEAS:VOLT?")
    response = meter.read()

    try:
        voltage = float(response.strip())
    except ValueError as e:
        print(f"Error parsing response: {e}, response = {response}")
        voltage = 0.0

    return voltage

# VISA機器初期化
rm = pyvisa.ResourceManager()
fg_addr = 'GPIB::2::INSTR'
meter_addr = 'GPIB::9::INSTR'

fg = rm.open_resource(fg_addr)
meter = rm.open_resource(meter_addr)
meter.timeout = 5000

# 波形・出力設定
fg.write(":FUNC SIN")
fg.write("VOLT 2")
fg.write("FREQ 100")
fg.write("OUTP ON")

meter.write("MAIN:FUNC ACV")
time.sleep(0.1)

# 測定準備
freqs = np.logspace(2, 5, 31)
measured = []
theoretical = []

plt.ion()
fig, ax = plt.subplots()
line_meas, = ax.semilogx([], [], 'o-', label='Measured')
line_theo, = ax.semilogx([], [], 'x-', label='Theoretical')

ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Voltage (V)')
ax.set_title('RC Filter Response')
ax.grid(True, which='both', linestyle=':')
ax.legend()

for i, f in enumerate(freqs):
    print(f"Measuring at {f:.2f} Hz...")
    v_meas = get_voltage(f)
    v_theo = calc_voltage(f)

    measured.append(v_meas)
    theoretical.append(v_theo)

    line_meas.set_data(freqs[:len(measured)], measured)
    line_theo.set_data(freqs[:len(theoretical)], theoretical)

    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)

# データ保存
with open('4.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Frequency (Hz)', 'Measured Voltage (V)', 'Theoretical Voltage (V)'])
    for f, vm, vt in zip(freqs, measured, theoretical):
        writer.writerow([f, vm, vt])

# クローズ処理
meter.close()
fg.close()
rm.close()

plt.ioff()
plt.show()
