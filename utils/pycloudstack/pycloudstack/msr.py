"""
MSR(Model Specific Register) class to operate the MSR register.

"""

import os
import glob
import struct
import logging

__author__ = 'cpio'

LOG = logging.getLogger(__name__)


class MSR:

    """
    MSR(Model Specific Register) Class

    /dev/cpu/CPUNUM/msr provides an interface to read and write the
    model-specific registers (MSRs) of an x86 CPU.  CPUNUM is the
    number of the CPU to access as listed in /proc/cpuinfo.

    The register access is done by opening the file and seeking to
    the MSR number as offset in the file, and then reading or writing
    in chunks of 8 bytes.  An I/O transfer of more than 8 bytes means
    multiple reads or writes of the same register.

    This file is protected so that it can be read and written only by
    the user root, or members of the group root.

    For more information about the MSR, please read https://man7.org/linux/man-pages/man4/msr.4.html
    """

    IA32_FEATURE_CONTROL = 0x3a
    IA32_TME_ACTIVATE = 0x982

    def __init__(self):
        self._check_kmod()

    @staticmethod
    def _check_kmod():
        """
        Check whether the MSR is loaded, modprobe if not.
        """
        if not os.path.exists("/dev/cpu/0/msr"):
            os.system("modprobe msr")

    @staticmethod
    def readmsr(msr, highbit=63, lowbit=0, cpu=0):
        """
        Read MSR register
        """
        assert abs(msr) < 0xffffffff
        assert os.geteuid() == 0, "need root priviledge"

        try:
            fdobj = os.open(f'/dev/cpu/{cpu}/msr', os.O_RDONLY)
        except (IOError, OSError) as err:
            LOG.error("Fail to open MSR device file: %d", err.errno)
            return None

        os.lseek(fdobj, msr, os.SEEK_SET)
        val = struct.unpack('Q', os.read(fdobj, 8))[0]
        os.close(fdobj)

        bits = highbit - lowbit + 1
        if bits < 64:
            val >>= lowbit
            val &= (1 << bits) - 1

        return val

    @staticmethod
    def writemsr(msr, val):
        """
        Write MSR register
        """
        assert abs(msr) < 0xffffffff
        assert os.geteuid() == 0, "need root priviledge"

        items = glob.glob('/dev/cpu/[0-9]*/msr')
        for cpu in items:
            try:
                fdobj = os.open(cpu, os.O_WRONLY)
            except (IOError, OSError) as err:
                LOG.error("Fail to open MSR device file: %d", err.errno)
                return False

            os.lseek(fdobj, msr, os.SEEK_SET)

            try:
                os.write(fdobj, struct.pack('Q', val))
            except (IOError, OSError) as err:
                LOG.error("Fail to write MSR device file: %d", err.errno)
                os.close(fdobj)
                return False

            os.close(fdobj)

        return True
