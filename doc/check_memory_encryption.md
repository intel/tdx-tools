## Verify memory of TD Guest is encrypted

### Install dependencies

The tool `extract-vmlinux` is used to extract vmlinux from the guest kernel. The tool is from
the host kernel devel package. Install it:

```
sudo dnf install intel-mvp-tdx-host-kernel-devel
```

### Check the original `text` code section of guest kernel

#### 1. Extract the guest kernel

```
/usr/src/kernels/$(uname -r)/scripts/extract-vmlinux <path-to-guest-kernel-file > vmlinux
```

#### 2. Disassemble the TD guest kernel `vmlinux`

```
objdump -d vmlinux > disassembled-vmlinux.asm && head -n 20 disassembled-vmlinux.asm

...
ffffffff81000000 <.text>:
ffffffff81000000:   48 8d 25 51 3f c0 01    lea   0x1c03f51(%rip),%rsp
ffffffff81000007:   48 8d 3d f2 ff ff ff    lea   -0xe(%rip),%rdi
ffffffff8100000e:   56                      push %rsi
ffffffff8100000f:   e8 dc 06 00 00          callq 0xffffffff810006f0
...
```

The result shows that the virtual address of `text` section start from `0xffffffff81000000`.

#### Verify the instructions at the same address in a non-TD guest

#### 1. Launch a non-TD VM

`nokaslr` should be appended to VM's kernel command line to disable kernal randomization.
And a qemu monitor shell with telnet should also be created.

The `qemu-kvm` command is like:

```
/usr/libexec/qemu-kvm  -monitor telnet:127.0.0.1:9001,server,nowait -kernel <path-to-the-guest-kernel-file> -append "root=/dev/vda3 rw console=hvc0 nokaslr ..."
```

#### 2. Enter qemu monitor shell

```
telnet 127.0.0.1 9001
```

#### 3. Stop VM, dissemble and check virtual address `0xffffffff8100000`

In the qemu monitor shell:

```
(qemu) stop

(qemu) x /10i 0xffffffff8100000
0x01000000:  48 8d 25 51 3f c0 01     leaq     0x1c03f51(%rip), %rsp
0x01000007:  48 8d 3d f2 ff ff ff     leaq     -0xe(%rip), %rdi
0x0100000e:  56                       pushq    %rsi
0x0100000f:  e8 dc 06 00 00           callq    0x10006f0
...
```

The disassembled instructions should be unique to the original static kernel image.

### Verify the instructions at the same address in a TD guest

#### 1. Launch a TD guest with following change:

- Enable debug by appending `debug=on` to `tdx-guest` object in qemu command line parameter, like:

```
-object tdx-guest,id=tdx,debug=on
```

- Append `nokaslr` in kernel command, like:

```
-append "root=/dev/vda1 console=hvc0 earlyprintk=ttyS0 ignore_loglevel tdx_disable_filter nokaslr"

```

- Create a qemu monitor console:

```
-monitor telnet:127.0.0.1:9001
```

#### 2. Enter qemu monitor shell

```
telnet 127.0.0.1 9001
```

#### 3. Stop TD guest, dissemble and check virtual address `0xffffffff8100000`

In the qemu monitor shell:

```
(qemu) stop
(qemu) x /10i 0xffffffff81000000
0xffffffff81000000:  98                       cwtl
0xffffffff81000001:  f8                       clc
0xffffffff81000002:  49 5e                    popq     %r14
0xffffffff81000004:  5a                       popq     %rdx
0xffffffff81000005:  55                       pushq    %rbp
...
```

The  disassembled instructions should differ from non-TD, meaningless since the memory is encrypted.
