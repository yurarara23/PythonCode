import pyvisa
import time
import numpy as np

rm = pyvisa.ResourceManager()
fg_addr = "GPIB::2::INSTR"
fg = rm.open_resource(fg_addr)

# 初期設定
fg.write("FUNC SIN")
fg.write("VOLT 2.0")
fg.write("FREQ 100")
fg.write("OUTP ON")

time.sleep(2)

# 周波数スイープ（100 Hz ～ 100 kHz）
frequencies = np.logspace(2, 5, 16)  # 10^2 ～ 10^5 Hz

for f in frequencies:
    print(f"Setting frequency to {f:.1f} Hz")
    fg.write(f"FREQ {f}")
    time.sleep(0.5)  # 安定化待ち（機器によって調整）

# 終了処理
fg.write("OUTP OFF")
fg.close()
rm.close()
