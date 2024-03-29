
from .core_impl import VMSProfile
from .profiles_enc import PrStnAndPrProfilesEncoding
from .enc import ArrayOf, LineEnding

def read_vms_profiles(src, ver='vms'):
    """
    Read a binary VMS file into a ``list()`` of :class:`VMSProfile`
    objects.

    :param src: A filename or file-like object

    >>> from medsrtqc.vms import read_vms_profiles
    >>> from medsrtqc.resources import resource_path
    >>> profiles = read_vms_profiles(resource_path('BINARY_VMS.DAT'))
    >>> profiles[0]['TEMP'].value
    masked_array(data=[3.49900007, 3.45300007, 3.45799994, 3.48900008,
                    3.46799994, 3.49099994, 3.4690001 , 3.50999999,
                    3.45799994, 3.4849999 , 3.49699998, 3.42199993,
                    3.45700002, 3.48900008, 3.48900008, 3.46700001,
                    3.51699996],
                mask=False,
        fill_value=1e+20)
    """

    global _file_encoding
    _file_encoding = ArrayOf(PrStnAndPrProfilesEncoding(ver))

    data = None
    if isinstance(src, str):
        with open(src, 'rb') as f:
            data = _file_encoding.decode(f)
    elif hasattr(src, 'read'):
        data = _file_encoding.decode(src)
    else:
        raise TypeError("Can't interpret `src` as a file or file-like object")

    return [VMSProfile(item) for item in data]


def write_vms_profiles(profiles, dest, ver='vms'):
    """
    Write a binary VMS file from a ``list()`` of :class:`VMSProfile`
    objects.

    :param profiles: A ``list()`` of :class:`VMSProfile` objects.
    :param dest: A filename or file-like object

    >>> from medsrtqc.vms import write_vms_profiles, read_vms_profiles
    >>> from medsrtqc.resources import resource_path
    >>> import tempfile
    >>> profiles = read_vms_profiles(resource_path('BINARY_VMS.DAT'))
    >>> with tempfile.TemporaryFile() as f:
    ...     write_vms_profiles(profiles, f)
    """
    
    global _file_encoding
    _file_encoding = ArrayOf(PrStnAndPrProfilesEncoding(ver))

    for i, item in enumerate(profiles):
        if not isinstance(item, VMSProfile): # pragma: no cover
            msg = 'All items in `profiles` must be a VMSProfile objects.'
            msg += f' profiles[{i}] is not a VMSProfile object'
            raise TypeError(msg)

    if isinstance(dest, str):
        with open(dest, 'wb') as f:
            _file_encoding.encode(f, [item._data for item in profiles],)
        if ver == 'win':
            line_end = False
            with open(dest, 'rb') as f:
                f.seek(-2, 2)
                if f.read() != b'\r\n':
                    line_end = True
            
            if line_end:
                with open(dest, 'ab') as f:
                    LineEnding().encode(f)

    elif hasattr(dest, 'write'):
        _file_encoding.encode(dest, [item._data for item in profiles],)
        if ver == 'win':
            dest.close()
            fn = dest.name
            line_end = False
            with open(fn, 'rb') as f:
                f.seek(-2, 2)
                if f.read() != b'\r\n':
                    line_end = True
            
            if line_end:
                with open(fn, 'ab') as f:
                    LineEnding().encode(f)
    else:
        raise TypeError("Can't interpret `dest` as a file or file-like object")
    
def check_vms(k):

    vms_list = [
        'VREF','PHPH','PHTO','CDO$','CDOM','FLU3','FLU1','B700','BBP$',
        'C1PH','C2PH','DOXY','PPOX','OTMP'
    ]

    return k in vms_list

def translate_vms(k):
    keys = [
        'PHPH','PHTO','CDO$','CDOM','FLU3','FLU1','B700','BBP$',
        'C1PH','C2PH','DOXY','PPOX','OTMP'
    ]
    vals = [
        'PH_IN_SITU_FREE', 'PH_IN_SITU_TOTAL', 'FLUORESCENCE_CDOM',
        'CDOM', 'CHLA', 'FLUORESCENCE_CHLA', 'BETA_BACKSCATTERING', 'BBP700',
        'C1PHASE_DOXY','C2PHASE_DOXY','DOXY','PPOX_DOXY','TEMP_DOXY'
    ]

    dc = {key:val for key, val in zip(keys, vals)}

    return dc[k]
