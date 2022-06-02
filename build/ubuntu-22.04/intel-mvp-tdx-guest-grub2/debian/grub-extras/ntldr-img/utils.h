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

#ifndef __UTILS_H
#define __UTILS_H

#if defined(__cplusplus) || defined(c_plusplus)
extern "C" {
#endif

#define MAX_DISKS		10
#define MAX_PARTS		30

#define FST_OTHER		0
#define FST_MBR			1
#define FST_FAT16		2
#define FST_FAT32		3
#define FST_NTFS		4
#define FST_EXT2		5

typedef struct {
  unsigned char	cur;		// Current partition number
  unsigned char	nxt;		// Next partition number
  unsigned char	dfs;		// File system flag
  unsigned char	pad;		// Padding
  unsigned long	bse;		// Partition start address
  unsigned long len;		// Partition length
  unsigned long ebs;		// Base address for the extended partition
} __attribute__ ((packed)) xde_t;

static inline unsigned short
get16 (const void *buf_, unsigned offset)
{
  unsigned char *buf = (unsigned char *) buf_ + offset;
  return buf[0] | (buf[1] << 8);
}
static inline unsigned int
get32 (const void *buf_, unsigned offset)
{
  unsigned char *buf = (unsigned char *) buf_ + offset;
  return buf[0] | (buf[1] << 8) | (buf[1] << 16) | (buf[1] << 24);
}

static inline void
set16 (void *buf_, unsigned offset, unsigned short val)
{
  unsigned char *buf = (unsigned char *) buf_ + offset;
  buf[0] = val;
  buf[1] = val >> 8;
}

static inline void
set32 (void *buf_, unsigned offset, unsigned int val)
{
  unsigned char *buf = (unsigned char *) buf_ + offset;
  buf[0] = val;
  buf[1] = val >> 8;
  buf[2] = val >> 16;
  buf[3] = val >> 24;
}

extern int mbr_nhd, mbr_spt;
int go_sect(int,unsigned long);
int xd_enum(int,xde_t*);
int get_fstype(unsigned char*);
const char* fst2str(int);
const char* dfs2str(int);

#if defined(__cplusplus) || defined(c_plusplus)
}
#endif
#endif /* __UTILS_H */
