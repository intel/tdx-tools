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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>
#include <unistd.h>

#ifndef WIN32

#define O_BINARY		0

#endif

#include "grub_mbr.h"
#include "utils.h"
#include "version.h"

// Application flags, used by this program

#define AFG_VERBOSE		1
#define AFG_PAUSE		2
#define AFG_READ_ONLY		4
#define AFG_NO_BACKUP_MBR	8
#define AFG_FORCE_BACKUP_MBR	16
#define AFG_RESTORE_PREVMBR	32
#define AFG_LIST_PART		64
#define AFG_IS_FLOPPY		128
#define AFG_LBA_MODE		256
#define AFG_CHS_MODE		512
#define AFG_OUTPUT		1024
#define AFG_EDIT		2048

// Grldr flags, this flag is used by grldr.mbr

#define GFG_DISABLE_FLOPPY	1
#define GFG_DISABLE_OSBR	2
#define GFG_DUCE		4
#define GFG_PREVMBR_LAST	128

#define APP_NAME		"grubinst: "

#define print_pause		if (afg & AFG_PAUSE) {fputs("Press <ENTER> to continue ...\n",stderr); fflush(stderr); fgetc(stdin);}

#define print_apperr(a)		{ fprintf(stderr,APP_NAME "%s\n",a); print_pause; }
#define print_syserr(a)		{ perror(APP_NAME a); print_pause; }

