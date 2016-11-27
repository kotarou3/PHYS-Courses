#!/usr/bin/python3

from multiprocessing import Pool
import numpy
from scipy.integrate import simps
from scipy.interpolate import splev, splprep
from scipy.optimize import brentq
from scipy.signal import detrend, savgol_filter
from matplotlib import pyplot

n_p = 584
n_s = 773
R_p = 2
R = 22e3
C = 9.39e-6
r = 50e-3
W = 2e-3
h = 30e-3
f = 50
k = n_p / (n_s * R_p)

def findRemanence(H, B):
    assert(len(H) == len(B))
    tck, u = splprep((H, B), s = 0)

    # Find intersections with H = 0 (B-axis)
    BIntercepts = []
    for a, b in zip(u, u[1:]):
        if splev(a, tck)[0] * splev(b, tck)[0] < 0:
            root = brentq(lambda u: splev(u, tck)[0], a, b)
            rootH, rootB = splev(root, tck)
            BIntercepts.append(rootB)
            #pyplot.plot(rootH, rootB, "go", markersize = 5)

    assert(len(BIntercepts) == 2)
    return abs(BIntercepts[1] - BIntercepts[0]) / 2

def analyse(n, withIntegrator):
    # Read the data
    n = "{:04d}".format(n)
    path = ("with" if withIntegrator else "without") + "-integrator"
    t, ch1 = numpy.loadtxt(path + "/ALL{0}/F{0}CH1.CSV".format(n), delimiter = ",", usecols = (3, 4), unpack = True)
    ch2 = numpy.loadtxt(path + "/ALL{0}/F{0}CH2.CSV".format(n), delimiter = ",", usecols = (4,))
    dt = t[1] - t[0]
    period = 1 / f / dt
    assert(len(t) == len(ch1) == len(ch2))
    assert(0.4999 < (period + 0.5) % 1 < 0.5001)
    period = int(round(period))

    # Smooth it
    smoothedCh1 = savgol_filter(ch1, 101, 3)
    smoothedCh2 = savgol_filter(ch2, 101, 3)

    if withIntegrator:
        # Extract one period from the middle
        start = (len(t) - period) // 2
        end = start + period
        t = t[start:end]
        ch1 = ch1[start:end]
        ch2 = ch2[start:end]
        smoothedCh1 = smoothedCh1[start:end]
        smoothedCh2 = smoothedCh2[start:end]

        # Print our results
        Vrms = numpy.sqrt(numpy.mean(numpy.square(smoothedCh1)))
        XdY = simps(numpy.multiply(smoothedCh1, numpy.gradient(smoothedCh2)))
        YdX = -simps(numpy.multiply(smoothedCh2, numpy.gradient(smoothedCh1)))
        Hmax = abs(numpy.ptp(smoothedCh1) / 2) * n_p / (2 * numpy.pi * r * R_p)
        Br = findRemanence(smoothedCh1, smoothedCh2) * R * C / (n_s * W * h)
        print("{:6.3f}\t{:8.5f}\t{:5.0f}\t{:6.4f}\t{}".format(Vrms, k * R * C * (XdY + YdX) / 2, Hmax, Br, n))

        # Save an image of the plot
        pyplot.xlabel(r"$V_X \:(\mathrm{V})$")
        pyplot.ylabel(r"$V_{Y1} \:(\mathrm{V})$")
        pyplot.plot(ch1, ch2, "b.", markersize = 0.5)
        pyplot.plot(smoothedCh1, smoothedCh2, "r")
    else:
        # Integrate channel 2
        ch2Int = [0] + [simps(ch2[:n], dx = dt) for n in range(1, len(ch2))]
        smoothedCh2Int = [0] + [simps(smoothedCh2[:n], dx = dt) for n in range(1, len(ch2))]

        # Extract one period from the middle
        start = (len(t) - period) // 2
        end = start + period
        t = t[start:end]
        ch1 = ch1[start:end]
        ch2 = ch2[start:end]
        ch2Int = ch2Int[start:end]
        smoothedCh1 = smoothedCh1[start:end]
        smoothedCh2 = smoothedCh2[start:end]
        smoothedCh2Int = smoothedCh2Int[start:end]

        # Remove DC offset from ch2Int
        ch2Int = detrend(ch2Int, type = "constant")
        smoothedCh2Int = detrend(smoothedCh2Int, type = "constant")

        # Print our results
        Vrms = numpy.sqrt(numpy.mean(numpy.square(smoothedCh1)))
        XYdt = simps(numpy.multiply(smoothedCh1, smoothedCh2), dx = dt)
        Hmax = abs(numpy.ptp(smoothedCh1) / 2) * n_p / (2 * numpy.pi * r * R_p)
        Br = findRemanence(smoothedCh1, smoothedCh2Int) / (n_s * W * h)
        print("{:6.3f}\t{:8.5f}\t{:5.0f}\t{:6.4f}\t{}*".format(Vrms, k * XYdt, Hmax, Br, n))

        # Save an image of the plot
        pyplot.xlabel(r"$V_X \:(\mathrm{V})$")
        pyplot.ylabel(r"$\int_0^t V_{Y2} \:\mathrm{d}t \:(\mathrm{V s})$")
        pyplot.plot(ch1, ch2Int, "b.", markersize = 0.5)
        pyplot.plot(smoothedCh1, smoothedCh2Int, "r")
    pyplot.savefig(path + "/{}.png".format(n), dpi = 150)
    pyplot.clf()

print("Vrms\tEPerCycle\tHmax\tBr\tsource")
with Pool() as p:
    for n in range(0, 40):
        p.apply_async(analyse, (n, False))
    for n in range(14, 66):
        p.apply_async(analyse, (n, True))
    p.close()
    p.join()
