
"""
The classes in the ``vms`` module make reading binary input files
exported from a VAX/VMS system more expressive and easier to debug
without affecting the clarity of real-time processing code. In normal
usage you should only need :func:`read_vms_profiles` and
:func:`write_vms_profiles`.
"""

from .read import read_vms_profiles, write_vms_profiles
from .core_impl import VMSProfile, VMSProfileList

__all__ = ['read_vms_profiles', 'write_vms_profiles', 'VMSProfile', 'VMSProfileList']
