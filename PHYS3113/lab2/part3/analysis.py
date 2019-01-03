#!/usr/bin/env python3

import glob, numpy
from scipy.integrate import simps
from scipy.signal import savgol_filter
from matplotlib import pyplot

pyplot.rcParams["figure.figsize"] = (9, 5)

def analyse(tsv):
    # Read the data
    ch1, ch2 = numpy.loadtxt(tsv, delimiter = "\t", skiprows = 1, unpack = True)
    P = list(map(lambda v: v / 3.75e-5, ch1))
    V = list(map(lambda v: v / 417, ch2))

    # Smooth it
    smoothedP = savgol_filter(P, 101, 3)
    smoothedV = savgol_filter(V, 101, 3)

    # Truncate to a whole number of periods
    dP = numpy.gradient(smoothedP)
    for t in reversed(range(0, len(smoothedP) - 1)):
        if (smoothedP[t] - smoothedP[0]) * (smoothedP[t + 1] - smoothedP[0]) < 0 and dP[0] * dP[t] > 0:
            smoothedP = smoothedP[0:t + 1]
            smoothedV = smoothedV[0:t + 1]
            break
    halfPeriods = numpy.sum(numpy.abs(numpy.gradient(numpy.sign(savgol_filter(numpy.gradient(smoothedP), 101, 3))))) / 2
    assert(halfPeriods % 2 == 0)
    periods = halfPeriods / 2

    # Integrate the area
    PdV = simps(numpy.multiply(smoothedP, numpy.gradient(smoothedV))) / periods
    VdP = simps(numpy.multiply(smoothedV, numpy.gradient(smoothedP))) / periods
    print(tsv, PdV, PdV * 0.05, "mJ")

    pyplot.xlabel(r"$V \:(\mathrm{L})$")
    pyplot.ylabel(r"$P \:(\mathrm{Pa})$")
    pyplot.xlim((numpy.min(V), numpy.max(V)))
    pyplot.ylim((numpy.min(P), numpy.max(P)))
    pyplot.scatter(V, P, s = 0.1)
    pyplot.plot(smoothedV, smoothedP)
    pyplot.savefig(tsv.replace(".tsv", ".png"), dpi = 150)
    pyplot.clf()
    #pyplot.show()

for tsv in glob.iglob("*.tsv"):
    analyse(tsv)
