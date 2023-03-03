"""
This module provide the case to test shutdown for TD/EFI/Legacy guest via
libvirt with different modes.
shutdown mode: acpi|agent|initctl|signal|paravirt|hard
Quote from https://bugzilla.redhat.com/show_bug.cgi?id=1744156
"libvirt's QEMU driver, used to manage KVM guests, only supports
the 'agent' and 'acpi' reboot modes because those are the ones QEMU
itself supports. The 'signal' and 'initctl' modes are used by the LXC driver.
"""

import logging
import time
import pytest
from pycloudstack.vmparam import VM_TYPE_LEGACY, VM_STATE_SHUTDOWN, VM_TYPE_EFI, VM_TYPE_TD

__author__ = 'cpio'

LOG = logging.getLogger(__name__)


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.vm_image("latest-guest-image"),
    pytest.mark.vm_kernel("latest-guest-kernel"),
]

testdata = [
    (VM_TYPE_TD, "default"),
    (VM_TYPE_TD, "acpi"),
    (VM_TYPE_TD, "agent"),
    (VM_TYPE_EFI, "default"),
    (VM_TYPE_EFI, "acpi"),
    (VM_TYPE_EFI, "agent"),
    (VM_TYPE_LEGACY, "default"),
    (VM_TYPE_LEGACY, "acpi"),
    (VM_TYPE_LEGACY, "agent"),
]


@pytest.mark.parametrize("vm_type, mode", testdata)
def test_vm_shutdown_mode(vm_factory, vm_type, mode):
    """
    Test shutdown guest via Virsh operator with different mode
    """
    LOG.info("Create guest")
    inst = vm_factory.new_vm(vm_type, auto_start=True)
    inst.wait_for_ssh_ready()

    LOG.info("Shutdown guest")
    inst.shutdown(mode)

    # Sleep for a while
    time.sleep(3)
    assert inst.wait_for_state(VM_STATE_SHUTDOWN, timeout=60), "Shutdown fail"
