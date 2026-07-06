
from pathlib import Path
from netCDF4 import Dataset

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import argopy
import bgcArgoDMQC as bgc

datadir = Path('../data/chla_reprocess/dac/meds/E/')
for floatdir in datadir.iterdir():
    for fn in (floatdir / 'profiles/').glob('B*'):

        if np.random.rand() < 0.1:
            bgcprof = bgc.prof(file=fn)
            fig, ax = plt.subplots()
            sns.scatterplot(data=bgcprof.df, x='CHLA', y='PRES', hue='CHLA_QC', ax=ax, hue_order=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1], palette=argopy.ArgoColors('qc_flag').palette)
            sns.scatterplot(data=bgcprof.df, x='CHLA_ADJUSTED', y='PRES', hue='CHLA_ADJUSTED_QC', ax=ax, hue_order=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1], palette=argopy.ArgoColors('qc_flag').palette)
            ax.set_ylim((2100, -100))

            nc = Dataset(fn)
            _, chla_index = bgc.io.find_param(nc, 'CHLA')
            print(bgc.io.read_ncstr(nc['SCIENTIFIC_CALIB_COMMENT'][0,-1,chla_index,:]))
            print(bgc.io.read_ncstr(nc['SCIENTIFIC_CALIB_EQUATION'][0,-1,chla_index,:]))
            print(bgc.io.read_ncstr(nc['SCIENTIFIC_CALIB_COEFFICIENT'][0,-1,chla_index,:]))
            print(bgc.io.read_ncstr(nc['CHLA_QC'][:].flatten()))
            print(bgc.io.read_ncstr(nc['CHLA_ADJUSTED_QC'][:].flatten()))

            print(bgcprof.df.CHLA / bgcprof.df.CHLA_ADJUSTED)

            nc.close()

            plt.show()

            break
    break