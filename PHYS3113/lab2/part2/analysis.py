#!/usr/bin/env python3

import glob, numpy

for tsv in glob.iglob("*.tsv"):
    V = numpy.loadtxt(tsv, delimiter = "\t", skiprows = 1, unpack = True)
    print(tsv, numpy.mean(V), 1.96 * numpy.std(V))
