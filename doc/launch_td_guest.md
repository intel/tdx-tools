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

Make use of the provided [start-qemu.sh](https://github.com/intel/tdx-tools/blob/main/start-qemu.sh) script to start a TD
via QEMU.

A simple usage of the script to launch Red Hat RHEL8.5 VM would be as follows:

```
./start-qemu.sh -i td-guest-rhel-8.5.qcow2 -k vmlinuz
```

Or to use the guest's grub bootloader:

```
./start-qemu.sh -i td-guest-rhel-8.5.qcow2 -b grub
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

**NOTE:** For Red Hat Host OS please choose libvirt template for [direct boot](https://github.com/intel/tdx-tools/blob/main/doc/tdx_libvirt_direct.xml.template)
or [grub boot](https://github.com/intel/tdx-tools/blob/main/doc/tdx_libvirt_grub.xml.template).
If running Ubuntu as the host OS, use Ubuntu use templates [direct boot_ubuntu](https://github.com/intel/tdx-tools/blob/main/doc/tdx_libvirt_direct.ubuntu.xml.template) or [grub boot_ubuntu](https://github.com/intel/tdx-tools/blob/main/doc/tdx_libvirt_grub.ubuntu.xml.template)


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
    
    **NOTE:**'/path/to/OVMF_VARS.fd' is the desired destination of OVMF_VARS.fd.
    
   The XML templates are minimalistic, feel free to modify other features (CPUs, memory, network ...) as desired.
  

   ```
    <domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>
      <name>td-guest</name>
      <memory unit='KiB'>2097152</memory>
      <vcpu placement='static'>1</vcpu>
      <os>
        <type arch='x86_64' machine='q35'>hvm</type>
        <loader type='generic'>/usr/share/qemu/OVMF_CODE.fd</loader>
        <nvram template='/usr/share/qemu/OVMF_VARS.fd'>/path/to/OVMF_VARS.fd</nvram>
        <boot dev='hd'/>
        <kernel>/path/to/vmlinuz</kernel>
        <cmdline>root=/dev/vda3 selinux=0 rw console=hvc0</cmdline>
      </os>
      <features>
        <acpi/>
        <apic/>
        <ioapic driver='qemu'/>
        <pic state='off'/>
      </features>
      <clock offset='utc'>
        <timer name='hpet' present='no'/>
      </clock>
      <on_poweroff>destroy</on_poweroff>
      <on_reboot>restart</on_reboot>
      <on_crash>destroy</on_crash>
      <pm>
        <suspend-to-mem enable='no'/>
        <suspend-to-disk enable='no'/>
      </pm>
      <cpu mode='host-passthrough'>
        <topology sockets='1' cores='1' threads='1'/>
      </cpu>
      <devices>
        <emulator>/usr/libexec/qemu-kvm</emulator>
        <disk type='file' device='disk'>
          <driver name='qemu' type='qcow2'/>
          <source file='/path/to/td-guest.qcow2'/>
          <target dev='vda' bus='virtio'/>
        </disk>
        <interface type="user">
          <model type="virtio"/>
        </interface>
        <console type='pty'>
          <target type='virtio' port='0'/>
        </console>
        <channel type='unix'>
          <source mode='bind'/>
          <target type='virtio' name='org.qemu.guest_agent.0'/>
        </channel>
      </devices>
      <allowReboot value='no'/>
      <launchSecurity type='tdx'>
        <policy>0x1</policy>
      </launchSecurity>
      <qemu:commandline>
        <qemu:arg value='-cpu'/>
        <qemu:arg value='host,-kvm-steal-time'/>
      </qemu:commandline>
    </domain>
    ```

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
