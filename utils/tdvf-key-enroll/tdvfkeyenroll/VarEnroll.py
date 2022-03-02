#!/usr/bin python
# -*- coding: UTF-8 -*-

import argparse
import struct
import sys
import uuid
import time
import re
import os
from enum import Enum

VAR_ENROLL_VERSION = '0.10'
VAR_ENROLL_NAME = 'TDVF VarEnroll Utility'
EFI_GLOBAL_VARIABLE = '8BE4DF61-93CA-11d2-AA0D-00E098032B8C'
EFI_IMAGE_SECURITY_DATABASE_GUID = "d719b2cb-3d3a-4596-a3bc-dad00e67656f"

def is_guid(s):
    if s is None or type(s) is not str:
        return False
    c = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}')
    res = c.match(s.lower())
    return False if res is None else True


def guid2str(b):
    '''Convert binary GUID to string.'''
    if len(b) != 16:
        return ""
    a, b, c, d = struct.unpack("<IHH8s", b)
    d = ''.join('%02x' % c for c in bytes(d))
    return "%08x-%04x-%04x-%s-%s" % (a, b, c, d[:4], d[4:])


def str2guid(s):
    '''
        Convert string GUID to binary
        "aaf32c78-947b-439a-a180-2e144ec37792"
    '''
    if s is None or not is_guid(s):
        raise Exception("Invalid GUID string - %s" %("" if s is None else s))

    fields = uuid.UUID(s).fields
    guid1 = struct.pack('<IHHBB', fields[0], fields[1], fields[2], fields[3], fields[4])
    guid2 = struct.pack('>Q', fields[5])
    return guid1 + guid2[2:]


def str2blob(s):
    '''
        Convert string to blob, such as:
        'PK' => b'50 00 4B 00 00 00'
    '''
    sarray = s.encode()
    blob = b''
    for s in sarray:
        b = struct.pack('<H', s)
        blob += b
    return blob + b'\0\0'


def ALIGN_BY_4(val):
    return (val + 3) & (~3)


def ALIGN_BY_8(val):
    return (val + 7) & (~7)


class FirmwareVolume:
    '''Describes the features and layout of the firmware volume.
    See PI Spec 3.2.1
    struct EFI_FIRMWARE_VOLUME_HEADER {
        UINT8: Zeros[16]
        UCHAR: FileSystemGUID[16]
        UINT64: Length
        UINT32: Signature (_FVH)
        UINT8: Attribute mask
        UINT16: Header Length
        UINT16: Checksum
        UINT16: ExtHeaderOffset
        UINT8: Reserved[1]
        UINT8: Revision
        [<BlockMap>]+, <BlockMap(0,0)>
    };
    '''

    _HEADER_SIZE = 0x38
    _NVRAM = "fff12b8d-7696-4c8b-a985-2747075b4f50"

    name = None

    def __init__(self, data):
        self.valid_header = False
        try:
            header = data[:self._HEADER_SIZE]
            self.rsvd, self.guid, self.size, self.magic, self.attributes, \
            self.hdrlen, self.checksum, self.extHeaderOffset, self.rsvd2, \
            self.revision = struct.unpack("<16s16sQ4sIHHH1sB", header)
        except Exception as e:
            print("Exception in FirmwareVolume::__init__: %s" % (str(e)))
            return

        if self.magic != b'_FVH':
            return

        str_guid = guid2str(self.guid)
        if str_guid == self._NVRAM:
            self.name = "NVRAM"
        else:
            return

        self.valid_header = True
        pass


