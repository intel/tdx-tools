#!/bin/bash
#
# Check the TDX guest status
#

tdx_cpuinfo=$(grep -o tdx_guest /proc/cpuinfo)
if [[ $tdx_cpuinfo =~ "tdx_guest$" ]]; then
  echo "This is NOT a TDX guest!"
  echo "No config in cpuinfo!"
  exit 1
fi

if [[ ! -e /sys/firmware/acpi/tables/CCEL ]]; then
  echo "This is NOT a TDX guest!"
  echo "No CCEL table!"
  echo "Please reference:"
  echo "    https://www.intel.com/content/www/us/en/developer/articles/technical/intel-trust-domain-extensions.html"
  echo "    https://uefi.org/specs/ACPI/6.5/05_ACPI_Software_Programming_Model.html#cc-event-log-acpi-table"
  exit 1
fi

if [[ ! -e /dev/tdx_guest ]]; then
  echo "This is NOT a TDX guest!"
  echo "No tdx_guest device!"
  echo "Please reference:"
  echo "    https://docs.kernel.org/virt/coco/tdx-guest.html"
  exit 1
fi

echo This is a TDX guest!
