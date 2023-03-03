"""
Call "reboot" command within VM
"""

import logging
import time
import pytest
from pycloudstack.vmparam import VM_TYPE_LEGACY, VM_STATE_RUNNING, VM_TYPE_EFI, VM_TYPE_TD

__author__ = 'cpio'

LOG = logging.getLogger(__name__)


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.vm_image("latest-guest-image"),
    pytest.mark.vm_kernel("latest-guest-kernel"),
]


def test_tdvm_acpi_reboot(vm_factory, vm_ssh_pubkey, vm_ssh_key):
    """
    Test ACPI reboot for TDVM
    """
    LOG.info("Create TD guest")
    inst = vm_factory.new_vm(VM_TYPE_TD)
    inst.image.inject_root_ssh_key(vm_ssh_pubkey)

    # create and start VM instance
    inst.create()
    inst.start()
    assert inst.wait_for_ssh_ready()

    inst.ssh_run(["shutdown -r now"], vm_ssh_key)

    # Sleep for a while for shutdown first
    time.sleep(5)
    assert inst.wait_for_state(VM_STATE_RUNNING), "Reboot fail"
    assert inst.wait_for_ssh_ready(), "Reboot timeout"

def test_efi_acpi_reboot(vm_factory, vm_ssh_pubkey, vm_ssh_key):
    """
    Test ACPI reboot for EFI VM
    """
    LOG.info("Create EFI guest")
    inst = vm_factory.new_vm(VM_TYPE_EFI)
    inst.image.inject_root_ssh_key(vm_ssh_pubkey)

    # create and start VM instance
    inst.create()
    inst.start()
    assert inst.wait_for_ssh_ready()

    inst.ssh_run(["shutdown -r now"], vm_ssh_key)

    # Sleep for a while for shutdown first
    time.sleep(5)
    assert inst.wait_for_state(VM_STATE_RUNNING), "Reboot fail"
    assert inst.wait_for_ssh_ready(), "Reboot timeout"

def test_legacy_acpi_reboot(vm_factory, vm_ssh_pubkey, vm_ssh_key):
    """
    Test ACPI reboot for legacy VM
    """
    LOG.info("Create legacy guest")
    inst = vm_factory.new_vm(VM_TYPE_LEGACY)
    inst.image.inject_root_ssh_key(vm_ssh_pubkey)

    # create and start VM instance
    inst.create()
    inst.start()
    assert inst.wait_for_ssh_ready()

    inst.ssh_run(["shutdown -r now"], vm_ssh_key)

    # Sleep for a while for shutdown first
    time.sleep(5)
    assert inst.wait_for_state(VM_STATE_RUNNING), "Reboot fail"
    assert inst.wait_for_ssh_ready(), "Reboot timeout"
    