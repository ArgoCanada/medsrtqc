
import traceback

try:
    import pandas as pd
    from medsrtqc.resources import resource_path
    from netCDF4 import Dataset

    fn = resource_path('CHLA_netCDF_info.csv')
    pd.read_csv(fn)
except:
    with open("exceptions.log", "a") as logfile:
        traceback.print_exc(file=logfile)
    raise