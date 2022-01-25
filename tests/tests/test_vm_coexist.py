"""
This module provide the case to test the coexistance between TDX guest and non TD
guest. There are two types of non-TD guest:

1. Boot with legacy BIOS, it is default loader without pass "-loader" or "-bios"
   option
2. Boot with OVMF UEFI BIOS, will boot with "-loader" => OVMFD.fd compiled from
   the latest edk2 project.
"""

import logging
import pytest
from pycloudstack.vmparam import VM_TYPE_LEGACY, VM_TYPE_EFI, VM_TYPE_TD

__author__ = 'cpio'

LOG = logging.getLogger(__name__)


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.vm_image("latest-guest-image"),
    pytest.mark.vm_kernel("latest-guest-kernel"),
]


def test_tdguest_with_legacy_base(vm_factory):
    """
    Test the different type VM run parallel

    Test Steps
    ----------
    1. Launch a TD guest
    2. Launch a legacy guest
    3. Launch an OVMF guest
    """
    LOG.info("Create a TD guest")
    td_inst = vm_factory.new_vm(VM_TYPE_TD, auto_start=True)

    LOG.info("Create a legacy guest")
    legacy_inst = vm_factory.new_vm(VM_TYPE_LEGACY, auto_start=True)

    LOG.info("Create an OVMF guest")
    efi_inst = vm_factory.new_vm(VM_TYPE_EFI, auto_start=True)

    assert td_inst.wait_for_ssh_ready(), "Could not reach TD VM"
    assert legacy_inst.wait_for_ssh_ready(), "Could not reach legacy VM"
    assert efi_inst.wait_for_ssh_ready(), "Could not reach EFI VM"
