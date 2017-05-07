#!/usr/bin/env python3

import numpy, time, visa

rm = visa.ResourceManager()
print(rm.list_resources())
scope = rm.open_resource("USB0::0x0699::0x0368::C013793::INSTR")
psu = rm.open_resource("ASRL4::INSTR", read_termination="\n")
scope.timeout = 25000
psu.timeout = 25000

print("Scope is:", scope.query("*IDN?"))
#print("PSU is:", psu.query("*IDN?"))

scope.write("HEAD OFF") # Headers off in returned data
scope.write("HOR:MAI:SCA 5e-5") # Horizontal scale: 5e-5 s/div
scope.write("CH1:SCA 1") # Vertical scale: 1 V/div
scope.write("CH1:CURRENTPRO 1") # Probe scaling: 1

scope.write("DAT:ENC ASCI") # Return ASCII from the scope
scope.write("DAT:SOU CH1") # We want to measure CH1
scope.write("DAT:WID 2") # 16-bit resolution

# Collect 2500 points per reading
scope.write("DAT:STAR 1")
scope.write("DAT:STOP 2500")

yScale = float(scope.query("WFMP:YMU?"))
for voltage in numpy.linspace(0, 5, 51):
    psu.write("VSET1:{:.1f}".format(voltage))
    time.sleep(1)
    data = yScale * numpy.fromstring(scope.query("CURV?"), sep=",", dtype=float)
    print("{:.1f}".format(voltage), numpy.mean(data), numpy.std(data), sep="\t")
