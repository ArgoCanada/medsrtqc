
"""
The ``resources`` module facilitates inclusion of data files
that serve as examples or simplify the code required to
implement some QC functions. Resource files are accessed using
:func:`resource_path`. Resource files that can be accessed
include:

``'BINARY_VMS.DAT'``, ``'BINARY_VMS.json'```
    A VMS export containing two ascents of a float in binary
    VMS format. This file is used to test
    :func:`medsrtqc.vms.read_vms_profiles`. The ``.json``
    version is a human-readable dump of the ``.DAT`` file.

``'OUTPUT_RT.DAT'``, ``'OUTPUT_RT.json'``
    A QC-applied version of ``'BINARY_VMS.DAT'``. The ``.json``
    version is a human-readable dump of the ``.DAT`` file.

``'BR6904117_085.nc'``, ``'R6904117_085.nc'``
    A core and BGC Argo NetCDF file for use testing BGC variables.
"""

import sys
import os

def config_path(path):

    cwd = os.getcwd()
    parent, child = os.path.split(cwd)
    base = parent if child == 'lib' else cwd
    abs_path = os.path.join(base, 'config', path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"'{path}' is not a resource within the {os.path.dirname(abs_path)} directory.")
    return abs_path

def resource_path(path):
    """
    Calculate the absolute path to a resource file or raise
    ``FileNotFoundError`` if the file does not exist.

    :param path: The relative path to the data file within the
        ``resources`` module.

    >>> from medsrtqc.resources import resource_path
    >>> resource_path('BINARY_VMS.DAT')
    """

    try:
        abs_path = config_path(path)
    except FileNotFoundError as exception:
        abs_path = os.path.join(os.path.dirname(__file__), path)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"'{path}' is not a resource within the medsrtqc.resources or config module.")
    return abs_path