class EfiTime:
    '''
    ///
    /// EFI Time Abstraction:
    ///  Year:       1900 - 9999
    ///  Month:      1 - 12
    ///  Day:        1 - 31
    ///  Hour:       0 - 23
    ///  Minute:     0 - 59
    ///  Second:     0 - 59
    ///  Nanosecond: 0 - 999,999,999
    ///  TimeZone:   -1440 to 1440 or 2047
    ///
    typedef struct {
      UINT16  Year;
      UINT8   Month;
      UINT8   Day;
      UINT8   Hour;
      UINT8   Minute;
      UINT8   Second;
      UINT8   Pad1;
      UINT32  Nanosecond;
      INT16   TimeZone;
      UINT8   Daylight;
      UINT8   Pad2;
    } EFI_TIME;
    '''

    def __init__(self, data=None):
        self.valid = False
        if data is None:
            data = b'\x00' * 16
        try:
            self.year, self.month, self.day, self.hour, self.minute, self.second, \
            self.pad1, self.nanosecond, self.timezone, self.daylight, self.pad2 \
                = struct.unpack('<HBBBBBBIHBB', data)
        except Exception as e:
            return
        self.valid = True
        pass

    @staticmethod
    def now():
        curr = time.gmtime()
        et = EfiTime()
        et.year = curr.tm_year
        et.month = curr.tm_mon
        et.day = curr.tm_mday
        et.hour = curr.tm_hour
        et.minute = curr.tm_min
        et.second = curr.tm_sec
        et.pad1 = 0
        et.nanosecond = 0
        et.timezone = 0
        et.daylight = 0
        et.pad2 = 0
        return et

    def blob(self):
        return struct.pack('<HBBBBBBIHBB', self.year, self.month, self.day, \
                           self.hour, self.minute, self.second, self.pad1, \
                           self.nanosecond, self.timezone, self.daylight, self.pad2)

    def dump(self):
        return "%04d-%02d-%02dT%02d:%02d:%02d" % (self.year, self.month, self.day, self.hour, self.minute, self.second)

    pass


class EfiVariableAuthentication2:
    '''

    typedef struct _WIN_CERTIFICATE {
      UINT32  dwLength;
      UINT16  wRevision;
      UINT16  wCertificateType;
      //UINT8 bCertificate[ANYSIZE_ARRAY];
    } WIN_CERTIFICATE;

    typedef struct _WIN_CERTIFICATE_UEFI_GUID {
      WIN_CERTIFICATE   Hdr;
      EFI_GUID          CertType;
      UINT8             CertData[1];
    } WIN_CERTIFICATE_UEFI_GUID;

    typedef struct {
      EFI_TIME                    TimeStamp;
      WIN_CERTIFICATE_UEFI_GUID   AuthInfo;
     } EFI_VARIABLE_AUTHENTICATION_2;

    '''
    def __init__(self, data):
        self.valid = False
        if data is None or len(data) < 20:
            return
        self.time_stamp = EfiTime(data[:16])
        if not self.time_stamp.valid:
            return
        self.authinfo_2_size = struct.unpack('<I', data[16:20])[0]
        self.authinfo_2_size += 16
        self.valid = True
        pass
    pass


