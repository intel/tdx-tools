"""
VM params package manages the several parameters' class for guest VM.
"""
VM_TYPE_EFI = "efi"
VM_TYPE_LEGACY = "legacy"
VM_TYPE_TD = "td"
VM_TYPE_SGX = "sgx"

BOOT_TYPE_DIRECT = "direct"
BOOT_TYPE_GRUB = "grub"

#
# Please make sure the rootfs at partition /dev/vda3 in guest image
# Also, hvc0 is the default console for TD VM, ttyS0 will be filtered
# due to security concern.
#
DEFAULT_CMDLINE = "root=/dev/vda3 rw selinux=0 console=hvc0 "

# Installed from the package of intel-mvp-qemu-kvm
BIOS_OVMF_CODE = "/usr/share/qemu/OVMF_CODE.fd"
BIOS_OVMF_VARS = "/usr/share/qemu/OVMF_VARS.fd"
BIOS_BINARY_LEGACY = "/usr/share/qemu-kvm/bios.bin"

VM_STATE_RUNNING = "running"
VM_STATE_PAUSE = "paused"
VM_STATE_SHUTDOWN = "shutdown"
VM_STATE_SHUTDOWN_IN_PROGRESS = "shutting down"

BOOT_TIMEOUT = 180

# MODEL array:  #vcpus  #sockets #cores #threads
MODEL_BASE = {"vcpus": 1, "sockets": 1, "cores": 1, "threads": 1, "memsize": 1}
MODEL_LARGE = {"vcpus": 8, "sockets": 1,
               "cores": 4, "threads": 2, "memsize": 32}
MODEL_NUMA = {"vcpus": 16, "sockets": 2,
              "cores": 4, "threads": 2, "memsize": 32}

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
        self._cmdline += field_str

    def add_field(self, key, value=None):
        """
        Add a field from key, value
        """
        if value is None:
            self._cmdline += key
        else:
            self._cmdline += f"{key}={value}"

    def is_field_exists(self, field_str):
        """
        Does the field exist from a complete field string
        """
        return self._cmdline.find(field_str) != -1

    def is_field_key_exists(self, field_key):
        """
        Does the field exists from given field key
        """
        return field_key in self.field_keys

    def remove_field_from_string(self, field_str):
        """
        Remove field from given full field string
        """
        self._cmdline = self._cmdline.replace(field_str, '')

    def remove_fields(self, key):
        """
        Remove all fields from given key
        """
        items = self._cmdline.strip().split(' ')
        retval = ''
        for item in items:
            if item.split('=')[0] != key:
                retval += ' ' + item
        self._cmdline = retval


class CPUTopology:
    """
    CPU Topology parameter for VM configure.
    """

    def __init__(self, sockets=1, cores=1, threads=1):
        self.sockets = sockets
        self.cores = cores
        self.threads = threads

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
