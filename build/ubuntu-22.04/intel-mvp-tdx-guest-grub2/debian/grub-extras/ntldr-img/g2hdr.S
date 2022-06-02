/*
 *  GRUB Utilities --  Utilities for GRUB Legacy, GRUB2 and GRUB for DOS
 *  Copyright (C) 2007 Bean (bean123@126.com)
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

#include <grub/machine/kernel.h>

	.file	"g2hdr.S"

	.text

	.code16

	.globl	start, _start

start:
_start:

	// We are at 0x2000:0
	// Move itself to 0x800:0
	// Don't modify dx

	cld
	movw	%cs, %ax
	movw	%ax, %ds
	movw	$0x800, %ax
	movw	%ax, %es
	xorw	%si, %si
	movw	%si, %di
	movw	$0x80, %cx

	rep
	movsl

	ljmp	$0, $(jump_start-start+0x8000)

jump_start:
	// Move data from 0x2040:0 to 0x820:0

	movw	$0x2040, %ax
	movw	%ax, %ds
	movw	$0x820, %ax
	movw	%ax, %es
	xorl	%eax, %eax
	movb	%dh, (GRUB_DECOMPRESSOR_I386_PC_BOOT_DEVICE + 2)
	movl	GRUB_DECOMPRESSOR_MACHINE_COMPRESSED_SIZE, %eax
	addl	$GRUB_DECOMPRESSOR_I386_PC_MAX_DECOMPRESSOR_SIZE, %eax
	xorl	%ecx, %ecx

1:
	xorw	%si, %si
	movw	%si, %di

	movw	$0x8000, %cx
	cmpl	%ecx, %eax
	jae	2f
	movw	%ax, %cx
2:

	pushw	%cx
	addw	$3, %cx
	shrw	$2, %cx

	rep
	movsl

	popw	%cx

	movw	%ds, %si
	addw	$0x800, %si
	movw	%si, %ds

	movw	%es, %si
	addw	$0x800, %si
	movw	%si, %es

	subl	%ecx, %eax
	jnz	1b

	ljmp	$0, $(0x8000 + 0x200)

	. = _start + 0x200 - 2

	.word 0xAA55
