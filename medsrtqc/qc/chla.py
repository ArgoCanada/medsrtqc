
import numpy as np
import gsw

from .operation import QCOperation, QCOperationError
from .flag import Flag


class ChlaDarkTest(QCOperation):

    def run_impl(self):
        chla = self.profile['CHLA']

        self.log('Setting previously unset flags for CHLA to PROBABLY_BAD')
        Flag.update_safely(chla.qc, to=Flag.PROBABLY_BAD)

        self.log('Setting previously unset flags for CHLA_ADJUSTED to GOOD')
        Flag.update_safely(chla.adjusted_qc, to=Flag.GOOD)

        self.log('Applying global range test to CHLA')
        values_outside_range = (chla.value < -0.1) | (chla.value > 100.0)
        Flag.update_safely(chla.qc, Flag.BAD, values_outside_range)
        Flag.update_safely(chla.adjusted_qc, Flag.BAD, values_outside_range)

        # the DARK correction is not well-defined yet because it needs some
        # values from the NetCDF that aren't actually in any NetCDFs yet
        # these variables are FLOAT_DARK/FLOAT_DARK_QC (which may not exist)
        # and PRELIM_DARK (which stores the iDARK values until there are 5, at which
        # point the FLOAT_DARK/FLOAT_DARK_QC is calculated)
        self.log('Checking for previous FLOAT_DARK, FLOAT_DARK_QC, and PRELIM_DARK')

        # the mixed layer depth calculation can fail
        mixed_layer_depth = None
        try:
            mixed_layer_depth = self.mixed_layer_depth()
        except QCOperationError as e:
            self.log(e)

        if mixed_layer_depth is not None:
            self.log(f"Mixed layer depth calculated ({mixed_layer_depth} dbar)")

        # here is where we'd apply the non-photochemical quenching (NPC) correction

        # update the CHLA trace
        self.update_trace('CHLA', chla)

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

        with self.pyplot() as plt:
            plt.plot(density, pres.value)
            plt.gca().invert_yaxis()
            plt.gca().set_xlabel('sigma0')

        mixed_layer_start = (np.diff(density) > 0.03) & (pres.value[:-1] > 10)
        if not np.any(mixed_layer_start):
            self.error("Can't determine mixed layer depth (no density changes > 0.03 below 10 dbar)")

        mixed_layer_start_index = np.where(mixed_layer_start)[0][0]
        mixed_layer_depth = pres.value[mixed_layer_start_index]
        self.log(f'...mixed layer depth found at {mixed_layer_depth} dbar')

        with self.pyplot() as plt:
            plt.gca().axhline(y = mixed_layer_depth, linestyle='--')

        return mixed_layer_depth
