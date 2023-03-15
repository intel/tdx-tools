"""
VM Guest class
"""
import os
import uuid
import logging
import time
import socket
import errno
import datetime
import getpass
from .cmdrunner import SSHCmdRunner, NativeCmdRunner
from .dut import DUT
from .vmimg import VMImage
from .vmm import VMMLibvirt
from .vmparam import VM_TYPE_TD, VM_TYPE_SGX, BOOT_TYPE_DIRECT,\
BOOT_TYPE_GRUB, HUGEPAGES_2M, BOOT_TIMEOUT, KernelCmdline, VMSpec

__author__ = 'cpio'

LOG = logging.getLogger(__name__)

LOOPBACK = "127.0.0.1"
DEFAULT_SSH_PORT = 22


class VMGuest:

    """
    VM Guest instance with VM customization.

    The VM guest is controlled by VMM operator either VMMQemu or VMMLibvirt.

    An example code to manage VM guest is:

        img = vmimg.VMImage("test1.qcow2")
        img.inject_root_ssh_key()
        vminst = VMGuest(img, kernel="vmlinuz1", vmm_class=VMMLibvirt)
        vminst.vmm.create()
        vminst.vmm.start()
        vminst.wait_for_ssh_ready()
        vminst.destory()

    """

    def __init__(self, image, guest_distro, name, vmid,
                 vmtype=VM_TYPE_TD, vmspec=VMSpec.model_base(),
                 boot=BOOT_TYPE_DIRECT, kernel=None,
                 cmdline=KernelCmdline(),
                 hugepages=False, hugepage_size=HUGEPAGES_2M,
                 vsock=False, vsock_cid=0,
                 vmm_class=None, cpu_ids=None, mem_numa=True,
                 io_mode=None, cache=None, diskfile_path=None,
                 migtd_pid=None, incoming_port=None):

        self.vmid = vmid
        self.name = name
        self.image = image
        self.guest_distro = guest_distro
        self.vmspec = vmspec
        self.vmtype = vmtype
        self.boot = boot
        self.kernel = kernel
        self.cmdline = cmdline
        self.hugepages = hugepages
        self.hugepage_size = hugepage_size
        self.vsock = vsock
        self.vsock_cid = vsock_cid
        self.keep = False
        self.cpu_ids = cpu_ids
        self.mem_numa = mem_numa
        self.io_mode = io_mode
        self.cache = cache
        self.diskfile_path = diskfile_path
        self.migtd_pid = migtd_pid
        self.incoming_port = incoming_port

        # Update rootfs in kernel command line depending on distro
        rootfs_ubuntu = "root=/dev/vda1"
        rootfs_centos = "root=/dev/vda3"
        if guest_distro == "ubuntu":
            self.cmdline.add_field_from_string(rootfs_ubuntu)
        else:
            self.cmdline.add_field_from_string(rootfs_centos)

        self.ssh_forward_port = DUT.find_free_port()
        LOG.info("VM SSH forward: %d", self.ssh_forward_port)
        assert isinstance(self.image, VMImage)
        if self.boot == BOOT_TYPE_DIRECT:
            assert self.kernel is not None
            assert os.path.exists(self.kernel)
            self.kernel = os.path.realpath(self.kernel)
        self.vmm = vmm_class(self)

    def ssh_run(self, cmdarr, ssh_id_key, no_wait=False):
        """
        Run remote command via SSH. cmdarr is the list of command like:
        ["ls", "/boot"] for "ls /boot"
        """
        if isinstance(cmdarr, str):
            cmdarr = cmdarr.split()

        try:
            runner = SSHCmdRunner(
                cmdarr, ssh_id_key, DEFAULT_SSH_PORT, ip=self.get_ip())
        except NotImplementedError:
            # Fall back to SSH forward mode if fail to get bridge IP
            runner = SSHCmdRunner(
                cmdarr, ssh_id_key, self.ssh_forward_port)

        if no_wait:
            runner.runnowait()
        else:
            runner.runwait()

        # if ssh_run fails, set keep to True so that the VM will not be destroyed
        if runner.retcode != 0:
            self.keep = True
        return runner

    def scp_in(self, source, target, ssh_id_key):
        """
        Copy files/directories into VM via SSH
        """
        if not os.path.exists(source):
            LOG.error("The source %s does not exist.", source)
            return False

        os.chmod(ssh_id_key, 0o600)
        cmdarr = ["scp",
                  "-o", "StrictHostKeyChecking=no",
                  "-o", "UserKnownHostsFile=/dev/null",
                  "-o", "ConnectTimeout=30",
                  "-o", "PreferredAuthentications=publickey",
                  "-i", ssh_id_key,
                  "-r", source, f"root@{self.get_ip()}:{target}"]
        runner = NativeCmdRunner(cmdarr)
        runner.runwait()
        return runner

    def scp_out(self, source, target, ssh_id_key):
        """
        Copy files/directories out of VM via SSH
        """
        os.chmod(ssh_id_key, 0o600)
        cmdarr = ["scp",
                  "-o", "StrictHostKeyChecking=no",
                  "-o", "UserKnownHostsFile=/dev/null",
                  "-o", "ConnectTimeout=30",
                  "-o", "PreferredAuthentications=publickey",
                  "-i", ssh_id_key,
                  "-r", f"root@{self.get_ip()}:{source}", target]
        runner = NativeCmdRunner(cmdarr)
        runner.runwait()
        return runner

    def wait_for_ssh_ready(self, timeout=BOOT_TIMEOUT):
        """
        Wait for the port of forwarded SSH ready until timeout
        @return True is ready, False is timeout
        """

        tstart = time.time()
        tnow = time.time()
        ssh_ok = False

        LOG.debug("Checking if guest (%s) is live on SSH", self.name)

        ssh_port = None
        ssh_ip = None

        # use *(tnow - tstart) < timeout * check to ensure it really elapsed *timeout* seconds
        while ((tnow - tstart) < timeout and not ssh_ok):
            try:
                ssh_ip = self.get_ip(force_refresh=True)
                ssh_port = DEFAULT_SSH_PORT
                if ssh_ip is None:
                    LOG.error("Fail to get IP address, ARP is not ready yet")
                    tnow = time.time()
                    continue
            except NotImplementedError:
                # Fall back to ssh forward approach
                ssh_ip = LOOPBACK
                ssh_port = self.ssh_forward_port
                LOG.debug("No IP allocated for %s, using %s:%s", self.name, ssh_ip, ssh_port)

            assert ssh_port is not None and ssh_ip is not None

            # Open SSH socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            retcode = sock.connect_ex((ssh_ip, ssh_port))
            if retcode != 0:
                LOG.error("Fail to connect SSH for guest %s, connect error: %d", self.name, retcode)
                sock.close()
                time.sleep(1)
                tnow = time.time()
                continue

            # Recev SSH packet
            try:
                data = sock.recv(4096)
            except socket.timeout:
                sock.close()
                LOG.error("Fail to connect SSH for guest %s!", self.name)
                tnow = time.time()
                continue

            # Check the SSH- header
            if data is not None:
                sdata = data.decode('utf-8')
                if "SSH-" in sdata[0:4]:
                    ssh_ok = True

            # close socket for either SSH ready or timeout
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except (socket.error, OSError) as err:
                if err.errno == errno.ENOTCONN:
                    pass
            sock.close()

            # If SSH is ready for connection
            if ssh_ok:
                LOG.info("SSH for guest %s is ready. (duration: %d seconds)", self.name,
                         time.time() - tstart)
                return True

            # Update tnow for a new round socket check
            tnow = time.time()

        LOG.error("SSH connect timeout!")
        return False

    def create(self, stop_at_begining=True):
        """
        Create VM via VMM operator
        """
        LOG.debug("+ Create guest %s", self.name)
        assert self.vmm is not None
        self.vmm.create(stop_at_begining)

    def start(self):
        """
        Start VM via VMM operator
        """
        LOG.debug("+ Start guest %s", self.name)
        assert self.vmm is not None
        self.vmm.start()

    def suspend(self):
        """
        Suspend VM
        """
        LOG.debug("+ Suspend guest %s", self.name)
        assert self.vmm is not None
        self.vmm.suspend()

    def resume(self):
        """
        Resume VM
        """
        LOG.debug("+ Resume guest %s", self.name)
        assert self.vmm is not None
        self.vmm.resume()

    def shutdown(self, mode=None):
        """
        Shutdown a VM
        """
        LOG.debug("+ Shutdown guest %s", self.name)
        assert self.vmm is not None
        if mode is None:
            self.vmm.shutdown()
        else:
            self.vmm.shutdown(mode)

    def destroy(self, delete_image=False, delete_log=False):
        """
        Destroy VM Guest
        """
        LOG.debug("+ Destroy guest %s", self.name)
        self.vmm.destroy()
        if delete_image:
            self.image.destroy()
        if delete_log:
            self.vmm.delete_log()

    def reboot(self):
        """
        Remove VM guest
        """
        LOG.debug("+ Reboot guest %s", self.name)
        assert self.vmm is not None
        self.vmm.reboot()

    def state(self):
        """
        Get VM state
        """
        assert self.vmm is not None
        return self.vmm.state()

    def wait_for_state(self, state, timeout=20):
        """
        Wait for VM state to be given value until timeout
        """
        count = 0
        while count < timeout:
            assert self.vmm.state() is not None
            if self.vmm.state() == state:
                return True
            time.sleep(1)
            count += 1
        return False

    def get_ip(self, force_refresh=False):
        """
        Get VM available IP on virtual or physical bridge
        """
        return self.vmm.get_ip(force_refresh=force_refresh)

    def update_kernel_cmdline(self, cmdline):
        """
        Update kernel command line
        """
        self.cmdline = cmdline
        return self.vmm.update_kernel_cmdline(cmdline)

    def update_kernel(self, kernel):
        """
        Update kernel used in vm
        """
        self.kernel = kernel
        return self.vmm.update_kernel(kernel)

    def update_vmspec(self, new_vmspec):
        """
        Update cpu topology
        """
        self.vmspec = new_vmspec
        return self.vmm.update_vmspec(new_vmspec)


