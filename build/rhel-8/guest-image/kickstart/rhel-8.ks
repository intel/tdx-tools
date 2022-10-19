%packages --instLangs en_US --excludedocs --excludeWeakdeps --ignoremissing
@Core
bash-completion
bzip2
chrony
dnf-utils
efi-filesystem
iotop
iperf3
man-pages
mlocate
nano
openssh-clients
policycoreutils-python-utils
prefixdevname
psmisc
python3
python3-libselinux
python3-pip
setools-console
strace
tar
tuned
unzip
util-linux-user
vim
wget
zsh
podman-docker

-a*firmware*
-biosdevname
-dracut-config-rescue
-geolite2-*
-i*firmware*
-iprutils
-kernel-tools
-lib*firmware*
-libxkbcommon
-network-scripts
-NetworkManager-team
-NetworkManager-tui
-parted
-plymouth
-*rhn*
-*spacewalk*
-sqlite
-sssd*
-subs*

# Repositories
#centos-stream-release
#centos-stream-repos
epel-release

%end

%post --erroronfail --log=/var/log/ks-rhel-8.log

echo ""
echo "POST BASE CENTOS *************************************"
echo ""

# Enable PowerTools repo
dnf config-manager --set-enabled powertools

# Load variables with current OS info
source /etc/os-release

# Guest Agent / Performance
mkdir -p /etc/qemu-ga /etc/tuned
echo '[general]' > /etc/qemu-ga/qemu-ga.conf
echo 'logfile = /var/log/qemu-ga/qemu-ga.log' >> /etc/qemu-ga/qemu-ga.conf
mkdir -p /var/log/qemu-ga
echo 'verbose = 1' >> /etc/qemu-ga/qemu-ga.conf
sed -i 's/BLACKLIST_RPC/#BLACKLIST_RPC/g' /etc/sysconfig/qemu-ga
echo virtual-guest > /etc/tuned/active_profile

# Services
systemctl disable dnf-makecache.timer loadmodules.service nis-domainname.service remote-fs.target

# Make sure rescue image is not built without a configuration change
echo dracut_rescue_image=no > /etc/dracut.conf.d/no-rescue.conf

# Finalize
rm -f /var/lib/systemd/random-seed
restorecon -R /etc > /dev/null 2>&1 || :

# Clean
dnf -C clean all
/bin/rm -rf /etc/*- /etc/*.bak /root/* /tmp/* /var/tmp/*
/bin/rm -rf /var/cache/dnf/* /var/lib/dnf/modulefailsafe/*
/bin/rm -rf /var/log/*debug /var/log/anaconda /var/lib/rhsm

%end
