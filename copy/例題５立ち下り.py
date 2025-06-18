import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import csv

# リソースマネージャの作成
rm = pyvisa.ResourceManager()

# マルチメータのGPIBアドレス
measurement_device_address = 'GPIB::9::INSTR'  # VOAC7520Hのアドレス
measurement_device = rm.open_resource(measurement_device_address)

# マルチメータの初期設定
measurement_device.write(':MAIN:FUNC VOLT:DCV')  # 直流電圧測定モード
measurement_device.write('VOLT:DC:RANG:5')  # レンジを5Vに設定

# GPD-4303sのアドレス
power_supply_resource = 'COM12'
power_supply = rm.open_resource(power_supply_resource)

# 電源装置の初期設定
power_supply.write('TRACK0')  # 独立モード
power_supply.write('VSET1:0')  # CH1の電圧を設定
power_supply.write('ISET1:0')  # CH1の電流を設定
power_supply.write('OUT1')  # 出力をON
time.sleep(10)  # 設定が適用されるまでの待機時間

# 計測データの保存用リスト
time_data = []
voltage_data = []

# 計測開始時間を記録
start_time = time.time()

# 計測パラメータ
max_time = 100  # 最大計測時間(秒)
measurement_interval = 0.1  # 計測間隔(秒)
supply_voltage = 1.0  # 電源電圧(V)

# グラフの初期設定
plt.ion()
fig, ax = plt.subplots()
line_charge, = ax.plot([], [], 'o-', label='Charge Voltage')  # 立ち上がり用のライン # 変更点
line_discharge, = ax.plot([], [], 'x-', label='Discharge Voltage')  # 立ち下がり用のライン # 変更点
ax.set_xlabel('Time (s)')
ax.set_ylabel('Voltage (V)')
ax.set_title('RC Time Constant Measurement')
ax.legend()  # 変更点（凡例表示）
ax.grid(True)

# 計測開始時の設定
power_supply.write('VSET1:1.0')  # CH1の電圧を1.0Vに設定
power_supply.write('ISET1:0.3')  # CH1の電流を0.3Aに設定

# 立ち上がり（充電）フェーズの測定
while True:
    current_time = time.time() - start_time  # 現在の経過時間を計算

    # マルチメータから電圧値を取得
    measurement_device.write(':MAIN:DATA?')  # 電圧値の取得コマンドを送信
    response = measurement_device.read()  # データを取得

    # 返されたデータから電圧値を抽出
    try:
        voltage_str = response.split(',')[3]
        voltage = float(voltage_str)
    except (IndexError, ValueError) as e:
        print(f"データの解析中にエラーが発生しました: {e}")
        voltage = 0.0

    # データをリストに保存
    time_data.append(current_time)
    voltage_data.append(voltage)

    # 進捗を表示
    print(f"時間: {current_time:.3f} s, 電圧: {voltage:.3f} V")

    # 終了条件のチェック
    if current_time >= max_time or voltage >= 0.99 * supply_voltage:
        break

    # グラフの更新
    line_charge.set_xdata(time_data)  # 変更点
    line_charge.set_ydata(voltage_data)  # 変更点
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)

    time.sleep(measurement_interval)

# 放電フェーズへ（出力OFF）
print("放電フェーズ開始")
power_supply.write('OUT0')  # 出力OFF
time.sleep(0.5)

# 放電データ用
discharge_time = []
discharge_voltage = []
start_discharge = time.time()

# 放電中の計測
while True:
    current_time = time.time() - start_discharge
    measurement_device.write(':MAIN:DATA?')
    response = measurement_device.read()

    try:
        voltage_str = response.split(',')[3]
        voltage = float(voltage_str)
    except (IndexError, ValueError) as e:
        print(f"データの解析中にエラー: {e}")
        voltage = 0.0

    discharge_time.append(current_time)
    discharge_voltage.append(voltage)

    print(f"[放電] 時間: {current_time:.3f}s, 電圧: {voltage:.3f}V")

    if current_time > max_time or voltage <= 0.01:
        break

    # グラフの更新（充電時間を加味してx軸を連続表示）
    total_discharge_time = [t + time_data[-1] for t in discharge_time]  

    line_discharge.set_xdata(total_discharge_time)  
    line_discharge.set_ydata(discharge_voltage)  
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)

    time.sleep(measurement_interval)

# CSVファイルで結果を出力
with open('例題5.2.csv', mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    if file.tell() == 0:  # ファイルが空であればヘッダーを書き込む
        writer.writerow(['Time (s)', 'Measured Voltage (V)'])
    for t, v in zip(time_data, voltage_data):
        writer.writerow([t, v])

    # 空行で区切り
    writer.writerow([])  # 変更点（空行挿入で見やすく）
    writer.writerow(['Time (s)', 'Voltage (V)'])
    for t, v in zip(discharge_time, discharge_voltage):
        writer.writerow([t, v])

# 計測器とファンクションジェネレータを解放
measurement_device.close()
power_supply.close()
rm.close()

# グラフの後処理
plt.ioff()
plt.show()