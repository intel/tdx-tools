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

#ifdef LINUX

#define _FILE_OFFSET_BITS 64	// This is required to enable 64-bit off_t
#include <unistd.h>

#endif

#include <stdio.h>
#include <string.h>
#include <fcntl.h>

#include "utils.h"

static unsigned char ebuf[512];

#if defined(WIN32)

#ifdef __GNUC__				// Mingw or Cygwin

#define u_off_t		off64_t
#define u_lseek		lseek64

#else

#define u_off_t		__int64
#define u_lseek		_lseeki64

#endif

#else

#define u_off_t		off_t		// In FreeBSD, off_t is 64-bit !
#define u_lseek		lseek

#endif

int go_sect(int hd,unsigned long sec)
{
  // Test if 64-bit seek is supported
  if (sizeof(u_off_t)>=8)
    {
      u_off_t bs,rs;

      bs=sec;
      bs<<=9;
      rs=u_lseek(hd,bs,SEEK_SET);
      return (bs!=rs);
    }
  else
    {
      unsigned long bs[2];

      bs[0]=sec<<9;
      bs[1]=sec>>23;
      if (bs[1])
        return 1;
      return (lseek(hd,bs[0],SEEK_SET)!=(off_t)bs[0]);
    }
}

// Partition enumerator
// xe->cur is the current partition number, before the first call to xd_enum,
// it should be set to 0xFF
// xe->nxt is the target partition number, if it equals 0xFF, it means enumerate
// all partitions, otherwise, it means jump to the specific partition.
int xd_enum(int hd,xde_t* xe)
{
  int nn=512,kk=1,cc;

  for (cc=xe->cur;;)
    {
      if (cc==0xFF)
        {
          unsigned long pt[4][2];
          int i,j,np;

          if (go_sect(hd,0))
            return 1;
          if (read(hd,ebuf,nn)!=nn)
            return 1;
          if (get16(ebuf,0x1FE)!=0xAA55)
            return 1;
          np=0;
          for (i=0x1BE;i<0x1FE;i+=16)
            if (ebuf[i+4])
              {
                if ((pt[np][1]=get32(ebuf,i+12))==0)
                  return 1;
                pt[np++][0]=get32(ebuf,i+8);
              }
          if (np==0)
            return 1;
          // Sort partition table base on start address
          for (i=0;i<np-1;i++)
            {
              int k=i;
              for (j=i+1;j<np;j++)
                if (pt[k][0]>pt[j][0]) k=j;
              if (k!=i)
                {
                  unsigned long tt;

                  tt=pt[i][0];
                  pt[i][0]=pt[k][0];
                  pt[k][0]=tt;
                  tt=pt[i][1];
                  pt[i][1]=pt[k][1];
                  pt[k][1]=tt;
                }
            }
          // Should have space for MBR
          if (pt[0][0]==0)
            return 1;
          // Check for partition overlap
          for (i=0;i<np-1;i++)
            if (pt[i][0]+pt[i][1]>pt[i+1][0])
              return 1;
          cc=0;
        }
      else if (kk)
        cc++;
      if ((unsigned char)cc>xe->nxt)
        return 1;
      if (cc<4)
        {
          if (xe->nxt<4)
            {
              // Empty partition
              if (! ebuf[xe->nxt*16+4+0x1BE])
                return 1;
              xe->cur=xe->nxt;
              xe->dfs=ebuf[xe->nxt*16+4+0x1BE];
              xe->bse=get32(ebuf,xe->nxt*16+8+0x1BE);
              xe->len=get32(ebuf,xe->nxt*16+12+0x1BE);
              return 0;
            }
          else if (xe->nxt!=0xFF)
            cc=4;
          else while (cc<4)
            {
              if (ebuf[cc*16+4+0x1BE])
                {
                  xe->cur=cc;
                  xe->dfs=ebuf[cc*16+4+0x1BE];
                  xe->bse=get32(ebuf,cc*16+8+0x1BE);
                  xe->len=get32(ebuf,cc*16+12+0x1BE);
                  return 0;
                }
              cc++;
            }
        }
      if ((cc==4) && (kk))
        {
          int i;

          // Scan for extended partition
          for (i=0;i<4;i++)
            if ((ebuf[i*16+4+0x1BE]==5) || (ebuf[i*16+4+0x1BE]==0xF)) break;
          if (i==4)
            return 1;
          xe->ebs=xe->bse=get32(ebuf,i*16+8+0x1BE);
        }
      else
        {
          // Is end of extended partition chain ?
          if (((ebuf[4+0x1CE]!=0x5) && (ebuf[4+0x1CE]!=0xF)) ||
              (get32(ebuf,8+0x1CE)==0))
            return 1;
          xe->bse=xe->ebs+get32(ebuf,8+0x1CE);
        }
      {
        while (1)
          {
            if (go_sect(hd,xe->bse))
              return 1;

            if (read(hd,ebuf,nn)!=nn)
              return 1;

            if (get16(ebuf,0x1FE)!=0xAA55)
              return 1;

            if ((ebuf[4+0x1BE]==5) || (ebuf[4+0x1BE]==0xF))
	      {
		if (get32(ebuf,8+0x1BE)==0)
		  return 1;
		else
		  {
		    xe->bse=xe->ebs+get32(ebuf,8+0x1BE);
		    continue;
		  }
	      }
            break;
          }
        kk=(ebuf[4+0x1BE]!=0);
        if ((kk) && ((xe->nxt==0xFF) || (cc==xe->nxt)))
          {
            xe->cur=cc;
            xe->dfs=ebuf[4+0x1BE];
            xe->bse+=get32(ebuf,8+0x1BE);
            xe->len=get32(ebuf,12+0x1BE);
            return 0;
          }
      }
    }
}

