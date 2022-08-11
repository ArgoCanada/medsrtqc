
import sys
import contextlib

from medsrtqc.vms import read_vms_profiles, write_vms_profiles
from medsrtqc.qc.chla import ChlaTest
from medsrtqc.qc.bbp import bbpTest

log_file = open('realistic_log.log', 'w')

vms_file = sys.argv[1]
print(vms_file)
profs = read_vms_profiles(vms_file)

chla_test = ChlaTest()
bbp_test  = bbpTest()

for p in profs:
    with contextlib.redirect_stderr(log_file):
        chla_test.run(p)
        bbp_test.run(p)

write_vms_profiles(profs, 'output_file.dat')
