
import numpy as np

from medsrtqc.qc.operation import QCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.qc.history import QCx

class bbpTest(QCOperation):

    def run_impl(self):
        bbp = self.profile['BBP$']
        all_passed = True

        self.log('Setting previously unset flags for BBP to GOOD')
        Flag.update_safely(bbp.qc, to=Flag.GOOD)

        new_tests = True
        # dall'olmo paper tests
        if new_tests:
            
            # missing data test
            self.log('Performing missing data test')
            bins = [0, 50, 156, 261, 367, 472, 578, 683, 789, 894, 1000]
            hist, bins = np.histogram(bbp.pres, bins=bins)
            new_flag = Flag.PROBABLY_BAD if sum(hist == 0) > 1 else Flag.GOOD
            new_flag = Flag.BAD if sum(hist != 0) == 1 else new_flag
            new_flag = Flag.MISSING if all(hist == 0) else new_flag
            all_passed = all_passed and not any(hist == 0)
            Flag.update_safely(bbp.qc, new_flag)
            self.log(f'Missing data test results: flags set to {new_flag.decode()}')

            # high deep value test
            self.log('Performing high deep value')
            median_bbp = self.running_median(5)
            high_deep_value = (sum(bbp.pres > 700) > 5) & (np.nanmedian(median_bbp[bbp.pres > 700]) > 5e-4)
            new_flag = Flag.PROBABLY_BAD if high_deep_value else Flag.GOOD
            all_passed = all_passed and not high_deep_value
            Flag.update_safely(bbp.qc, new_flag)
            self.log(f'High deep value test results: flags set to {new_flag.decode()}')

            # noisy profile test
            self.log('Performing noisy profile test')
            deep_ix = bbp.pres > 100
            residual = bbp.value - median_bbp
            high_residuals = residual > 0.0005
            high_residuals = high_residuals[deep_ix]
            pct_residuals = 100*sum(high_residuals)/len(high_residuals)
            many_high_residuals = pct_residuals > 10
            new_flag = Flag.PROBABLY_BAD if many_high_residuals else Flag.GOOD
            all_passed = all_passed and not many_high_residuals
            Flag.update_safely(bbp.qc, new_flag)
            self.log(f'Noisy profile test results: flags set to {new_flag.decode()}')

            # negative bbp test
            self.log('Performing negative bbp test')
            shallow_and_negative = (bbp.pres < 5) & (bbp.value < 0)
            if any(shallow_and_negative): # pragma: no cover
                self.log(f'Negative bbp test results: shallow negative flags set to {Flag.BAD.decode()}')
            Flag.update_safely(bbp.qc, Flag.BAD, where=shallow_and_negative)
            deep_and_negative = (bbp.pres > 5) & (bbp.value < 0)
            pct_negative = 100*sum(deep_and_negative)/len(deep_and_negative)
            many_negative = pct_negative > 10
            new_flag = Flag.PROBABLY_BAD if any(deep_and_negative) else Flag.GOOD
            new_flag = Flag.BAD if many_negative else new_flag
            all_passed = all_passed and not any(deep_and_negative)
            Flag.update_safely(bbp.qc, new_flag)
            self.log(f'Negative bbp test result: flags set to {new_flag.decode()}')

            # parking hook test
            ascending = self.profile.direction == 'A'
            if ascending:
                pres = bbp.pres
                pres[np.abs(pres) > 6000] = np.nan
                pres = np.sort(pres)
                deepest_diff = pres[-1] - pres[-2]
                if deepest_diff < 20:
                    parking_pres = 1000
                    parking_diff = np.abs(pres[-1] - parking_pres)
                    if parking_diff < 100:
                        self.log('Performing parking hook test')
                        ix = (bbp.pres < (pres[-1] - 20)) & (bbp.pres > (pres[-1] - 50))
                        baseline = np.median(bbp.value[ix]) + 0.0002
                        deep_above_baseline = (bbp.pres > (pres[-1] - 50)) & (bbp.value > baseline)
                        all_passed = all_passed and not any(deep_above_baseline)
                        Flag.update_safely(bbp.qc, Flag.BAD, where=deep_above_baseline)
                        self.log(f'Parking hook test results: {sum(deep_above_baseline)} points set to 4')
                    
        # # old tests - still run or no?

        # if 'B700' in self.profile.keys() or 'BBP700' in self.profile.keys():
        #     lower_lim = -0.000025
        # elif 'B532' in self.profile.keys() or 'BBP532' in self.profile.keys(): # pragma: no cover
        #     lower_lim = -0.000005
        # else: # pragma: no cover
        #     self.log(f'No valid wavelength information found, setting lower limit of range check to -0.000025')
        #     lower_lim = -0.000025

        # # global range test
        # self.log('Applying global range test to BBP')
        # values_outside_range = (bbp.value < lower_lim) | (bbp.value > 0.1)
        # Flag.update_safely(bbp.qc, Flag.PROBABLY_BAD, values_outside_range)
        # QCx.update_safely(self.profile.qc_tests, 6, not any(values_outside_range))
        # all_passed = all_passed and not any(values_outside_range)

        # # BBP spike test
        # self.log('Performing negative spike test')
        # median_bbp = self.running_median(5)
        # res = bbp.value - median_bbp
        # spike_values = res < 2*np.percentile(res, 10)
        # Flag.update_safely(bbp.qc, Flag.BAD, spike_values)
        # all_passed = all_passed and not any(spike_values)
        # QCx.update_safely(self.profile.qc_tests, 9, not any(spike_values))

        # # stuck value test
        # self.log('Performing stuck value test on bbp')
        # stuck_value = all(bbp.value == bbp.value[0])
        # if stuck_value: # pragma: no cover
        #     self.log('stuck values found, setting all profile flags to 4')
        #     Flag.update_safely(bbp.qc, Flag.BAD)
        # QCx.update_safely(self.profile.qc_tests, 13, not stuck_value)

        # update QCP/QCF
        QCx.update_safely(self.profile.qc_tests, 62, all_passed)

        # update trace
        self.update_trace('BBP$', bbp)

    def running_median(self, n):
        self.log(f'Calculating running median over window size {n}')
        x = self.profile['BBP$'].value
        ix = np.arange(n) + np.arange(len(x)-n+1)[:,None]
        b = [row[row > 0] for row in x[ix]]
        k = int(n/2)
        med = [np.median(c) for c in b]
        med = np.array(k*[np.nan] + med + k*[np.nan])
        return med

