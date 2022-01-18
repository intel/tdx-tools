"""
Manage the DUT(Device Under Test)
"""
import logging
import socket
from contextlib import closing
import cpuinfo

__author__ = 'cpio'

LOG = logging.getLogger(__name__)


class DUT:
    """
    Manange DUT device
    """

    @staticmethod
    def support_tdx():
        """
        Check whether support TDX in CPU info
        """
        return 'tdx' in cpuinfo.get_cpu_info()['flags']

    @staticmethod
    def support_sgx():
        """
        Check whether support TDX in CPU info
        """
        return 'sgx' in cpuinfo.get_cpu_info()['flags']

    @staticmethod
    def cmdline_contains(needle):
        """
        Check whether kernel command line contains given string
        """
        return DUT.file_contains("/proc/cmdline", needle)

    @staticmethod
    def file_contains(fpath, needle):
        """
        Check whether file contains given string
        """
        with open(fpath, "r", encoding="utf8") as fobj:
            for line in fobj.readlines():
                if needle in line:
                    return True
        return False

    @staticmethod
    def find_free_port():
        """
        Find a free port on dut device for container service.
        """
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.bind(('', 0))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return sock.getsockname()[1]
        return None

    @staticmethod
    def check_port(port, ipaddr="127.0.0.1"):
        """
        Check whether a port is open to determine whether service started.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ipaddr, port))
        sock.close()
        if result == 0:
            LOG.debug("Port %d is opened", port)
            return True

        LOG.debug("Port %d is not opened", port)
        return False

    @staticmethod
    def get_cpu_base_freq():
        """
        psutil does not return correct frequency value, so read
        /sys/devices/system/cpu/cpu0/cpufreq/base_frequency
        """
        with open("/sys/devices/system/cpu/cpu0/cpufreq/base_frequency",
                "r", encoding="utf8") \
                as fobj:
            value = fobj.read()
            assert value is not None
            return int(value.strip())
        return None
