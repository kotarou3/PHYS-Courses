#!/usr/bin/env python3

import glob

for file in glob.glob("measurements/XR-*-elements.txt"):
    lines = open(file).read().split("\n")[5:-3]
    elements = {}
    for line in lines:
        parts = line.split()
        element = parts[0]
        weight = float(parts[4])
        weightError = float(parts[6])
        count = float(parts[5])
        countError = weightError / weight * count

        elements[element] = ((weight, weightError), (count, countError))

    def format(name, value, error):
        if error < 1:
            return "{} \\SI{{{:.2f} \pm {:.2f}}}{{}}".format(name, value, error)
        elif error < 10:
            return "{} \\SI{{{:.1f} \pm {:.1f}}}{{}}".format(name, value, error)
        else:
            return "{} \\SI{{{:.0f} \pm {:.0f}}}{{}}".format(name, value, error)

    print("{} & ".format(file), end = "")
    """print(", ".join(map(
        lambda e: format(e[0], e[1][0][0], e[1][0][1]),
        sorted(elements.items(), key = lambda e: -e[1][0][0])
    )), end = "")
    print(" & ", end = "")"""
    print(", ".join(map(
        lambda e: format(e[0], e[1][1][0], e[1][1][1]),
        sorted(elements.items(), key = lambda e: -e[1][1][0])
    )), end = "")
    print(" \\\\")
