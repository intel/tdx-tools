"""
TDX Guest check: to verify TDX guest basic environment:
2. TSC clock source
3. TSC frequency
...
"""
import os
import re
import datetime
import logging
import pytest
from pycloudstack.dut import DUT
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


@pytest.fixture(scope="module")
def base_td_guest_inst(vm_factory, vm_ssh_pubkey):
    """
    Create and start a td guest instance
    """
    td_inst = vm_factory.new_vm(VM_TYPE_TD)
    td_inst.image.inject_root_ssh_key(vm_ssh_pubkey)
    td_inst.create()
    td_inst.start()
    assert td_inst.wait_for_ssh_ready(), "Boot timeout"

    yield td_inst

    td_inst.destroy()


def _remote_run_and_fetch(td_inst, vm_ssh_key, output, command, output_file):
    """
    Runs a command in TD guest and then scp_out the result

    The result is fetched to host and the caller will do further check
    on the result, though the "further check" can also take place in guest.
    One of the reason to fetch the result to host is to save the original output
    and upload to log server for manual analysis in case needed.
    """
    runner = td_inst.ssh_run(command.split(), vm_ssh_key)
    assert runner.retcode == 0, "failed to execute remote command"

    runner = td_inst.scp_out(
        os.path.join('/tmp', output_file), output, vm_ssh_key)
    assert runner.retcode == 0, "failed to copy-out result file"


def test_tdvm_clocksource_tsc(base_td_guest_inst, vm_ssh_key, output):
    """
    check clocksource is *tsc* in TD guest.

    1. remotely run *cat /sys/devices/system/clocksource/clocksource0/current_clocksource*
    2. copy result from td guest to local dir
    3. compare the clocksource name with *tsc*
    """
    LOG.info("Test if clocksource is tsc in TD guest")

    output_file = f"tdx_clocksource_check_{DATE_SUFFIX}.log"
    command = f"cat /sys/devices/system/clocksource/clocksource0/current_clocksource\
                > /tmp/{output_file}"

    _remote_run_and_fetch(base_td_guest_inst, vm_ssh_key, output, command, output_file)

    saved_file = os.path.join(output, output_file)
    with open(saved_file, 'r', encoding="utf8") as fsaved:
        assert fsaved.read().strip() == "tsc"
        LOG.info("TD guest clocksource is tsc")


def test_tdvm_cpuid_tscfreq(base_td_guest_inst, vm_ssh_key, output):
    """
    Check cpuid 0x15.0 in TD guest.
    To make it simple, we only check EAX value, it should be statically 1.

    Refer to:
      Intel® 64 and IA-32 Architectures Software Developer’s Manual 3B
      Section 18.18.3 Determining the Processor Base Frequency
        Nominal TSC frequency
           = (CPUID.15H.ECX[31:0]*CPUID.15H.EBX[31:0])÷CPUID.15H.EAX[31:0]

    1. remotely run *cpuid -r -l 0x15*
    2. copy result from td guest to local dir
    3. check eax value
    """
    LOG.info("Check cpuid 0x15.0 TD guest, eax = 0x00000001")
    output_file = f"cpuid_0x15_check_{DATE_SUFFIX}.log"
    command = f"cpuid -r -l 0x15 > /tmp/{output_file}"

    _remote_run_and_fetch(base_td_guest_inst, vm_ssh_key, output, command, output_file)

    saved_file = os.path.join(output, output_file)
    found_exe_1 = False
    with open(saved_file, 'r', encoding="utf8") as fsaved:
        cpuid_strs = fsaved.readlines()
        for line in cpuid_strs:
            if line.find('eax=0x00000001') != -1:
                LOG.info("EAX value of cpuid#0x15.0 is 0x00000001")
                found_exe_1 = True
                break
    assert found_exe_1


def test_tdvm_compare2_host_tscfreq(base_td_guest_inst, vm_ssh_key, output):
    """
    Comparing tsc frequence of host & guest.
    Be noticed that when host tsc frequency is less than 1G Hz,
    the guest tsc frequency will be 1G Hz

    1. get host tsc freq (DUT.get_cpu_base_freq)
    2. get guest tsc freq (via dmesg, td guest doesn't have the base_frequency file)
    3. compare tsc frequency of host and guest
    """
    LOG.info("Comparing TD guest tsc freqeuency to host")

    host_freq = DUT.get_cpu_base_freq()
    assert host_freq is not None
    LOG.info("host tsc frequency is %d", host_freq)

    host_freq = max(host_freq, 1000000)

    output_file = f"guest_tsc_freq_check_{DATE_SUFFIX}.log"
    command = f"dmesg |grep mhz -i > /tmp/{output_file}"

    _remote_run_and_fetch(base_td_guest_inst, vm_ssh_key, output, command, output_file)

    saved_file = os.path.join(output, output_file)
    guest_freq = 0
    with open(saved_file, 'r', encoding="utf8") as fsaved:
        lines = fsaved.readlines()
        assert len(lines) == 1
        str_freq = re.findall("Detected (.+?) MHz", lines[0])
        guest_freq = int(float(str_freq[0].strip())) * 1000
        LOG.info("TD guest tsc frequency is %d", guest_freq)
    assert host_freq == guest_freq