class VariableTimeBasedAuth:
    '''
    Represents the Time based authenticated Variable Header
    typedef struct {
      UINT16      StartId;  // 0x55AA
      UINT8       State;
      UINT8       Reserved;
      UINT32      Attributes;
      UINT64      MonotonicCount;
      EFI_TIME    TimeStamp;    // 16 bytes
      UINT32      PubKeyIndex;
      UINT32      NameSize;
      UINT32      DataSize;
      EFI_GUID    VendorGuid;
    } VARIABLE_HEADER_TIME_BASED_AUTH;
    '''
    _VAR_START_ID = 0x55aa
    _VAR_IN_DELETED_TRANSITION = 0xfe
    _VAR_DELETED = 0xfd
    _VAR_HEADER_VALID_ONLY = 0x7f

    VAR_ADDED = 0x3f
    HEADER_SIZE = 60

    def __init__(self, data=None):
        self.valid_header = False
        self.raw_data = None
        self.name_blob = None
        self.name = None
        self.data = None
        self.start_id = 0x55aa
        self.state = 0x3f
        self.rsvd = 0
        self.attributes = 0
        self.count = 0
        self.time_stamp_blob = None
        self.time_stamp = None
        self.pk_index = 0
        self.name_size = 0
        self.data_size = 0
        self.vendor_guid = None
        self.full_size = 0
        self.vendor_guid_str = None
        self.valid_header = False

        if data is None:
            return

        try:
            self.start_id, self.state, self.rsvd, self.attributes, \
            self.count, self.time_stamp_blob, self.pk_index, \
            self.name_size, self.data_size, self.vendor_guid \
                = struct.unpack('<HBBIQ16sIII16s', data[:self.HEADER_SIZE])
        except Exception as e:
            print("Exception in parsing VariableTimeBasedAuth header - " + str(e))
            return
        self.time_stamp = EfiTime(self.time_stamp_blob)
        if not self.time_stamp.valid:
            return

        self.full_size = self.data_size + self.name_size + self.HEADER_SIZE
        self.vendor_guid_str = guid2str(self.vendor_guid)
        self.valid_header = True
        pass

    def update(self, attributes, time_stamp, buffer, size, append):
        self.attributes = attributes
        self.time_stamp = time_stamp
        self.time_stamp_blob = time_stamp.blob()

        if append:
            self.data += buffer
            self.data_size += size
            self.full_size = self.data_size + self.name_size + self.HEADER_SIZE
        else:
            self.data = buffer
            self.data_size = size
        return True

    def blob(self):
        blob = struct.pack("<HBBIQ16sIII16s", \
                           self.start_id, self.state, self.rsvd, self.attributes, \
                           self.count, self.time_stamp_blob, self.pk_index, \
                           self.name_size, self.data_size, self.vendor_guid)
        blob += self.name_blob
        blob += self.data
        return blob

    def parse_body(self):
        if not self.valid_header or not self.raw_data:
            raise Exception("Invalid header or raw_data")

        ## name
        self.name_blob = self.raw_data[self.HEADER_SIZE: self.HEADER_SIZE + self.name_size]
        self.name = self.name_blob.decode()

        ## data
        self.data = self.raw_data[self.HEADER_SIZE + self.name_size:]

    def dump(self):
        print(">>  name           : %s" % self.name)
        print("    vendor_guid    : %s" % self.vendor_guid_str)
        print("    full size      : 0x%x" % self.full_size)
        print("    attributes     : 0x%x" % self.attributes)
        print("    state          : 0x%x" % self.state)
        print("    Monotonic Cnt  : 0x%x" % self.count)
        print("    PubKey Index   : 0x%x" % self.pk_index)
        print("    TimeStamp      : %s" % self.time_stamp.dump())

    pass


