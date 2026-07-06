
import argopy

from pathlib import Path
import numpy as np
import pandas as pd

import bgcArgoDMQC as bgc

data_path = Path('/Users/GordonC/Documents/data/Argo/dac/meds/')

index = argopy.ArgoIndex(index_file='bgc-b').load().to_dataframe()
index = index.loc[(index.dac == 'meds') & (index.parameters.str.contains('DOXY'))]

with open(Path('../medsrtqc/resources/median_doxy_gains_woa23.csv'), 'w') as fid:

    fid.write('wmo,gain,date\n')

    for flt in data_path.glob('*'):
        sprof_file = list(flt.glob('*sprof*.nc'))
        if len(sprof_file) > 0:
            wmo = int(flt.name)
            if wmo in index.wmo.values:
                sprof = bgc.sprof(wmo)
                if sprof.track.shape[0] > 1:
                    gains = sprof.calc_gains(ref='WOA')

                    fid.write(f'{wmo},{np.nanmedian(gains)},{pd.Timestamp("now").strftime("%Y-%m-%d")}\n')
