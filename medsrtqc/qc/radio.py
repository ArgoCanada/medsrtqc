
import numpy as np

from medsrtqc.qc.operation import QCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.qc.history import QCx

class radiometryTest(QCOperation):

    def run_impl(self, rad=True, par=True):
        wavelength_keys = ['P380', 'P412', 'P443', 'P490']
        wavelength_lims = [
            (-1, 1.7),
            (-1, 2.9),
            (-1, 3.2),
            (-1, 3.4),
        ]
        range_test_pairs = {k:v for k, v in zip(wavelength_keys, wavelength_lims)}

        # irradiance tests
        all_passed = True
        for k, v in range_test_pairs.items():
            if k in self.profile.keys():
                rad_trace = self.profile[k]
                # global range test
                self.log(f'Applying global range test to {k}')
                values_outside_range = (rad_trace.value < v[0]) | (rad_trace.value > v[1])
                Flag.update_safely(rad_trace.qc, Flag.BAD, values_outside_range)
                QCx.update_safely(self.profile.qc_tests, 6, not any(values_outside_range))
                all_passed = all_passed and not any(values_outside_range)
                self.update_trace(k, rad_trace)
            QCx.update_safely(self.profile.qc_tests, 61, all_passed)

        # perform separately for PAR as it has its own test number
        if 'PAR$' in self.profile.keys():
            all_passed = True
            k = 'PAR$'
            v = (-1, 4672)
            rad_trace = self.profile[k]
            # global range test
            self.log(f'Applying global range test to {k}')
            values_outside_range = (rad_trace.value < v[0]) | (rad_trace.value > v[1])
            Flag.update_safely(rad_trace.qc, Flag.BAD, values_outside_range)
            QCx.update_safely(self.profile.qc_tests, 6, not any(values_outside_range))
            all_passed = all_passed and not any(values_outside_range)
            self.update_trace(k, rad_trace)
            QCx.update_safely(self.profile.qc_tests, 60, all_passed)