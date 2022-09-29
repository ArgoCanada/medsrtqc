
import sys
import contextlib

from medsrtqc.vms import read_vms_profiles, write_vms_profiles
from medsrtqc.qc.chla import ChlaTest
from medsrtqc.qc.bbp import bbpTest

# more likely open('logs/f{date}_log.log')
log_file = open('realistic_log.log', 'w')
with contextlib.redirect_stderr(log_file):

    # read from command line
    vms_file = sys.argv[1]
    profs = read_vms_profiles(vms_file)

    # run tests on chlorophyll and bbp
    chla_test = ChlaTest()
    bbp_test  = bbpTest()
    for p in profs:
        chla_test.run(p)
        # bbp_test.run(p)

    # export profiles with altered flags, CHLA_ADJUSTED likely populated
    f = open('output_file.dat', 'wb')
    write_vms_profiles(profs, f)
    f.close()