#!/usr/bin/python

from pathlib import Path

import matplotlib.pyplot as plt

from medsrtqc.qc.bbp import bbpTest
from medsrtqc.nc import read_nc_profile
from medsrtqc.qc.check import preTestCheck

import pandas as pd
import seaborn as sns

def plot_profile_flags(nc, ax=None):
    if ax is None:
        fig, ax = plt.subplots()

    # put netcdf Profile into dataframe
    df = pd.DataFrame(dict(PRES=nc["BBP700"].pres, BBP700=nc["BBP700"].value, QC=nc["BBP700"].qc))

    # plot results
    g = sns.scatterplot(data=df, x="BBP700", y="PRES", hue="QC", ax=ax)

    return g

# example files
files = ["BD1901339_001.nc", "BD7900561_008.nc", "BD6901004_041.nc"]
# fig/axes to plot results
fig, axes = plt.subplots(1, 3, sharey=True)

check = preTestCheck()
bbp = bbpTest()

# loop through each profile
for fn, ax in zip(files, axes):
    nc = read_nc_profile("scripts/data/" + fn)
    tests = check.run(nc)

    nc.prepare(tests)

    bbp.run(nc)
    g = plot_profile_flags(nc, ax=ax)
