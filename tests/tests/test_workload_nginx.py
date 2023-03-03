"""
This test module provides the nginx workload testing for VM
This benchmark is running with bombardier
"""
import os
import logging
import pytest
from pycloudstack.vmparam import VM_TYPE_TD

__author__ = 'cpio'

CURR_DIR = os.path.dirname(__file__)
LOG = logging.getLogger(__name__)

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.vm_kernel("latest-guest-kernel"),
    pytest.mark.vm_image("latest-guest-image"),
]


def test_tdvm_nginx(vm_factory, vm_ssh_pubkey, vm_ssh_key):
    """
    Run nginx benchmark test
    Use official docker images nginx:latest
    Test Steps:
    1. start VM
    2. Run remote command "systemctl status docker" to check docker service's status
    3. Run remote command "systemctl start docker" to force start docker service
    4. Run remote command "root/bat-script/nginx-bench.sh"
       to launch nginx container and benchmark testing
    """
    LOG.info("Create VM to run nginx benchmark")
    td_inst = vm_factory.new_vm(VM_TYPE_TD)

    # customize the VM image
    td_inst.image.inject_root_ssh_key(vm_ssh_pubkey)
    td_inst.image.copy_in(
        os.path.join(CURR_DIR, "nginx-bench.sh"), "/root/")

    # create and start VM instance
    td_inst.create()
    td_inst.start()
    td_inst.wait_for_ssh_ready()

    cmd = 'sysctl -w net.ipv6.conf.all.disable_ipv6=1'
    runner = td_inst.ssh_run(cmd.split(), vm_ssh_key)

    command_list = [
        'systemctl start docker',
        '/root/nginx-bench.sh'
    ]
    for cmd in command_list:
        LOG.debug(cmd)
        runner = td_inst.ssh_run(cmd.split(), vm_ssh_key)
        assert runner.retcode == 0, "Failed to execute remote command"
