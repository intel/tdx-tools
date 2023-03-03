"""
This test module tests QEMU Guest Agent QMP command to shutdown a VM:
{"execute":"guest-shutdown"}
Please make sure QEMU guest agent is installed in your guest image.
"""

import logging
import pytest
from libvirt import libvirtError, VIR_ERR_AGENT_UNRESPONSIVE

from pycloudstack.vmparam import VM_TYPE_TD, VM_TYPE_EFI, VM_TYPE_LEGACY

__author__ = 'cpio'

LOG = logging.getLogger(__name__)

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.vm_image("latest-guest-image"),
    pytest.mark.vm_kernel("latest-guest-kernel"),
]


def test_tdvm_qga_shutdown(vm_factory):
    """
    Test shutting down a TD guest using QEMU Guest Agent command

    Step 1: Create TD guest
    Step 2: Send command to QEMU Guest agent to shutdown the TD guest
    """

    LOG.info("Create TD guest")
    inst = vm_factory.new_vm(VM_TYPE_TD)
    inst.create()
    inst.start()
    assert inst.wait_for_ssh_ready()

    LOG.info("Request QEMU Guest Agent to shutdown the TD guest")
    # QEMU Guest Agent shuts the TD guest down abruptly, checking
    # for VM state does not work.
    try:
        inst.vmm.qemu_agent_shutdown()
    except libvirtError as e:
        LOG.info(e)
        assert e.get_error_code() == VIR_ERR_AGENT_UNRESPONSIVE, "QEMU Guest Agent shutdown fail"

def test_efi_qga_shutdown(vm_factory):
    """
    Test shutting down a EFI guest using QEMU Guest Agent command

    Step 1: Create EFI guest
    Step 2: Send command to QEMU Guest agent to shutdown the EFI guest
    """

    LOG.info("Create EFI guest")
    inst = vm_factory.new_vm(VM_TYPE_EFI)
    inst.create()
    inst.start()
    assert inst.wait_for_ssh_ready()

    LOG.info("Request QEMU Guest Agent to shutdown the EFI guest")
    try:
        inst.vmm.qemu_agent_shutdown()
    except libvirtError as e:
        LOG.info(e)
        assert e.get_error_code() == VIR_ERR_AGENT_UNRESPONSIVE, "QEMU Guest Agent shutdown fail"

def test_legacy_qga_shutdown(vm_factory):
    """
    Test shutting down a legacy VM using QEMU Guest Agent command

    Step 1: Create legacy VM
    Step 2: Send command to QEMU Guest agent to shutdown the legacy VM
    """

    LOG.info("Create legacy VM")
    inst = vm_factory.new_vm(VM_TYPE_LEGACY)
    inst.create()
    inst.start()
    assert inst.wait_for_ssh_ready()

    LOG.info("Request QEMU Guest Agent to shutdown the legacy VM")
    try:
        inst.vmm.qemu_agent_shutdown()
    except libvirtError as e:
        LOG.info(e)
        assert e.get_error_code() == VIR_ERR_AGENT_UNRESPONSIVE, "QEMU Guest Agent shutdown fail"
