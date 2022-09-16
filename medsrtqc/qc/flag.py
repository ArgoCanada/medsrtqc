
# a lot of this is copied+modified from
# https://github.com/euroargodev/argortqcpy/blob/main/argortqcpy/checks.py
# in the future this package should import that one and use it where
# possible!

class Flag:
    """
    Flags for check output. These values are valid values of the
    ``qc`` and ``adjusted_qc`` attributes of a
    :class:`~medsrtqc.core.Trace` object. Utility functions are
    provided as static methods to get the name or value of a flag
    or to update flag values ensuring that values that are already
    marked at a "worse" QC level are not inadvertently changed.
    """

    @staticmethod
    def label(flag):
        """Return the label of a QC flag"""
        return Flag._names[flag]

    @staticmethod
    def value(label):
        """Return the value of a QC flag"""
        for value, lab in Flag._names.items():
            if label == lab:
                return value
        raise KeyError(f"'{label}' is not the name of a QC flag")

    @staticmethod
    def update_safely(qc, to, where=None):
        """
        Safely update ``qc`` to the value ``to``. Values that are
        already marked at a "worse" QC level are not modified.
        """
        where = slice(None) if where is None else where
        flags = qc[where]
        for overridable_flag in Flag._precedence[to]:
            flags[flags == overridable_flag] = to
        qc[where] = flags

    NO_QC = b'0'
    GOOD = b'1'
    PROBABLY_GOOD = b'2'
    PROBABLY_BAD = b'3'
    BAD = b'4'
    CHANGED = b'5'
    # '6' not used
    # '7' not used
    ESTIMATED = b'8'
    MISSING = b'9'
    FILL_VALUE = b''

    _names = {
        NO_QC: 'NO_QC',
        GOOD: 'GOOD',
        PROBABLY_GOOD: 'PROBABLY_GOOD',
        PROBABLY_BAD: 'PROBABLY_BAD',
        BAD: 'BAD',
        CHANGED: 'CHANGED',
        ESTIMATED: 'ESTIMATED',
        MISSING: 'MISSING',
        FILL_VALUE: 'FILL_VALUE'
    }

    _precedence = {
        NO_QC: set(),
        GOOD: {
            NO_QC,
            FILL_VALUE,
        },
        PROBABLY_GOOD: {
            NO_QC,
            GOOD,
            CHANGED,
            FILL_VALUE,
        },
        PROBABLY_BAD: {
            NO_QC,
            GOOD,
            PROBABLY_GOOD,
            CHANGED,
            FILL_VALUE,
        },
        BAD: {
            NO_QC,
            GOOD,
            PROBABLY_GOOD,
            CHANGED,
            PROBABLY_BAD,
            FILL_VALUE,
        },
        CHANGED: {
            NO_QC,
            FILL_VALUE,
        },
        ESTIMATED: {
            NO_QC,
            GOOD,
            PROBABLY_GOOD,
            FILL_VALUE,
        },
        MISSING: {
            NO_QC,
            FILL_VALUE,
        },
    }
