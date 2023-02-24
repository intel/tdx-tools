"""
VM params package manages the several parameters' class for guest VM.
"""
VM_TYPE_EFI = "efi"
VM_TYPE_LEGACY = "legacy"
VM_TYPE_TD = "td"
VM_TYPE_SGX = "sgx"
VM_TYPE_TD_PERF = "td_perf"
VM_TYPE_EFI_PERF = "efi_perf"
VM_TYPE_LEGACY_PERF = "legacy_perf"

# VM params for live migration
VM_TYPE_MIGTD = "mig_td"
MIGTD_DISK_IMAGE = "/usr/share/td-migration/migtd.bin"

BOOT_TYPE_DIRECT = "direct"
BOOT_TYPE_GRUB = "grub"

# Note:
#   1.  hvc0 is the default console for TD VM, ttyS0 will be filtered
#   due to security concern.

DEFAULT_CMDLINE = "rw selinux=0 console=hvc0 earlyprintk console=tty0"

QEMU_EXEC_CENTOS = "/usr/libexec/qemu-kvm"
QEMU_EXEC_UBUNTU = "/usr/bin/qemu-system-x86_64"

BIOS_BINARY_LEGACY_CENTOS = "/usr/share/qemu-kvm/bios.bin"
BIOS_BINARY_LEGACY_UBUNTU = "/usr/share/seabios/bios.bin"

# Installed from the package of intel-mvp-qemu-kvm
BIOS_OVMF = "/usr/share/qemu/OVMF.fd"

VM_STATE_RUNNING = "running"
VM_STATE_PAUSE = "paused"
VM_STATE_SHUTDOWN = "shutdown"
VM_STATE_SHUTDOWN_IN_PROGRESS = "shutting down"

BOOT_TIMEOUT = 180

HUGEPAGES_1G = "1G"
HUGEPAGES_2M = "2M"


class KernelCmdline:
    """
    Kernel cmdline class to manage the add/delete/update of command line string.

    Example Code:
        cmdobj = KernelCmdline()
        print(cmdobj.field_keys)
        print(cmdobj.get_value("tsc"))
        cmdobj.add_field_from_string("console=hvc0")
        cmdobj.add_field_from_string("console=ttyS0,115200")
        cmdobj.remove_fields("console")
        cmdobj += "console=ttyS0"
        cmdobj += "console=hvc0"
        print(cmdobj)
    """

    def __init__(self, default=DEFAULT_CMDLINE):
        self._cmdline = default

    def __str__(self):
        return self._cmdline

    def __iadd__(self, value):
        for item in value.split(" "):
            if item not in self._cmdline.strip().split(' '):
                self._cmdline += f' {value}'
        return self

    @property
    def field_keys(self):
        """
        The key array for all fields in kernel command line
        """
        return [item.split('=')[0] for item in self._cmdline.strip().split(' ')]

    def get_value(self, field_key):
        """
        Get the value for given field's key
        """
        for item in self._cmdline.strip().split(' '):
            arr = item.split('=')
            if arr[0] == field_key:
                if len(arr) > 1:
                    return arr[1]
        return None

    def add_field_from_string(self, field_str):
        """
        Add a field from full string include key=value
        """
        if not self.is_field_exists(field_str):
            self._cmdline += " " + field_str

    def add_field(self, key, value=None):
        """
        Add a field from key, value
        """
        if value is None:
            self._cmdline += " " + key
        else:
            self._cmdline += f" {key}={value}"

    def is_field_exists(self, field_str):
        """
        Does the field exist from a complete field string
        """
        assert field_str is not None
        return self._cmdline.find(field_str.strip()) != -1

    def is_field_key_exists(self, field_key):
        """
        Does the field exists from given field key
        """
        assert field_key is not None
        return field_key.strip() in self.field_keys

    def remove_field_from_string(self, field_str):
        """
        Remove field from given full field string
        """
        assert field_str is not None
        self._cmdline = self._cmdline.replace(field_str.strip(), '')

    def remove_fields(self, key):
        """
        Remove all fields from given key
        """
        assert key is not None
        items = self._cmdline.strip().split(' ')
        retval = ''
        for item in items:
            if item.split('=')[0] != key.strip():
                retval += ' ' + item
        self._cmdline = retval


class VMSpec:
    """
    CPU Topology parameter for VM configure.
    """

    def __init__(self, sockets=1, cores=4, threads=1, memsize=None):
        self.sockets = sockets
        self.cores = cores
        self.threads = threads
        self.memsize = memsize
        if memsize is None:
            self.memsize = self.vcpus * 4 * 1024 * 1024

    @property
    def vcpus(self):
        """
        Total number of vcpu
        """
        return self.sockets * self.cores * self.threads

    def is_numa(self):
        """
        Is the NUMA enabled
        """
        return self.sockets > 1

    @staticmethod
    def model_migtd():
        """
        Generate migtd model
        """
        return VMSpec(sockets=1, cores = 1, threads=1, memsize=64*1024)

    @staticmethod
    def model_base():
        """
        Generate base model
        """
        return VMSpec(sockets=1, cores = 4, threads=1, memsize=16*1024*1024)

    @staticmethod
    def model_large():
        """
        Generate large model
        """
        return VMSpec(sockets=1, cores=8, threads=1, memsize=32*1024*1024)

    @staticmethod
    def model_numa():
        """
        Generate numa model
        """
        return VMSpec(sockets=2, cores=4, threads=1, memsize=32*1024*1024)


class SGXVMSpec(VMSpec):
    """
    SGX specific configurations
    """

    def __init__(self, sockets=1, cores=4, threads=1, memsize=None, epc=None):
        """
        The EPC configuration should be like:
            -object memory-backend-epc,id=mem1,size=64M,prealloc=on \
            -object memory-backend-epc,id=mem2,size=28M \
            -M sgx-epc.0.memdev=mem1,sgx-epc.0.node=0, \
               sgx-epc.1.memdev=mem2,sgx-epc.1.node=1
        so define epc parameter as a list, like:
            epc = [{'size': '64M', 'prealloc': True, 'node': 0},
                   {'size': '28M', 'prealloc': False, 'node': 1}]
        """
        super().__init__(sockets, cores, threads, memsize)
        assert epc is not None and len(epc) > 0
        self.epc = epc
