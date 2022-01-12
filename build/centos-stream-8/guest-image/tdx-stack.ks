
%post --erroronfail --log=/var/log/ks-tdx-stack.log

dnf -y check-update
dnf remove -y grub2-pc
dnf -y install \
    intel-mvp-tdx-guest-grub2-efi-x64 \
    intel-mvp-tdx-guest-grub2-pc \
    intel-mvp-tdx-guest-shim \
    intel-mvp-tdx-guest-kernel-spr

# GRUB / console
sed -i -e 's,GRUB_TERMINAL.*,GRUB_TERMINAL="serial console",' /etc/default/grub
sed -i -e '/GRUB_SERIAL_COMMAND/d' -e '$ i GRUB_SERIAL_COMMAND="serial --speed=115200"' /etc/default/grub
sed -i -e 's/console=tty0 //' -e 's/ console=ttyS0,115200//' /etc/default/grub
sed -i -e 's,GRUB_CMDLINE_LINUX.*,GRUB_CMDLINE_LINUX="root=/dev/vda3 rw console=hvc0",' /etc/default/grub
sed -i -e 's,rhgb ,,g' /etc/default/grub
echo -e "\nGRUB_DISABLE_OS_PROBER=true" >> /etc/default/grub
grubcfg=/boot/efi/EFI/centos/grub.cfg
grub2-mkconfig -o $grubcfg
systemctl enable serial-getty@ttyS0.service

cat > $grubcfg <<EOF
set timeout=5
menuentry 'TD Guest (2022WW03)' {
	insmod gzio
	insmod part_gpt
	insmod ext2
	set root='hd0,gpt3'
  search --no-floppy --label --set=root td_root
	linux	/boot/vmlinuz-5.15.0-3.mvp45.el8.x86_64+spr root=/dev/vda3 rw console=hvc0
	initrd	/boot/initramfs-5.15.0-3.mvp45.el8.x86_64+spr.img
}
menuentry 'Guest OS (CentOS-STREAM8)' {
	insmod gzio
	insmod part_gpt
	insmod ext2
  set root='hd0,gpt3'
  search --no-floppy --label --set=root td_root
	linux	/boot/vmlinuz-4.18.0-348.7.1.el8_5.x86_64 root=/dev/vda3 rw earlyprintk console=tty0 console=ttyS0
	initrd	/boot/initramfs-4.18.0-348.7.1.el8_5.x86_64.img
}
EOF

grubby --set-default /boot/vmlinuz-5.14.0-10.mvp43.el8.x86_64+spr

%end