class VariableStore:
    '''
    Describe the layout of Variable Store
    typedef struct {
      EFI_GUID  Signature;
      // Size of entire variable store,
      // including size of variable store header but not including the size of FvHeader.
      UINT32  Size;
      // Variable region format state.
      UINT8   Format;
      // Variable region healthy state.
      UINT8   State;
      UINT16  Reserved;
      UINT32  Reserved1;
    } VARIABLE_STORE_HEADER;

    '''
    _EFI_VARIABLE_GUID = \
        "ddcf3616-3275-4164-98b6-fe85707ffe7d"
    _EFI_AUTHENTICATED_VARIABLE_BASED_TIME_GUID = \
        "aaf32c78-947b-439a-a180-2e144ec37792"
    _EFI_AUTHENTICATED_VARIABLE_GUID = \
        "515fa686-b06e-4550-9112-382bf1067bfb"
    _HEADER_SIZE = 28

    def __init__(self, fv, offset_in_fd):
        '''
        :param  fv          : the Variable Firmware Volume
        :param  offset_in_fd: offset of the fv in FD
        '''
        self.fv = fv
        self.offset_in_fd = offset_in_fd + fv.hdrlen
        self.vars_size = 0
        self.header = fv.raw_data[fv.hdrlen: fv.hdrlen + self._HEADER_SIZE]
        try:
            self.signature, self.size, self.format, self.state, self.rsvd, self.rsvd1 \
                = struct.unpack("<16sIBBHI", self.header)
        except Exception as e:
            print("Exception in parsing VariableStore header - " + str(e))
            return

        self.raw_data = fv.raw_data[fv.hdrlen:]
        self.type, supported = self.check_type(self.signature)
        self.vars_list = []
        self.valid_header = supported

    def del_variable(self, name, vendor_guid):
        '''
        Delete a variable
        '''
        vars_count = len(self.vars_list)
        if vars_count == 0:
            return False

        name_blob = str2blob(name)
        i = 0
        hit = False
        for i in range(vars_count):
            var = self.vars_list[i]
            if var.name_blob == name_blob and var.vendor_guid_str == vendor_guid.lower():
                hit = True
                break
        if not hit:
            return False

        del self.vars_list[i]
        return True

    def add_variable(self, name, vendor_guid, attributes, time_stamp, buffer, size, append):
        '''
        add/append an variable into VariableStore
        '''
        if (attributes & EfiVariableAttributes.TIMEBASED_AUTH_WRITE_ACCESS.value) != 0 and time_stamp is None:
            time_stamp = EfiTime.now()
        if time_stamp is None:
            time_stamp = EfiTime()

        var = self.find_var_in_list(name, vendor_guid)
        if var:
            ## update the variable
            return var.update(attributes, time_stamp, buffer, size, append)

        ## create a new variable
        var = VariableTimeBasedAuth()
        var.time_stamp = time_stamp
        var.time_stamp_blob = time_stamp.blob()
        var.data_size = size
        var.data = buffer
        var.attributes = attributes
        var.name = name
        var.name_blob = str2blob(name)
        var.name_size = len(var.name_blob)
        var.vendor_guid_str = vendor_guid.lower()
        var.vendor_guid = str2guid(vendor_guid)
        var.full_size = var.data_size + var.name_size + var.HEADER_SIZE
        var.valid_header = True
        self.vars_list.append(var)

        return True

    def find_var_in_list(self, name, vendor_guid):
        name_blob = str2blob(name)
        for var in self.vars_list:
            if var.name_blob == name_blob and var.vendor_guid_str == vendor_guid.lower():
                return var
        return None

    def sync_to_file(self, fd_data, output_file):
        '''
        Sync the self.vars_list to the output_file
        '''
        ret = False
        fd_size = len(fd_data)
        buffer = bytearray(fd_size)
        buffer[:] = fd_data[:]

        # clear the Variable Region
        vars_start = self.offset_in_fd + self._HEADER_SIZE
        size = self.size - self._HEADER_SIZE
        buffer[vars_start: vars_start + size] = b'\xff' * size

        # generate the blob of the variables
        blob = b''
        for var in self.vars_list:
            b = var.blob()
            blen = len(b)
            blen_aligned = ALIGN_BY_4(blen)
            pad = blen_aligned - blen
            if pad > 0:
                b += b'\xff' * pad
            blob += b

        # copy the blob to variables region in VariableStore
        blob_size = len(blob)
        if blob_size > 0:
            buffer[vars_start: vars_start + blob_size] = blob

        # save to output file
        try:
            with open(output_file, 'wb') as fo:
                fo.write(buffer)
                fo.flush()
            ret = True
        except Exception as e:
            print("Error: Cannot write variables to file (%s) (%s)." % (output_file, str(e)))

        return ret

    def sync_to_vars_list(self):
        '''
        Sync the vars in VariableFV to self.vars_list
        '''
        begin = self._HEADER_SIZE
        end = self.size
        while begin < end:
            ## check if it is valid variable
            sig = struct.unpack('<H', self.raw_data[begin: begin + 2])
            if sig[0] != 0x55aa:
                break
            ##
            ## we only support Time based authenticated variable now
            ## get the header of VariableTimeBasedAuth
            var = VariableTimeBasedAuth(self.raw_data[begin:begin + VariableTimeBasedAuth.HEADER_SIZE])
            if not var.valid_header:
                break
            var.raw_data = self.raw_data[begin:begin + var.full_size]
            begin += var.full_size
            begin = ALIGN_BY_4(begin)

            if var.state != VariableTimeBasedAuth.VAR_ADDED:
                continue

            var.parse_body()
            self.vars_list.append(var)

        self.vars_size = begin - self._HEADER_SIZE
        pass

    def check_type(self, signature):
        str_guid = guid2str(signature)
        type = None
        supported = False
        if str_guid == self._EFI_VARIABLE_GUID:
            type = 'Normal'
        elif str_guid == self._EFI_AUTHENTICATED_VARIABLE_GUID:
            type = 'Authenticated'
        elif str_guid == self._EFI_AUTHENTICATED_VARIABLE_BASED_TIME_GUID:
            type = 'TimeBasedAuthenticated'
            supported = True
        else:
            type = 'Unknown'
        pass

        print("VariableFV: %s - %s" % (type, 'Supported' if supported else 'Unsupported'))
        return (type, supported)

    def dump(self):
        '''
        Dump the information of Variable Store information
        '''
        ## dump header
        # signature
        print("Signature    : %s" % guid2str(self.signature))
        # type
        print("Type         : %s" % self.type)
        # format
        print("Format       : 0x%x" % self.format)
        # state
        print("State        : 0x%x" % self.format)
        # header size
        print("Header size  : 0x%x" % self._HEADER_SIZE)
        # body size
        print("Body size    : 0x%x" % self.size)
        # full size
        print("Full size    : 0x%x" % (self.size + self._HEADER_SIZE))

        print("Variables    : %d" % len(self.vars_list))
        ## dump variable list
        for var in self.vars_list:
            var.dump()

        return True

    pass


