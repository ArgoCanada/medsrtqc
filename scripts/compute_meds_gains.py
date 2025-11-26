
from pathlib import Path
import pandas as pd

import bgcArgoDMQC as bgc

data_path = Path('/Users/GordonC/Documents/data/Argo/dac/meds/')

with open(Path('../medsrtqc/resources/doxy_gains.csv'), 'w') as fid:

    fid.write('wmo,gain,date\n')

    for flt in data_path.glob('*'):
        sprof_file = list(flt.glob('*sprof*.nc'))[0]
        if sprof_file.exists():
            wmo = int(flt.name)
            try:
                sprof = bgc.sprof(wmo)
            except KeyError:
                print(f'Error loading float {wmo}')
            gains = sprof.calc_gains(ref='WOA')

            fid.write(f'{wmo},{sprof.gain},{pd.Timestamp('now').strftime('%Y-%m-%d')}\n')

            
