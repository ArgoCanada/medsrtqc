
import urllib.request
import io
import os
import shutil
import reprlib
from netCDF4 import Dataset
from .core import Profile, Trace


class NetCDFProfile(Profile):
    """
    A :class:`medsrtqc.core.Profile` implementation backed by a
    ``netCDF4.Dataset`` representation of an Argo profile NetCDF file.
    The NetCDF file should be a single-profile NetCDF. These objects
    are normally created using :func:`read_nc_profile`.

    :param dataset: An existing ``netCDF4.Dataset``.
    """

    def __init__(self, dataset):
        self._dataset = dataset


def read_nc_profile(src):
    """
    Load a ``netCDF4.Dataset` from a filename, url, bytes, or existing
    ``netCDF4.Dataset``.

    :param src: A URL, filename, bytes, or existing ``netCDF4.Dataset``.

    >>> from medsrtqc.nc import read_nc_profile
    >>> from medsrtqc.resources import resource_path
    >>> profile = read_nc_profile(resource_path('BR2902746_001.nc'))
    >>> profile['TEMP'].value
    """

    if not isinstance(src, (Dataset, bytes, str)):
        raise TypeError('`src` must be a filename, url, bytes, or netCDF4.Dataset object')

    if isinstance(src, Dataset):
        return NetCDFProfile(src)
    elif isinstance(src, str) and os.path.exists(src):
        return NetCDFProfile(Dataset(src))
    elif isinstance(src, bytes):
        return NetCDFProfile(Dataset('in-mem-file', mode='r', memory=src))
    elif src.startswith('http://') or src.startswith('https://') or src.startswith('ftp://'):
        buf = io.BytesIO()
        with urllib.request.urlopen(src) as f:
            shutil.copyfileobj(f, buf)
        return NetCDFProfile(Dataset('in-mem-file', mode='r', memory=buf.getvalue()))
    else:
        raise ValueError(f"Don't know how to open '{reprlib.repr(src)}'\n.Is it a valid file or URL?")
