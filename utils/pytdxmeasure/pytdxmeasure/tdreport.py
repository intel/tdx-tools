"""
Parse td report struct, see:
https://software.intel.com/content/dam/develop/external/us/en/documents/tdx-module-1eas-v0.85.039.pdf  # pylint: disable=line-too-long
https://software.intel.com/content/dam/develop/external/us/en/documents-tps/intel-tdx-cpu-architectural-specification.pdf  # pylint: disable=line-too-long
"""

import os
import logging
import struct
import fcntl
from .binaryblob import BinaryBlob


__author__ = "cpio"

LOG = logging.getLogger(__name__)


class ReportMacStruct(BinaryBlob):
    """
    Struct REPORTMACSTRUCT
    """

    def __init__(self, data):
        super().__init__(data)
        self.report_type = None
        self.reserverd1 = None
        self.cpusvn = None
        self.tee_tcb_info_hash = None
        self.tee_info_hash = None
        self.report_data = None
        self.reserverd2 = None
        self.mac = None
        self.parse()

    def parse(self):
        """
        parse the raw data for Struct REPORTMACSTRUCT

        Struct REPORTMACSTRUCT's layout:
        offset, len
        0x0,    0x8     report_type
        0x8,    0x8     reserverd1
        0x10,   0x10    cpusvn
        0x20,   0x30    tee_tcb_info_hash
        0x50,   0x30    tee_info_hash
        0x80,   0x40    report_data
        0xc0,   0x20    reserverd2
        0xe0,   0x20    mac
        """
        offset = 0

        self.report_type, offset = self.get_bytes(offset, 0x8)
        self.reserverd1, offset = self.get_bytes(offset, 0x8)
        self.cpusvn, offset = self.get_bytes(offset, 0x10)
        self.tee_tcb_info_hash, offset = self.get_bytes(offset, 0x30)
        self.tee_info_hash, offset = self.get_bytes(offset, 0x30)
        self.report_data, offset = self.get_bytes(offset, 0x40)
        self.reserverd2, offset = self.get_bytes(offset, 0x20)
        self.mac, offset = self.get_bytes(offset, 0x20)


class TeeTcbInfo(BinaryBlob):
    """
    Struct TEE_TCB_INFO
    """

    def __init__(self, data):
        super().__init__(data)
        self.valid = None
        self.tee_tcb_svn = None
        self.mrseam = None
        self.mrsignerseam = None
        self.attributes = None
        self.reserved = None
        self.parse()

    def parse(self):
        """
        parse the raw data for Struct TEE_TCB_INFO

        Struct TEE_TCB_INFO's layout:
        offset, len
        0x0,    0x8     valid
        0x8,    0x10    tee_tcb_svn
        0x18,   0x30    mrseam
        0x48,   0x30    mrsignerseam
        0x78,   0x8     attributes
        0x80,   0x6f    reserved
        """
        offset = 0

        self.valid, offset = self.get_bytes(offset, 0x8)
        self.tee_tcb_svn, offset = self.get_bytes(offset, 0x10)
        self.mrseam, offset = self.get_bytes(offset, 0x30)
        self.mrsignerseam, offset = self.get_bytes(offset, 0x30)
        self.attributes, offset = self.get_bytes(offset, 0x8)
        self.reserved, offset = self.get_bytes(offset, 0x6f)


class TdInfo(BinaryBlob):
    """
    Struct TDINFO_STRUCT
    """

    def __init__(self, data):
        super().__init__(data)
        self.attributes = None
        self.xfam = None
        self.mrtd = None
        self.mrconfigid = None
        self.mrowner = None
        self.mrownerconfig = None
        self.rtmr_0 = None
        self.rtmr_1 = None
        self.rtmr_2 = None
        self.rtmr_3 = None
        self.reserved = None
        self.parse()

    def parse(self):
        '''
        parse the raw data for Struct TDINFO_STRUCT

        Struct TDINFO_STRUCT's layout:
        offset, len
        0x0,    0x8     attributes
        0x8,    0x8     xfam
        0x10,   0x30    mrtd
        0x40,   0x30    mrconfigid
        0x70,   0x30    mrowner
        0xa0,   0x30    mrownerconfig
        0xd0,   0x30    rtmr_0
        0x100,  0x30    rtmr_1
        0x130,  0x30    rtmr_2
        0x160,  0x30    rtmr_3
        0x190,  0x70    reserved
        '''
        offset = 0

        self.attributes, offset = self.get_bytes(offset, 0x8)
        self.xfam, offset = self.get_bytes(offset, 0x8)
        self.mrtd, offset = self.get_bytes(offset, 0x30)
        self.mrconfigid, offset = self.get_bytes(offset, 0x30)
        self.mrowner, offset = self.get_bytes(offset, 0x30)
        self.mrownerconfig, offset = self.get_bytes(offset, 0x30)
        self.rtmr_0, offset = self.get_bytes(offset, 0x30)
        self.rtmr_1, offset = self.get_bytes(offset, 0x30)
        self.rtmr_2, offset = self.get_bytes(offset, 0x30)
        self.rtmr_3, offset = self.get_bytes(offset, 0x30)


class TdReport(BinaryBlob):
    """
    Struct TDREPORT_STRUCT
    """

    def __init__(self, data):
        super().__init__(data)
        self.report_mac_struct = None
        self.tee_tcb_info = None
        self.reserved = None
        self.td_info = None
        self.parse()

    def parse(self):
        '''
        parse the raw data for Struct TDREPORT_STRUCT

        Struct TDREPORT_STRUCT's layout:
        offset, len
        0x0,    0x100   ReportMacStruct
        0x100,  0xef    TeeTcbInfo
        0x1ef,  0x11    Reserved
        0x200,  0x200   TdInfo
        '''
        offset = 0

        data, offset = self.get_bytes(offset, 0x100)
        self.report_mac_struct = ReportMacStruct(data)
        self.report_mac_struct.parse()

        data, offset = self.get_bytes(offset, 0xef)
        self.tee_tcb_info = TeeTcbInfo(data)
        self.tee_tcb_info.parse()

        data, offset = self.get_bytes(offset, 0x11)
        self.reserved = data

        data, offset = self.get_bytes(offset, 0x200)
        self.td_info = TdInfo(data)
        self.td_info.parse()

    @staticmethod
    def get_td_report(report_data=b'1' * 64):
        """
        Perform ioctl on the device file /dev/tdx-attes, to get td-report
        """
        tdx_attest_file = '/dev/tdx-attest'
        if not os.path.exists(tdx_attest_file):
            LOG.error("Could not find device node %s", tdx_attest_file)
            return None
        try:
            fd_tdx_attest = os.open(tdx_attest_file, os.O_RDWR)
        except (PermissionError, IOError, OSError):
            LOG.error("Fail to open file %s", tdx_attest_file)
            return None

        data = bytearray(1024)
        data[0:64] = report_data
        try:
            fcntl.ioctl(fd_tdx_attest,
                int.from_bytes(struct.pack('Hcb', 0x08c0, b'T', 1), 'big'),
                data)
        except OSError:
            LOG.error("Fail to execute ioctl for file %s", tdx_attest_file)
            os.close(fd_tdx_attest)
            return None
        os.close(fd_tdx_attest)

        report = TdReport(data)
        report.parse()
        return report
