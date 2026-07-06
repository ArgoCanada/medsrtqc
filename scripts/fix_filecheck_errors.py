
from pathlib import Path
import sys
import copy
import pandas as pd
from netCDF4 import Dataset

wmo = 4902691
df = pd.read_csv(f'/Users/GordonC/Documents/projects/meds-dmqc/checker/summary/{wmo}/files.txt')

for fn in df.files:
    full_fn = Path(f'/Users/GordonC/Documents/projects/medsrtqc/data/chla_reprocess/dac/meds/E/{wmo}/profiles') / fn
    sys.stdout.write(f'Working on {full_fn}...')
    nc = Dataset(full_fn.absolute(), 'r+')
    for varname in ['CHLA']:
        flags = copy.deepcopy(nc[varname+'_QC'][:])
        flags[nc[varname][:].mask] = b'9'
        nc[varname+'_QC'][:] = flags
        flags = copy.deepcopy(nc[varname+'_ADJUSTED_QC'][:])
        flags[nc[varname][:].mask] = b'9'
        nc[varname+'_ADJUSTED_QC'][:] = flags
    profile = copy.deepcopy(nc['PROFILE_CHLA_QC'][:])
    profile[3] = b'A'
    nc['PROFILE_CHLA_QC'][:] = profile

    nc.close()
    sys.stdout.write('done\n')