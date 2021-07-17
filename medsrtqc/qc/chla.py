
import numpy as np
import gsw

from .operation import QCOperation
from .flag import Flag


class ChlaDarkTest(QCOperation):

    def run_impl(self):
        # need chla
        chla = self.profile['CHLA']

        self.log('Setting initial flags to PROBABLY_BAD')
        Flag.update_safely(chla.qc, to=Flag.PROBABLY_BAD)

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

        # update the CHLA trace
        self.update_trace('CHLA', chla)
