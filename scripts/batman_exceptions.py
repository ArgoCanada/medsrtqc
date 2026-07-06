
import traceback

try:
    
    import sys
    import contextlib

    import pandas as pd

    from medsrtqc.vms import read_vms_profiles, write_vms_profiles
    from medsrtqc.qc.check import preTestCheck

    now = pd.Timestamp('now', tz='utc')

    with open(f'../bgc_logs/{now.strftime("%Y%m%d_%H%M")}_log.log', 'w') as log_file:
        with contextlib.redirect_stderr(log_file):

            # read from command line
            input_file = sys.argv[1]
            try:
                profs = read_vms_profiles(input_file,  ver='win')
                ver = 'win'
            except:
                try:
                    profs = read_vms_profiles(input_file, ver='vms')
                    ver = 'vms'
                except:
                    raise IOError('Could not read file with either VMS or Windows encoding')

            # run tests on appropriate bgc variables
            check = preTestCheck()
            all_tests = []
            for p in profs:
                # which tests to do based on variables in profile
                tests = check.run(p)
                # add FLUA if appropriate, and QCP/QCF variables if they don't exist
                tests = p.prepare(tests, reset=True)
                all_tests.append(tests)
                for t in tests:
                    t.run(p)

            # only export a file if we actually did anything to it
            if len(all_tests) > 0:
                # export profiles with altered flags, CHLA_ADJUSTED likely populated
                output_file = input_file.replace('.dat', '_output.dat')
                f = open(output_file, 'wb')
                write_vms_profiles(profs, f, ver=ver)
                f.close()
except:
    with open("exceptions.log", "a") as logfile:
        traceback.print_exc(file=logfile)
    raise