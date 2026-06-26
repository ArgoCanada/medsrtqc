
import pandas as pd
import numpy as np
import gsw

from medsrtqc.resources import resource_path
from medsrtqc.core import Trace
from medsrtqc.qc.operation import QCOperation, QCOperationError
from medsrtqc.qc.flag import Flag
from medsrtqc.qc.history import QCx
from medsrtqc.coefficient import coeff

class chlaTest(QCOperation):

    def run_impl(self):

        self.profile['FLU1'].adjusted.mask = False
        chla = self.profile['FLU1']
        fluo = self.profile['FLU3']
        adjusted = self.profile['FLUA']

        all_passed = True

        self.chla_info = self.get_chla_info()

        dark_chla = coeff[f'{self.profile.wmo}']['DARK_CHLA']
        scale_chla = coeff[f'{self.profile.wmo}']['SCALE_CHLA']

        self.log('Setting previously unset flags for CHLA to GOOD')
        Flag.update_safely(chla.qc, to=Flag.GOOD)

        self.log('Setting previously unset flags for CHLA_ADJUSTED to GOOD')
        Flag.update_safely(adjusted.qc, to=Flag.GOOD)

        # global range test
        self.log('Applying global range test to CHLA')
        values_outside_range = (chla.value < -0.1) | (chla.value > 50.0)
        Flag.update_safely(chla.qc, Flag.BAD, values_outside_range)
        Flag.update_safely(adjusted.qc, Flag.BAD, values_outside_range)
        QCx.update_safely(self.profile.qc_tests, 6, not any(values_outside_range))
        all_passed = all_passed and not any(values_outside_range)

        # the mixed layer depth calculation can fail
        mixed_layer_depth = None
        flag_mld = True
        try:
            mixed_layer_depth = self.mixed_layer_depth()
            flag_mld = False
        except QCOperationError as e: # pragma: no cover
            self.log(e)

        if mixed_layer_depth is not None:
            self.log(f'Mixed layer depth calculated ({mixed_layer_depth} dbar)')
        
        # check if float_dark_chla is available yet
        if self.chla_info is not None and self.chla_info.FLOAT_DARK_CHLA.notna().any():
            float_dark_chla = self.chla_info.loc[self.chla_info.FLOAT_DARK_CHLA.notna(), 'FLOAT_DARK_CHLA'].iloc[-1]
            if self.chla_info.loc[self.chla_info.FLOAT_DARK_CHLA.notna(), 'FLOAT_DARK_CHLA'].unique().shape[0] > 1:
                raise ValueError('Multiple FLOAT_DARK_CHLA found - only one value should be present')
            prelim_dark_chla = self.chla_info.PRELIM_DARK_CHLA
            idark_chla = None
        else:
            float_dark_chla = None
            float_dark_chla_qc = None
            
            # minimum depth test
            deeper_than_950 = any(chla.pres > 950)

            # determine idark_chla
            if deeper_than_950:
                idark_chla = np.nanmin(self.running_median(fluo.value[fluo.pres > 5], 5))
            else:
                idark_chla = None
            idark_chla = None if np.isnan(idark_chla) else idark_chla

            # check if any prelim_dark_chla available
            if self.chla_info is not None and self.chla_info.PRELIM_DARK_CHLA.notna().any():
                prelim_dark_chla = self.chla_info.PRELIM_DARK_CHLA
            else:
                prelim_dark_chla = None

            # differing cases based availability of idark_chla and prelim_dark_chla
            if idark_chla is None and prelim_dark_chla is None:
                dark_prime_chla = dark_chla
                # fluo adjusted should be updated too, but no variable for that
                Flag.update_safely(adjusted.qc, Flag.PROBABLY_GOOD)
            elif idark_chla is not None and prelim_dark_chla is None:
                dark_prime_chla = idark_chla
                prelim_dark_chla = pd.Series([idark_chla])
                # fluo adjusted should be updated too, but no variable for that
                Flag.update_safely(adjusted.qc, Flag.PROBABLY_GOOD)
            elif idark_chla is None and prelim_dark_chla is not None:
                dark_prime_chla = prelim_dark_chla.median()
                # fluo adjusted should be updated too, but no variable for that
                Flag.update_safely(adjusted.qc, Flag.PROBABLY_GOOD)
            elif idark_chla is not None and prelim_dark_chla is not None:
                prelim_dark_chla = pd.concat([prelim_dark_chla, pd.Series(idark_chla)])
                if prelim_dark_chla.notna().sum() >= 5:
                    dark_prime_chla = prelim_dark_chla.median()
                    float_dark_chla = dark_prime_chla
                else:
                    # fluo adjusted should be updated too, but no variable for that
                    dark_prime_chla = prelim_dark_chla.median()
                    Flag.update_safely(adjusted.qc, Flag.PROBABLY_GOOD)

        if float_dark_chla is not None:
            near_factory_value = np.abs(float_dark_chla - dark_chla) < 0.25*dark_chla
            all_passed = all_passed and near_factory_value
            if near_factory_value:
                float_dark_chla_qc = 1
                Flag.update_safely(adjusted.qc, Flag.GOOD)
                self.log(f'float_dark_chla value ({float_dark_chla}) within reasonable range of factory dark value ({dark_chla}), setting QC=1')
            else:
                float_dark_chla_qc = 3
                self.log(f'float_dark_chla value ({float_dark_chla}) outside of reasonable range of factory dark value ({dark_chla}), setting QC=3')
                Flag.update_safely(adjusted.qc, Flag.PROBABLY_BAD)

        physio_ratio = self.get_rt_slope()
        self.sci_calib_flag = 'physio'
        if np.isnan(physio_ratio):
            self.log('Invalid position and/or slope, checking for previous value')
            self.log_chla = False
            physio_ratio = None
            if self.chla_info is not None:
                if self.chla_info.loc[:self.profile.cycle_number, 'PHYSIOLOGICAL_RATIO'].notna().any():
                    sub = self.chla_info.loc[(self.chla_info.PHYSIOLOGICAL_RATIO.notna()) & (self.chla_info.CYCLE < self.profile.cycle_number)]
                    physio_ratio = sub.loc[sub.index.max(), 'PHYSIOLOGICAL_RATIO']
                    self.log(f'Using last valid physiological scale factor from cycle {sub.CYCLE.max()}: {physio_ratio}')
                    self.sci_calib_flag = 'previous'
            else:
                self.log('No previous valid value found, falling back to 2 from Roesler et al. 2017')
                self.sci_calib_flag = 'roesler'
        else:
            self.log(f'Physiological scale found near position ({self.profile.longitude:.2f}, {self.profile.latitude:.2f}): {physio_ratio}')
            
        dark_count_adjusted = dark_prime_chla if float_dark_chla is None else float_dark_chla
        dark_prime_chla = dark_prime_chla if float_dark_chla is None else None
        adj_scale = physio_ratio if physio_ratio is not None else 2
        print(self.sci_calib_flag, adj_scale)
        adjusted = Trace(
            pres=adjusted.pres, 
            value=self.convert(dark_count_adjusted, scale_chla)/adj_scale,
            qc=adjusted.qc,
            mtime=adjusted.mtime
        )

        # CHLA spike test
        self.log('Performing negative spike test on CHLA')
        median_chla = self.running_median(chla.value, 5)
        res = chla.value - median_chla
        spike_values = res < 2*np.percentile(res, 10)

        Flag.update_safely(chla.qc, Flag.BAD, spike_values)
        Flag.update_safely(adjusted.qc, Flag.BAD, spike_values)
        all_passed = all_passed and not any(spike_values)
        QCx.update_safely(self.profile.qc_tests, 9, not any(spike_values))

        # stuck value test
        self.log('Performing stuck value test on CHLA')
        stuck_value = all(chla.value == chla.value[0])
        if stuck_value: # pragma: no cover
            self.log('stuck values found, setting all profile flags to 4 for both CHLA and CHLA_ADJUSTED')
            Flag.update_safely(chla.qc, Flag.BAD)
            Flag.update_safely(adjusted.qc, Flag.BAD)
        QCx.update_safely(self.profile.qc_tests, 13, not stuck_value)
        
        # CHLA NPQ correction
        self.log('Performing Non-Photochemical Quenching (NPQ) test')
        chla_npq = None
        zmax_fluo = None
        if not flag_mld:
            positive_spikes = res > 2*np.percentile(res, 90)
            depthNPQ_ix = np.where(median_chla[~positive_spikes] == np.nanmax(median_chla[~positive_spikes]))[0][0]
            depthNPQ = chla.pres[depthNPQ_ix]
            if depthNPQ < 0.9*mixed_layer_depth:
                self.log(f'Adjusting surface values (P < {depthNPQ}dbar) to CHLA({depthNPQ}) = {chla.value[depthNPQ_ix]}mg/m3')
                adjusted.value[:depthNPQ_ix] = chla.value[depthNPQ_ix]
                self.log('Setting values above this depth in CHLA_QC to PROBABLY_BAD, and in CHLA_ADJUSTED_QC to changed')
                Flag.update_safely(chla.qc, to=Flag.PROBABLY_BAD, where=chla.pres < depthNPQ)
                Flag.update_safely(adjusted.qc, to=Flag.CHANGED, where=chla.pres < depthNPQ)
                all_passed = False
                chla_npq = chla.value[depthNPQ_ix]
                zmax_fluo = depthNPQ
        
        # update QCP/QCF
        QCx.update_safely(self.profile.qc_tests, 63, all_passed)

        print(prelim_dark_chla)

        self.scientific_calib_coefficient = {
            'CHLA_NPQ':chla_npq,
            'ZMaxFluo':zmax_fluo,
            'PRELIM_DARK_CHLA':prelim_dark_chla.loc[prelim_dark_chla.notna()].astype(int).tolist() if prelim_dark_chla is not None else prelim_dark_chla,
            'iDARK_CHLA':int(idark_chla) if idark_chla is not None else idark_chla,
            'FLOAT_DARK_CHLA':int(float_dark_chla) if float_dark_chla is not None else float_dark_chla,
            'FLOAT_DARK_CHLA_QC':int(float_dark_chla_qc) if float_dark_chla_qc is not None else float_dark_chla_qc,
            'SCALE_CHLA':scale_chla,
            'PHYSIO_RATIO':physio_ratio,
        }

        self.write_chla_log()

        # update the CHLA trace
        self.update_trace('FLU1', chla)
        self.update_trace('FLUA', adjusted)

        return chla

    def mixed_layer_depth(self):
        self.log('Calculating mixed layer depth')
        pres = self.profile['PRES']
        temp = self.profile['TEMP']
        psal = self.profile['PSAL']
        if np.any(pres.value != temp.pres) or np.any(pres.value != psal.pres):
            self.error('PRES, TEMP, and PSAL are not aligned along the same pressure axis')

        # the longitude isn't actually important here because we're calculating relative
        # density in the same location
        longitude = 0
        latitude = 0
        abs_salinity = gsw.SA_from_SP(psal.value, pres.value, longitude, latitude)
        conservative_temp = gsw.CT_from_t(abs_salinity, temp.value, pres.value)
        density = gsw.sigma0(abs_salinity, conservative_temp)

        mixed_layer_start = (np.abs(np.diff(density)) > 0.03) & (pres.value[1:] > 10)
        if not np.any(mixed_layer_start): # pragma: no cover
            self.error("Can't determine mixed layer depth (no density changes > 0.03 below 10 dbar)")

        mixed_layer_depth = np.nanmin(pres.value[1:][mixed_layer_start])
        self.log(f'...mixed layer depth found at {mixed_layer_depth} dbar')

        return mixed_layer_depth

    def convert(self, dark, scale):
        fluo = self.profile['FLU3']

        return (fluo.value - dark) * scale

    def running_median(self, x, n):
        self.log(f'Calculating running median over window size {n}')
        ix = np.arange(n) + np.arange(len(x)-n+1)[:,None]
        b = [row[row > 0] for row in x[ix]]
        k = int(n/2)
        med = [np.median(c) for c in b]
        med = np.array(k*[np.nan] + med + k*[np.nan])
        return med

    def read_physio_meta(self):

        fn = resource_path('fluo_to_chl_physiological_ratio_LUT.csv')
        with open(fn) as fid:
            meta = {line.split(':')[0]:line.split(':')[1].strip().strip('"') for line in [fid.readline() for i in range(26)]}
        
        return meta
    
    def get_rt_slope(self):

        lon = self.profile.longitude
        lat = self.profile.latitude

        if np.isnan(lon) or np.isnan(lat):
            self.log('No valid position found, returning nan')
            return np.nan
        else:
            slope = pd.read_csv(resource_path('fluo_to_chl_physiological_ratio_LUT.csv'), skiprows=27)
            index = ((slope.longitude - lon)**2 + (slope.latitude - lat)**2).idxmin()
            return slope.loc[index].fluorescence_chlorophyll_ratio
    
    def write_chla_log(self):

        sci_calib_coeff = ''
        for key, item in self.scientific_calib_coefficient.items():
            if item is not None and key != 'iDARK_CHLA':
                if key in ['CHLA_NPQ', 'SCALE_CHLA', 'PHYSIO_RATIO']:
                    sci_calib_coeff += f'{key}={item:.4f}, '
                elif key == 'ZMaxFluo':
                    sci_calib_coeff += f'{key}={item:.1f}, '
                else:
                    sci_calib_coeff += f'{key}={item}, '

        sci_calib_coeff = sci_calib_coeff[:-2]

        for key, item in self.scientific_calib_coefficient.items():
            if item is None:
                self.scientific_calib_coefficient[key] = ''

        fn = resource_path('CHLA_netCDF_info.csv')
        with open(fn, 'a') as fid:
            fid.write(f'{self.profile.wmo},{self.profile.cycle_number},{self.profile.direction},')
            fid.write(f'{self.scientific_calib_coefficient["iDARK_CHLA"]},{self.scientific_calib_coefficient["FLOAT_DARK_CHLA"]},')
            fid.write(f'{self.scientific_calib_coefficient["FLOAT_DARK_CHLA_QC"]},{self.scientific_calib_coefficient["PHYSIO_RATIO"]},')
            fid.write(f'"{sci_calib_coeff}"\n')

    def get_chla_info(self):

        fn = resource_path('CHLA_netCDF_info.csv')
        df = pd.read_csv(fn)
        df = df.loc[df.DIRECTION == 'A']

        if df.WMO.isin([self.profile.wmo]).any():
            df = df.set_index(['WMO', 'CYCLE'])
            return df.loc[self.profile.wmo]
        else:
            self.log(f'No previous entries for float {self.profile.wmo} in {fn}.')
            return None
