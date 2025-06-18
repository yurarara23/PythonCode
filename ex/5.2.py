import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import csv

rm = pyvisa.ResourceManager()

# デバイス接続
dmm = rm.open_resource('GPIB::9::INSTR')     # マルチメータ (VOAC7520H)
psu = rm.open_resource('COM12')              # 電源装置 (GPD-4303S)

# 初期設定
dmm.write(':MAIN:FUNC VOLT:DCV')
dmm.write('VOLT:DC:RANG:5')

psu.write('TRACK0')       # 独立モード
psu.write('VSET1:0')
psu.write('ISET1:0')
psu.write('OUT1')         # 出力ON
time.sleep(2)

# パラメータ
v_target = 1.0
i_limit = 0.3
t_max = 100
dt = 0.1

# リアルタイムプロット準備
plt.ion()
fig, ax = plt.subplots()
line_charge, = ax.plot([], [], 'o-', label='Charge')
line_discharge, = ax.plot([], [], 'x-', label='Discharge')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Voltage (V)')
ax.set_title('RC Charging and Discharging')
ax.legend()
ax.grid(True)

# 測定開始
psu.write(f'VSET1:{v_target}')
psu.write(f'ISET1:{i_limit}')
t_start = time.time()

t_charge = []
v_charge = []

while True:
    t_now = time.time() - t_start
    dmm.write(':MAIN:DATA?')
    try:
        v_str = dmm.read().split(',')[3]
        v = float(v_str)
    except Exception as e:
        print(f"[充電] 取得失敗: {e}")
        v = 0.0

    t_charge.append(t_now)
    v_charge.append(v)
    print(f"[充電] t = {t_now:.2f}s, V = {v:.3f}V")

    # 終了条件
    if t_now >= t_max or v >= 0.99 * v_target:
        break

    # グラフ更新
    line_charge.set_data(t_charge, v_charge)
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)
    time.sleep(dt)

# 放電フェーズ
print("放電開始")
psu.write('OUT0')
time.sleep(0.5)

t_discharge = []
v_discharge = []
t_start_d = time.time()

while True:
    t_now = time.time() - t_start_d
    dmm.write(':MAIN:DATA?')
    try:
        v_str = dmm.read().split(',')[3]
        v = float(v_str)
    except Exception as e:
        print(f"[放電] 取得失敗: {e}")
        v = 0.0

    t_discharge.append(t_now + t_charge[-1])
    v_discharge.append(v)
    print(f"[放電] t = {t_now:.2f}s, V = {v:.3f}V")

    if t_now >= t_max or v <= 0.01:
        break

    line_discharge.set_data(t_discharge, v_discharge)
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)
    time.sleep(dt)

# 結果出力
with open('5.2.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Time (s)', 'Voltage (V)', 'Phase'])
    for t, v in zip(t_charge, v_charge):
        writer.writerow([t, v, 'Charge'])
    for t, v in zip(t_discharge, v_discharge):
        writer.writerow([t, v, 'Discharge'])

# 後始末
dmm.close()
psu.close()
rm.close()
plt.ioff()
plt.show()
