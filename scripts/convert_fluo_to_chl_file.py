
from pathlib import Path

import xarray as xr

resource_path = Path('../medsrtqc/resources')
file = resource_path / 'fluo_to_chl_physiological_ratio_LUT.nc'
ds = xr.open_dataset(file)

dest = Path(file.as_posix().replace('.nc', '.csv'))
ds.to_dataframe().to_csv(dest)

with open(dest, 'r') as fid:
    data = fid.read()

with open(dest, 'w') as fid:
    for name, att in ds.attrs.items():
        fid.write(f'{name}:"{att}"\n')
    fid.write('\n')
    fid.write(data)