
import numpy as np
import gsw

from medsrtqc.resources import resource_path
from medsrtqc.core import Trace
from medsrtqc.qc.operation import QCOperation, QCOperationError
from medsrtqc.qc.flag import Flag
from medsrtqc.qc.history import QCx
from medsrtqc.coefficient import coeff

class ChlaTest(QCOperation):

    def run_impl(self):
        self.profile['FLU1'].adjusted.mask = False
        chla = self.profile['FLU1']
        fluo = self.profile['FLU3']
        adjusted = self.profile['FLUA']

        all_passed = True

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

        # dark count test
        self.log('Checking for previous DARK_CHLA')
        # get previous dark count here
        last_dark_chla = self.read_last_dark_chla()

        self.log('Testing if factory calibration matches last good dark count')
        # test 1
        if dark_chla != last_dark_chla:
            self.log('LAST_DARK_CHLA does not match factory DARK_CHLA, flagging CHLA as PROBABLY_BAD')
            Flag.update_safely(chla.qc, to=Flag.PROBABLY_BAD)
            all_passed = False
        else: # pragma: no cover
            self.log('LAST_DARK_CHLA and DARK_CHLA match, leaving CHLA_QC flags as GOOD')

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
        
        # constants for mixed layer test
        delta_depth = 200
        delta_dark = 50

        # maximum pressure reached on this profile
        max_pres = np.nanmax(chla.pres)

        # I find the QC manual unclear on what to do here, should check with perhaps Catherine Schmechtig on how to process w/ no MLD
        if flag_mld: # pragma: no cover
        # test 2
            self.log('No mixed layer found, setting DARK_PRIME_CHLA to LAST_DARK_CHLA, CHLA_QC to PROBABLY_GOOD, and CHLA_ADJUSTED_QC to PROBABLY_GOOD')
            dark_prime_chla = last_dark_chla
            Flag.update_safely(chla.qc, to=Flag.PROBABLY_GOOD)
            Flag.update_safely(adjusted.qc, to=Flag.PROBABLY_GOOD)
        elif max_pres < mixed_layer_depth + delta_depth + delta_dark:
            self.log('Max pressure is insufficiently deep, setting DARK_PRIME_CHLA to LAST_DARK_CHLA, CHLA_QC to PROBABLY_GOOD, and CHLA_ADJUSTED_QC to PROBABLY_GOOD')
            dark_prime_chla = last_dark_chla
            Flag.update_safely(chla.qc, to=Flag.PROBABLY_GOOD)
            Flag.update_safely(adjusted.qc, to=Flag.PROBABLY_GOOD)
        else:
            dark_prime_chla = np.nanmedian(fluo.value[fluo.pres > (max_pres - delta_dark)])
    
        # test 3
        if np.abs(dark_prime_chla - dark_chla) > 0.2*dark_chla:
            self.log('DARK_PRIME_CHLA is more than 20%% different than last good calibration, reverting to LAST_DARK_CHLA and setting CHLA_QC to PROBABLY_BAD, CHLA_ADJUSTED_QC to PROBABLY_BAD')
            dark_prime_chla = last_dark_chla
            Flag.update_safely(chla.qc, to=Flag.PROBABLY_BAD)
            Flag.update_safely(adjusted.qc, to=Flag.PROBABLY_BAD)
            all_passed = False
        else:
            # test 4
            if dark_prime_chla != last_dark_chla:
                self.log('New DARK_CHLA value found, setting CHLA_QC to PROBABLY_BAD, CHLA_ADJUSTED_QC to GOOD, and updating LAST_DARK_CHLA')
                last_dark_chla = dark_prime_chla
                Flag.update_safely(chla.qc, to=Flag.PROBABLY_BAD)
                Flag.update_safely(adjusted.qc, to=Flag.GOOD)
                all_passed = False

        self.save_last_dark_chla(int(last_dark_chla))

        adjusted = Trace(
            pres=adjusted.pres, 
            value=self.convert(dark_prime_chla, scale_chla)/2, # Roesler et al. 2017 factor of 2 global bias
            qc=adjusted.qc,
            mtime=adjusted.mtime
        )

        # CHLA spike test
        self.log('Performing negative spike test on CHLA')
        median_chla = self.running_median(5)
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
        if not flag_mld:
            positive_spikes = res > 2*np.percentile(res, 90)
            depthNPQ_ix = np.where(median_chla[~positive_spikes] == np.nanmax(median_chla[~positive_spikes]))[0][0]
            depthNPQ = chla.pres[depthNPQ_ix]
            if depthNPQ < 0.9*mixed_layer_depth:
                self.log(f'Adjusting surface values (P < {depthNPQ}dbar) to CHLA({depthNPQ}) = {chla.value[depthNPQ_ix]}mg/m3')
                chla.adjusted[:depthNPQ_ix] = chla.adjusted[depthNPQ_ix]
                self.log('Setting values above this depth in CHLA_QC to PROBABLY_BAD, and in CHLA_ADJUSTED_QC to changed')
                Flag.update_safely(chla.qc, to=Flag.PROBABLY_BAD, where=chla.pres < depthNPQ)
                Flag.update_safely(adjusted.qc, to=Flag.CHANGED, where=chla.pres < depthNPQ)
                all_passed = False
        
        # update QCP/QCF
        QCx.update_safely(self.profile.qc_tests, 63, all_passed)

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

    def running_median(self, n):
        self.log(f'Calculating running median over window size {n}')
        x = self.profile['FLU1'].value
        ix = np.arange(n) + np.arange(len(x)-n+1)[:,None]
        b = [row[row > 0] for row in x[ix]]
        k = int(n/2)
        med = [np.median(c) for c in b]
        med = np.array(k*[np.nan] + med + k*[np.nan])
        return med

    def read_last_dark_chla(self):

        with open(resource_path('last_dark_chla.csv'), 'r') as fid:
            fid.readline()
            wmo = []
            cyc = []
            ldc = []
            for line in fid:
                line_list = [int(s.strip()) for s in line.split(',')]
                wmo.append(line_list[0])
                cyc.append(line_list[1])
                ldc.append(line_list[2])

            wmo = np.array(wmo)
            cyc = np.array(cyc)
            ldc = np.array(ldc)

            if self.profile.wmo not in wmo:
                self.log(f'No LAST_DARK_CHLA found for WMO {self.profile.wmo}. Writing manufacturer value to cycle 0 and continuing.')
                self.save_last_dark_chla(int(coeff[f'{self.profile.wmo}']['DARK_CHLA']), cycle=0)
                return coeff[f'{self.profile.wmo}']['DARK_CHLA']
            else:
                ix = np.where((wmo == self.profile.wmo) & (cyc == np.nanmax(cyc[(wmo == self.profile.wmo) & (cyc <= self.profile.cycle_number)])))[0][0]
                return ldc[ix]

    def save_last_dark_chla(self, v, cycle=None):

        cycle = self.profile.cycle_number if cycle is None else cycle

        with open(resource_path('last_dark_chla.csv'), 'a') as fid:
            fid.write(f'{self.profile.wmo:d},{cycle:d},{v:d}\n')
