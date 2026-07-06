
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

    try:
        abs_path = meds_path(path)
    except (KeyError, FileNotFoundError) as exception:
        abs_path = os.path.join(os.path.dirname(__file__), path)

        if not os.path.exists(abs_path):
            raise Exception([exception, FileNotFoundError(f"'{path}' is not a resource within the medsrtqc.resources or config module.")])

    return abs_path

def meds_path(path):
    """
    Get the absolute path to a resource file on the MEDS server
    or raise ``FileNotFoundError`` of the file does not exist.

    :param path: The relative path within the home Batman Apps 
        directory.

    >>> from medsrtqc.resources import meds_path
    >>> meds_path('doxy_calibration_coef.csv')
    """

    meds_file_paths = {
        'doxy_calibration_coef.csv':{'e':'Argo_QC/config','d':'Argo BGC RTQC Test/config'},
        'fluo_to_chl_physiological_ratio_LUT.csv':{'e':'Argo_QC/config','d':'Argo BGC RTQC Test/config'},
        'CHLA_netCDF_info.csv':{'e':'Argo_QC/config','d':'Argo BGC RTQC Test/config'},
        'park_depth.csv':{'e':'Argo_QC/config','d':'Argo BGC RTQC Test/config'},
        'median_doxy_gains_woa23.csv':{'e':'Argo_QC/config','d':'Argo BGC RTQC Test/config'},
    }

    cwd = os.path.dirname(__file__)
    drive = f'{cwd.split(":")[0]}:'
    root = '\\'

    base = os.path.join(drive, root)
    abs_path = os.path.join(os.path.join(base, meds_file_paths[path][drive.strip(':').lower()]), path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"'{path}' is not a resource within the medsrtqc.resources or config module.")
    return abs_path