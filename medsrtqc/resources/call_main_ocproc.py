
#import ocprocReader_general as ocproc
#import mainOcprocQC as ocprocQC
from ocproc import ocprocReadWrite
from os import path
import sys
sys.path.append(path.abspath('../realtime_qcsrc/dfo/meds/core_ArgoQcTests')) 


input = "C://Users//trana//input//arvor_bgc_win.dat"  #VMS encoding or Windows encoding
#input = "C://Users//trana//input//OUTPUT_PROF.DAT"  
output = "C://Users//trana//input//TEST_output.DAT"  #Windows encoding
encodeFrom = "WINDOWS"  #need to change depending if incoming file has 'VMS' or 'WINDOWS' encoding
encodeTo = "WINDOWS"  #need to change depending if out file has 'VMS' or 'WINDOWS' encoding

print(input)
oc = ocprocReadWrite.readWrite(input, encodeFrom, encodeTo, output)
oc_data = oc.read_byte_from_File()
print('\n','ANH HEADER STRUCTURE','\n')
# impossible date test
obs_date_time = oc_data.get('header')['obs_date'] + oc_data.get('header')['obs_time']
print('\n',obs_date_time)


