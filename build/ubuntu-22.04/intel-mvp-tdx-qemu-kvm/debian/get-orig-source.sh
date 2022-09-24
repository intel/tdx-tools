#! /bin/sh

set -e

base=https://download.qemu.org/
comp=.xz

dir() {
  if [ -d $1 ]; then
     echo removing $1/...
     rm -rf $1
  else
     echo $1/ already removed
  fi
}

file() {
  for f in "$@"; do
    if [ -f "$f" ]; then
      rm -vf -- "$f"
    else
      echo "$f already removed"
    fi
  done
}

clean_dfsg() {
# remove only those blobs which does not have packaged source
# remove all other blobs too

file pc-bios/bios.bin		# roms/seabios/
file pc-bios/bios-256k.bin	# roms/seabios/
file pc-bios/bios-microvm.bin	# roms/qboot/ (old)
file pc-bios/qboot.rom		# roms/qboot/
file pc-bios/hppa-firmware.img	# roms/seabios-hppa/
file pc-bios/sgabios.bin	# roms/sgabios/
file pc-bios/slof.bin		# roms/SLOF/
file pc-bios/vgabios*.bin	# roms/vgabios/
file pc-bios/pxe-*.rom		# roms/ipxe/
file pc-bios/efi-*.rom		# roms/ipxe/
file pc-bios/edk2-*.fd.bz2	# roms/edk2/
file pc-bios/bamboo.dtb		# pc-bios/bamboo.dts
file pc-bios/canyonlands.dtb
file pc-bios/openbios-*		# roms/openbios/
file pc-bios/opensbi-*.bin	# roms/opensbi/
file pc-bios/opensbi-*.elf	# roms/opensbi/
file pc-bios/palcode-clipper	# roms/qemu-palcode/ alpha palcode
file pc-bios/s390-ccw.img	# pc-bios/s390-ccw/
file pc-bios/s390-netboot.img	# pc-bios/s390-ccw/
file pc-bios/kvmvapic.bin	# pc-bios/optionrom/
file pc-bios/linuxboot*.bin	# ditto
file pc-bios/multiboot.bin	# ditto
file pc-bios/pvh.bin		# ditto
file pc-bios/skiboot.lid	# roms/skiboot/
file pc-bios/u-boot.e500	# roms/u-boot/
file pc-bios/u-boot-sam460-20100605.bin	# roms/u-boot-sam460ex/
file pc-bios/QEMU,*.bin	# roms/openbios/
file pc-bios/qemu_vga.ndrv	# roms/QemuMacDrivers/
file pc-bios/vof.bin		# pc-bios/vof/

# remove other software (git submodules)
dir roms/ipxe		# separate package
dir roms/seabios	# separate package
file roms/SLOF/board-js2x/rtas/i2c_bmc.oco
file roms/SLOF/board-js2x/rtas/ipmi_oem.oco
file roms/SLOF/clients/takeover/takeover.oco
file roms/SLOF/lib/libipmi/libipmi.oco
dir roms/edk2		# separate package
dir roms/u-boot		# separate package
file roms/u-boot.tar.*
#dir roms/u-boot-sam460ex # this one is not built by u-boot and requires older compiler
dir roms/QemuMacDrivers

dir dtc		# system dtc exists and used
dir capstone	# system capstone exists and used
dir slirp	# system libslirp exists and used
dir meson	# meson build system

}

case "$#$1" in
  1clean | 1dfsg | 1dfsg[-_]clean)
    if [ -f softmmu/vl.c -a -f hw/block/block.c -a -d pc-bios ]; then
      clean_dfsg
      exit 0
    fi
    echo "apparently not a qemu source dir" >&2; exit 1
    ;;

  1[2-6].*) ;;

  *)
    echo "unknown arguments.  Should be either 'dfsg' or a version number" >&2
    exit 1
    ;;
esac

deb="${1%-*}" # strip debian revision number
upstream="${deb%+dfsg}"
case "$upstream" in
   *~rc*) upstream=$(echo "$upstream" | sed 's/~rc/-rc/') ;;
esac
case "$upstream" in
   [2-6].[0-9] | [2-6].[0-9][!0-9.]* ) # add .0 to a version number
     upstream=$(echo "$upstream" | sed 's/^.\../&.0/') ;;
esac

basetar=qemu-$upstream.tar$comp
basedir=qemu-$deb
debtar=qemu_$deb.orig.tar.xz

if [ ! -f $basetar ]; then

  echo getting upstream version $upstream ...
  wget -Nc $base/$basetar

fi

if [ ! -f $debtar ]; then

  if [ -e $basedir ]; then
    echo "$basedir already exists, please move it away" >&2
    exit 1
  fi

  echo extracting source in $basedir and cleaning up ...
  mkdir $basedir
  cd $basedir
  tar -x -f ../$basetar --strip-components=1
  clean_dfsg

  cd ..
  echo repacking to $debtar ...
  XZ_OPT="-v6" \
  tar -caf $debtar --owner=root --group=root --mode=a+rX --sort=name \
     $basedir

  rm -rf $basedir

fi
