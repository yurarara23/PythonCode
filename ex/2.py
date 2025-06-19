import pyvisa
import time
import numpy as np

#WF1973
rm = pyvisa.ResourceManager()
fg_addr = "GPIB::2::INSTR"
fg = rm.open_resource(fg_addr)

# 初期設定
fg.write(":MAIN:FUNC SINE")
fg.write(":MAIN:VOLT 2.0")
fg.write(":MAIN:FREQ 100")
fg.write(":MAIN:OUTP ON")

time.sleep(5)

# 周波数スイープ（100 Hz ～ 100 kHz）
frequencies = np.logspace(2, 5, 16)  # 10^2 ～ 10^5 Hz

for f in frequencies:
    print(f"Setting frequency to {f:.1f} Hz")
    fg.write(f":FREQ {f}")
    time.sleep(10)  # 保持

# 終了処理
fg.write("OUTP OFF")
fg.close()
rm.close()
