import pyvisa
import time
import matplotlib.pyplot as plt
import numpy as np

rm = pyvisa.ResourceManager()
function_generator_address = "GPIB::2::INSTR"
function_generator = rm.open_resource(function_generator_address)

function_generator.write(':MAIN:FUNC SINE')
function_generator.write(':MAIN:VOLT 2.0')
function_generator.write(':MAIN:FREQ 100')
function_generator.write(':MAIN:OUTP ON')

time.sleep(5) 

frequencies = np.linspace(2, 5, 16)
voltage = []

for freq in frequencies:
    function_generator.write(f':FREQ {freq}')
    time.sleep(0.1)  

function_generator.close()
rm.close()
