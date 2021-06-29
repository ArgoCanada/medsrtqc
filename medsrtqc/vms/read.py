
from .core_impl import VMSProfileList
from .profiles_enc import PrStnAndPrProfilesEncoding
from .enc import ArrayOf


_file_encoding = ArrayOf(PrStnAndPrProfilesEncoding())


def read_vms_profiles(src):
    """
    Read a binary VMS file into a ProfileList.
    """

    data = []
    if isinstance(src, str):
        with open(src, 'rb') as f:
            _file_encoding.decode(f, data)
    elif hasattr(src, 'read'):
        _file_encoding.decode(src, data)
    else:
        raise TypeError("Can't interpret `src` as a file or file-like object")

    return VMSProfileList(data)
