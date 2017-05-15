#!/usr/bin/python3

import glob
import numpy
from scipy.signal import find_peaks_cwt, savgol_filter
from matplotlib import pyplot

pyplot.rcParams["figure.figsize"] = (9, 5)

def ch2keV(ch):
    return -2.17522 + 0.17746 * ch + 2.79139e-6 * ch**2

def analyse(tsv):
    # Read the data
    ch, counts = numpy.loadtxt(tsv, delimiter = "\t", skiprows = 3, unpack = True)

    # Smooth it
    smoothedCounts = savgol_filter(counts, 51, 3)

    # Find peaks
    """peaks = numpy.append(
        find_peaks_cwt(smoothedCounts, numpy.arange(20, 200)),
        find_peaks_cwt(smoothedCounts, numpy.arange(200, 400))
    )
    peaks = list(reversed(sorted(peaks, key = lambda peak: smoothedCounts[peak])))

    # Find FWHM
    print("\n{}".format(tsv))
    for peak in peaks:
        for c in reversed(range(0, peak)):
            if smoothedCounts[c] < smoothedCounts[peak] / 2:
                loHM = c
                break
        for c in range(peak, len(smoothedCounts)):
            if smoothedCounts[c] < smoothedCounts[peak] / 2:
                hiHM = c
                break
        print(ch2keV(peak), smoothedCounts[peak], ch2keV(hiHM) - ch2keV(loHM))"""

    # Plot
    pyplot.xlabel(r"$\mathrm{keV}$")
    pyplot.ylabel("Counts")
    pyplot.xlim((0, ch2keV(ch[-1])))
    pyplot.ylim((0, 1.1 * numpy.max(counts)))
    pyplot.scatter(list(map(ch2keV, ch)), counts, s = 0.1)
    pyplot.plot(list(map(ch2keV, ch)), smoothedCounts)
    #pyplot.vlines(list(map(ch2keV, peaks)), 0, numpy.max(counts))
    #pyplot.show()
    pyplot.savefig(tsv.replace(".tsv", ".png"), dpi = 150)
    pyplot.clf()

for tsv in glob.iglob("*0*.tsv"):
    analyse(tsv)
