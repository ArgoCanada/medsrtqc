from medsrtqc.vms import read_vms_profiles
from medsrtqc.resources import resource_path
from medsrtqc.qc.chla import ChlaTest

# load a bgc VMS file (source files from coriolis)
profs = read_vms_profiles(resource_path('bgc_vms.dat'))
prof = profs[0]
test = ChlaTest()

# I edited test.run to return the Trace() for ease here
chla = test.run(prof)

# show trace values where chla.adjusted and chla.adjusted_qc have been updated
print('chla Trace:')
print(chla)

# show that those fields have not been updated in prof
print('"FLU1" Profile field:')
print(prof['FLU1'])