class VMGuestFactory:

    """
    Create and manage multiple VMs
    """

    def __init__(self, vm_mother_image, vm_kernel, part=None):
        self.vms = {}
        if part is None:
            part = {"root": "/dev/sda3", "efi": "/dev/sda2"}
        self._mother_image = VMImage(
            vm_mother_image, part["root"], part["efi"])
        self._vm_kernel = vm_kernel
        self._keep_issue_vm = False

    def new_vm(self, vmtype, vmspec=VMSpec.model_base(), vm_class=VMMLibvirt,
               cmdline=KernelCmdline(),auto_start=False, hugepages=False,
               hugepage_size=None, boot=BOOT_TYPE_DIRECT, disk_img=None,
               vsock=False, vsock_cid=3, io_mode=None, cache=None,
               diskfile_path=None, cpu_ids=None, migtd_pid=None,
               incoming_port=None):
        """
        Creat a VM.
        """

        if hugepage_size is None:
            hugepage_size = HUGEPAGES_2M

        # default io mode is native
        if io_mode is None:
            io_mode = "native"

        # default cache is none
        if cache is None:
            cache = "none"

        vm_id = str(uuid.uuid4())
        user_name = getpass.getuser()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        vm_name = f"{vmtype}-{user_name}-{current_time}"

        # SGX VM use grub to boot
        if vmtype == VM_TYPE_SGX:
            boot = BOOT_TYPE_GRUB

        # Get guest image distro
        if "ubuntu" in self._mother_image.filepath:
            guest_distro = "ubuntu"
        else:
            guest_distro = "centos"

        if disk_img is None:
            disk_img = self._mother_image.clone(vm_name + ".qcow2")

        inst = VMGuest(disk_img, guest_distro=guest_distro, name=vm_name, vmid=vm_id,
                       kernel=self._vm_kernel, vmtype=vmtype, boot=boot,
                       vmspec=vmspec, cmdline=cmdline, vmm_class=vm_class,
                       hugepages=hugepages, hugepage_size=hugepage_size,
                       vsock=vsock, vsock_cid=vsock_cid,
                       io_mode=io_mode, cache=cache,
                       diskfile_path=diskfile_path, cpu_ids=cpu_ids,
                       migtd_pid=migtd_pid, incoming_port=incoming_port)

        self.vms[vm_name] = inst

        if auto_start:
            inst.create()
            inst.start()

        return inst

    def remove(self, inst):
        """
        Remove the VM instance from factory. If self._keep_issue_vm=True, keep unhealthy VM
        """
        if not self._keep_issue_vm:
            inst.destroy(delete_image=True, delete_log=True)
            if inst.name in self.vms:
                del self.vms[inst.name]
        else:
            if not inst.keep:
                inst.destroy(delete_image=True, delete_log=True)
                if inst.name in self.vms:
                    del self.vms[inst.name]

    def removeall(self):
        """
        Remove all VM instance.
        """
        for inst in list(self.vms.values()):
            self.remove(inst)

    def set_keep_issue_vm(self, keep_issue_vm):
        """
        Set value for keep_issue_vm. If it's true, do NOT destroy unhealthy VMs
        """
        self._keep_issue_vm = keep_issue_vm

    def __del__(self):
        self.removeall()
