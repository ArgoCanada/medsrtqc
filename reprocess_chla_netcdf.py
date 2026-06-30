
from pathlib import Path

from medsrtqc.core import Profile, Trace
from medsrtqc.qc.chla import chlaTest
from medsrtqc.nc import read_nc_profile

import bgcArgoDMQC as bgc

local_data = Path('data/chla_reprocess/meds')
for wmo_path in local_data.iterdir():
    print(wmo_path)

    for fn in (wmo_path / 'profiles').glob('B*.nc'):
        print(fn)
        prof = read_nc_profile(fn)
        break