static void help(void)
{
  fputs("Usage:\n"
        "\tgrubinst  [OPTIONS]  DEVICE_OR_FILE\n\n"
        "OPTIONS:\n\n"
        "\t--help,-h\t\tShow usage information\n\n"
        "\t--pause\t\t\tPause before exiting\n\n"
        "\t--version\t\tShow version information\n\n"
        "\t--verbose,-v\t\tVerbose output\n\n"
        "\t--list-part,-l\t\tList all logical partitions in DEVICE_OR_FILE\n\n"
        "\t--save=FN,-s=FN\t\tSave the orginal MBR/BS to FN\n\n"
        "\t--restore=FN,-r=FN\tRestore MBR/BS from previously saved FN\n\n"
        "\t--restore-prevmbr,-r\tRestore previous MBR saved in the second sector\n"
        "\t\t\t\tof DEVICE_OR_FILE\n\n"
        "\t--read-only,-t\t\tdo everything except the actual write to the\n"
        "\t\t\t\tspecified DEVICE_OR_FILE. (test mode)\n\n"
        "\t--no-backup-mbr\t\tdo not copy the old MBR to the second sector of\n"
        "\t\t\t\tDEVICE_OR_FILE.\n\n"
        "\t--force-backup-mbr\tforce the copy of old MBR to the second sector\n"
        "\t\t\t\tof DEVICE_OR_FILE.(default)\n\n"
        "\t--mbr-enable-floppy\tenable the search for GRLDR on floppy.(default)\n\n"
        "\t--mbr-disable-floppy\tdisable the search for GRLDR on floppy.\n\n"
        "\t--mbr-enable-osbr\tenable the boot of PREVIOUS MBR with invalid\n"
        "\t\t\t\tpartition table (usually an OS boot sector).\n"
        "\t\t\t\t(default)\n\n"
        "\t--mbr-disable-osbr\tdisable the boot of PREVIOUS MBR with invalid\n"
        "\t\t\t\tpartition table (usually an OS boot sector).\n\n"
        "\t--duce\t\t\tdisable the feature of unconditional entrance\n"
        "\t\t\t\tto the command-line.\n\n"
        "\t--boot-prevmbr-first\ttry to boot PREVIOUS MBR before the search for\n"
        "\t\t\t\tGRLDR.\n\n"
        "\t--boot-prevmbr-last\ttry to boot PREVIOUS MBR after the search for\n"
        "\t\t\t\tGRLDR.(default)\n\n"
        "\t--preferred-drive=D\tpreferred boot drive number, 0 <= D < 255.\n\n"
        "\t--preferred-partition=P\tpreferred partition number, 0 <= P < 255.\n\n"
        "\t--time-out=T,-t=T\twait T seconds before booting PREVIOUS MBR. if\n"
        "\t\t\t\tT is 0xff, wait forever. The default is 5.\n\n"
        "\t\t\t\tbefore booting PREVIOUS MBR. K is a word\n"
        "\t\t\t\tvalue, just as the value in AX register\n"
        "\t\t\t\treturned from int16/AH=1. The high byte is the\n"
        "\t\t\t\tscan code and the low byte is ASCII code. The\n"
        "\t\t\t\tdefault is 0x3920 for space bar.\n\n"
        "\t--key-name=S\t\tSpecify the name of the hot key.\n\n"
        "\t--floppy,-f\t\tif DEVICE_OR_FILE is floppy, use this option.\n\n"
        "\t--floppy=N\t\tif DEVICE_OR_FILE is a partition on a hard\n"
        "\t\t\t\tdrive, use this option. N is used to specify\n"
        "\t\t\t\tthe partition number: 0,1,2 and 3 for the\n"
        "\t\t\t\tprimary partitions, and 4,5,6,... for the\n"
        "\t\t\t\tlogical partitions.\n\n"
        "\t--sectors-per-track=S\tspecifies sectors per track for --floppy.\n"
        "\t\t\t\t1 <= S <= 63, default is 63.\n\n"
        "\t--heads=H\t\tspecifies number of heads for --floppy.\n"
        "\t\t\t\t1 <= H <= 256, default is 255.\n\n"
        "\t--start-sector=B\tspecifies hidden sectors for --floppy=N.\n\n"
        "\t--total-sectors=C\tspecifies total sectors for --floppy.\n"
        "\t\t\t\tdefault is 0.\n\n"
        "\t--lba\t\t\tuse lba mode for --floppy. If the floppy BIOS\n"
        "\t\t\t\thas LBA support, you can specify --lba here.\n"
        "\t\t\t\tIt is assumed that all floppy BIOSes have CHS\n"
        "\t\t\t\tsupport. So you would rather specify --chs.\n"
        "\t\t\t\tIf neither --chs nor --lba is specified, then\n"
        "\t\t\t\tthe LBA indicator(i.e., the third byte of the\n"
        "\t\t\t\tboot sector) will not be touched.\n\n"
        "\t--chs\t\t\tuse chs mode for --floppy. You should specify\n"
        "\t\t\t\t--chs if the floppy BIOS does not support LBA.\n"
        "\t\t\t\tWe assume all floppy BIOSes have CHS support.\n"
        "\t\t\t\tSo it is likely you want to specify --chs.\n"
        "\t\t\t\tIf neither --chs nor --lba is specified, then\n"
        "\t\t\t\tthe LBA indicator(i.e., the third byte of the\n"
        "\t\t\t\tboot sector) will not be touched.\n\n"
        "\t--install-partition=I\tInstall the boot record onto the boot area of\n"
        "\t-p=I\t\t\tpartition number I of the specified hard drive\n"
        "\t\t\t\tor harddrive image DEVICE_OR_FILE.\n\n"
        "\t--boot-file=F,-b=F\tChange the name of boot file.\n\n"
        "\t--load-seg=S\t\tChange load segment for boot file.\n\n"
        "\t--grub2,-2\t\tLoad grub2 kernel g2ldr instead of grldr.\n\n"
        "\t--output,-o\t\tSave embeded grldr.mbr to DEVICE_OR_FILE.\n\n"
        "\t--edit,-e\t\tEdit external grldr/grldr.mbr.\n",
        stderr);
}

int afg,gfg,def_drive,def_part,time_out,hot_key,part_num;
int def_spt,def_hds,def_ssc,def_tsc;
char *save_fn,*restore_fn,boot_file_83[12];
const char *key_name;
const char *boot_file;
unsigned short load_seg;

static char fn_buf[24];

static char* get_disk_name(int n)
{
#if defined(WIN32)
  sprintf(fn_buf,"\\\\.\\PhysicalDrive%d",n);
#elif defined(LINUX)
  sprintf(fn_buf,"/dev/hd%c",'a'+n);
#elif defined(FREEBSD)
  sprintf(fn_buf,"/dev/ad%d",n);
#else
  print_apperr("Disk device is not supported in your system");
  return NULL;
#endif
  return fn_buf;
}

static char* get_flop_name(int n)
{
#if defined(WIN32)
  if (n>1)
    {
      print_apperr("Only two floppy drives are supported");
      return NULL;
    }
  sprintf(fn_buf,"\\\\.\\%c:",'A'+n);
#elif defined(LINUX) || defined(FREEBSD)
  sprintf(fn_buf,"/dev/fd%d",n);
#else
  print_apperr("Floppy device is not supported in your system");
  return NULL;
#endif
  return fn_buf;
}

