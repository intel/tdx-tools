"""
TDX Guest check: to verify TDX guest basic environment:
1. TDX initialized (dmesg)
"""

import datetime
import logging
import pytest
from pycloudstack.vmparam import VM_TYPE_TD

__author__ = 'cpio'

# Disable redefined-outer-name since it is false positive for pytest's fixture
# pylint: disable=redefined-outer-name

LOG = logging.getLogger(__name__)

DATE_SUFFIX = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.vm_kernel("latest-guest-kernel"),       # from artifacts.yaml
    pytest.mark.vm_image("latest-guest-image"),    # from artifacts.yaml
]


@pytest.fixture(scope="function")
def base_td_guest_inst(vm_factory, vm_ssh_pubkey):
    """
    Create and start a td guest instance
    """
    td_inst = vm_factory.new_vm(VM_TYPE_TD)
    # customize the VM image
    td_inst.image.inject_root_ssh_key(vm_ssh_pubkey)

    # create and start VM instance
    td_inst.create()
    td_inst.start()
    assert td_inst.wait_for_ssh_ready(), "Boot timeout"

    yield td_inst

    td_inst.destroy()


def test_tdvm_tdx_initialized(base_td_guest_inst, vm_ssh_key):
    """
    check cpu flag "tdx_guest" in TD guest.
    """

    LOG.info("Test if TDX is enabled in TD guest")
    command = "lscpu | grep -i flags"

    runner = base_td_guest_inst.ssh_run(command.split(), vm_ssh_key)
    assert runner.retcode == 0, "Failed to execute remote command"

    LOG.info(runner.stdout[0])
    assert "tdx_guest" in runner.stdout[0], "TDX initilization failed in the guest!"
