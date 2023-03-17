## Launch TD Guest

### Prerequisites

For direct boot, make sure the guest kernel binary is available to the host. For Ubuntu kernels follow these steps:
```
dpkg -x build/ubuntu-22.04/guest_repo/linux-image-unsigned-*.deb extracted
cp extracted/boot/vmlinuz-* ./vmlinuz
rm -rf extracted
```
Steps for Red Hat kernels:
```
rpm2cpio build/rhel-8/repo/guest/x86_64/intel-mvp-tdx-kernel-guest-core* | cpio -id
cp lib/modules/*/vmlinuz .
rm -rf usr/ lib/
```

### Launch via qemu-kvm

Make use of the provided [start-qemu.sh](../start-qemu.sh) script to start a TD
via QEMU.

A simple usage of the script to launch Red Hat RHEL8.5 VM would be as follows:

```
./start-qemu.sh -i td-guest-rhel-8.6.qcow2 -k vmlinuz
```

Or to use the guest's grub bootloader:

```
./start-qemu.sh -i td-guest-rhel-8.6.qcow2 -b grub
```

Equivalent steps to launch Ubuntu VMs:

```
sudo  ./start-qemu.sh -i td-guest-ubuntu-22.04.qcow2 -k vmlinuz -r /dev/vda1
```
Or to use the guest's grub bootloader:

```
sudo ./start-qemu.sh -i td-guest-ubuntu-22.04.qcow2 -b grub
```
For more advanced configurations, please check the help menu:

```
./start-qemu.sh -h
```

### Launch via Libvirt

**NOTE:** For Red Hat Host OS please choose libvirt template for [direct boot](tdx_libvirt_direct.xml.template)
or [grub boot](tdx_libvirt_grub.xml.template).
If running Ubuntu as the host OS, use Ubuntu use templates [direct boot_ubuntu](tdx_libvirt_direct.ubuntu_host.xml.template) or [grub boot_ubuntu](tdx_libvirt_grub.ubuntu_host.xml.template)


1. Configure libvirt

- As the root user, uncomment and save the following settings in */etc/libvirt/qemu.conf*:

    ```
    user = "root"
    group = "root"
    dynamic_ownership = 0
    ```

- To make sure libvirt uses these settings, restart the libvirt service:

    ```
    sudo systemctl restart libvirtd
    ```

2. Copy the template XML file to *tdx.xml* and edit the XML configuration file *tdx.xml* by
    replacing all occurences of the '/path/to' with absolute paths.
    
    **NOTE:**
    - '/path/to/OVMF.fd' is the desired destination of OVMF.fd.
    - If you are using Ubuntu guest image, modify `root=/dev/vda3` to `root=/dev/vda1`

3. Launch TD guest

    ```
    sudo virsh create tdx.xml
    ```

    To keep the guest domain, please use:

    ```
    sudo virsh define tdx.xml
    sudo virsh start td-guest
    ```
Once the TD guest VM is launched, you can verify it is truly TD VM by querying cpuinfo:

<pre>
cat /proc/cpuinfo | grep tdx_guest
flags        : fpu vme de pse tsc msr pae cx8 apic sep pge mca cmov pat pse36 clflush dts mmx fxsr sse sse2 ss ht syscall
nx pdpe1gb rdtscp lm constant_tsc bts rep_good nopl xtopology tsc_reliable cpuid tsc_known_freq pni pclmulqdq dtes64 ds_cpl
ssse3 sdbg fma cx16 pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor
lahf_lm abm 3dnowprefetch cpuid_fault invpcid_single ssbd ibrs ibpb stibp ibrs_enhanced <b>tdx_guest</b> fsgsbase bmi1 hle
avx2 smep bmi2 erms invpcid rtm avx512f avx512dq rdseed adx smap avx512ifma clflushopt clwb avx512cd sha_ni avx512bw 
avx512vlxsaveopt xsavec xgetbv1 xsaves avx_vnni avx512_bf16 wbnoinvd arat avx512vbmi umip pku ospke waitpkg avx512_vbmi2 
shstk gfni vaes vpclmulqdq avx512_vnni avx512_bitalg avx512_vpopcntdq la57 rdpid bus_lock_detect cldemote movdiri movdir64b
pks fsrm md_clear serialize tsxldtrk ibt amx_bf16 avx512_fp16 amx_tile amx_int8 flush_l1d arch_capabilities
</pre>
