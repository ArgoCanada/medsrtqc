#!/usr/bin/env python

import contextlib

from medsrtqc.vms import read_vms_profiles
from medsrtqc.resources import resource_path
from medsrtqc.qc.named_tests import PressureIncreasingTest

# open a file to log results of running tests
fid = open('meds_python_rtqc_log.log', 'w')

# the following packages are not required for this scriot
# but I will attempt to import them here in order to see if
# their import will throw an error

fid.write(80*'-' + '\n')
fid.write('Module Import Tests\n')
fid.write(80*'-' + '\n\n')

try:
    import gsw
    fid.write('gsw successfully imported\n\n')
except Exception as err:
    fid.write(f'Exception: {err}\n\n')

try:
    from medsrtqc.qc.chla import ChlaTest
    test = ChlaTest()
    fid.write('medsrtqc.qc.chla.ChlaTest successfully imported\n\n')
except Exception as err:
    fid.write(f'Exception: {err}\n\n')

try:
    from medsrtqc.qc.bbp import bbpTest
    test = bbpTest()
    fid.write('medsrtqc.qc.bbp.bbpTest successfully imported\n\n')
except Exception as err:
    fid.write(f'Exception: {err}\n\n')

try:
    from medsrtqc.nc import read_nc_profile
    url = 'https://data-argo.ifremer.fr/dac/coriolis/6904117/profiles/R6904117_085.nc'
    profile = read_nc_profile(url)
    fid.write('medsrtqc.nc.read_nc_profile successfully imported and executed\n\n')
except Exception as err:
    fid.write(f'Exception: {err}\n\n')

try:
    from medsrtqc.interactive import plot
    fid.write('meds.interactie.plot successfully imported\n\n')
except Exception as err:
    fid.write(f'Exception: {err}\n\n')

# load file
profs = read_vms_profiles(resource_path('BINARY_VMS.DAT'))

# run test on a prof that will fail
test = PressureIncreasingTest()
prof = profs[0]

# print out the profile and flags before test
fid.write(80*'-' + '\n')
fid.write('Example: Pressure Increasing Test\n')
fid.write(80*'-' + '\n\n')
fid.write('Before Pressure Increasing Test:\n\n')
fid.write('>> prof["PRES"]\n\n')
fid.write(repr(prof['PRES']) + '\n\n')
fid.write('>> prof["TEMP"].qc\n\n')
fid.write(repr(prof['TEMP'].qc) + '\n\n')

# run the test
fid.write('>> test = PressureIncreasingTest()\n')
fid.write('>> test.run(prof)\n\n')
test.run(prof)  # False

# print out the profile and flags after the test
fid.write('After Pressure Increasing Test:\n\n')
fid.write('>> prof["PRES"]\n\n')
fid.write(repr(prof['PRES']) + '\n\n')

fid.write('>> prof["TEMP"].qc\n\n')
fid.write(repr(prof['TEMP'].qc) + '\n')

# now load a BGC profile
profs = read_vms_profiles(resource_path('bgc_vms.dat'))
prof = profs[0]

fid.write(80*'-' + '\n')
fid.write('Example: BGC VMS File\n')
fid.write(80*'-' + '\n\n')

# show chlorophyll
fid.write('>> prof["FLU1"] # chlorophyll\n\n')
fid.write(repr(prof['FLU1']) + '\n\n')

# try to run chla test
fid.write('>> test = ChlaTest()\n')
fid.write('>> test.run(prof)\n\n')
test = ChlaTest()
with contextlib.redirect_stderr(fid):
    test.run(prof)
fid.write('\n>> prof["FLU1"] # chlorophyll\n\n')
fid.write(repr(prof['FLU1']) + '\n\n')

fid.close()
