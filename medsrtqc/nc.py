
from typing import Iterable
import urllib.request
import io
import os
import shutil
import reprlib
import numpy as np
from netCDF4 import Dataset, chartostring
from numpy.core.fromnumeric import var
from .core import Profile, Trace


class NetCDFProfile(Profile):
    """
    A :class:`medsrtqc.core.Profile` implementation backed by a
    ``netCDF4.Dataset`` representation of an Argo profile NetCDF file.
    The NetCDF file should be a single-profile NetCDF. These objects
    are normally created using :func:`read_nc_profile`.

    :param dataset: An existing ``netCDF4.Dataset``.
    """

    def __init__(self, *dataset):
        self._datasets = list(dataset)
        self._variables = None
        for dataset in self._datasets:
            self._variables = self._locate_variables(dataset, self._variables)
        
    def _locate_variables(self, dataset, all_params=None):
        param_array = chartostring(dataset['PARAMETER'][:])
        n_prof = len(dataset.dimensions['N_PROF'])

        if all_params is None:
            all_params = {}

        for i_prof in range(n_prof):
            for item in np.nditer(param_array[i_prof]):
                item_trim = str(item).strip()
                if item_trim and item_trim not in all_params:
                    all_params[item_trim] = (dataset, i_prof)
        
        return all_params
    
    def keys(self) -> Iterable[str]:
        if self._variables is not None:
            return self._variables.keys()
        else:
            return ()
    
    def __getitem__(self, k) -> Trace:
        dataset, i_prof = self._variables[k]

        var_names = {
            'value': k,
            'value_qc': k + '_QC',
            'adjusted': k + '_ADJUSTED',
            'adjusted_qc': k + '_ADJUSTED_QC',
            'adjusted_error': k + '_ADJUSTED_ERROR',
            'pres': 'PRES',
            'mtime': 'MTIME'
        }

        var_values = {}
        for trace_name, nc_key in var_names.items():
            if nc_key in dataset.variables:
                var_values[trace_name] = dataset[nc_key][i_prof]

        n_values = var_values['value'].shape[0]
        
        # don't include non value variables that are 100% mask
        for k in list(var_values.keys()):
            if k != 'value' and np.all(var_values[k].mask):
                del var_values[k]

        # don't include trailing fill values when all variables have a trailing fill
        if n_values:
            last_finite = []
            for v in var_values.values():
                if not np.any(v.mask):
                    last_finite.append(n_values)
                elif not np.all(v.mask):
                    last_finite.append(np.where(~v.mask)[0].max())
            
            if last_finite:
                for k in list(var_values.keys()):
                    var_values[k] = var_values[k][:max(last_finite)]

        return Trace(**var_values)


def _load_dataset(src):
    if not isinstance(src, (Dataset, bytes, str)):
        raise TypeError('`src` must be a filename, url, bytes, or netCDF4.Dataset object')

    if isinstance(src, Dataset):
        return src
    elif isinstance(src, str) and os.path.exists(src):
        return Dataset(src)
    elif isinstance(src, bytes):
        return Dataset('in-mem-file', mode='r', memory=src)
    elif src.startswith('http://') or src.startswith('https://') or src.startswith('ftp://'):
        buf = io.BytesIO()
        with urllib.request.urlopen(src) as f:
            shutil.copyfileobj(f, buf)
        return Dataset('in-mem-file', mode='r', memory=buf.getvalue())
    else:
        raise ValueError(f"Don't know how to open '{reprlib.repr(src)}'\n.Is it a valid file or URL?")


def read_nc_profile(*src):
    """
    Load a ``netCDF4.Dataset` from a filename, url, bytes, or existing
    ``netCDF4.Dataset``.

    :param src: A URL, filename, bytes, or existing ``netCDF4.Dataset``.
        If more than one is passed, the first
        data set will mask variables available in subsequent data sets.
        This is useful for combining BGC and core files.
        
    >>> from medsrtqc.nc import read_nc_profile
    >>> from medsrtqc.resources import resource_path
    >>> profile = read_nc_profile(resource_path('BR2902746_001.nc'))
    >>> profile['TEMP'].value
    """

    return NetCDFProfile(*[_load_dataset(s) for s in src])
