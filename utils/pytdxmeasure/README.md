# TDX Measurement Tool

It run within TD guest to get RTMR value from TDREPORT via Linux attestion
driver, and get the full TD event log from TDEL ACPI table. Then use the TD
event log to verify the RTMR value or change.

CSP or tenant developer could use it to analyze and debug the TDX measurement
before providing the TDX guest VM.

![](/doc/tdx_measurement.png)

## Getting Started

### Prerequisites

The Log Area Start Address (LASA) is from ACPI TDEL table. Please see [GHCI specification](https://software.intel.com/content/dam/develop/external/us/en/documents/intel-tdx-guest-hypervisor-communication-interface.pdf).


### Run

1. Get Event Log

```
./tdx_eventlogs
```

The example output for the event log in [grub boot](/doc/tdx_measure_log_grub_boot.txt)
and [direct boot](/doc/tdx_measure_log_direct_boot.txt)

2. Get TD Report

```
./tdx_tdreport
```

3. Verify the RTMR

```
./tdx_verify_rtmr
```

## Installation

Build and install TDX Measurement Tool:

```sh
python3 setup.py bdist_wheel
pip3 install dist/*.whl --force-reinstall
```
