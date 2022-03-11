## Launch TD Guest

### 1. qemu-kvm

_**NOTE**:_

- Please replace `<KERNELVERSION>` with real version in below script.
- Change GUEST_IMG to your image name.
- Change the `root=/dev/vda3` to your rootfs node.
- Copy `/usr/share/qemu/OVMF_VARS.fd` to your directory `/path/to/OVMF_VARS.fd`

```
#!/bin/bash
# To specify the number of vcpus of TD guest
CORES=1

# To specify the memory of TD guest, you can use xxxM or xxxG
MEM=2G
OVMF_CODE=/usr/share/qemu/OVMF_CODE.fd
OVMF_VARS=/path/to/OVMF_VARS.fd

GUEST_IMG=$HOME/rhel84.qcow2
KERNEL=$HOME/guest-kernel/lib/modules/<KERNELVERSION>.el8.x86_64+spr/vmlinuz

sudo /usr/libexec/qemu-kvm \
    -accel kvm \
    -no-reboot \
    -name process=tdxvm \
    -cpu host,-kvm-steal-time \
    -smp ${CORES},sockets=1 \
    -m ${MEM} \
    -object tdx-guest,id=tdx \
    -machine q35,kvm-type=tdx,pic=no,kernel_irqchip=split,confidential-guest-support=tdx \
    -device loader,file=${OVMF_CODE},id=fd0,config-firmware-volume=${OVMF_VARS} \
    -vga none \
    -device virtio-net-pci,netdev=mynet0,mac=00:16:3E:68:00:10,romfile= \
    -netdev user,id=mynet0,hostfwd=tcp::10026-:22,hostfwd=tcp::12378-:2375 \
    -device vhost-vsock-pci,guest-cid=3 \
    -chardev stdio,id=mux,mux=on,logfile=./td-guest.log \
    -device virtio-serial,romfile= \
    -device virtconsole,chardev=mux -serial chardev:mux -monitor chardev:mux \
    -drive file=${GUEST_IMG},if=virtio,format=qcow2 \
    -kernel ${KERNEL} \
    -append "root=/dev/vda3 console=hvc0 earlyprintk=ttyS0 \
            ignore_loglevel" \
    -monitor pty \
    -monitor telnet:127.0.0.1:9001,server,nowait \
    -no-hpet -nodefaults
```

### 2. Libvirt

**NOTE:** Please get libvirt template for [direct boot](https://github.com/intel/tdx-tools/blob/main/doc/tdx_libvirt_direct.xml.template)
and [grub boot](https://github.com/intel/tdx-tools/blob/main/doc/tdx_libvirt_grub.xml.template).

1. Create a XML configuration file *tdx.xml*

    _**NOTE:**_
    - Please replace the '/path/to' with absolute path in below xml file
    - '/path/to/OVMF_VARS.fd' is destination of OVMF_VARS template.

    ```
    <domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>
      <name>REPLACEME_NAME</name>
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

2. Launch TD guest

    ```
    sudo virsh create tdx.xml
    ```

    If want to keep the guest domain, please uses:

    ```
    sudo virsh define tdx.xml
    sudo virsh start td-guest
    ```