static char* parse_fname(char* fn)
{
  if ((afg & AFG_OUTPUT) && (fn[0]=='('))
    {
      print_apperr("Can\'t use device name while using --output option");
      return NULL;
    }
  if ((! strncmp(fn,"(hd",3)) || (! strncmp(fn,"(fd",3)))
    {
      int n;
      char *p;

      n=strtol(&fn[3],&p,0);
      if ((n<0) || (n>=MAX_DISKS))
        {
          print_apperr("Invalid device number");
          return NULL;
        }
      if (*p==',')
        {
          part_num=strtol(p+1,&p,0);
          if ((part_num<0) || (part_num>=MAX_PARTS))
            {
              print_apperr("Invalid partition number");
              return NULL;
            }
        }
      if ((*p!=')') || (*(p+1)!=0))
        {
          print_apperr("Invalid device name");
          return NULL;
        }
      if (fn[1]=='h')
        fn=get_disk_name(n);
      else
        {
          fn=get_flop_name(n);
          afg|=AFG_IS_FLOPPY;
        }
    }
  return fn;
}

static char* str_upcase(char* str)
{
  int i;

  for (i=0;str[i];i++)
    if ((str[i]>='a') && (str[i]<='z'))
      str[i]-='a'-'A';

  return str;
}

static char* str_lowcase(char* str)
{
  int i;

  for (i=0;str[i];i++)
    if ((str[i]>='A') && (str[i]<='Z'))
      str[i]+='a'-'A';

  return str;
}

static int SetBootFile(char* fn)
{
  char* pc;

  if (*fn==0)
    return 1;
  if (strlen(fn)>7)
    return 1;
  pc=strchr(fn,'.');
  if (pc)
    if ((pc==fn) || (pc-fn>8) || (strlen(pc+1)>3))
      return 1;
  str_upcase(fn);
  memset(boot_file_83,' ',sizeof(boot_file_83)-1);
  if (pc)
    {
      memcpy(boot_file_83,fn,pc-fn);
      memcpy(&boot_file_83[8],pc+1,strlen(pc+1));
    }
  else
    memcpy(boot_file_83,fn,strlen(fn));
  str_lowcase(fn);
  boot_file=fn;
  return 0;
}

static void list(int hd)
{
  xde_t xe;

  xe.cur=xe.nxt=0xFF;
  fprintf(stderr," #  id        base        leng\n");
  while (! xd_enum(hd,&xe))
    fprintf(stderr,"%2d  %02" PRIX64 "    %8" PRIX64 "    %8" PRIX64 "\n",
	    xe.cur,
	    (uint64_t) xe.dfs,
	    (uint64_t) xe.bse,
	    (uint64_t) xe.len);
}

static int is_grldr_mbr(unsigned char* buf)
{
  int i,n;

  i=0x1B7;
  n=sizeof("Missing MBR-helper.")-1;

  while ((i>n) && (buf[i]==0))
    i--;
  return (! memcmp(&buf[i-n+1],"Missing MBR-helper.", sizeof("Missing MBR-helper.")));
}

