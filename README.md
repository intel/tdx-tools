# Intel&reg; TDX (Trust Domain Extensions) 

![CI Check Shell](https://github.com/intel/tdx-tools/actions/workflows/pr-check-shell.yml/badge.svg)
![CI Check Python](https://github.com/intel/tdx-tools/actions/workflows/pr-check-python.yml/badge.svg)
![CI Check License](https://github.com/intel/tdx-tools/actions/workflows/pr-check-license.yml/badge.svg)
![CI Check Document](https://github.com/intel/tdx-tools/actions/workflows/pr-check-document.yml/badge.svg)

## 1. Overview

### 1.1 Intel&reg; Trust Domain Extensions(TDX)
Intel&reg; Trust Domain Extensions(TDX) refers to an Intel technology that
extends Virtual Machine Extensions(VMX) and Multi-Key Total Memory
Encryption(MK-TME) with a new kind of virtual machine guest called a Trust
Domain(TD). A TD runs in a CPU mode that protects the confidentiality of its
memory contents and its CPU state from any other software, including the hosting
Virtual Machine Monitor (VMM). Please see details at [here](https://www.intel.com/content/www/us/en/developer/tools/trust-domain-extensions/documentation.html).

### 1.2 Hardware Availability

- Azure already [launched](https://azure.microsoft.com/en-us/updates/confidential-vms-with-intel-tdx-dcesv5-ecesv5/) the
  TDX based confidential computing at zone of `DCesv5` and `ECesv5` series.
- Google published [Intel Trust Domain Extensions (TDX) Security Review](https://services.google.com/fh/files/misc/intel_tdx_-_full_report_041423.pdf)
- Please contact Intel sales representative for on-premise bare metal server or processor.

### 1.3 Software Availability

You can follow Red Hat [documentation](https://sigs.centos.org/virt/tdx/) for Intel TDX technology early access with CentOS Stream 9 or refer to Canonical [README](https://github.com/canonical/tdx/blob/main/README.md) for TDX build with Ubuntu 23.10.
More information can be found in Red Hat [blog](https://www.redhat.com/en/blog/enabling-hardware-backed-confidential-computing-centos-sig) and Canonical [blog](https://ubuntu.com/blog/intel-tdx-1-0-preview-on-ubuntu-23-10).

## 2. How to launch TD

Use the script [start-qemu.sh](https://github.com/intel/tdx-tools/blob/tdx-mid-stream/start-qemu.sh) to start a TD
via QEMU.

A simple usage of the script to launch TD would be as follows:

```
./start-qemu.sh -i <guest image file> -k <guest kernel file>
```

Or to use the guest's grub bootloader:

```
./start-qemu.sh -i <guest image file> -b grub
```

For more advanced configurations, please check the help menu:

```
./start-qemu.sh -h
```

Once the TD guest VM is launched, you can verify it is truly TD VM by querying `cpuinfo`. It's supposed to have tdx_guest flag.

```
cat /proc/cpuinfo | grep tdx_guest
```
