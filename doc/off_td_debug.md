## Off-TD Debug

### Prepare for Debug Info

You can install debug info from the yum repository that provides the guest kernel debuginfo

```
sudo dnf install intel-mvp-tdx-guest-kernel-debuginfo
```

or install the RPMs directly

```
cd <path to guest-kernel packages>
sudo dnf install intel-mvp-tdx-guest-kernel-debuginfo-common-x86_64-<guest-kernel-version>.el8.x86_64.rpm \
intel-mvp-tdx-guest-kernel-debuginfo-<guest-kernel-version>.el8.x86_64.rpm
```

After debug info installed, you can find debuggable modules in `/usr/lib/debug/usr/lib/modules/` and sources in `/usr/src/debug/`

### Start a Debuggable TD guest

Please use the qemu command to Launch TD guest via qemu-kvm and add below parameters.

- Append `debug=on` to `tdx-guest` to turn on debugging, like

```
-object tdx-guest,id=tdx,debug=on
```

- Add `-s -S` parameter to qemu-kvm to sets GDB stub server on localhost port 1234 and wait for connection from GDB to Qemu

- Append `nokaslr` to TD kernel command line to disable kernel address randomization

After that, the qemu process starts and waits for GDB connection.

```
/usr/libexec/qemu-kvm -s -S -accel kvm -monitor telnet:127.0.0.1:9001,server,nowait -object tdx-guest,id=tdx,debug=on -append "nokaslr ..." ...
char device redirected to /dev/pts/5 (label compat_monitor0)
```

### Connect to Qemu GDB Stub

On another console, set MOD_DIR in below script and run the script to start GDB

```bash
#!/usr/bin/env bash

GDB=gdb
MOD_DIR=/usr/lib/debug/usr/lib/modules/<guest kernel>/

$GDB \
-ex "add-auto-load-safe-path $MOD_DIR" \
-ex "file $MOD_DIR/vmlinux" \
-ex "set arch i386:x86-64:intel" \
-ex "set remotetimeout 360" \
-ex "target remote 127.0.0.1:1234"
```

Then the connection is established and GDB waits for you operation:

```
GNU gdb (GDB) Red Hat Enterprise Linux 8.2-18.el8
Copyright (C) 2018 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-redhat-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
<http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word".
BFD: warning: /home/keping/auto-build/src-tdx_guest_v5.15/vmlinux: unsupported GNU_PROPERTY_TYPE (5) type: 0xc0010001
BFD: warning: /home/keping/auto-build/src-tdx_guest_v5.15/vmlinux: unsupported GNU_PROPERTY_TYPE (5) type: 0xc0010002
Reading symbols from vmlinux...done.
The target architecture is assumed to be i386:x86-64:intel
Remote debugging using 127.0.0.1:1234
0x00000000fffffff0 in ?? ()
(gdb)
```

Please use `hb` command in GDB to set the first breakpoint, e.g. `hb start_kernel`.
Please note the software breakpoint is available after the kernel is loaded into GPA space by Qemu.

```
(gdb) hb start_kernel
Hardware assisted breakpoint 1 at 0xffffffff8351c050: file init/main.c, line 938.
(gdb) continue
Continuing.

Breakpoint 1, start_kernel () at init/main.c:938
938             set_task_stack_end_magic(&init_task);
(gdb)
```