class EfiSignatureList:
    '''
    typedef struct {
      EFI_GUID            SignatureType;
      UINT32              SignatureListSize;
      UINT32              SignatureHeaderSize;
      UINT32              SignatureSize;
      //UINT8             SignatureData
    } EFI_SIGNATURE_LIST;
    '''
    SIZE = 28

    def __init__(self):
        self.SignatureType = None
        self.SignatureListSize = 0
        self.SignatureHeaderSize = 0
        self.SignatureSize = 0
        self.SignatureData = None
        pass

    def blob(self):
        blob1 = struct.pack('<III', self.SignatureListSize, self.SignatureHeaderSize, self.SignatureSize)
        return self.SignatureType + blob1 + self.SignatureData

    pass


class EfiSignatureData:
    '''
    typedef struct {
      EFI_GUID          SignatureOwner;
      UINT8             SignatureData[1];
    } EFI_SIGNATURE_DATA;
    '''
    SIZE = 16

    def __init__(self):
        self.SignatureOwner = None
        self.SignatureData = None

    def blob(self):
        '''concat the fields into one binary blob'''
        return self.SignatureOwner + self.SignatureData

    pass


class EfiVariableAttributes(Enum):
    NON_VOLATILE = 0x1
    BOOTSERVICE_ACCESS = 0x2
    RUNTIME_ACCESS = 0x4
    TIMEBASED_AUTH_WRITE_ACCESS = 0x20
    pass


def find_var_info(input_data):
    '''
    walk thru fd to find out Variable FV
    :param input_data: data of fd
    :return: VariableStore object
    '''
    total_len = len(input_data)

    ## walk thru input_data
    offset = 0
    fv = None
    while offset < total_len:
        data = input_data[offset:offset + 128]
        fv = FirmwareVolume(data)
        if fv.valid_header == True:
            if fv.name == "NVRAM":
                fv.raw_data = input_data[offset:offset + fv.size]
                break

    if not fv.valid_header:
        return None

    ## now the VariableStore
    var_store = VariableStore(fv, offset)
    if not var_store.valid_header:
        return None

    var_store.sync_to_vars_list()

    return var_store


