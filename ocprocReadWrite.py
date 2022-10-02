"""
Created on Thu Aug 20 21:02:21 2020

@author: ChiuJ
"""


import struct
from builtins import dict
from codecs import decode


'''
from argoRTtests import impossibleDateTest, impossibleLocationTest, globalRangeTest, positionOnLandTest 
from argoRTtests import regionalRangeTest, pressureIncreasingTest, spikeTest, deepestPressureTest
from argoRTtests import impossibleSpeedTest, digitRolloverTest, stuckValueTest, densityInversionTest
from argoRTtests import grossTSSensorDriftTest, frozenProfileTest, MEDDtest
'''



class readWrite:
    '''
    classdocs    
    '''
    #
    # * The encoding method for floating-point numbers for a VAX/VMS system
    # * which is a sort of middle-endian byte order
    # */
    FLOATING_POINT_ENCODING_VMS = 1
    #
    # The encoding method for floating-point numbers on a non-VAX/VMS system
    # which uses a little-endian byte order (e.g. Windows, Unix)
    #/
    FLOATING_POINT_ENCODING_STANDARD = 2;

    #
    # Specifies the line control characters used on a VAX/VMS system
    # * which is 2 bytes at the beginning of a record to indicate its size
    #
    LINE_CONTROL_SEQUENCE_VMS = 1;
    #/**
    # * Specifies the line control characters used on a Windows system
    # * which is a carriage-return and line-feed at the end of the line
    # */
    LINE_CONTROL_SEQUENCE_WINDOWS = 2;
    #/**
    # * Specifies the line control characters used on a Unix system
    # * which is a line-feed at the end of the line
    # */
    LINE_CONTROL_SEQUENCE_UNIX = 3;
    #
    # * Specifies that no line control characters are used in the file - this would be the normal
    # * case for a binary file format like OCPROC
    # */
    LINE_CONTROL_SEQUENCE_NONE = 4;
    FLOATING_POINT_ENCODING=0
    LINE_CONTROL_SEQUENCE =0    
    skipBytes =0
    numberOfOddRecordSizes = 0;
    num_surface_byte_to_read = 9 
    num_surf_code_byte_to_read = 15           

    header_vars = [['mkey',8,'s'], ['one_deg_sq',4,'i'], ['cr_number',10,'s'],['obs_date',8,'s'],['obs_time',4,'s'],
                ['data_type',2,'s'], ['iumsgno',4,'i'], ['stream_source',1,'s'], ['u_flag',1,'s'],['stn_number',2,'h'], 
                ['latitude',4,'f'], ['longitude',4,'f'], ['q_pos',1,'s'], ['q_date_time',1,'s'], ['q_record',1,'s'],
                ['up_date',8,'s'], ['bul_time',12,'s'], ['bul_header',6,'s'], ['source_id',4,'s'], ['stream_ident',4,'s'], 
                ['qc_version',4,'s'], ['avail',1,'s'], ['num_prof',2,'h'], ['nparms',2,'h'], ['sparms',2,'h'], ['num_hist',2,'h']]
    
    header_vars_prof = [['mkey',8,'s'], ['one_deg_sq',4,'i'], ['cr_number',10,'s'],['obs_date',8,'s'],['obs_time',4,'s'],
                    ['data_type',2,'s'], ['iumsgno',4,'i'], ['prof_type',4,'s'], ['profile_seg',2,'s'], 
                    ['no_depths',2,'h'], ['d_p_code', 1, 's']]
    
    profile_metadata_vars = [['no_seg',2,'h'], ['prof_type',4,'s'], ['dup_flag',1,'s'], ['digit_code',1,'s'], ['standard',1,'s'], ['deep_depth',4,'f']]
    
    surface_vars = [['pcode',4,'s'], ['parm',4,'f'], ['q_parm',1,'s']]
    
    surf_code_vars = [['pcode',4,'s'], ['cparm',10,'s'], ['q_parm',1,'s']]
    
    history_vars = [['ident_code',2,'s'], ['prc_code',4,'s'], ['version',4,'s'], ['prc_date',4,'i'], ['act_code',2,'s'],
                ['act_parm',4,'s'], ['aux_id',4,'f'], ['o_value',4,'f']]
    
    profile_vars = [['prof_type', 4, 's'], ['profile_seg', 2, 's'],
                    ['no_depths', 2, 'h'],['d_p_code', 1, 's']]
    
    profile_level_var = [['depth_press',4,'f'], ['dp_flag',1,'s'], ['parm',4,'f'], ['q_parm',1,'s']]


    #
    # The encoding method for floating-point numbers for a VAX/VMS system
    # which is a sort of middle-endian byte order
    def __init__(self, fileName,fileEncodingFrom, line_control_sequence, fileout):
        
        self.fileName = fileName
        self.fileout =fileout

        self.fileEncodingFrom = fileEncodingFrom
        print(fileEncodingFrom)
        if (fileEncodingFrom.upper() == 'VMS'):
            self.num_surface_byte_to_read = 9 
            self.num_surf_code_byte_to_read = 15        
            self.FLOATING_POINT_ENCODING = 'FLOATING_POINT_ENCODING_VMS'
            self.surface_vars = [['pcode',4,'s'], ['parm',4,'f'], ['q_parm',1,'s']]    
            self.surf_code_vars = [['pcode',4,'s'], ['cparm',10,'s'], ['q_parm',1,'s']]

        elif (fileEncodingFrom.upper() == 'WINDOWS'):
            self.floatingPointEncoding = 'FLOATING_POINT_ENCODING_STANDARD'
            self.surface_vars = [['pcode',150,'s'], ['parm',4,'f'], ['q_parm',1,'s']]
            self.num_surface_byte_to_read= 155    
            self.surf_code_vars = [['pcode',150,'s'], ['cparm',512,'s'], ['q_parm',1,'s']]
            self.num_surf_code_byte_to_read = 663
        elif (fileEncodingFrom.upper() == 'UNIX'):
            self.floatingPointEncoding = 'FLOATING_POINT_ENCODING_UNIX'
           
        if(line_control_sequence.upper() == 'VMS'):
            self.skipBytes = self.LINE_CONTROL_SEQUENCE_VMS
            self.LINE_CONTROL_SEQUENCE = 'VMS'
        elif(line_control_sequence.upper() == 'WINDOWS'):
            self.skipBytes = self.LINE_CONTROL_SEQUENCE_WINDOWS
            self.LINE_CONTROL_SEQUENCE = 'WINDOWS'
        elif(line_control_sequence.upper() == 'NONE'):
            self.skipBytes = self.LINE_CONTROL_SEQUENCE_NONE
            self.LINE_CONTROL_SEQUENCE ='NONE'
        elif(line_control_sequence.upper() == 'UNIX'):
            self.skipBytes = self.LINE_CONTROL_SEQUENCE_UNIX
            self.LINE_CONTROL_SEQUENCE ='UNIX'
                

        
    def read_byte_from_File(self):        
        with open(self.fileName, 'rb') as binFile:
            current_loc = binFile.tell()
            oc_stn = []
            while binFile.peek(1) != b'':
                print('current_loc: ', binFile.tell() )              
                b_data = binFile.read(102) #102 bytes in OCPROC FXD structure
                if b_data == b'':
                    break
                else:
                    ocproc = self.decode_stn_rec(b_data, binFile)
                    '''            
                    print('\n','STATION--------------', '\n')
                    print('\n','HEADER STRUCTURE','\n')
                    print(ocproc.get('header'))
                    print('\n','PROFILE STRUCTURE','\n')
                    print(ocproc.get('profile_meta'))
                    print('\n','SURFACE STRUCTURE','\n')
                    print(ocproc.get('surface'))
                    print('\n','SURF CODES STRUCTURE','\n')
                    print(ocproc.get('surf_codes'))
                    print('\n','HISTORY STRUCTURE','\n')
                    print(ocproc.get('history'))
                    print('\n','PROFILE---','\n')
                    print(ocproc.get('profile_rec'))
                    print('current loc now ', binFile.tell())
                    '''
                    oc_stn.append(ocproc)

                    #return ocproc
                        

                    #QC tests
                    #if (ocproc['profile_meta']):
                    #    profile_data_QC, check1 = deepestPressureTest(ocproc['header']['cr_number'],ocproc['profile_rec'])
                    #if (self.LINE_CONTROL_SEQUENCE == 'WINDOWS'):
                    #    self.write_ByteFile(ocproc)
                    #elif (self.LINE_CONTROL_SEQUENCE == 'VMS'):
                    #    self.write_ByteFile(ocproc)

            return oc_stn
    
    #writing the OCPROC data in memory to binary file - Windows encoding
    def write_ByteFile(self, _ocproc):
    
        
        with open(self.fileout, 'ab') as out:
           
            #MKEY
            for ii_var in range(len(self.header_vars)):
                out.write(self.encode_bytes(_ocproc['header'][self.header_vars[ii_var][0]], self.header_vars[ii_var][2]))
     
            # profiles
            for ii in range(_ocproc['header']['num_prof']):
                headername = 'prof' + str(ii+1)                
                for ii_var in range(len(self.profile_metadata_vars)):
                    out.write(self.encode_bytes(_ocproc['profile_meta'][ii][headername][self.profile_metadata_vars[ii_var][0]], self.profile_metadata_vars[ii_var][2]))

            #surface 
            for ii in range(_ocproc['header']['nparms']):              
                for ii_var in range(len(self.surface_vars)):
                    out.write(self.encode_bytes(_ocproc['surface'][ii][self.surface_vars[ii_var][0]], self.surface_vars[ii_var][2]))
            
            #surf_codes
            for ii in range(_ocproc['header']['sparms']):
                for ii_var in range(len(self.surf_code_vars)):
                    out.write(self.encode_bytes(_ocproc['surf_codes'][ii][self.surf_code_vars[ii_var][0]], self.surf_code_vars[ii_var][2]))

            #history
            for ii in range(_ocproc['header']['num_hist']):
                for ii_var in range(len(self.history_vars)):
                    out.write(self.encode_bytes(_ocproc['history'][ii][self.history_vars[ii_var][0]], self.history_vars[ii_var][2]))
 
            #Windows line control sequence
            out.write(b'\r\n')
            #header profile record
            count = 0
            for ii in range(self.numberOfProfileSegments): 
                for ii_var in range(len(self.header_vars_prof)):
                    out.write(self.encode_bytes(_ocproc['profile_rec'][count]['profile_header'][self.header_vars_prof[ii_var][0]], self.header_vars_prof[ii_var][2]))                    
                    
      
                num_depth_values = _ocproc['profile_rec'][count]['profile_header'][self.header_vars_prof[9][0]]      
                count = count + 1
                
                for num in range(num_depth_values):
                    for iii_var in range(len(self.profile_level_var)):
                        out.write(self.encode_bytes(_ocproc['profile_rec'][count]['profile_var'][self.profile_level_var[iii_var][0]], self.profile_level_var[iii_var][2]))
                    count = count + 1

                #Windows line control sequence
                out.write(b'\r\n')
    
     #writing the OCPROC data in memory to binary file - VMS encoding
    def write_ByteFile_VMS(self, ocproc):
        
         with open(self.fileout, 'ab') as out:
           
            #MKEY
            for ii_var in range(len(self.header_vars)):
                out.write(self.encode_bytes_vms(ocproc['header'][self.header_vars[ii_var][0]], self.header_vars[ii_var][2]))
     
            # profiles
            for ii in range(ocproc['header']['num_prof']):
                headername = 'prof' + str(ii+1)                
                for ii_var in range(len(self.profile_metadata_vars)):
                    out.write(self.encode_bytes_vms(ocproc['profile_meta'][ii][headername][self.profile_metadata_vars[ii_var][0]], self.profile_metadata_vars[ii_var][2]))

            #surface 
            for ii in range(ocproc['header']['nparms']):              
                for ii_var in range(len(self.surface_vars)):
                    out.write(self.encode_bytes_vms(ocproc['surface'][ii][self.surface_vars[ii_var][0]], self.surface_vars[ii_var][2]))
            
            #surf_codes
            for ii in range(ocproc['header']['sparms']):
                for ii_var in range(len(self.surf_code_vars)):
                    out.write(self.encode_bytes_vms(ocproc['surf_codes'][ii][self.surf_code_vars[ii_var][0]], self.surf_code_vars[ii_var][2]))

            #history
            for ii in range(ocproc['header']['num_hist']):
                for ii_var in range(len(self.history_vars)):
                    out.write(self.encode_bytes_vms(ocproc['history'][ii][self.history_vars[ii_var][0]], self.history_vars[ii_var][2]))
 

            #header profile record
            count = 0
            for ii in range(self.numberOfProfileSegments): 
                for ii_var in range(len(self.header_vars_prof)):
                    out.write(self.encode_bytes_vms(ocproc['profile_rec'][count]['profile_header'][self.header_vars_prof[ii_var][0]], self.header_vars_prof[ii_var][2]))                    
                    
      
                num_depth_values = ocproc['profile_rec'][count]['profile_header'][self.header_vars_prof[9][0]]      
                count = count + 1
                
                for num in range(num_depth_values):
                    for iii_var in range(len(self.profile_level_var)):
                        out.write(self.encode_bytes_vms(ocproc['profile_rec'][count]['profile_var'][self.profile_level_var[iii_var][0]], self.profile_level_var[iii_var][2]))
                    count = count + 1


                    
    def decode_stn_rec(self, b_data, binFile):
        
        self.numOfProfiles = 0
        self.numOfSurfaces = 0
        self.numOfSurfCodes = 0
        self.numOfHistory = 0
        self.numberOfProfileSegments=0;
        self.numberOfDepths = 0;
        self.numberOfOddRecordSizes = 0;
        self.totalNumberOfDepths = 0;
        self.vmsEventRecordSizeIsOdd = False
        ii_start = 0          
        if (self.LINE_CONTROL_SEQUENCE == 'VMS'):
            self.vmsRecordSize = int.from_bytes(b_data[0:2], byteorder = 'little')
