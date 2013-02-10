#!/usr/bin/env python

import sys
import numpy as np

labels = ["X1", "Y1", "FWHM1", "Flux1", "Back1", "Noise1", "SigXY1", "SNR1",
          "Strehl1", "X2", "Y2", "FWHM2", "Flux2", "Back2", "Noise2",
          "SigXY2", "SNR2", "Strehl2", "Sep", "Sig_Sep", "ExpTime"]

file = sys.argv[1]

outfile = file.split('.')[0] + ".stats"

date = file.split('.')[0].split('-')[0].split('_')[1]
time = file.split('.')[0].split('-')[1]

out = open(outfile, 'w')

data = np.loadtxt(file, unpack=True)

for i in range(len(data)):
    out.write("%10s  %10.3f \t %7.3f\n" % (labels[i],
                                            np.mean(data[i]),
                                            np.std(data[i])))
    file = labels[i] + ".dat"
    fp = open(file, 'a')
    fp.write("%s %s \t  %10.3f \t %7.3f\n" % (date,
                                              time,
                                              np.mean(data[i]),
                                              np.std(data[i])))
    fp.close()

f1 = data[3]
f2 = data[12]
scin1 = ((f1 / f1.mean()) ** 2).mean() - 1
scin2 = ((f2 / f2.mean()) ** 2).mean() - 1
scin12 = ((f1 / f1.mean() - f2 / f2.mean()) ** 2).mean()

fp = open("Scin.dat", 'a')
fp.write("%s %s \t  %6.3f \t %6.3f \t %6.3f\n" % (date,
                                                  time,
                                                  scin1,
                                                  scin2,
                                                  scin12))
fp.close()
out.close()
