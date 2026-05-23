
from netCDF4 import Dataset
import pandas as pd

def get_rt_slope(lat, lon, ref):
    '''
    INPUTS:
        - lat: profile latitude
        - lon: profile longitude
        - ref: loaded netCDF object

    RETURNS:
        - slope: nearest physiological ratio to (lat, lon)
    '''

    # get nearest ratio, pandas maybe overkill here but easy
    ilat = pd.Series((ref['latitude'][:] - lat)**2).idxmin()
    ilon = pd.Series((ref['longitude'][:] - lon)**2).idxmin()
    
    return ref['fluorescence_chlorophyll_ratio'][ilat,ilon]

# load netcdf
ref = Dataset('fluo_to_chl_physiological_ratio_LUT.nc')

# hypothetical profile location
lat = 42.24
lon = -61.41

# get nearest ratio
ratio = get_rt_slope(lat, lon, ref)

# generate scientific calib comment
sci_calib_comment = f'{ref.source}. {ref.usage.split(":")[0].replace("a given (lat, lon)", f"({lat:.2f}, {lon:.2f}.)").replace("fluorescence_chlorophyll_ratio (latitude, longitude)", f"{ratio:.2f}")}.'
print(sci_calib_comment)