#           self.vmsRecordSize = self.decode_bytes(b_data[0:2], 'i')
#            ii_start = 2
            if (self.vmsRecordSize % 2 != 0):
                self.vmsEventRecordSizeIsOdd = True
                self.numberOfOddRecordSizes = self.numberOfOddRecordSizes + 1
                print ("VMSRECORDSIZE IS ODD")
 
        #mkey        
        ocproc_data = {'header':dict()}
        for ii_var in range(len(self.header_vars)):            
            ocproc_data['header'][self.header_vars[ii_var][0]] = self.decode_bytes(b_data[ii_start:(ii_start+self.header_vars[ii_var][1])],
                                                                     self.header_vars[ii_var][2]) 
            ii_start +=self.header_vars[ii_var][1]
        
        
        # profiles
        ocproc_data['profile_meta']=[]
        for ii in range(ocproc_data['header']['num_prof']):
            headername = 'prof' + str(ii+1)
            temp_data = {headername: dict()}
            ii_start = 0
            b_data = binFile.read(13)          
            for ii_var in range(len(self.profile_metadata_vars)): 
                temp_data[headername][self.profile_metadata_vars[ii_var][0]] = self.decode_bytes(b_data[ii_start:(ii_start + 
                                                                                   self.profile_metadata_vars[ii_var][1])], self.profile_metadata_vars[ii_var][2])
                ii_start += self.profile_metadata_vars[ii_var][1]

            self.numberOfProfileSegments += temp_data[headername]['no_seg']
            ocproc_data['profile_meta'].append(temp_data)

        
        #surface
        ocproc_data['surface'] = []
        for ii in range(ocproc_data['header']['nparms']):
            ii_start = 0
            b_data= binFile.read(self.num_surface_byte_to_read)
            temp_data = dict()
            for ii_var in range(len(self.surface_vars)):
                temp_data[self.surface_vars[ii_var][0]]= self.decode_bytes(b_data[ii_start:(ii_start+ self.surface_vars[ii_var][1])], 
                                                                            self.surface_vars[ii_var][2])
                
                ii_start += self.surface_vars[ii_var][1]
            ocproc_data['surface'].append(temp_data)
            #print(ocproc_data['surface'])            
        #surf_codes
        ocproc_data['surf_codes'] = []
        for ii in range(ocproc_data['header']['sparms']):
            ii_start = 0
            b_data = binFile.read(self.num_surf_code_byte_to_read)
            temp_data = dict()
            for ii_var in range(len(self.surf_code_vars)):
                temp_data[self.surf_code_vars[ii_var][0]]= self.decode_bytes(b_data[ii_start:(ii_start+ self.surf_code_vars[ii_var][1])],
                                                                                     self.surf_code_vars[ii_var][2])
                ii_start += self.surf_code_vars[ii_var][1]
            ocproc_data['surf_codes'].append(temp_data)    
 
        #history
        ocproc_data['history'] = []
        for ii in range(ocproc_data['header']['num_hist']):
            ii_start = 0
            temp_data = dict()
            b_data = binFile.read(28)
            for ii_var in range(len(self.history_vars)):
                temp_data[self.history_vars[ii_var][0]]= self.decode_bytes(b_data[ii_start:(ii_start+ self.history_vars[ii_var][1])],
                                                                                     self.history_vars[ii_var][2])
                ii_start += self.history_vars[ii_var][1]
            ocproc_data['history'].append(temp_data)    
        
    
        ## reading the profile section
        if (self.LINE_CONTROL_SEQUENCE == 'UNIX'):
            binFile.read(self.skipBytes)
        elif(self.LINE_CONTROL_SEQUENCE == 'WINDOWS'):
            binFile.read(self.skipBytes)
        # Skip the byte of padding if the record size is an odd number for VMS
        # (VMS padds the end of the record witha 0x00 byte if the record size is odd)
        if (self.LINE_CONTROL_SEQUENCE == 'VMS' and self.vmsEventRecordSizeIsOdd):
            binFile.read(self.skipBytes)
            print('VMS line control sequence and vmsEventRecordSizeIsOdd')
            
        ## profile.fxd section
        ocproc_data['profile_rec']=[]

        for ii_profileSeg in range (self.numberOfProfileSegments):
            self.vmsEventRecordSizeIsOdd = False
            if (self.LINE_CONTROL_SEQUENCE == 'VMS'):
                self.vmsRecordSize = int.from_bytes(b_data[0:2], byteorder = 'little')
                print ('vmsRecordSize:', self.vmsRecordSize)
                if (self.vmsRecordSize % 2 != 0):
                    self.vmsEventRecordSizeIsOdd = True
                    self.numberOfOddRecordSizes += self.numberOfOddRecordSizes
                        
            ii_start = 0  
            temp_data = {'profile_header': dict()}
            b_data = binFile.read(49) # profile structured FXD
            for ii_var in range(len(self.header_vars_prof)): 
                temp_data['profile_header'][self.header_vars_prof[ii_var][0]] = self.decode_bytes(b_data[ii_start:(ii_start+self.header_vars_prof[ii_var][1])], 
                                                                                    self.header_vars_prof[ii_var][2]) 
                ii_start +=self.header_vars_prof[ii_var][1]
            

            ocproc_data['profile_rec'].append(temp_data)
            
            no_depth_values = temp_data['profile_header'][self.header_vars_prof[9][0]]
        
            #profile depths
            for ii in range(no_depth_values):
                ii_start = 0
                temp_data = {'profile_var': dict()}
                b_data = binFile.read(10)
                for ii_var in range(len(self.profile_level_var)):
                    temp_data['profile_var'][self.profile_level_var[ii_var][0]]= self.decode_bytes(b_data[ii_start:(ii_start+ self.profile_level_var[ii_var][1])],
                                                                                     self.profile_level_var[ii_var][2])
                    ii_start += self.profile_level_var[ii_var][1]

                    
                ocproc_data['profile_rec'].append(temp_data)   
             
            if (self.LINE_CONTROL_SEQUENCE == 'WINDOWS'):
                binFile.read(self.skipBytes)


        return ocproc_data
    
    
    
    
    def decode_bytes(self,ocproc_bytes, output_type):
        
        '''
        Decode OCPROC bytes. Decoding based on the original Java code (courtesy of Anh Tran)
        '''
        if output_type=='s':
            output_data = ocproc_bytes.decode()

        elif output_type in ['h','i']:
            output_data = struct.unpack(output_type,ocproc_bytes)[0]

        elif output_type=='f':
                 
            if self.FLOATING_POINT_ENCODING == "FLOATING_POINT_ENCODING_VMS":                    

                #converting from mid-endian
                temp_buffer =  bytearray(len(ocproc_bytes))
                temp_buffer[0]=ocproc_bytes[2]
                temp_buffer[1]=ocproc_bytes[3]
                temp_buffer[2]=ocproc_bytes[0]
                temp_buffer[3]=ocproc_bytes[1]
                                                            
                output_data = struct.unpack('>f',struct.pack('>l',struct.unpack('>l',struct.pack('>f',struct.unpack('f',temp_buffer)[0]))[0]-16777216))[0]

                ''' statement breakdown
                a = struct.unpack('f',temp_buffer)[0]                
                b = struct.pack('>f', a)
                c = struct.unpack('>l', b)[0]  
                d = struct.pack('>l', c - 16777216)  
                e = struct.unpack ('>f', d)[0]
                print ('e:', e)
                '''
            else:
               # https://stackoverflow.com/questions/14431170/get-the-bits-of-a-float-in-python,
               output_data = struct.unpack('>f',struct.pack('>l',struct.unpack('>l',struct.pack('>f',struct.unpack('f',ocproc_bytes)[0]))[0]-16777216))[0]

            
            if (output_data == -170141183460469230000000000000000000000.000):
                  output_data = 0.0;
    
            
        return output_data


    def encode_bytes(self,ocproc_bytes, output_type):
        
        '''
        Encode OCPROC bytes for writing to output file.
        '''
        if output_type=='s':
            output_data = ocproc_bytes.encode()

        elif output_type in ['h','i']:
            output_data = struct.pack(output_type,ocproc_bytes)

        elif output_type=='f':
                 
