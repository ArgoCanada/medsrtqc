
from .core_impl import VMSProfileList
from .profiles_enc import PrStnAndPrProfilesEncoding
from .enc import ArrayOf


_file_encoding = ArrayOf(PrStnAndPrProfilesEncoding())


def read_vms_profiles(src):
    """
    Read a binary VMS file into a :class:`VMSProfileList`.

    :param src: A filename or file-like object

    >>> from medsrtqc.vms import read_vms_profiles
    >>> profiles = read_vms_profiles('tests/test-data/BINARY_VMS.DAT')
    >>> profiles[0]['TEMP'].value
    masked_array(data=[3.49900007, 3.45300007, 3.45799994, 3.48900008,
                    3.46799994, 3.49099994, 3.4690001 , 3.50999999,
                    3.45799994, 3.4849999 , 3.49699998, 3.42199993,
                    3.45700002, 3.48900008, 3.48900008, 3.46700001,
                    3.51699996],
                mask=False,
        fill_value=1e+20)
    """

    data = None
    if isinstance(src, str):
        with open(src, 'rb') as f:
            data = _file_encoding.decode(f)
    elif hasattr(src, 'read'):
        data = _file_encoding.decode(src)
    else:
        raise TypeError("Can't interpret `src` as a file or file-like object")

    return VMSProfileList(data)
