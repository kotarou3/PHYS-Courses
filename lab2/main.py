#!/usr/bin/env python3

import numpy, time, visa

rm = visa.ResourceManager()
print(rm.list_resources())
scope1 = rm.open_resource("USB0::0x0699::0x0368::C013933::INSTR")
scope2 = rm.open_resource("USB0::0x0699::0x0368::C013793::INSTR")

for scope in [scope1, scope2]:
    scope.write("HEAD OFF") # Headers off in returned data
    scope.write("HOR:MAI:SCA 25e-3") # Horizontal scale: 25 ms/div
    scope.write("CH1:SCA 2") # Vertical scale: 2 V/div
    scope.write("CH1:CURRENTPRO 1") # Probe scaling: 1
    scope.write("CH2:SCA 2") # Vertical scale: 2 V/div
    scope.write("CH2:CURRENTPRO 1") # Probe scaling: 1

    scope.write("DAT:ENC ASCI") # Return ASCII from the scope
    scope.write("DAT:SOU CH1") # We want to measure CH1
    scope.write("DAT:WID 2") # 16-bit resolution

    # Collect 2500 points per reading
    scope.write("DAT:STAR 1")
    scope.write("DAT:STOP 2500")

scope1.write("CH1:SCA 1") # Vertical scale: 1 V/div
scope1.write("TRIGger:MAIn:EDGE:SOUrce CH2")
scope2.write("TRIGger:MAIn:EDGE:SOUrce CH1")

yScale1 = float(scope1.query("WFMP:YMU?"))
yScale2 = float(scope2.query("WFMP:YMU?"))
time.sleep(1)

data1 = yScale1 * numpy.fromstring(scope1.query("CURV?"), sep=",", dtype=float)
data2 = yScale2 * numpy.fromstring(scope2.query("CURV?"), sep=",", dtype=float)
for pair in numpy.transpose([data1, data2]):
	print(pair[0], pair[1], sep="\t")