def CreatePkX509CertificateList(cert_file, signature_owner):
    '''
    Create a signature list which contains the PK X509 cert list
    '''
    ## check the input params
    if signature_owner is None:
        raise Exception('Signature owner is empty!')

    sig_owner = str2guid(signature_owner)
    if len(sig_owner) != 16:
        raise Exception('Invalid Signature owner. - ' + signature_owner)

    try:
        with open(cert_file, 'rb') as fc:
            cert_data = fc.read()
    except Exception as e:
        raise Exception("Error: Cannot read file (%s) (%s)." % (cert_file, str(e)))

    ##
    EFI_CERT_X509_GUID = "a5c059a1-94e4-4aa7-87b5-ab155c2bf072"
    sig_list = EfiSignatureList()
    sig_list.SignatureListSize = EfiSignatureList.SIZE + EfiSignatureData.SIZE + len(cert_data)
    sig_list.SignatureSize = EfiSignatureData.SIZE + len(cert_data)
    sig_list.SignatureHeaderSize = 0
    sig_list.SignatureType = str2guid(EFI_CERT_X509_GUID)

    sig_data = EfiSignatureData()
    sig_data.SignatureOwner = sig_owner
    sig_data.SignatureData = cert_data

    sig_list.SignatureData = sig_data.blob()

    return sig_list


def EnrollPlatformKey(guid, cert_file, var_store):
    '''
    Enroll the PK

    :param  guid        : the guid of the signature owner in X509 cert
    :param  cert_file   : the input X509 cert file
    :param  var_store   : the input VariableStore

    :return True if success
    '''
    sig_list = CreatePkX509CertificateList(cert_file, guid)
    attr = EfiVariableAttributes.NON_VOLATILE.value \
           | EfiVariableAttributes.RUNTIME_ACCESS.value \
           | EfiVariableAttributes.BOOTSERVICE_ACCESS.value \
           | EfiVariableAttributes.TIMEBASED_AUTH_WRITE_ACCESS.value

    ret = var_store.add_variable('PK', EFI_GLOBAL_VARIABLE, \
                                attr, None, sig_list.blob(), \
                                sig_list.SignatureListSize, False)
    return ret


def EnrollPlatformKeyExchangeKey(guid, cert_file, var_store, append=False):
    '''
    Enroll the KEK

    :param  guid        : the guid of the signature owner in X509 cert
    :param  cert_file   : the input X509 cert file
    :param  var_store   : the input VariableStore
    :param  append      : append in VariableStore

    :return True if success
    '''
    sig_list = CreatePkX509CertificateList(cert_file, guid)
    attr = EfiVariableAttributes.NON_VOLATILE.value \
           | EfiVariableAttributes.RUNTIME_ACCESS.value \
           | EfiVariableAttributes.BOOTSERVICE_ACCESS.value \
           | EfiVariableAttributes.TIMEBASED_AUTH_WRITE_ACCESS.value

    ret = var_store.add_variable('KEK', EFI_GLOBAL_VARIABLE,
                                 attr, None, sig_list.blob(),
                                 sig_list.SignatureListSize, append)
    return ret


def EnrollSignatureDB(name, guid, data_file, var_store, append=False):
    '''
    Enroll the db/dbx

    :param  name        : name of the signature db, i.e. db/dbx
    :param  guid        : the guid of the signature owner in X509 cert or a bin file
    :param  data_file   : for db it is a X509 cert file, for dbx it is a bin file
    :param  var_store   : the input VariableStore
    :param  append      : append the variable

    :return True if success
    '''
    supported_db = ['db', 'dbx']
    if name not in supported_db:
        raise Exception("Unsupported SignatureDB - " + name)

    if name == 'db':
        sig_list = CreatePkX509CertificateList(data_file, guid)
        blob = sig_list.blob()
        size = sig_list.SignatureListSize
        time_stamp = None
    elif name == 'dbx':
        try:
            with open(data_file, 'rb') as fc:
                data = fc.read()
        except Exception as e:
            raise Exception("Error: Cannot read file (%s) (%s)." % (data_file, str(e)))
        auth2 = EfiVariableAuthentication2(data)
        if not auth2.valid:
            raise Exception('Error: Cannot parse the dbx bin file(%s)' % (data_file))
        size = len(data) - auth2.authinfo_2_size
        blob = data[auth2.authinfo_2_size:]
        time_stamp = auth2.time_stamp
    else:
        raise Exception('Unsupported var name in EnrollSignatureDB - %s' % name)

    attr = EfiVariableAttributes.NON_VOLATILE.value \
           | EfiVariableAttributes.RUNTIME_ACCESS.value \
           | EfiVariableAttributes.BOOTSERVICE_ACCESS.value \
           | EfiVariableAttributes.TIMEBASED_AUTH_WRITE_ACCESS.value

    ret = var_store.add_variable(name, EFI_IMAGE_SECURITY_DATABASE_GUID,
                                 attr, time_stamp, blob, size, append)
    return ret


