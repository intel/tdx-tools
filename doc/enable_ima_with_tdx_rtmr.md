
## Enable IMA with TDX RTMR

### IMA Overview

Integrity Measurement Architecture(IMA) is the kernel integrity subsystem to detect if files have
been accidentally or maliciously altered, both remotely and locally. Currently IMA maintains the
runtime measurement list if anchored in a hardware Trusted Platform Module(TPM) to make the measured
hashes of files immutable. It also supports the appraise mechanism to enforce local file integrity
by appraising the measurement against a "good" value stored as an extended attribute.

### Enable IMA in TDX RTMR

To enable the same mechanism in TDVMs to prove the integrity of the files, measurements needed to get
anchored inside TDX RTMR, which is an Intel specific runtime measurement register that is totally
compatible to Trusted Computing Group(TCG) standards.

### Configurations

To enable IMA measurements anchored under TDX RTMR, the following configurations are needed:

Add `ima_hash=sha384` inside the kernel cmdline before booting the VM to enable IMA measurements in
TDX RTMR. Otherwise, IMA will get enabled in TPM bypass mode.

Different IMA policies can be configured to measure different system sensitive files - executable
files, mmapped libraries, and files opened for read by root. Here are several options:

- (Default option) Measure boot aggregates: measure the boot process, no extra parameter needed for
kernel cmdline

- Measure critical data: specify `ima_policy=critical_data` in the kernel cmdline and it will measure
kernel integrity critical data

- Measure default tcb: specify `ima_policy=tcb` in the kernel cmdline and it will measure all programs
executed, files mmapped for exec, and all files opened by the read mode bit set by either the effective
uid (euid=0) or uid=0

- Measure with custom policy: need to add extra script to enable the custom policy. Please check
https://wiki.gentoo.org/wiki/Integrity_Measurement_Architecture#How_do_I_load_a_custom_IMA_policy.3F
for more details.