#           floating point for Windows encoding
            if (ocproc_bytes) != 0.0:
                a = struct.pack('>f', ocproc_bytes)
                b = struct.unpack('>l', a)[0]
                c = struct.pack ('>l', b + 16777216)
                d = struct.unpack('>f', c)[0]
                output_data = struct.pack('f', d)          
            else:
                output_data = struct.pack('>f', 0)
         
        return output_data

    def encode_bytes_vms(self,ocproc_bytes, output_type):
        
        '''
        Encode OCPROC bytes for writing to output file.
        '''
        if output_type=='s':
            output_data = ocproc_bytes.encode()

        elif output_type in ['h','i']:
            output_data = struct.pack(output_type,ocproc_bytes)

        elif output_type=='f':
              
            if (ocproc_bytes) != 0.0:
                a = struct.pack('>f', ocproc_bytes)
                b = struct.unpack('>l', a)[0]
                c = struct.pack ('>l', b + 16777216)
                d = struct.unpack('>f', c)[0]
                temp = struct.pack('f', d)
                
                #converting back to mid-endian
                temp_buffer =  bytearray(len(temp))
                temp_buffer[2]=temp[0]
                temp_buffer[3]=temp[1]
                temp_buffer[0]=temp[2]
                temp_buffer[1]=temp[3]
                
                output_data = temp_buffer
                
            else:
                output_data = struct.pack('>f', 0)
         
        return output_data

    def skipBytes(self, binFile, numOfBytes):
        binFile.read(numOfBytes)
    '''
    https://stackoverflow.com/questions/8751653/how-to-convert-a-binary-string-into-a-float-value
    '''
    def bin_to_float(self,b):
        #Convert binary string to a float.
        bf = self.int_to_bytes(int(b, 2), 8)  # 8 bytes needed for IEEE 754 binary64.
        return struct.unpack('>d', bf)[0]


    def int_to_bytes(self, n, length):  # Helper function
    
        '''
        Int/long to byte string.
        Python 3.2+ has a built-in int.to_bytes() method that could be used
        instead, but the following works in earlier versions including 2.x.
        '''
        
        return decode('%%0%dx' % (length << 1) % n, 'hex')[-length:]


    def float_to_bin(self, value):  # For testing.
        """ Convert float to 64-bit binary string. """
        [d] = struct.unpack(">Q", struct.pack(">d", value))
        return '{:064b}'.format(d)
    '''
    Method to extract the value of surface.parm or surf_codes.cparm when passing a pcode
    '''
    def find_pcode_value (self, _codes, _pcode, _codeValueFieldName):
        pcode_value = ''
        for i in range (len(_codes)):        
            if (_codes[i]['pcode'].strip()== _pcode ):
                pcode_value = _codes[i][_codeValueFieldName]
                if (type(pcode_value) == str):
                    pcode_value = pcode_value.strip()
        return pcode_value
