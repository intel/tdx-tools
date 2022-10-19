#---------------------------------------------------------------------------------------------------
#
# TD Guest Image Kickstart Script
#
# 1. Use RHEL 8.5 as base ISO/Repo
# 3. Add Linux TDX MVP stack repo
# 6. Create EFI GRUB for TD boot but keep legacy grub for legacy boot
#
#---------------------------------------------------------------------------------------------------

%include /rhel-8.ks

lang en_US.UTF-8
keyboard us
timezone US/Eastern
cmdline
zerombr
clearpart --all --initlabel
bootloader --timeout 5 --append "console=tty0 console=ttyS0,115200 net.ifnames.prefix=net ipv6.disable=1 quiet systemd.show_status=yes"
reqpart

# Create Partitions
part biosboot --fstype=biosboot --ondisk vda --size=1
part /boot/efi --fstype efi --ondisk vda --size 200 --fsoptions "umask=0077,shortname=winnt" --label "esp"
part / --fstype xfs --asprimary --size 1024 --grow --label "td_root"

selinux --disabled

# Set password
authselect --useshadow --passalgo sha512
rootpw --plaintext 123456

# Network
network --bootproto dhcp --onboot yes --hostname td-guest

firewall --enabled --service ssh
firstboot --disabled

services --enabled tuned

poweroff
