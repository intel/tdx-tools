#!/bin/bash
#
# Check the TDX guest status
#

tdx_cpuinfo=$(grep -o tdx_guest /proc/cpuinfo)
if [[ $tdx_cpuinfo == "tdx_guest" ]]; then
  echo TDX guest is enabled!
else
  echo TDX guest is not enabled!
fi