#define EXT2_SUPER_MAGIC      0xEF53

int mbr_nhd, mbr_spt;

static void split_chs(unsigned char* chs,unsigned long* c,unsigned long* h,unsigned long* s)
{
  *h=chs[0];
  *s=(chs[1] & 0x3F)-1;
  *c=((unsigned long)(chs[1]>>6))*256+chs[2];
}

static int chk_chs(unsigned long nhd,unsigned long spt,unsigned long lba,unsigned char* chs)
{
  unsigned long c,h,s;

  split_chs(chs,&c,&h,&s);
  if (c==0x3FF)
    return ((nhd==h+1) && (spt==s+1));
  else
    return (c*nhd*spt+h*spt+s==lba);
}

static int chk_mbr(unsigned char* buf)
{
  unsigned long nhd,spt,a1,a2,c2,h2,s2;
  int i;

  i=0x1BE;
  while ((i<0x1FE) && (buf[i+4]==0))
    i+=16;
  if (i>=0x1FE)
    return 0;
  a1=get32(&buf[i],8);
  a2=a1+get32(&buf[i],12)-1;
  if (a1>=a2)
    return 0;
  split_chs(buf+i+5,&c2,&h2,&s2);
  if (c2==0x3FF)
    {
      nhd=h2+1;
      spt=s2+1;
      if (! chk_chs(nhd,spt,a1,buf+i+1))
        return 0;
    }
  else
    {
      unsigned long c1,h1,s1;
      long n1,n2;

      split_chs(buf+i+1,&c1,&h1,&s1);
      if ((c1==0x3FF) || (c1>c2))
        return 0;
      n1=(long)(c1*a2)-(long)(c2*a1)-(long)(c1*s2)+(long)(c2*s1);
      n2=(long)(c1*h2)-(long)(c2*h1);
      if (n2<0)
        {
          n2=-n2;
          n1=-n1;
        }
      if ((n2==0) || (n1<=0) || (n1 % n2))
        return 0;
      spt=(unsigned long)(n1/n2);
      if (c2)
        {
          n1=(long)a2-(long)s2-(long)(h2*spt);
          n2=(long)(c2*spt);
          if ((n2==0) || (n1<=0) || (n1 % n2))
            return 0;
          nhd=(unsigned long)(n1/n2);
        }
      else
        nhd=h2+1;
    }
  if ((nhd==0) || (nhd>255) || (spt==0) || (spt>63))
    return 0;
  i+=16;
  while (i<0x1FE)
    {
      if (buf[i+4])
        {
          if ((! chk_chs(nhd,spt,get32(&buf[i],8),buf+i+1)) ||
              (! chk_chs(nhd,spt,get32(&buf[i],8)+get32(&buf[i],12)-1,buf+i+5)))
            return 0;
        }
      i+=16;
    }
  mbr_nhd=(int)nhd;
  mbr_spt=(int)spt;
  return 1;
}

int get_fstype(unsigned char* buf)
{
  if (chk_mbr(buf))
    return FST_MBR;

  // The first sector of EXT2 might not contain the 0xAA55 signature
  if (get16(&buf[1024],56)==EXT2_SUPER_MAGIC)
    return FST_EXT2;
  if (get16(&buf[0],0x1FE)!=0xAA55)
    return FST_OTHER;
  if (! memcmp(&buf[0x36],"FAT",3))
    return ((buf[0x26]==0x28) || (buf[0x26]==0x29))?FST_FAT16:FST_OTHER;
  if (! memcmp(&buf[0x52],"FAT32",5))
    return ((buf[0x42]==0x28) || (buf[0x42]==0x29))?FST_FAT32:FST_OTHER;
  if (! memcmp(&buf[0x3],"NTFS",4))
    return ((buf[0]==0xEB) && (buf[1]==0x52))?FST_NTFS:FST_OTHER;
  return FST_OTHER;
}

const char* fst2str(int fs)
{
  switch (fs) {
  case FST_OTHER:
    return "Other";
  case FST_MBR:
    return "MBR";
  case FST_FAT16:
    return "FAT12/FAT16";
  case FST_FAT32:
    return "FAT32";
  case FST_NTFS:
    return "NTFS";
  case FST_EXT2:
    return "EXT2/EXT3";
  default:
    return "Unknown";
  }
}

typedef struct {
  int id;
  const char* str;
} fstab_t;

static fstab_t fstab[]= {
  {0x1,"FAT12"},
  {0x4,"FAT16"},
  {0x5,"Extended"},
  {0x6,"FAT16B"},
  {0x7,"NTFS"},
  {0xB,"FAT32"},
  {0xC,"FAT32X"},
  {0xE,"FAT16X"},
  {0xF,"ExtendedX"},
  {0x11,"(H)FAT12"},
  {0x14,"(H)FAT16"},
  {0x16,"(H)FAT16B"},
  {0x17,"(H)NTFS"},
  {0x1B,"(H)FAT32"},
  {0x1C,"(H)FAT32X"},
  {0x1E,"(H)FAT16X"},
  {0x82,"Swap"},
  {0x83,"Ext2"},
  {0xA5,"FBSD"},
  {0,"Other"}};

const char* dfs2str(int fs)
{
  int i;

  for (i=0;fstab[i].id;i++)
    if (fs==fstab[i].id)
      return fstab[i].str;
  return fstab[i].str;
}