def EnrollVariable(name, guid, data_file, attributes, var_store, append=False):
    '''
    Enroll (add/append) a general variable

    :param  name        : name of the variable
    :param  guid        : guid of variable
    :param  data_file   : the input pay_load of the variable
    :param  attributes  : attributes of the variable
    :param  var_store   : the input VariableStore
    :param  append      : append the variable

    :return True if success
    '''

    try:
        with open(data_file, 'rb') as fc:
            pay_load = fc.read()
    except Exception as e:
        raise Exception("Error: Cannot read file (%s) (%s)." % (data_file, str(e)))

    ret = var_store.add_variable(name, guid, attributes, None, pay_load,
                                 len(pay_load), append)
    return ret


def DelVariable(name, guid, var_store):
    '''
    Delete a variable from the var_store
    '''
    ret = var_store.del_variable(name, guid)
    print('DelVariable(Del %s) - %s' % (name, 'Success' if ret else 'Failed'))
    return ret


def AddVariable(name, guid, data_file, attributes, var_store, append=False):
    '''
    Add/Append an Variable in the var_store

    :param  name        : name of the variable
    :param  guid        : for PK/KEK/db/dbx this param is the signature owner guid
                          for other variable, it is the vendor_guid
    :param  data_file   : the variable related data file,
                          for example, for PK/KEK/db, it is the cert file
                          for dbx, it is a bin file
                          for other variable, it is the related data file
    :param  attributes  : attributes of the variable. It maybe None
    :param  var_store   : the VariableStore object
    :param  append      : append the variable

    :return True if success
    '''

    op = 'append' if append else 'add'
    if name.lower() == 'pk':
        if append:
            raise Exception('PK cannot be appended.')
        ret = EnrollPlatformKey(guid, data_file, var_store)

    elif name.lower() == 'kek':
        ret = EnrollPlatformKeyExchangeKey(guid, data_file, var_store, append)

    elif name.lower() in ['db', 'dbx']:
        ret = EnrollSignatureDB(name.lower(), guid, data_file, var_store, append)

    else:
        ret = EnrollVariable(name, guid, data_file, attributes, var_store, append)

    return ret

def UpdateVariable(name, guid, data_file, attributes, var_store):
    '''
    Update an Variable in the var_store

    :param  name        : name of the variable
    :param  guid        : for PK/KEK/db/dbx this param is the signature owner guid
                          for other variable, it is the vendor_guid
    :param  data_file   : the variable related data file,
                          for example, for PK/KEK/db, it is the cert file
                          for dbx, it is a bin file
                          for other variable, it is the related data file
    :param  attributes  : attributes of the variable. It maybe None
    :param  var_store   : the VariableStore object

    :return True if success
    '''

    # first find the variable
    var = var_store.find_var_in_list(name, guid)
    if var is None:
        return False
    # then delete it
    var_store.del_variable(name, guid)

    # then add the new one
    return AddVariable(name, guid, data_file, attributes, var_store, True)

