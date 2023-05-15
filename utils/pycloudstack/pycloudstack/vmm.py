"""
VMM(Virtual Machine Manager) provide two types managers: Libvirt and Qemu


                      +---------+         +---------+
                      | VMMBase |  <----> | VMGuest |
                      +---------+         +---------+
    +------------+       ^   ^        +---------+
    | VMMLibvirt |-------|   |--------| VMMQemu |
    +------------+                    +---------+

"""
import os
import re
import logging
import time
import json
import libvirt
import libvirt_qemu
from .cmdrunner import NativeCmdRunner
from .dut import DUT
from .virtxml import VirtXml
from .vmparam import VM_TYPE_LEGACY, VM_TYPE_EFI, VM_TYPE_TD, VM_TYPE_SGX, \
    VM_STATE_SHUTDOWN, VM_STATE_RUNNING, VM_STATE_PAUSE, \
    VM_STATE_SHUTDOWN_IN_PROGRESS, BOOT_TYPE_GRUB, BIOS_BINARY_LEGACY_CENTOS, \
    BIOS_BINARY_LEGACY_UBUNTU, QEMU_EXEC_CENTOS, QEMU_EXEC_UBUNTU, \
    BIOS_OVMF, VM_TYPE_TD_PERF, VM_TYPE_EFI_PERF, VM_TYPE_LEGACY_PERF

__author__ = 'cpio'

LOG = logging.getLogger(__name__)

ARP_INTERVAL = 120


class VMMBase:

    """
    Virtual abstraction class for VMM, defining common interfacts like
    create/destroy/suspend/resume
    """

    def __init__(self, vminst):
        self.vminst = vminst

    def create(self, stop_at_begining=True):
        """
        Create a VM.

        If stop_at_begining is True, then the VM will paused/stopped
        after creation, until execute start() explicity.
        """
        raise NotImplementedError

    def destroy(self):
        """
        Destroy a VM.
        """
        raise NotImplementedError

    def start(self):
        """
        Start a VM if VM is not started.
        """
        raise NotImplementedError

    def suspend(self):
        """
        Suspend a VM if VM is running
        """
        raise NotImplementedError

    def resume(self):
        """
        Resume a VM if VM is stopped/paused
        """
        raise NotImplementedError

    def reboot(self):
        """
        Reboot a VM.
        """
        raise NotImplementedError

    def shutdown(self):
        """
        Shutdown a VM.
        """
        raise NotImplementedError

    def state(self):
        """
        Get VM state
        """
        raise NotImplementedError

    def get_ip(self, force_refresh=False):
        """
        Get VM available IP on virtual or physical bridge
        """
        raise NotImplementedError

    def update_kernel_cmdline(self, cmdline):
        """
        Update kernel command line
        """
        raise NotImplementedError

    def update_kernel(self, kernel):
        """
        Update kernel used in vm
        """
        raise NotImplementedError

    def update_vmspec(self, new_vmspec):
        """
        Update VM spec include CPU topology and memory size
        """
        raise NotImplementedError


