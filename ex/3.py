import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import csv

def get_voltage(freq):
    function_generator.write(f"FREQ {freq}")
    time.sleep(2)
    dmm.write("MEAS:VOLT?")
    response = dmm.read()

    try:
        voltage = float(response.strip())
    except ValueError as e:
        print(f"Error parsing voltage response: {e}, response = {response}")
        voltage = 0.0

    return voltage

# GPIB初期化
rm = pyvisa.ResourceManager()
function_generator = rm.open_resource('GPIB::2::INSTR')
dmm = rm.open_resource('GPIB::9::INSTR')
dmm.timeout = 5000

# ファンクションジェネレータ初期設定
function_generator.write("FUNC SIN")
function_generator.write("VOLT 2")
function_generator.write("FREQ 100")
function_generator.write("OUTP ON")

# 電圧測定モードに設定
dmm.write("FUNC 'VOLT:AC'")  # 正しいコマンドに要調整
time.sleep(0.1)

# 周波数スイープ準備
frequencies = np.logspace(2, 5, 31)
voltages = []

# グラフ初期化
plt.ion()
fig, ax = plt.subplots()
line, = ax.semilogx([], [], 'o-')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Voltage (V)')
ax.set_title('Voltage vs Frequency')
ax.grid(True)

# CSVファイル準備
with open('3.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Frequency (Hz)', 'Voltage (V)'])

    # 周波数ごとに測定と描画
    for freq in frequencies:
        voltage = get_voltage(freq)
        voltages.append(voltage)
        print(f"Frequency: {freq:.1f} Hz, Voltage: {voltage:.4f} V")

        # CSVに1行ずつ保存
        writer.writerow([freq, voltage])

        # グラフ更新
        line.set_data(frequencies[:len(voltages)], voltages)
        ax.relim()
        ax.autoscale_view()
        plt.draw()
        plt.pause(0.01)

# 後始末
dmm.close()
function_generator.close()
rm.close()

plt.ioff()
plt.show()