static int install(char* fn)
{
  int hd = -1,nn,fs,slen;
  unsigned char prev_mbr[sizeof(grub_mbr)];
  unsigned long ssec;

  if (fn==NULL)
    return 1;

  if (afg & AFG_EDIT)
    {
      unsigned short r1,r2;

      if (afg & AFG_VERBOSE)
        fprintf(stderr,"Edit mode\n");
      hd=open(fn,O_RDWR | O_BINARY,0644);
      if (hd==-1)
        {
          print_syserr("open");
          return errno;
        }
      r1=get16(&grub_mbr[0x1FFA],0);
      nn=read(hd,grub_mbr,sizeof(grub_mbr));
      if (nn==-1)
        {
          print_syserr("read");
          close(hd);
          return errno;
        }
      if (nn<(int)sizeof(grub_mbr))
        {
          print_apperr("The input file is too short");
          close(hd);
          return 1;
        }
      if (get32(&grub_mbr[0x1FFC],0)!=0xAA555247)
        {
          print_apperr("Invalid input file");
          close(hd);
          return 1;
        }
      r2=get16(&grub_mbr[0x1FFA],0);
      if (r1!=r2)
        {
          char buf[80];

          sprintf(buf,"Version number mismatched (old=%d new=%d)",r2,r1);
          print_apperr(buf);
          close(hd);
          return 1;
        }
      go_sect(hd,0);
      afg |= AFG_OUTPUT;
    }

  if (boot_file)
    {
      unsigned short ofs;

      // Patching the FAT32 boot sector
      ofs=get16(&grub_mbr,0x400+0x1EC) & 0x7FF;
      strcpy((char *) &grub_mbr[0x400+ofs],boot_file_83);
      if (load_seg)
        set16(&grub_mbr,0x400+0x1EA,load_seg);

      // Patching the FAT12/FAT16 boot sector
      ofs=get16(&grub_mbr,0x600+0x1EC) & 0x7FF;
      strcpy((char *) &grub_mbr[0x600+ofs],boot_file_83);
      if (load_seg)
        set16(&grub_mbr,0x600+0x1EA,load_seg);

      // Patching the EXT2 boot sector
      ofs=get16(grub_mbr,0x800+0x1EE) & 0x7FF;
      strcpy((char *) &grub_mbr[0x800+ofs],boot_file);

      // Patching the NTFS sector
      ofs=get16(grub_mbr,0xA00+0x1EC) & 0x7FF;
      strcpy((char *) &grub_mbr[0xA00+ofs],boot_file);
      if (load_seg)
        set16(grub_mbr,0xA00+0x1EA,load_seg);

      if (afg & AFG_VERBOSE)
        {
          fprintf(stderr,"Boot file changed to %s\n",boot_file);
          if (load_seg)
            fprintf(stderr,"Load segment changed to %04X\n",load_seg);
        }
    }

  if (afg & AFG_OUTPUT)
    {
      int mode;

      mode=(! (afg & AFG_READ_ONLY))?(O_TRUNC | O_CREAT):0;
      if (! (afg & AFG_EDIT))
        {
          if (afg & AFG_VERBOSE)
            fprintf(stderr,"Extract mode\n");
          hd=open(fn,O_RDWR | O_BINARY | mode,0644);
          if (hd==-1)
            {
              print_syserr("open");
              return errno;
            }
        }
      if (! (afg & AFG_READ_ONLY))
        if (write(hd,grub_mbr,sizeof(grub_mbr))!=sizeof(grub_mbr))
          {
            print_apperr("Write to output file fails");
            close(hd);
            return 1;
          }
      goto quit;
    }

  memset(&grub_mbr[512],0,512);
  grub_mbr[2] = gfg;
  grub_mbr[3]=time_out;
  set16(&grub_mbr,4,hot_key);
  grub_mbr[6] = def_drive;
  grub_mbr[7] = def_part;
  if ((key_name==NULL) && (hot_key==0x3920))
    key_name="SPACE";
  if (key_name)
    strcpy((char *) &grub_mbr[0x1fec],key_name);

  hd=open(fn,O_RDWR | O_BINARY,S_IREAD | S_IWRITE);
  if (hd==-1)
    {
      print_syserr("open");
      return errno;
    }
  if (afg & AFG_LIST_PART)
    {
      list(hd);
      close(hd);
      return 0;
    }
  if (part_num!=-1)
    {
      if (def_ssc!=-1)
        ssec=def_ssc;
      else
        {
          xde_t xe;

          xe.cur=0xFF;
          xe.nxt=part_num;
          if (xd_enum(hd,&xe))
            {
              print_apperr("Partition not found");
              close(hd);
              return 1;
            }
          ssec=xe.bse;
          if (afg & AFG_VERBOSE)
            fprintf(stderr,"Part Fs: %02X (%s)\nPart Leng: %" PRIu64 "\n",xe.dfs,dfs2str(xe.dfs),
		    (uint64_t) xe.len);
        }
    }
  else
    ssec=0;
  if (afg & AFG_VERBOSE)
    fprintf(stderr,"Start sector: %" PRIu64 "\n", (uint64_t) ssec);
  if ((ssec) && (go_sect(hd,ssec)))
    {
      print_apperr("Can\'t seek to the start sector");
      close(hd);
      return 1;
    }
  nn=read(hd,prev_mbr,sizeof(prev_mbr));
  if (nn==-1)
    {
      print_syserr("read");
      close(hd);
      return errno;
    }
  if (nn<(int)sizeof(prev_mbr))
    {
      print_apperr("The input file is too short");
      close(hd);
      return 1;
    }
  fs=get_fstype(prev_mbr);
  if (afg & AFG_VERBOSE)
    {
      fprintf(stderr,"Image type: %s\n",fst2str(fs));
      if (fs==FST_MBR)
        fprintf(stderr,"Num of heads: %d\nSectors per track: %d\n",mbr_nhd,mbr_spt);
    }
  if (fs==FST_OTHER)
    {
      print_apperr("Unknown image type");
      close(hd);
      return 1;
    }
  if (((part_num!=-1) || (afg & AFG_IS_FLOPPY)) && (fs==FST_MBR))
    {
      print_apperr("Should be a file system image");
      close(hd);
      return 1;
    }
  if ((part_num==-1) && ((afg & AFG_IS_FLOPPY)==0) && (fs!=FST_MBR))
    {
      print_apperr("Should be a disk image");
      close(hd);
      return 1;
    }
  if (fs==FST_MBR)
    {
      int n,nfs,sln;
      unsigned long ofs;
      unsigned char bs[1024];

      ofs=0xFFFFFFFF;
      for (n=0x1BE;n<0x1FE;n+=16)
        if (prev_mbr[n+4])
          {
            if (ofs>get32(&prev_mbr[n],8))
              ofs=get32(&prev_mbr[n],8);
          }
      if (ofs<(sizeof(prev_mbr)>>9))
        {
          print_apperr("Not enough room to install mbr");
          close(hd);
          return 1;
        }
      slen=sizeof(prev_mbr);
      if (go_sect(hd,ofs))
        {
          print_apperr("Can\'t seek to the first partition");
          close(hd);
          return 1;
        }
      if (read(hd,bs,sizeof(bs))!=sizeof(bs))
        {
          print_apperr("Fail to read boot sector");
          close(hd);
          return 1;
        }
      nfs=get_fstype(bs);
      if (nfs==FST_FAT32)
        sln=0x5A - 0xB;
      else if (nfs==FST_FAT16)
        sln=0x3E - 0xB;
      else
        sln=0;
      if (sln)
        {
          memcpy(&grub_mbr[0xB],&bs[0xB],sln);
          set32(&grub_mbr[0],0x1C,0);
          set16(&grub_mbr[0],0xE,get16(&grub_mbr[0],0xE) + ofs);
        }
    }
  else if (fs==FST_NTFS)
    slen=2048;
  else
    slen=512;

  if (go_sect(hd,ssec))
    {
      print_apperr("Can\'t seek to the start sector");
      close(hd);
      return 1;
    }

  if (save_fn)
    {
      int h2;

      h2=open(save_fn,O_CREAT | O_TRUNC | O_RDWR | O_BINARY,S_IREAD | S_IWRITE);
      if (h2==-1)
        {
          print_syserr("open save file");
          close(hd);
          return errno;
        }
      nn=write(h2,prev_mbr,slen);
      if (nn==-1)
        {
          print_syserr("write save file");
          close(hd);
          close(h2);
          return errno;
        }
      if (nn<slen)
        {
          print_apperr("Can\'t write the whole MBR to the save file");
          close(hd);
          close(h2);
          return 1;
        }
      close(h2);
    }
  if (afg & AFG_RESTORE_PREVMBR)
    {
      if (fs!=FST_MBR)
        {
          print_apperr("Not a disk image");
          close(hd);
          return 1;
        }
      if (memcmp(&prev_mbr[1024+3],"GRLDR",5))
        {
          print_apperr("GRLDR is not installed");
          close(hd);
          return 1;
        }
      if (get16(prev_mbr,512+510)!=0xAA55)
        {
          print_apperr("No previous saved MBR");
          close(hd);
          return 1;
        }
      memset(&grub_mbr,0,sizeof(grub_mbr));
      memcpy(&grub_mbr,&prev_mbr[512],512);
      memcpy(&grub_mbr[0x1b8],&prev_mbr[0x1b8],72);

      if (afg & AFG_VERBOSE)
        fprintf(stderr,"Restore previous MBR mode\n");
    }
  else
    {
      // Load MBR/BS from restore file or configure grub_mbr
      if (restore_fn)
        {
          int h2;

          h2=open(restore_fn,O_RDONLY | O_BINARY,S_IREAD);
          if (h2==-1)
            {
              print_syserr("open restore file");
              close(hd);
              return errno;
            }
          nn=read(h2,grub_mbr,slen);
          if (nn==-1)
            {
              print_syserr("read restore file");
              close(hd);
              close(h2);
              return errno;
            }
          if ((nn<512) || ((nn & 0x1FF)!=0) ||
              ((fs!=FST_EXT2) && (get16(grub_mbr,510)!=0xAA55)))
            {
              print_apperr("Invalid restore file");
              close(hd);
              close(h2);
              return 1;
            }
          close(h2);
          if (nn<slen)
            memset(&grub_mbr[nn],0,slen-nn);

          //if ((fs==FST_FAT16) || (fs==FST_FAT32) || (fs==FST_NTFS))
          if (fs!=FST_EXT2)
            {
              int new_fs;

              new_fs=get_fstype(grub_mbr);
              if (new_fs!=fs)
                {
                  print_apperr("Invalid restore file");
                  close(hd);
                  return 1;
                }
            }

          if (afg & AFG_VERBOSE)
            fprintf(stderr,"Restore mode\n");
        }
      else
        {
          if (fs==FST_MBR)
            {
              if (! (afg & AFG_NO_BACKUP_MBR))
                {
                  int i;

                  if (afg & AFG_FORCE_BACKUP_MBR)
                    i=512;
                  else
                    for (i=1;i<512;i++)
                      if (prev_mbr[512+i]!=prev_mbr[512])
                        break;

                  if ((i==512) && (! is_grldr_mbr(prev_mbr)))
                    memcpy(&grub_mbr[512],prev_mbr,512);
                  else
                    memcpy(&grub_mbr[512],&prev_mbr[512],512);
                }
              memcpy(&grub_mbr[0x1b8],&prev_mbr[0x1b8],72);
            }
          else if (fs==FST_FAT16)
            {
              memcpy(grub_mbr,&grub_mbr[0x600],slen);
              grub_mbr[0x41]=part_num;
            }
          else if (fs==FST_FAT32)
            {
              memcpy(grub_mbr,&grub_mbr[0x400],slen);
              grub_mbr[0x5D]=part_num;
            }
          else if (fs==FST_NTFS)
            {
              memcpy(grub_mbr,&grub_mbr[0xA00],slen);
              grub_mbr[0x57]=part_num;
            }
          else if (fs==FST_EXT2)
            {
              memcpy(&grub_mbr,&grub_mbr[0x800],slen);
              grub_mbr[0x25]=part_num;
              if (afg & AFG_LBA_MODE)
                grub_mbr[2]=0x42;
              else if (afg & AFG_CHS_MODE)
                grub_mbr[2]=0x2;
              if (def_spt!=-1)
                set16(&grub_mbr,0x18,def_spt);
              else if ((afg & AFG_IS_FLOPPY)==0)
                set16(&grub_mbr,0x18,63);
              if (def_hds!=-1)
                set16(&grub_mbr,0x1A,def_hds);
              else if ((afg & AFG_IS_FLOPPY)==0)
                set16(&grub_mbr,0x1A,255);
              if (def_tsc!=-1)
                set32(&grub_mbr,0x20,def_tsc);
              set32(&grub_mbr,0x1C,ssec);
              // s_inode_size
              if (prev_mbr[1024+0x4C]) // s_rev_level
                set16(&grub_mbr,0x26,get16(&prev_mbr[1024],0x58));
              else
                set16(&grub_mbr,0x26,0x80);
              // s_inodes_per_group
              set32(&grub_mbr,0x28,get32(&prev_mbr[1024],0x28));
              // s_first_data_block+1
              set32(&grub_mbr,0x2C,get32(&prev_mbr[1024],0x14)+1);
            }
          else
            {
              // Shouldn't be here
              print_apperr("Invalid file system");
              close(hd);
              return 1;
            }
          if ((fs==FST_FAT16) || (fs==FST_FAT32) || (fs==FST_NTFS))
            {
              if (afg & AFG_LBA_MODE)
                grub_mbr[2]=0xe;
              else if (afg & AFG_CHS_MODE)
                grub_mbr[2]=0x90;
              else
                grub_mbr[2]=prev_mbr[2];
            }

          if (afg & AFG_VERBOSE)
            fprintf(stderr,"Install mode\n");
        }
      // Patch the new MBR/BS with information from prev_mbr
      if (fs==FST_MBR)
        memcpy(&grub_mbr[0x1b8],&prev_mbr[0x1b8],72);
      else if (fs==FST_FAT16)
        {
          memcpy(&grub_mbr[0xB],&prev_mbr[0xB],0x3E - 0xB);
          set32(grub_mbr,0x1C,ssec);
        }
      else if (fs==FST_FAT32)
        {
          memcpy(&grub_mbr[0xB],&prev_mbr[0xB],0x5A - 0xB);
          set32(grub_mbr,0x1C,ssec);
        }
      else if (fs==FST_NTFS)
        {
          memcpy(&grub_mbr[0xB],&prev_mbr[0xB],0x54 - 0xB);
          set32(grub_mbr,0x1C,ssec);
        }
    }
  if (! (afg & AFG_READ_ONLY))
    {
      nn=write(hd,grub_mbr,slen);
      if (nn==-1)
        {
          print_syserr("write");
          close(hd);
          return errno;
        }
      if (nn<slen)
        {
          print_apperr("Can\'t write the whole mbr");
          close(hd);
          return 1;
        }
    }
  else if (afg & AFG_VERBOSE)
    fprintf(stderr,"Read only mode\n");
quit:
  close(hd);
  if (afg & AFG_PAUSE)
    {
      fputs("The MBR/BS has been successfully installed\n",stderr);
      print_pause;
    }
  return 0;
}

