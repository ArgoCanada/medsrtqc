
"""
The ``resources`` module facilitates inclusion of data files
that serve as examples or simplify the code required to
implement some QC functions. Resource files are accessed using
:func:`resource_path`. Resource files that can be accessed
include:

``'BINARY_VMS.DAT'``
    A VMS export containing two ascents of a float in binary
    VMS format. This file is used to test 
    :func:`medsrtqc.vms.read_vms_profiles`.

``'BINARY_VMS.json'``
    The human-readable JSON version of ``'BINARY_VMS.DAT'``.

``'BR6904117_085.nc'``, ``'R6904117_085.nc'``
    A core and BGC Argo NetCDF file for use testing BGC variables.
"""

import os


def resource_path(path):
    """
    Calculate the absolute path to a resource file or raise
    ``FileNotFoundError`` if the file does not exist.

    :param path: The relative path to the data file within the
        ``resources`` module.
    
    >>> from medsrtqc.resources import resource_path
    >>> resource_path('BINARY_VMS.DAT')
    """

    abs_path = os.path.join(os.path.dirname(__file__), path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"'{path}' is not a resource within the medsrtqc.resources module.")
    return abs_path
