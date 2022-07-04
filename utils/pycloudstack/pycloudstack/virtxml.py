"""
Libvirt XML class manage the xml file for VM define, create, destroy.
"""
import os
import logging
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom

__author__ = 'cpio'

LOG = logging.getLogger(__name__)
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
QEMUS_NS = "{http://libvirt.org/schemas/domain/qemu/1.0}"
HUGEPAGE_VALUES = ["2M", "1G"]


# pylint: disable=too-many-public-methods
class VirtXml:

    """
    Virt XML class to manage the setting via XML dom. In most time, you won't to
    create a virt XML from scratch, but load it from a template file.
    In template file, there are some magic string like "REPLACEME_xxx".
    Set the property for the VirtXml's property, will set these field with magic value.
    Then save the modified XML dom into new file.

    Please see the example code as below:

    ```
    vxobj = VirtXml()
    if vxobj.load(os.path.join(TEMP_DIR, "tdx-base.xml")):
        vxobj.name = "testtest2"
        vxobj.vcpu = "5"
        vxobj.vcpu = 4
        vxobj.uuid = "123123"
        vxobj.memory = 33333
        vxobj.save(os.path.join(TEMP_DIR, "test2.xml"))
    ```

    """

    _OUTPUT = THIS_DIR

    def __init__(self):
        self._tree = None
        self._name = None
        self._uuid = None
        self._kernel = None
        self._cmdline = None
        self._loader = None
        self._nvram = None
        self._memory = None
        self._vcpu = None
        self._imagefile = None
        self._logfile = None
        self._filepath = None
        self._sockets = None
        self._cores = None
        self._threads = None
        self._qemu_exec = None

    @property
    def name(self):
        """
        <domain>/<name> field in xml
        """
        return self._name

    @name.setter
    def name(self, new_name):
        if self._name == new_name:
            return
        if self._set_single_element_value(["name", ], new_name):
            self._name = new_name
        self.save()

    @property
    def uuid(self):
        """
        <domain>/<uuid> field in xml
        """
        return self._uuid

    @uuid.setter
    def uuid(self, new_uuid):
        if self._uuid == new_uuid:
            return
        if self._set_single_element_value(["uuid", ], new_uuid):
            self._uuid = new_uuid
        self.save()

    @property
    def kernel(self):
        """
        <domain>/<os>/<kernel> field in xml
        """
        return self._kernel

    @kernel.setter
    def kernel(self, new_kernel):
        if self._kernel == new_kernel:
            return
        if new_kernel is None:
            self._delete_element(["os", "kernel"])
            self._kernel = None
        else:
            if self._set_single_element_value(["os", "kernel"], new_kernel):
                self._kernel = new_kernel
        self.save()

    @property
    def loader(self):
        """
        <domain>/<os>/<loader> field in xml
        """
        return self._loader

    @loader.setter
    def loader(self, new_loader):
        if self._loader == new_loader:
            return
        if self._set_single_element_value(["os", "loader"], new_loader):
            self._loader = new_loader
        self.save()

    @property
    def nvram(self):
        """
        <domain>/<os>/<nvram> field in xml
        """
        return self._nvram

    @nvram.setter
    def nvram(self, new_nvram):
        if self._nvram == new_nvram:
            return
        if self._set_single_element_value(["os", "nvram"], new_nvram):
            self._nvram = new_nvram
        self.save()

    @property
    def cmdline(self):
        """
        <domain>/<os>/<cmdline> field in xml
        """
        return self._cmdline

    @cmdline.setter
    def cmdline(self, new_cmdline):
        if self._cmdline == new_cmdline:
            return
        if new_cmdline is None:
            self._delete_element(["os", "cmdline"])
            self._cmdline = None
        else:
            if self._set_single_element_value(["os", "cmdline"], new_cmdline):
                self._cmdline = new_cmdline
        self.save()

    @property
    def memory(self):
        """
        <domain>/<memory> field in xml
        """
        return self._memory

    @memory.setter
    def memory(self, new_memory):
        if isinstance(new_memory, int):
            new_memory = str(new_memory)
        if self._memory == new_memory:
            return
        if self._set_single_element_value(["memory", ], new_memory):
            self._memory = new_memory
        self.save()

    @property
    def vcpu(self):
        """
        <domain>/<vcpu> field in xml
        """
        return self._vcpu

    @vcpu.setter
    def vcpu(self, new_vcpu):
        """
        <domain>/<vcpu> field
        """
        if isinstance(new_vcpu, int):
            new_vcpu = str(new_vcpu)
        if self._vcpu == new_vcpu:
            return
        if self._set_single_element_value(["vcpu", ], new_vcpu):
            self._vcpu = new_vcpu
            self.save()
        else:
            LOG.error("Fail to set vcpu in virt XML")

    @property
    def sockets(self):
        """
        <domain>/<cpu>/<topology> field's attrib sockets
        """
        return self._sockets

    @sockets.setter
    def sockets(self, new_value):
        """
        <domain>/<cpu>/<topology> field's attrib sockets
        """
        if isinstance(new_value, int):
            new_value = str(new_value)
        if self._sockets == new_value:
            return
        if self._set_single_element_attrib(["cpu", "topology"], "sockets", new_value):
            self._sockets = new_value
            self.save()
        else:
            LOG.error("Fail to set sockets in virt XML")

    @property
    def cores(self):
        """
        <domain>/<cpu>/<topology> field's attrib cores
        """
        return self._cores

    @cores.setter
    def cores(self, new_value):
        """
        <domain>/<cpu>/<topology> field's attrib cores
        """
        if isinstance(new_value, int):
            new_value = str(new_value)
        if self._cores == new_value:
            return
        if self._set_single_element_attrib(["cpu", "topology"], "cores", new_value):
            self._cores = new_value
            self.save()
        else:
            LOG.error("Fail to set cores in virt XML")

    @property
    def threads(self):
        """
        <domain>/<cpu>/<topology> field's attrib threads
        """
        return self._threads

    @threads.setter
    def threads(self, new_value):
        """
        <domain>/<cpu>/<topology> field's attrib threads
        """
        if isinstance(new_value, int):
            new_value = str(new_value)
        if self._threads == new_value:
            return
        if self._set_single_element_attrib(["cpu", "topology"], "threads", new_value):
            self._threads = new_value
            self.save()
        else:
            LOG.error("Fail to set threads in virt XML")

    @property
    def imagefile(self):
        """
        <domain>/<devices>/<disk>/<source> - file field in xml
        """
        return self._imagefile

    @imagefile.setter
    def imagefile(self, new_file):
        if self._imagefile == new_file:
            return
        _, image_dom = self._find_single_element(["devices", "disk", "source"])
        image_dom.set("file", new_file)
        self._imagefile = new_file
        self.save()

    @property
    def logfile(self):
        """
        <domain>/<devices>/<console>/<log> - log file field in xml
        """
        return self._logfile

    @logfile.setter
    def logfile(self, new_file):
        if self._logfile == new_file:
            return
        _, log_dom = self._find_single_element(["devices", "console", "log"])
        log_dom.set("file", new_file)
        self._logfile = new_file
        self.save()

    @property
    def qemu_exec(self):
        """
        <domain>/<devices>/<emulator> - emulator field in xml
        """
        return self._qemu_exec

    @qemu_exec.setter
    def qemu_exec(self, qemu_exec):
        if self._qemu_exec == qemu_exec:
            return
        if self._set_single_element_value(["devices", "emulator"], qemu_exec):
            self._qemu_exec = qemu_exec
        self.save()

    @property
    def filepath(self):
        """
        File path for virt XML
        """
        return self._filepath

    def dump(self, dump_xml=False):
        """
        Dump the debug information
        """
        LOG.debug("-----------------------------------------------------------")
        LOG.debug("|-VM XML - %s", self._filepath)
        LOG.debug("|  * name    : %s  vcpu: %s memory: %s", self._name, self._vcpu,
                  self._memory)
        LOG.debug("|  * kernel  : %s", self._kernel)
        LOG.debug("|  * image   : %s", self._imagefile)
        LOG.debug("|  * cmdline : %s", self._cmdline)
        LOG.debug("|  * loader  : %s", self._loader)
        LOG.debug("|  * nvram   : %s", self._nvram)
        LOG.debug("|  * log     : %s", self._logfile)
        LOG.debug("-----------------------------------------------------------")

        if self._tree is not None and dump_xml:
            ET.dump(self._tree)

    def load(self, filepath):
        """
        Load virt XML from given filepath
        """
        if not os.path.exists(filepath):
            LOG.error("Fail to find the xml file %s", filepath)
            return False

        self._tree = ET.parse(filepath)
        self._name = self._get_single_element_value(["name", ])
        self._uuid = self._get_single_element_value(["uuid", ])
        self._kernel = self._get_single_element_value(["os", "kernel"])
        self._cmdline = self._get_single_element_value(["os", "cmdline"])
        self._vcpu = self._get_single_element_value(["vcpu", ])
        self._memory = self._get_single_element_value(["memory", ])
        self._loader = self._get_single_element_value(["os", "loader"])
        _, image = self._find_single_element(["devices", "disk", "source"])
        self._imagefile = image.get("file")

        self._filepath = filepath
        return True

    def save(self, filepath=None):
        """
        Save virt XML to given filepath
        """
        if filepath is None:
            if self._filepath is None:
                LOG.warning("Could not save since not real file associated.")
            else:
                filepath = self._filepath

        try:
            rawstr = "".join([item.strip() for item in self.tostring().split("\n")])
            xmlstr = minidom.parseString(rawstr).toprettyxml(indent="  ")
            with open(filepath, "w", encoding="utf8") as outf:
                outf.write(xmlstr)
        except IOError:
            LOG.error("Fail to save the file to %s", filepath)
            return False

        if self._filepath != filepath:
            self._filepath = filepath
        return True

    def tostring(self):
        """
        Dump the virt XML to string
        """
        return ET.tostring(self._tree.getroot(), encoding='unicode')

    def customize(self, imagefile, vmid=None, name=None, kernel=None, loader=None,
                  nvram=None, memory=2097152, cmdline=None):
        """
        Customize the XML object for name, uuid, memory, kernel, imagefile, loader.

        :name       VM instance's name. If none then equal to "vm-<uuid>"
        :uuid       UUID string, if None, then generate a new UUID
        :memory     Memory size, by default is 2097152
        :kernel     <kernel> for direct boot, none for grub
        :imagefile  VM image file name
        :loader     BIOS image, none for legacy boot
        :cmdline    <cmdline>
        """
        assert imagefile is not None
        self.imagefile = imagefile

        if vmid is None:
            self.uuid = str(uuid.uuid4())
        else:
            self.uuid = vmid

        if name is None:
            self.name = "vm-" + uuid
        else:
            self.name = name

        self.memory = memory

        if kernel is not None:
            self.kernel = kernel

        if loader is not None:
            self.loader = loader

        if nvram is not None:
            self.nvram = nvram

        if cmdline is not None:
            self.cmdline = cmdline

        self.dump()

    def _find_single_element(self, tag_arr):
        """
        Find a single element for give tag_arr

        :tag_arr  the tag array for element. For example ["os", "kernel"] means
            <os>
                <kernel>xxx</kernel>
            </os>
        """
        parent = self._tree.getroot()
        while len(tag_arr) > 0:
            curr = tag_arr.pop(0)
            items = parent.findall(curr)
            if items is None or len(items) != 1:
                LOG.error("Could not find %s", curr)
                return None, None
            if len(tag_arr) == 0:
                return parent, items[0]
            parent = items[0]
        return None, None

    def _get_single_element_value(self, tag_arr):
        """
        Get the value to a single type element. If could not find the given element
        or there are more than two same elements, return None

        :tag_arr  the tag array for element. For example ["os", "kernel"] means
            <os>
                <kernel>xxx</kernel>
            </os>
        """
        _, element = self._find_single_element(tag_arr)
        if element is not None:
            return element.text
        return None

    def _set_single_element_value(self, tag_arr, new_value):
        """
        Set the value to a single type element. If could not find the given element
        or there are more than two same elements, return False

        :tag_arr  the tag array for element. For example ["os", "kernel"] means
            <os>
                <kernel>xxx</kernel>
            </os>
        :new_value  new value for given element
        """
        _, element = self._find_single_element(tag_arr)
        if element is not None:
            element.text = new_value
            return True
        return False

    def _set_single_element_attrib(self, tag_arr, attrib, value):
        """
        Set an attrib's value for given element
        """
        _, element = self._find_single_element(tag_arr)
        if element is not None:
            element.set(attrib, value)
            return True
        return False

    def _add_new_element(self, tag_arr, attribs=None, allow_multi_same_leaf=False):
        """
        Add a new element with new parant under given parant item.

        For example: add ["memoryBacking", "hugepages", "page"]
        """
        assert len(tag_arr) >= 1
        parent = self._tree.getroot()

        tag_leaf = tag_arr.pop(len(tag_arr) - 1)

        # Find the parent
        while len(tag_arr) > 0:
            new_tag = tag_arr.pop(0)
            item = parent.find(new_tag)
            if item is None:
                # If not found the tag, then create one
                item = ET.SubElement(parent, new_tag)
            parent = item

        if allow_multi_same_leaf:
            # if allow multiple leaf, then create leaf item without checking existing
            leaf_item = ET.SubElement(parent, tag_leaf)
        else:
            # check whether exist leaf
            leaf_item = parent.find(tag_leaf)
            if leaf_item is None:
                # only create leaf when the leaf not exist
                leaf_item = ET.SubElement(parent, tag_leaf)
            else:
                LOG.warning("The leaf item %s already exist", tag_leaf)

        if attribs is not None:
            for attrib, value in attribs.items():
                leaf_item.set(attrib, value)

        return True

    def _delete_element(self, tag_arr):
        assert len(tag_arr) >= 1
        parent = self._tree.getroot()

        tag_leaf = tag_arr.pop(len(tag_arr) - 1)

        # Find the parent
        while len(tag_arr) > 0:
            new_tag = tag_arr.pop(0)
            parent = parent.find(new_tag)
            if parent is None:
                # If not found the tag, then create one
                LOG.warning("Item does not exist.")
                return True

        item = parent.find(tag_leaf)
        if item is not None:
            parent.remove(item)
        return True

    def enable_ssh_forward_port(self, port):
        """
        Enable SSH forward port in VirtXML
        """
        self._add_new_element(
            [f"{QEMUS_NS}commandline", f"{QEMUS_NS}arg"],
            {"value": "-device"},
            allow_multi_same_leaf=True)
        self._add_new_element(
            [f"{QEMUS_NS}commandline", f"{QEMUS_NS}arg"],
            {"value":
                {"driver": "virtio-net-pci", "netdev": "mynet0", "mac":
                "00:16:3E:68:00:10", "romfile": ""}
            },
            allow_multi_same_leaf=True)
        self._add_new_element(
            [f"{QEMUS_NS}commandline", f"{QEMUS_NS}arg"],
            {"value": "-netdev"},
            allow_multi_same_leaf=True)
        self._add_new_element(
            [f"{QEMUS_NS}commandline", f"{QEMUS_NS}arg"],
            {"value": f"user,id=mynet0,hostfwd=tcp::{port}-:22"},
            allow_multi_same_leaf=True)
        self.save()

    def set_hugepage_params(self, hugepage_size):
        """
        Set Hugepage parameters
        """
        assert (hugepage_size in HUGEPAGE_VALUES), "Hugepages must be 2M or 1G"
        unit = hugepage_size[1:]
        size = hugepage_size[:1]
        self._add_new_element(
            ["memoryBacking", "hugepages", "page"],
            {"unit": f"{unit}", "size": f"{size}"})
        self.save()

    def set_cpu_params(self, cpu_param):
        """
        Set CPU parameters
        """
        self._add_new_element(
            [f"{QEMUS_NS}commandline", f"{QEMUS_NS}arg"],
            {"value": "-cpu"},
            allow_multi_same_leaf=True)
        self._add_new_element(
            [f"{QEMUS_NS}commandline", f"{QEMUS_NS}arg"],
            {"value": f"{cpu_param}"},
            allow_multi_same_leaf=True)
        self.save()

    def bind_cpuids(self, cpu_ids):
        """
        bind available cpuids
        """
        # set iothread
        self._add_new_element(["cputune", "iothreadpin"],
                              {"iothread": "1", "cpuset": f"{cpu_ids.pop(0)}"}, True)
        vcpu_id = 0
        # bind specific vcpus for vm
        for cpu_id in cpu_ids:
            self._add_new_element(["cputune", "vcpupin"],
                                  {"vcpu": f"{vcpu_id}", "cpuset": f"{cpu_id}"}, True)
            vcpu_id += 1
        self.save()

    def set_mem_numa(self, memnuma):
        """
        set memory numa whether local or remote. True means local numa, false means remote numa.
        """
        self._add_new_element(["numatune", "memory"])
        self._set_single_element_attrib(["numatune", "memory"], "mode", "strict")
        if memnuma:
            self._set_single_element_attrib(["numatune", "memory"], "nodeset", "0")
        else:
            self._set_single_element_attrib(["numatune", "memory"], "nodeset", "1")
        self.save()

    def set_epc_params(self, epc_param):
        """
        Set SGX EPC parameters, for example:
            -object memory-backend-epc,id=mem1,size=64M,prealloc=on \
            -object memory-backend-epc,id=mem2,size=28M \
            -M sgx-epc.0.memdev=mem1,sgx-epc.0.node=0, \
               sgx-epc.1.memdev=mem2,sgx-epc.1.node=1
        """
        sgx_epc = ""
        num = 0
        for section in epc_param:
            num += 1
            prealloc = ",prealloc=on" if section['prealloc'] else ""
            self._add_new_element(
                [f"{QEMUS_NS}commandline", f"{QEMUS_NS}arg"],
                {"value": "-object"},
                allow_multi_same_leaf=True)
            self._add_new_element(
                [f"{QEMUS_NS}commandline", f"{QEMUS_NS}arg"],
                {"value": f"memory-backend-epc,id=mem{num},size={section['size']}"
                f"{prealloc}"}, allow_multi_same_leaf=True)
            sgx_epc += f"sgx-epc.{num - 1}.memdev=mem{num}"
            sgx_epc += f",sgx-epc.{num - 1}.node={section['node']},"

        self._add_new_element(
                [f"{QEMUS_NS}commandline", f"{QEMUS_NS}arg"],
                {"value": "-M"},
                allow_multi_same_leaf=True)
        self._add_new_element(
                [f"{QEMUS_NS}commandline", f"{QEMUS_NS}arg"],
                {"value": f"{sgx_epc[:-1]}"},
                allow_multi_same_leaf=True)
        self.save()

    def set_vsock(self, cid):
        """
        Enable and set cid for vsock
        """
        self._add_new_element(
            ["devices", "vsock", "cid"],
            {"auto": "no", "address": str(cid)}
        )
        self._set_single_element_attrib(["devices", "vsock"], "model", "virtio")
        self.save()

    @staticmethod
    def get_templates_dir():
        """
        Get default templates directory.
        """
        return os.path.join(THIS_DIR, "templates")

    @staticmethod
    def get_output_dir():
        """
        Get the default output directory.

        TODO: Need consider better location for output directory.
        """
        return VirtXml._OUTPUT

    @staticmethod
    def set_output_dir(outdir):
        """
        Config the global output directory, otherwise output to current dir.
        """
        VirtXml._OUTPUT = outdir

    @classmethod
    def clone(cls, template_name, new_name):
        """
        Clone a VM xml from a base XML, which could be base.xml or tdx-base.xml

        :template_name the name of template - base.xml or tdx-base.xml. The template
                       file should be at template directory.
        :new_xml_name  the new name for the xml filename
        """
        template_full_path = os.path.join(
            cls.get_templates_dir(), template_name + ".xml")
        if not os.path.exists(template_full_path):
            LOG.error("Could not find the template at %s", template_full_path)
            return None

        newxml_full_path = os.path.join(
            cls.get_output_dir(), new_name + ".xml")

        obj = cls()
        obj.load(template_full_path)
        obj.save(newxml_full_path)
        obj.name = new_name
        return obj
