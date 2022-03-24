"""
TDX Guest check: to verify TDX guest basic environment:
1. TDX initialized (dmesg)
"""

import os
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


def test_tdvm_tdx_initialized(base_td_guest_inst, vm_ssh_key, output):
    """
    check *TDX guest is initialized* string in TD guest dmesg.

    1. remotely run dmesg | grep tdx -i
    2. copy result from td guest to local dir
    3. find *TDX guest is initialized* in the output file
    """
    LOG.info("Test if TDX is enabled in TD guest")
    output_file = f"dmesg_tdx_check_{DATE_SUFFIX}.log"
    command = f"/bin/dmesg | grep tdx -i > /tmp/{output_file}"

    runner = base_td_guest_inst.ssh_run(command.split(), vm_ssh_key)
    assert runner.retcode == 0, "Failed to execute remote command"

    runner = base_td_guest_inst.scp_out(
        os.path.join('/tmp', output_file), output, vm_ssh_key)
    assert runner.retcode == 0

    saved_file = os.path.join(output, output_file)
    found_exe_1 = False
    with open(saved_file, 'r', encoding="utf8") as fsaved:
        lines = fsaved.readlines()
        for line in lines:
            if line.find('TDX guest is initialized'):
                LOG.info("TDX guest is initialized")
                found_exe_1 = True
                break
    assert found_exe_1
