"""
Parse td quote struct, see:
https://software.intel.com/content/dam/develop/external/us/en/documents/tdx-module-1eas-v0.85.039.pdf  # pylint: disable=line-too-long
https://software.intel.com/content/dam/develop/external/us/en/documents-tps/intel-tdx-cpu-architectural-specification.pdf  # pylint: disable=line-too-long
"""
import hashlib
import logging

from .utility import DeviceNode

from .binaryblob import BinaryBlob

__author__ = "cpio"

LOG = logging.getLogger(__name__)


class TdQuote(BinaryBlob):
    """
    Struct TDREPORT_STRUCT
    """
    def __init__(self, data, device_node=None):
        super().__init__(data)
        # auxiliary fileds
        if device_node is None:
            device_node = DeviceNode()
        self.device_node = device_node

    @staticmethod
    def get_quote(nonce=None, user_data=None, report_data=None):
        """
        Perform ioctl on the device file, to get td-report
        """
        if report_data is not None:
            LOG.info("Using report data directly to generate quote")
        else:
            if nonce is None and user_data is None:
                LOG.info("No report data, generating default quote")
            else:
                LOG.info("Calculate report data by nonce and user data")
                hash_algo = hashlib.sha512()
                if nonce is not None:
                    hash_algo.update(bytes(nonce))
                if user_data is not None:
                    hash_algo.update(bytes(user_data))
                report_data = hash_algo.digest()
        device_node = DeviceNode()
        tdquote_bytes = device_node.get_tdquote_bytes(report_data)
        if tdquote_bytes is not None:
            quote = TdQuote(tdquote_bytes, device_node)
            return quote
        return None
