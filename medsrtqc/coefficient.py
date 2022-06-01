
from .resources import resource_path

def read_coef_file():
    """
    A function to read the file 'doxy_bgc_calibration_coef.csv' which contains
    all the BGC coefficients for the MEDS DAC into a dict() object. The keys
    to this dict() will be the WMO numbers, and each entry will contain
    another dict() where the keys are the coefficient names. 

    >>> coef = read_coef_file()
    >>> coef['6903026']

    >>>  {'doxy_sn': '3639',
            'PhaseCoef0': -1.56841,
            'PhaseCoef1': 1.0,
            'PhaseCoef2': 0.0,
            'PhaseCoef3': 0.0,
            'ConcCoef0': 0.0,
            'ConcCoef1': 1.0,
            'c00': 0.0026835,
            'c01': 0.000118496,
            'c02': 2.23135e-06,
            'c03': 195.176,
            'c04': -0.208458,
            'c05': -41.8996,
            'c06': 3.85572,
            'Spreset': 0.0,
            'Pcoef1': 0.1,
            'Pcoef2': 0.00022,
            'Pcoef3': 0.0419,
            'B0': -0.00624523,
            'B1': -0.00737614,
            'B2': -0.010341,
            'B3': -0.00817083,
            'C0': -4.88682e-07,
            'D0': 24.4543,
            'D1': -67.4509,
            'D2': -4.8489,
            'D3': -0.000544,
            'A1_380': 1.56843e-07,
            'A0_380': 2150780000.0,
            'lm_380': 1.161,
            'A1_412': 2.10228e-07,
            'A0_412': 2149460000.0,
            'lm_412': 1.368,
            'A1_490': 2.40316e-07,
            'A0_490': 2146650000.0,
            'lm_490': 1.365,
            'A1_PAR': 3.20852e-06,
            'A0_PAR': 2147290000.0,
            'lm_PAR': 1.359,
            'SCALE_CHLA': 0.0073,
            'DARK_CHLA': 48.0,
            'DARK_BACKSCATTERING700': 47.0,
            'SCALE_BACKSCATTERING700': 1.891e-06,
            'delta': 0.039,
            'lambda': 700.0,
            'theta': 124.0,
            'khi': 1.076,
            'SCALE_CDOM': 0.0902,
            'DARK_CDOM': 49.0,
            'R': 8.31446,
            'F': 96485.0,
            'k0': -1.42365,
            'k2': -0.00106853,
            'f1': 1.8014e-05,
            'f2': -2.8288e-08,
            'f3': 2.638e-11,
            'f4': -1.3977e-14,
            'f5': 3.9869e-18,
            'f6': -4.7726e-22}
    """
    with open(resource_path('doxy_bgc_calibration_coef.csv')) as fid:
        fid.readline()
        coeff = dict()
        for line in fid:
            wmo = line.split(',')[0]
            line = ','.join(line.split(',')[1:])
            doxy_sn = line.split(',')[0]
            line = ','.join(line.split(',')[1:])
            
            coeff[wmo] = dict(DOXY_SN=doxy_sn)
            for c in line.split(','):
                if c.strip():
                    name, value = c.split('=')
                    value = float(value)
                    coeff[wmo][name] = value
    
    return coeff

coeff = read_coef_file()