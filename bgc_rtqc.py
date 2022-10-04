
import sys
from datetime import datetime
import contextlib

from medsrtqc.vms import read_vms_profiles, write_vms_profiles
from medsrtqc.qc.check import preTestCheck

with open(f'logs/{datetime.utcnow().strftime("%Y%m%d_%H%M")}_log.log') as log_file:
    with contextlib.redirect_stderr(log_file):

        # read from command line
        input_file = sys.argv[1]
        profs = read_vms_profiles(input_file)

        # run tests on appropriate bgc variables
        check = preTestCheck()
        for p in profs:
            # add FLUA if appropriate, and QCP/QCF variables if they don't exist
            p.prepare()
            # which tests to do based on variables in profile
            tests = check.run(p)
            for t in tests:
                t.run(p)

        # export profiles with altered flags, CHLA_ADJUSTED likely populated
        output_file = input_file.replace('.dat', '_output.dat')
        f = open(output_file, 'wb')
        write_vms_profiles(profs, f, ver=2)
        f.close()