
## Verify TDX Status

### Verify Host

After reboot into TDX host kernel,

- Check the system initialization messages after system boot:

  ```
  dmesg | grep -i TDX
  [   14.000509] tdx: TDX SEAM module: attributes 0x80000000 vendor_id 0x8086 build_date 0x13461cf build_num 0x1 minor_version 0x0 major_version 0x1.
  [   21.630876] tdx: TDX initialized.
  ```

- Check `/proc/cpuinfo` attributes

  ```
  grep -o tdx /proc/cpuinfo
  ```

  Empty results mean TDX is not enabled.

- Check MSR 0x1401 bit 11

  ```
  sudo rdmsr 0x1401 -f 11:11
  ```

  Result `1` means TDX enabled.

  _**NOTE**_ If rdmsr tool was not installed, please install it via:

  ```
  sudo dnf install -y epel-release
  sudo dnf install -y msr-tools
  ```

- Check TDX SEAM module version

  ```
  cat /sys/firmware/tdx_seam/*
  ```

- Check MK-TME is enabled according to [Intel&reg; Architecture Memory
Encryption Technologies](https://software.intel.com/sites/default/files/managed/a5/16/Multi-Key-Total-Memory-Encryption-Spec.pdf),
the bit 1 should be 1 for MSR IA32_TME_ACTIVATE

  ```
  rdmsr -f 1:1 0x982
  ```

- Check `MK-TME` keys

  Read the bits MK_TME_KEYID_BITS ( 35:32 ) of the value of MSR 0x982
according [Intel&reg; Architecture Memory
Encryption Technologies](https://software.intel.com/sites/default/files/managed/a5/16/Multi-Key-Total-Memory-Encryption-Spec.pdf)

  ```
  rdmsr -f 35:32 0x982
  ```
  The non-zero return value means `MK-TME` supported.

### Verify Guest

- Check the system initialization messages after TD guest boot:

  ```
  dmesg | grep tdx

  [    0.000000] x86/tdx: Guest initialized
  ```

- Check `/proc/cpuinfo` attributes:

  ```
  grep -o tdx_guest /proc/cpuinfo
  ```

  Empty result means TDX is not enabled.
