""" TDEL ACPI table for TDX Event Log.

see https://software.intel.com/content/dam/develop/external/us/en/documents/intel-tdx-guest-hypervisor-communication-interface.pdf> # pylint: disable=line-too-long

"""

import os
import logging

from .binaryblob import BinaryBlob

__author__ = "cpio"

LOG = logging.getLogger(__name__)


class TDEL(BinaryBlob):
    """
    Manage th TDEL ACPI table. It should run within TD guest.
    """

    @property
    def revision(self):
        """
        Revision value in integer
        """
        revision, _ = self.get_uint8(8)
        return revision

    @property
    def checksum(self):
        """
        Checksum value in integer
        """
        checksum, _ = self.get_uint8(9)
        return checksum

    @property
    def oem_id(self):
        """
        OEM ID value in byte array
        """
        oem_id, _ = self.get_bytes(10, 6)
        return oem_id

    @property
    def log_area_minimum_length(self):
        """
        LAML value in integer
        """
        laml, _ = self.get_uint64(40)
        return laml

    @property
    def log_area_start_address(self):
        """
        LASA value in integer
        """
        lasa, _ = self.get_uint64(48)
        return lasa

    def dump(self):
        """
        Dump the full information
        """
        super().dump()

        if not self.is_valid():
            LOG.error("TDEL is not valid")
            return

        LOG.info("Revision:     %d", self.revision)
        LOG.info("Length:       %d", self.length)
        LOG.info("Checksum:     %02X", self.checksum)
        LOG.info("OEM ID:       %s", self.oem_id)
        LOG.info("Log Lenght:   0x%08X", self.log_area_minimum_length)
        LOG.info("Log Address:  0x%08X", self.log_area_start_address)

    def is_valid(self):
        """
        Judge whether the TDEL data is valid.
        - Check the signature
        - Check the length
        """
        return self.length > 0 and \
            self.data[0:4] == b'TDEL' and \
            self.length == self.data[4]

    @staticmethod
    def create_from_acpi_file(acpi_file="/sys/firmware/acpi/tables/TDEL"):
        """
        Read the TDEL table from the /sys/firmware/acpi/tables/TDEL
        """
        if not os.path.exists(acpi_file):
            LOG.error("Could not find the ACPI file %s", acpi_file)
            return None

        try:
            with open(acpi_file, "rb") as fobj:
                data = fobj.read()
                assert len(data) > 0 and data[0:4] == b'TDEL', \
                    "Invalid TDEL table"
                return TDEL(data)
        except (PermissionError, OSError):
            LOG.error("Need root permission to open file %s", acpi_file)
            return None