def process_var(args, var_store, fd_data):
    '''
    process the variable

    :param  args        : arguments how to process the variable
    :param  var_store   : the VariableStore object
    :param  fd_data     : the original data of the FD
    '''
    operation = args.operation
    if args.attributes:
        attr = int(args.attributes, 16)
    else:
        attr = 0

    if operation == VarEnrollOps.add:
        ret = AddVariable(args.name, args.guid, args.data_file, attr, var_store, False)

    elif operation == VarEnrollOps.append:
        ret = AddVariable(args.name, args.guid, args.data_file, attr, var_store, True)

    elif operation == VarEnrollOps.delete:
        ret = DelVariable(args.name, args.guid, var_store)

    elif operation == VarEnrollOps.update:
        ret = UpdateVariable(args.name, args.guid, args.data_file, attr, var_store)

    else:
        raise Exception("Unkown operation - %s"%("" if operation is None else operation))

    print('EnrollVariable(%s %s) - %s' % (str(operation), args.name, 'Success' if ret else 'Failed'))
    if ret:
        ## sync the var_store to a new FD
        ret = var_store.sync_to_file(fd_data, args.output)
        print('Write Variable(%s) - %s' % (args.name, 'Success' if ret else 'Failed'))

    return ret


class VarEnrollOps(Enum):
    add = 'add'
    delete = 'delete'
    append = 'append'
    update = 'update'

    def __str__(self):
        return self.value


def check_args(args):
    '''
    Check the input args
    '''
    if args.name is None:
        raise Exception("Variable name is missing. -n var_name")

    if not is_guid(args.guid):
        raise Exception("Invalid input guid. - " + args.guid)

    if args.operation == VarEnrollOps.delete:
        return True

    if not os.path.isfile(args.data_file):
        raise Exception("Invalid input data file - " + args.data_file)

    if args.name.lower() in ['pk', 'kek', 'db', 'dbx'] \
            and args.operation in [VarEnrollOps.append, VarEnrollOps.add, VarEnrollOps.update]:
        pass
    elif args.operation in [VarEnrollOps.append, VarEnrollOps.add, VarEnrollOps.update]:
        # for other var_name,
        # we need to check below arguments
        # args.attributes
        try:
            attr = args.attributes
            int(attr, 16)
        except Exception as e:
            raise Exception("Invalid input attributes - " + attr if attr else '')
        pass

    return True


def var_enroll(args):
    fd_file = args.fd
    if fd_file is None:
        print("Error: -f is missing.")
        return False

    try:
        with open(fd_file, 'rb') as ft:
            fd_data = ft.read()
    except Exception as e:
        print("Error: Cannot read file (%s) (%s)." % (fd_file, str(e)))
        return False

    var_store = find_var_info(fd_data)

    if var_store is None:
        print("Variable FV is not found.")
        return False

    if args.info:
        return var_store.dump()

    try:
        check_args(args)
    except Exception as e:
        print('Exception when check_args - ' + str(e))
        return False
    
    try:
        process_var(args, var_store, fd_data)
    except Exception as e:
        print('Exception when process_var - ' + str(e))
        return False

    return True


def main():
    argparser = argparse.ArgumentParser(
        description="Enroll variables into FD")

    argparser.add_argument(
        '-i', "--info", action="store_true",
        help="Print the variable info in the FD")

    argparser.add_argument(
        '-f', "--fd",
        help="The input FD file")

    argparser.add_argument(
        '-op', '--operation', type=VarEnrollOps, choices=list(VarEnrollOps),
        help="Operation of the VarEnroll"
    )

    argparser.add_argument(
        '-n', '--name',
        help="Name of the variable to be enrolled, such as PK/KEK/db/dbx/SecureBootEnable etc"
    )

    argparser.add_argument(
        '-g', '--guid',
        help="For PK/KEK/db/dbx, it is the guid of signature owner. For other variable, it is the vendor guid"
    )

    argparser.add_argument(
        '-a', "--attributes",
        help="For PK/KEK/db/dbx, this param is ignored. For other variable, this param is its attribute, e.g 0x3")

    argparser.add_argument(
        '-d', '--data_file',
        help="File related to the variable. For PK/KEK/db/dbx, it is the cert file. Otherwise it is the payload of "
             "the variable. "
    )

    argparser.add_argument(
        '-o', '--output',
        help='Output file after the var is enrolled'
    )

    args = argparser.parse_args()

    return var_enroll(args)

if __name__ == "__main__":
    print("%s - %s"%(VAR_ENROLL_NAME, VAR_ENROLL_VERSION))
    ret = main()
    exit(0) if ret else exit(1)