class VMMLibvirt(VMMBase):

    """
    Implementation Class for VMMBase base on libvirt binding.
    """

    _TEMPLATE = {
        VM_TYPE_LEGACY: "legacy-base",
        VM_TYPE_EFI: "ovmf-base",
        VM_TYPE_TD: "tdx-base",
        VM_TYPE_SGX: "sgx-base",
        VM_TYPE_TD_PERF: "tdx-base-perf",
        VM_TYPE_EFI_PERF: "ovmf-base-perf",
        VM_TYPE_LEGACY_PERF: "legacy-base-perf"
    }

    def __init__(self, vminst):
        super().__init__(vminst)
        self._virt_conn = self._connect_virt()
        assert self._virt_conn is not None, "Fail to connect libvirt, please make"\
            "sure the libvirt is started and current user in libvirt group"
        self._xml = self._prepare_domain_xml()
        self._ip = None


    def _prepare_domain_xml(self):
        xmlobj = VirtXml.clone(
            self._TEMPLATE[self.vminst.vmtype],
            self.vminst.name)
        xmlobj.memory = self.vminst.vmspec.memsize
        xmlobj.uuid = self.vminst.vmid
        xmlobj.imagefile = self.vminst.image.filepath
        xmlobj.iomode = self.vminst.io_mode
        xmlobj.cache = self.vminst.cache
        xmlobj.logfile = "/tmp/" + self.vminst.name + ".log"
        xmlobj.vcpu = self.vminst.vmspec.vcpus
        xmlobj.sockets = self.vminst.vmspec.sockets
        xmlobj.cores = self.vminst.vmspec.cores
        xmlobj.threads = self.vminst.vmspec.threads

        if self.vminst.cpu_ids:
            xmlobj.bind_cpuids(self.vminst.cpu_ids)
            xmlobj.set_mem_numa(self.vminst.mem_numa)

        if self.vminst.hugepages:
            xmlobj.set_hugepage_params(self.vminst.hugepage_size)

        if self.vminst.vsock:
            xmlobj.set_vsock(self.vminst.vsock_cid)

        if self.vminst.diskfile_path:
            xmlobj.set_disk(self.vminst.diskfile_path)

        self.set_cpu_params_xml(xmlobj)

        if self.vminst.mwait is not None:
            xmlobj.set_overcommit_params(f"cpu-pm={self.vminst.mwait}")

        if self.vminst.boot == BOOT_TYPE_GRUB:
            xmlobj.kernel = None
            xmlobj.cmdline = None
        else:
            xmlobj.kernel = self.vminst.kernel
            xmlobj.cmdline = str(self.vminst.cmdline)

        return xmlobj

    def set_cpu_params_xml(self, xmlobj):
        """
        set specific cpu parameters in domain xml based on different vm type
        """
        distro = DUT.get_distro()
        if "ubuntu" in distro:
            bios_legacy = BIOS_BINARY_LEGACY_UBUNTU
            xmlobj.qemu_exec = QEMU_EXEC_UBUNTU
        else:
            bios_legacy = BIOS_BINARY_LEGACY_CENTOS
            xmlobj.qemu_exec = QEMU_EXEC_CENTOS

        if self.vminst.vmtype in [VM_TYPE_LEGACY, VM_TYPE_LEGACY_PERF]:
            xmlobj.loader = bios_legacy
            xmlobj.set_cpu_params("host,-kvm-steal-time,pmu=off")
        elif self.vminst.vmtype in [VM_TYPE_EFI, VM_TYPE_EFI_PERF]:
            xmlobj.loader = BIOS_OVMF
            xmlobj.set_cpu_params("host,-kvm-steal-time,pmu=off")
        elif self.vminst.vmtype == VM_TYPE_SGX:
            xmlobj.loader = bios_legacy
            xmlobj.set_cpu_params(
                "host,host-phys-bits,+sgx,+sgx-debug,+sgx-exinfo,"
                "+sgx-kss,+sgx-mode64,+sgx-provisionkey,+sgx-tokenkey,+sgx1,+sgx2,+sgxlc")
            xmlobj.set_epc_params(self.vminst.vmspec.epc)
        elif self.vminst.vmtype in [VM_TYPE_TD, VM_TYPE_TD_PERF]:
            xmlobj.loader = BIOS_OVMF

            param_cpu = ""
            if DUT.get_cpu_base_freq() < 1000000:
                param_cpu = "host,-shstk,-kvm-steal-time,pmu=off,tsc-freq=1000000000"
            else:
                param_cpu = "host,-shstk,-kvm-steal-time,pmu=off"

            if self.vminst.tsx is False:
                param_cpu += ",-hle,-rtm"
            if self.vminst.tsc is False:
                param_cpu += ",-tsc-deadline"

            xmlobj.set_cpu_params(param_cpu)


    def _connect_virt(self):
        LOG.debug("Create libvirt connection")
        try:
            self._virt_conn = libvirt.open("qemu:///system")
            return self._virt_conn
        except libvirt.libvirtError:
            LOG.error(
                "Fail to connect libvirt, please make sure current user in libvirt group")
            assert False
        return None

    def _close_virt(self):
        LOG.debug("Close libvirt connection")
        if self._virt_conn is not None:
            self._virt_conn.close()

    def _get_domain(self):
        assert self._virt_conn is not None
        try:
            return self._virt_conn.lookupByUUIDString(self.vminst.vmid)
        except libvirt.libvirtError:
            LOG.warning("Fail to get the domain %s", self.vminst.vmid)
            return None

    def __del__(self):
        self._close_virt()

    def create(self, stop_at_begining=True):
        """
        Create a VM.

        If stop_at_begining is True, then the VM will paused/stopped
        after creation, until execute start() explicity.
        """
        assert self._virt_conn is not None
        self._xml.dump()
        domain = self._virt_conn.defineXML(self._xml.tostring())
        domain.create()

    def destroy(self):
        """
        Destroy a VM.
        Table of Contents:https://libvirt.org/html/libvirt-libvirt-domain.html
        """

        try:
            dom = self._get_domain()
        except libvirt.libvirtError:
            LOG.warning("Unable to find the domain %s", self.vminst.vmid)
        else:
            if dom is not None:
                try:
                    if dom.isActive():
                        dom.destroy()
                except libvirt.libvirtError:
                    LOG.warning("Fail to delete the domain %s", self._xml.name)

                try:
                    dom.undefineFlags(libvirt.VIR_DOMAIN_UNDEFINE_NVRAM)
                except libvirt.libvirtError:
                    LOG.warning("Unable to undefine the domain %s", self._xml.name)

        # Delete XML file
        if os.path.exists(self._xml.filepath):
            try:
                os.remove(self._xml.filepath)
            except (OSError, IOError):
                LOG.warning("Fail to delete Virt XML %s", self._xml.filepath)

    def delete_log(self):
        """
        Delete VM log file.
        """
        if os.path.exists(self._xml.logfile):
            try:
                os.remove(self._xml.logfile)
                LOG.debug("Delete VM log file %s", self._xml.logfile)
            except (OSError, IOError):
                LOG.warning("Fail to delete VM log file %s", self._xml.logfile)

    def start(self):
        """
        Start a VM if VM is not started.
        """
        if self.is_shutoff():
            dom = self._get_domain()
            dom.create()
        else:
            self.resume()

    def suspend(self):
        """
        Suspend a VM if VM is running
        """
        dom = self._get_domain()
        if self.is_running():
            dom.suspend()

    def resume(self):
        """
        Resume a VM if VM is stopped/paused
        """
        dom = self._get_domain()
        if not self.is_running():
            dom.resume()

    def reboot(self):
        """
        Reboot a VM.
        """
        dom = self._get_domain()
        dom.reboot()

    def shutdown(self, mode=None):
        """
        Shutdown a VM.
        """
        dom = self._get_domain()
        if mode is None:
            dom.shutdown()
        elif mode == "default":
            dom.shutdownFlags(libvirt.VIR_DOMAIN_SHUTDOWN_DEFAULT)
        elif mode == "acpi":
            dom.shutdownFlags(libvirt.VIR_DOMAIN_SHUTDOWN_ACPI_POWER_BTN)
        elif mode == "agent":
            dom.shutdownFlags(libvirt.VIR_DOMAIN_SHUTDOWN_GUEST_AGENT)

    def is_running(self):
        """
        Check whether a VM is running
        """
        dom = self._get_domain()
        state, _ = dom.state()
        return state == libvirt.VIR_DOMAIN_RUNNING

    def is_shutoff(self):
        """
        Check whether a VM is shutoff
        """
        dom = self._get_domain()
        state, _ = dom.state()
        return state == libvirt.VIR_DOMAIN_SHUTOFF

    def state(self):
        """
        Get VM state
        """
        dom = self._get_domain()
        state, _ = dom.state()
        if state == libvirt.VIR_DOMAIN_RUNNING:
            return VM_STATE_RUNNING
        if state == libvirt.VIR_DOMAIN_PAUSED:
            return VM_STATE_PAUSE
        if state == libvirt.VIR_DOMAIN_SHUTDOWN:
            return VM_STATE_SHUTDOWN_IN_PROGRESS
        if state == libvirt.VIR_DOMAIN_SHUTOFF:
            return VM_STATE_SHUTDOWN
        return None

    def get_ip(self, force_refresh=False):
        """
        Get VM available IP on virtual or physical bridge

        force_refresh parameter is added so callers can force me to refresh IP
        even when self._ip is not None.
        """
        if (not force_refresh) and (self._ip is not None):
            return self._ip

        dom = self._get_domain()
        vm_mac_address = re.search(
            r"<mac address='([a-zA-Z0-9:]+)'", dom.XMLDesc(0)).groups()
        if vm_mac_address is None:
            LOG.warning("Could not find the available MAC address for VM")
            return None

        tstart = time.time()
        retry = ARP_INTERVAL
        while retry > 0:
            runner = NativeCmdRunner(["arp", "-a"], silent=True)
            runner.runwait()

            for line in runner.stdout:
                ipaddr = re.search(
                    r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', line)
                macaddr = re.search(r'(\w+:\w+:\w+:\w+:\w+:\w+)', line)
                if ipaddr is None or macaddr is None:
                    continue
                if macaddr.groups(0)[0] == vm_mac_address[0]:
                    self._ip = ipaddr.groups(0)[0]

            if self._ip is not None:
                break
            retry -= 1
            time.sleep(1)

        LOG.debug("IP address of %s: %s (duration: %d seconds)",
                  self.vminst.name, self._ip, time.time() - tstart)
        return self._ip

    def update_kernel_cmdline(self, cmdline):
        """
        Update kernel command line
        """
        raise NotImplementedError

    def update_kernel(self, kernel):
        """
        Update kernel used in vm
        """
        raise NotImplementedError

    def update_vmspec(self, new_vmspec):
        """
        Update VM spec include CPU topology and memory size
        """
        raise NotImplementedError

    def _qemu_agent_command(self, cmd):
        dom = self._get_domain()
        return libvirt_qemu.qemuAgentCommand(dom, cmd, 30, 0)

    def qemu_agent_shutdown(self):
        """
        Shutdown VM using QEMU Guest agent 'guest-shutdown' command.
        """
        return self._qemu_agent_command('{"execute": "guest-shutdown"}')

    def qemu_agent_reboot(self):
        """
        Reboot VM using QEMU Guest agent 'guest-shutdown' command, mode "reboot".
        """
        return self._qemu_agent_command(
            '{"execute": "guest-shutdown", "arguments": {"mode": "reboot"}}')

    def qemu_agent_file_write(self, path, content):
        """
        Write to a file within the VM using QEMU Guest commands.
        """
        # pylint: disable=consider-using-f-string
        ret = self._qemu_agent_command(
            '{"execute": "guest-file-open", "arguments":{"path": "%s", "mode": "w+"}}' % path)
        assert 'return' in ret
        j = json.loads(ret)
        filedescriptor = j['return']
        # pylint: disable=consider-using-f-string
        ret = self._qemu_agent_command(
            '{"execute": "guest-file-write", "arguments" : {"handle": %s, "buf-b64": "%s" }}' %
            (filedescriptor, content))
        assert 'return' in ret
        # pylint: disable=consider-using-f-string
        ret = self._qemu_agent_command(
            '{"execute": "guest-file-close", "arguments":{"handle": %s }}' % filedescriptor)
        assert 'return' in ret
        return True

    def qemu_agent_file_read(self, path):
        """
        Read from a file within the VM using QEMU Guest commands.
        """
        # pylint: disable=consider-using-f-string
        ret = self._qemu_agent_command(
            '{"execute": "guest-file-open", "arguments":{"path": "%s", "mode": "r"}}' % path)
        assert 'return' in ret
        j = json.loads(ret)
        filedescriptor = j['return']
        # pylint: disable=consider-using-f-string
        content = self._qemu_agent_command(
            '{"execute": "guest-file-read", "arguments" : {"handle": %s }}' % filedescriptor)
        assert 'return' in ret
        # pylint: disable=consider-using-f-string
        ret = self._qemu_agent_command(
            '{"execute": "guest-file-close", "arguments": {"handle": %s }}' % filedescriptor)
        assert 'return' in ret

        j = json.loads(content)
        return j['return']['buf-b64']