int main(int argc,char** argv)
{
  int idx;

  afg=gfg=0;
  part_num=def_drive=def_part=def_spt=def_hds=def_ssc=def_tsc=-1;
  afg=0;
  gfg=GFG_PREVMBR_LAST;
  time_out=5;
  hot_key=0x3920;
  save_fn=NULL;
  restore_fn=NULL;
  for (idx=1;idx<argc;idx++)
    {
      if (argv[idx][0]!='-')
        break;
      if ((! strcmp(argv[idx],"--help"))
          || (! strcmp(argv[idx],"-h")))
        {
          help();
          print_pause;
          return 1;
        }
      else if (! strcmp(argv[idx],"--version"))
        {
          fprintf(stderr,"grubinst version : " VERSION "\n");
          print_pause;
          return 1;
        }
      else if ((! strcmp(argv[idx],"--verbose")) ||
               (! strcmp(argv[idx],"-v")))
        afg |=AFG_VERBOSE;
      else if (! strcmp(argv[idx],"--pause"))
        afg|=AFG_PAUSE;
      else if ((! strcmp(argv[idx],"--read-only"))
               || (! strcmp(argv[idx],"-t")))
        afg|=AFG_READ_ONLY;
      else if (! strcmp(argv[idx],"--no-backup-mbr"))
        afg|=AFG_NO_BACKUP_MBR;
      else if (! strcmp(argv[idx],"--force-backup-mbr"))
        afg|=AFG_FORCE_BACKUP_MBR;
      else if (! strcmp(argv[idx],"--mbr-enable-floppy"))
        gfg&=~GFG_DISABLE_FLOPPY;
      else if (! strcmp(argv[idx],"--mbr-disable-floppy"))
        gfg|=GFG_DISABLE_FLOPPY;
      else if (! strcmp(argv[idx],"--mbr-enable-osbr"))
        gfg&=~GFG_DISABLE_OSBR;
      else if (! strcmp(argv[idx],"--mbr-disable-osbr"))
        gfg|=GFG_DISABLE_OSBR;
      else if (! strcmp(argv[idx],"--duce"))
        gfg|=GFG_DUCE;
      else if (! strcmp(argv[idx],"--boot-prevmbr-first"))
        gfg&=~GFG_PREVMBR_LAST;
      else if (! strcmp(argv[idx],"--boot-prevmbr-last"))
        gfg|=GFG_PREVMBR_LAST;
      else if (! strncmp(argv[idx],"--preferred-drive=",18))
        {
          def_drive=strtol(&argv[idx][18],NULL,0);
          if ((def_drive<0) || (def_drive>=255))
            {
              print_apperr("Invalid preferred drive number");
              return 1;
            }
        }
      else if (! strncmp(argv[idx],"--preferred-partition=",22))
        {
          def_part=strtol(&argv[idx][22],NULL,0);
          if ((def_part<0) || (def_part>=255))
            {
              print_apperr("Invalid preferred partition number");
              return 1;
            }
        }
      else if ((! strncmp(argv[idx],"--time-out=",11)) ||
               (! strncmp(argv[idx],"-t=",3)))
        {
          time_out=strtol((argv[idx][2]=='=')?&argv[idx][3]:&argv[idx][11],NULL,0);
          if ((time_out<0) || (time_out>255))
            {
              print_apperr("Invalid timeout value");
              return 1;
            }
        }
      else if ((! strncmp(argv[idx],"--key-name=",11)))
        {
          key_name=&argv[idx][11];
          if (strlen(key_name)>13)
            {
              print_apperr("Key name too long");
              return 1;
            }
        }
      else if ((! strcmp(argv[idx],"--restore-prevmbr")) ||
               (! strcmp(argv[idx],"-r")))
        afg|=AFG_RESTORE_PREVMBR;
      else if ((! strncmp(argv[idx],"--save=",7)) ||
               (! strncmp(argv[idx],"-s=",3)))
        {
          save_fn=(argv[idx][2]=='=')?&argv[idx][3]:&argv[idx][7];
          if (*save_fn==0)
            {
              print_apperr("Empty filename");
              return 1;
            }
        }
      else if ((! strncmp(argv[idx],"--restore=",10)) ||
               (! strncmp(argv[idx],"-r=",3)))
        {
          restore_fn=(argv[idx][2]=='=')?&argv[idx][3]:&argv[idx][10];
          if (*restore_fn==0)
            {
              print_apperr("Empty filename");
              return 1;
            }
        }
      else if ((! strcmp(argv[idx],"--list-part")) ||
               (! strcmp(argv[idx],"-l")))
        afg|=AFG_LIST_PART;
      else if ((! strcmp(argv[idx],"--floppy")) ||
               (! strcmp(argv[idx],"-f")))
        afg|=AFG_IS_FLOPPY;
      else if ((! strncmp(argv[idx],"--floppy=",9)) ||
               (! strncmp(argv[idx],"--install-partition=",20)) ||
               (! strncmp(argv[idx],"-p=",3)))
        {
          char *p;

          if (argv[idx][2]=='f')
            p=&argv[idx][9];
          else if (argv[idx][2]=='i')
            p=&argv[idx][20];
          else
            p=&argv[idx][3];
          part_num=strtoul(p,NULL,0);
          if ((part_num<0) || (part_num>=MAX_PARTS))
            {
              print_apperr("Invalid partition number");
              return 1;
            }
        }
      else if (! strcmp(argv[idx],"--lba"))
        afg|=AFG_LBA_MODE;
      else if (! strcmp(argv[idx],"--chs"))
        afg|=AFG_CHS_MODE;
      else if (! strncmp(argv[idx],"--sectors-per-track=",20))
        {
          def_spt=strtol(&argv[idx][10],NULL,0);
          if ((def_spt<1) || (def_spt>63))
            {
              print_apperr("Invalid sector per track");
              return 1;
            }
        }
      else if (! strncmp(argv[idx],"--heads=",8))
        {
          def_hds=strtol(&argv[idx][8],NULL,0);
          if ((def_hds<1) || (def_hds>255))
            {
              print_apperr("Invalid number of heads");
              return 1;
            }
        }
      else if (! strncmp(argv[idx],"--start-sector=",15))
        {
          def_spt=strtol(&argv[idx][15],NULL,0);
          if (def_ssc<0)
            {
              print_apperr("Invalid start sector");
              return 1;
            }
        }
      else if (! strncmp(argv[idx],"--total-sectors=",16))
        {
          def_tsc=strtol(&argv[idx][16],NULL,0);
          if (def_tsc<0)
            {
              print_apperr("Invalid total sectors");
              return 1;
            }
        }
      else if ((! strncmp(argv[idx],"--boot-file=",12)) ||
               (! strncmp(argv[idx],"-b=",3)))
        {
          if (SetBootFile((argv[idx][2]=='=')?&argv[idx][3]:&argv[idx][12]))
            {
              print_apperr("Invalid boot file name");
              return 1;
            }
        }
      else if (! strncmp(argv[idx],"--load-seg=",11))
        {
          load_seg=strtoul(&argv[idx][11],NULL,16);
          if (load_seg<0x1000)
            {
              print_apperr("Load address too small");
              return 1;
            }
        }
      else if ((! strcmp(argv[idx],"--grub2")) ||
               (! strcmp(argv[idx],"-2")))
        {
          if (! boot_file)
            {
              boot_file="g2ldr";
              strcpy(boot_file_83,"G2LDR      ");
            }
        }
      else if ((! strcmp(argv[idx],"--output")) ||
               (! strcmp(argv[idx],"-o")))
        afg|=AFG_OUTPUT;
      else if ((! strcmp(argv[idx],"--edit")) ||
               (! strcmp(argv[idx],"-e")))
        afg|=AFG_EDIT;
      else
        {
          print_apperr("Invalid option, please use --help to see all valid options");
          return 1;
        }
    }
  if (idx>=argc)
    {
      print_apperr("No filename specified");
      return 1;
    }
  if (idx<argc-1)
    {
      print_apperr("Extra parameters");
      return 1;
    }
  return install(parse_fname(argv[idx]));
}
