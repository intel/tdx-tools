## Launch TD Guest

### Prerequisites

For direct boot, make sure the guest kernel binary is available to the host:

```
mkdir kernels && pushd kernels
rpm2cpio repo/guest/x86_64/intel-mvp-tdx-kernel-guest-core* | cpio -id
cp cp lib/modules/*/vmlinuz .
popd
```

### Launch via qemu-kvm

Make use of the provided [start_qemu.sh](https://github.com/intel/tdx-tools/main/start-qemu.sh) script to start a TD
via QEMU.

A simple usage of the script would be as follows:

```
./start_qemu.sh -i td-guest-rhel-8.5.qcow2 -k kernels/vmlinuz
```

Or to use the guest's grub bootloader:

```
./start_qemu.sh -i td-guest-rhel-8.5.qcow2 -b direct
```

For more advanced configurations, please check the help menu:

```
./start_qemu.sh -h
```

### Launch via Libvirt

**NOTE:** Please get libvirt template for [direct boot](https://github.com/intel/tdx-tools/blob/main/doc/tdx_libvirt_direct.xml.template)
and [grub boot](https://github.com/intel/tdx-tools/blob/main/doc/tdx_libvirt_grub.xml.template).

1. Configure libvirt

  - As the root user, uncomment and save the following settings in /etc/libvirt/qemu.conf:
    - user = "root"
    - group = "root"
    - dynamic_ownership = 0
  - To make sure libvirt uses these settings, restart the libvirt service:

    ```
    sudo systemctl restart libvirtd
    ```

2. Create a XML configuration file *tdx.xml*

    _**NOTE:**_
    - Please replace the '/path/to' with absolute path in below xml file
    - '/path/to/OVMF_VARS.fd' is destination of OVMF_VARS template.

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
        <kernel>/path/to/kernels/vmlinuz</kernel>
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
        <qemu:arg value='host,-shstk,-kvm-steal-time'/>
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
