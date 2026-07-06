
import sys
from pathlib import Path

from netCDF4 import Dataset
import pandas as pd
import numpy as np

from medsrtqc.qc.chla import chlaTest
from medsrtqc.nc import read_nc_profile

import bgcArgoDMQC as bgc

local_data = Path('data/chla_reprocess/dac/meds')
for wmo_path in local_data.iterdir():
    print(wmo_path)
    if int(wmo_path.name) < 4902688:
        continue

    for fn in (wmo_path / 'profiles').glob('B*.nc'):
        print(fn)
        wmo, cycdir = fn.name.split('_')
        wmo = int(wmo.strip('BRD'))
        cyc = int(cycdir.strip('D.nc'))
        drt = 'D' if cycdir.split('.')[0][-1] == 'D' else 'A'
        meta = pd.read_csv('medsrtqc/resources/CHLA_netCDF_info.csv').set_index(['WMO', 'CYCLE', 'DIRECTION'])
        missing = pd.read_csv('data/chla_reprocess/missing_chla.csv')
        if (wmo, cyc, drt) in meta.index or fn.as_posix() in missing.file.values:
            continue

        # load file in bgcArgoDMQC profile object
        bgcprof = bgc.prof(file=fn)

        if 'CHLA' not in bgcprof.df.columns:
            with open('data/chla_reprocess/missing_chla.csv', 'a') as fid:
                fid.write(fn.as_posix())
                fid.write('\n')
                continue

        # history fields
        history = {
            'INSTITUTION':'BI',
            'ACTION':'CV',
            'STEP':'ARGQ',
            'PARAMETER':'CHLA',
        }

        # extract dimensions
        nc = Dataset(fn.absolute())
        n_prof = nc.dimensions['N_PROF'].size
        n_levels = nc.dimensions['N_LEVELS'].size
        
        # reset all CHLA related flags
        bgcprof.update_field('CHLA_QC', -1)
        bgcprof.update_field('CHLA_ADJUSTED_QC', -1)

        # export to an edited file
        fn_e = bgcprof.update_file(history)

        fn_p = fn.parent / fn.name.strip('B')
        fn_p = fn.parent / fn.name.replace('R', 'D') if not fn_p.exists() else fn_p
        phys = read_nc_profile(fn_p)

        prof = read_nc_profile(fn_e, mode='r+')
        test = chlaTest()
        prof.prepare(tests=[test])

        prof.add_aux_data({
            'PRES':phys['PRES'],
            'TEMP':phys['TEMP'],
            'PSAL':phys['PSAL'],
        })
        
        test.run(prof)
        wmo, cycle, direction = prof.wmo, prof.cycle_number, prof.direction
        pres, chla_adj, flags = prof['CHLA_ADJUSTED'].pres, prof['CHLA_ADJUSTED'].value, prof['CHLA_ADJUSTED'].qc
        prof.close()

        meta = pd.read_csv('medsrtqc/resources/CHLA_netCDF_info.csv').set_index(['WMO', 'CYCLE', 'DIRECTION'])
        coeff = meta.loc[(wmo, cycle, direction), 'SCIENTIFIC_CALIB_COEFFICIENT']
        prelim_dark = meta.loc[(wmo, cycle, direction), 'PRELIM_DARK_COEFFICIENT']

        sci_calib = {
            'CHLA':{
                'COMMENT':'CHLA real time adjustment (specified in http://dx.doi.org/10.13155/35385 and computed with MLD_LIMIT = 0.03, and following recommendations of Sauzede et al., 2025 (https://doi.org/10.17882/105732))',
                'EQUATION':'CHLA_ADJUSTED = CHLA_NPQ for PRES in [0, ZMaxFluo ], CHLA_ADJUSTED = ((FLUORESCENCE_CHLA-MEDIAN(PRELIM_DARK_CHLA)*SCALE_CHLA)/PHYSIO_RATIO',
                'COEFFICIENT':coeff,
            },
            'FLUORESCENCE_CHLA':{
                'COMMENT':'FLUORESCENCE_CHLA real time adjustment (specified in http://dx.doi.org/10.13155/35385 and computed with MLD_LIMIT = 0.03)',
                'EQUATION':'FLUORESCENCE_CHLA_ADJUSTED = FLUORESCENCE_CHLA - MEDIAN(PRELIM_DARK_CHLA)',
                'COEFFICIENT':prelim_dark,
            }
        }

        nc = Dataset(fn_e, 'r+')
        nc = bgc.io.update_sci_calib(nc, sci_calib)
        nc.close()