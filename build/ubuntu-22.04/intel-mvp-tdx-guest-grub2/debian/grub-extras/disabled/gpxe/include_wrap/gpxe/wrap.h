/*
 * Copyright © 2009 Vladimir 'phcoder' Serbinenko <phcoder@gmail.com>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   Redistributions of source code must retain the above copyright
 *   notice, this list of conditions and the following disclaimer.
 *
 *   Redistributions in binary form must reproduce the above copyright
 *   notice, this list of conditions and the following disclaimer in
 *   the documentation and/or other materials provided with the
 *   distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */     

FILE_LICENCE ( BSD2 );

#ifndef _GPXE_WRAP_H
#define _GPXE_WRAP_H

#include <config.h>

#include <grub/misc.h>
#include <grub/dl.h>
#include <errno.h>
#include <grub/mm.h>
#include <gpxe/list.h>
#include <gpxe/timer.h>

void *
memchr (void *s, grub_uint8_t c, grub_size_t size);

#define be64_to_cpu grub_be_to_cpu64
#define cpu_to_be64 grub_cpu_to_be64
#define cpu_to_be32 grub_cpu_to_be32
#define cpu_to_be16 grub_cpu_to_be16
#define le16_to_cpu grub_le_to_cpu16
#define be16_to_cpu grub_be_to_cpu16
#define be32_to_cpu grub_be_to_cpu32
#define cpu_to_le16 grub_cpu_to_le16
#define cpu_to_le32 grub_cpu_to_le32
#define le32_to_cpu grub_le_to_cpu32

/* In gPXE codebase following has to be a macro.
   So grub_cpu_to_be isn't usable.  */
#define bswap_16(x) ((((x) & 0xff) << 8) | (((x) & 0xff00) >> 8))
#define swap16 bswap_16
#ifdef GRUB_CPU_WORDS_BIGENDIAN
#define htons(x) (x)
#define htonl(x) (x)
#else
#define htons(x) (bswap_16(x))
#define htonl(x) ((((x) & 0xff) << 24) | (((x) & 0xff00) << 8) | (((x) & 0xff0000) >> 8) | (((x) & 0xff000000) >> 24))
#endif

#define ntohl(x) htonl(x)
#define ntohs(x) htons(x)

typedef grub_uint64_t u64;
typedef grub_uint64_t uint64_t;
typedef grub_uint32_t u32;
typedef grub_int32_t s32;
typedef grub_uint32_t uint32_t;
typedef grub_int32_t int32_t;
typedef grub_uint16_t u16;
typedef grub_int16_t s16;
typedef grub_uint16_t uint16_t;
typedef grub_int16_t int16_t;
typedef grub_uint8_t u8;
typedef grub_uint8_t uint8_t;
typedef grub_int8_t int8_t;
typedef grub_size_t size_t;

#define __malloc
#define __shared
#define __unused __attribute__ ((unused))

#define off_t grub_off_t

#define strcpy grub_strcpy

#if 0
typedef void *userptr_t;

static inline void memcpy_user ( userptr_t dest, off_t dest_off,
				 userptr_t src, off_t src_off, size_t len )
{
  grub_memcpy ((void *) (dest + dest_off), (void *) (src + src_off), len);
}
#endif

#define memcpy grub_memcpy

#define zalloc grub_zalloc
#define strdup grub_strdup
#define strncmp grub_strncmp
#define strchr grub_strchr
#define strcasecmp grub_strcasecmp
#define printf grub_printf
#define intptr_t grub_addr_t

static inline void *
malloc (grub_size_t size)
{
  return grub_malloc (size);
}

static inline void *
realloc (void *ptr, grub_size_t size)
{
  return grub_realloc (ptr, size);
}

static inline grub_size_t
strlen (const char *s)
{
  return grub_strlen (s);
}

static inline int 
strcmp (const char *s1, const char *s2)
{
  return grub_strcmp (s1, s2);
}

static inline int
toupper (int c)
{
  return grub_toupper (c);
}

static inline int
tolower (int c)
{
  return grub_tolower (c);
}

unsigned long strtoul ( const char *p, char **endp, int base );

static inline int 
isspace (int c)
{
  return grub_isspace (c);
}

static inline int 
isdigit (int c)
{
  return grub_isdigit (c);
}

static inline int 
isalpha (int c)
{
  return grub_isalpha (c);
}

static inline int
islower (int c)
{
  return (c >= 'a' && c <= 'z');
}

static inline int
isupper (int c)
{
  return (c >= 'A' && c <= 'Z');
}

typedef grub_ssize_t ssize_t;

static inline void 
free (void *ptr)
{
  grub_free (ptr);
}

#define assert(x) assert_real(__FILE__, __LINE__, x)

static inline void
assert_real (const char *file, int line, int cond)
{
  if (!cond)
    grub_fatal ("Assertion failed at %s:%d\n", file, line);
}

#define __assert_fail grub_abort

#define __always_inline

#define VERSION_MAJOR 1
#define VERSION_MINOR 97
#define VERSION_PATCH 1

#define strstr grub_strstr
#define alloc_memblock(size,align) grub_memalign(align,size)

#define DBG(fmt,args...) grub_dprintf("net", fmt, ## args)
#define DBG2(fmt,args...) grub_dprintf("net", fmt, ## args)
#define DBG_HD(data,len) 
#define DBGP(fmt,args...) grub_dprintf("net", fmt, ## args)
#define DBGP_HD(data,len) 
#define DBGC(ptr, fmt,args...) grub_dprintf("net", fmt, ## args)
#define DBGCP(ptr, fmt,args...) grub_dprintf("net", fmt, ## args)
#define DBGC2(ptr, fmt,args...) grub_dprintf("net", fmt, ## args)
#define DBGC_HD(ptr,data,len)
#define DBGCP_HD(ptr,data,len)
#define DBGC_HDA(ptr,s,data,len)
#define DBGC2_HDA(ptr,s,data,len)
#define DBGCP_HDA(ptr,s,data,len)

#define strrchr grub_strrchr

static inline void
memswap (void *b1, void *b2, grub_size_t size)
{
  register grub_uint8_t t;
  while (size--)
    {
      t = *(grub_uint8_t *) b1;
      *(grub_uint8_t *) b1 = *(grub_uint8_t *) b2;
      *(grub_uint8_t *) b2 = t;
      b1 = (grub_uint8_t *) b1 + 1;
      b2 = (grub_uint8_t *) b2 + 1;
    }
}

static inline int
flsl (long n)
{
  int i;
  for (i = sizeof (n) - 1; i >= 0; i--)
    if (n & (1 << i))
      return i + 1;
  return 0;
}

#define INT_MAX 2147483647L

#define putchar(x) grub_printf("%c", x)

#define snprintf grub_snprintf
#define ssnprintf grub_snprintf
#define vsnprintf grub_vsnprintf

#endif
