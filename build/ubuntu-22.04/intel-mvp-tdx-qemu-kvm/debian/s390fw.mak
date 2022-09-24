# Makefile for s390x qemu firmware, building two files:
# s390-ccw.img and s390-netboot.img
# Uses SLOF sources for netboot.

OUT =

S390X_CROSSPFX=s390x-linux-gnu-

LDFLAGS = -Wl,-pie -fPIE -nostdlib \
 -std=gnu99 -fwrapv -fno-common \
 -ffreestanding -fno-delete-null-pointer-checks -msoft-float \
 -march=z900 -fPIE -fno-strict-aliasing -fno-stack-protector \
 -fno-asynchronous-unwind-tables

all: ${OUT}s390-ccw.img ${OUT}s390-netboot.img

CCW_SRCS = start.S main.c bootmap.c jump2ipl.c sclp.c menu.c \
          virtio.c virtio-scsi.c virtio-blkdev.c libc.c cio.c dasd-ipl.c
CCW_FSRCS = $(addprefix pc-bios/s390-ccw/,${CCW_SRCS})

${OUT}s390-ccw.img: $(CCW_FSRCS)
	${S390X_CROSSPFX}gcc -o $@ ${LDFLAGS} $^
	${S390X_CROSSPFX}strip --strip-unneeded $@
	chmod -x $@

NETBOOT_SRCS = start.S sclp.c cio.c virtio.c virtio-net.c jump2ipl.c netmain.c
NETBOOT_FSRCS = $(addprefix pc-bios/s390-ccw/,${NETBOOT_SRCS})

SLOF = roms/SLOF
SLOFLIB = ${SLOF}/lib/libc/

SLOF_LIBSRCS = \
 $(addprefix ${SLOFLIB}ctype/,isdigit.c isxdigit.c toupper.c) \
 $(addprefix ${SLOFLIB}string/,strcat.c strchr.c strrchr.c strcpy.c strlen.c strncpy.c \
              strcmp.c strncmp.c strcasecmp.c strncasecmp.c strstr.c \
              memset.c memcpy.c memmove.c memcmp.c) \
 $(addprefix ${SLOFLIB}stdlib/,atoi.c atol.c strtoul.c strtol.c rand.c malloc.c free.c) \
 $(addprefix ${SLOFLIB}stdio/,sprintf.c snprintf.c vfprintf.c vsnprintf.c vsprintf.c fprintf.c \
             printf.c putc.c puts.c putchar.c stdchnls.c fileno.c) \
 ${SLOF}/slof/sbrk.c \
 $(addprefix ${SLOF}/lib/libnet/,args.c dhcp.c dns.c icmpv6.c ipv6.c tcp.c udp.c bootp.c \
              dhcpv6.c ethernet.c ipv4.c ndp.c tftp.c pxelinux.c) \

${OUT}s390-netboot.img: ${NETBOOT_FSRCS} ${SLOF_LIBSRCS}
	${S390X_CROSSPFX}gcc -o $@ ${LDFLAGS} -Ttext=0x7800000 \
	  -nostdinc -I${SLOFLIB}include -I${SLOF}/lib/libnet -DDHCPARCH=0x1F \
	  $^
	${S390X_CROSSPFX}strip --strip-unneeded $@
	chmod -x $@
