import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import csv

rm = pyvisa.ResourceManager()

# GPIBマルチメータ初期化
dmm = rm.open_resource('GPIB::9::INSTR')
dmm.write(':MAIN:FUNC VOLT:DCV')
dmm.write(':VOLT:DCV:RANG 5')

# 電源装置初期化 GPD-4303
psu = rm.open_resource('ASRL10::INSTR')
psu.write('TRACK0')
psu.write('VSET1:0')
psu.write('ISET1:0')
psu.write('OUT1')
time.sleep(5)

# 測定設定
t_data = []
v_data = []

start_time = time.time()
max_time = 100
interval = 0.1
v_target = 1.0

# グラフ初期化
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], label='Measured Voltage')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Voltage (V)')
ax.set_title('Voltage Measurement Over Time')
ax.legend()
ax.grid(True)

# 電圧印加
psu.write(f'VSET1:{v_target}')
psu.write('ISET1:0.3')

while True:
    t_now = time.time() - start_time

    dmm.write(':MAIN:DATA?')
    try:
        response = dmm.read()
        v_str = response.split(',')[3]
        v = float(v_str)
    except (IndexError, ValueError) as e:
        print(f"Error parsing voltage: {e}")
        v = 0.0

    t_data.append(t_now)
    v_data.append(v)

    print(f"Time: {t_now:.3f} s, Voltage: {v:.3f} V")

    if t_now >= max_time or v >= 0.99 * v_target:
        break

    line.set_xdata(t_data)
    line.set_ydata(v_data)
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)

    time.sleep(interval)

# CSV保存
with open('5.1.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Time (s)', 'Voltage (V)'])
    for t, v in zip(t_data, v_data):
        writer.writerow([t, v])

# 終了処理
dmm.close()
psu.close()
rm.close()

plt.ioff()
plt.show()
