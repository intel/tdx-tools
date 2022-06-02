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

#include <gpxe/wrap.h>
#include <gpxe/uaccess.h>

void
memcpy_user (userptr_t dest, off_t dest_off,
	     userptr_t src, off_t src_off, size_t len )
{
  grub_memcpy ((void *) dest+dest_off, (void *) src+src_off, len);
}

userptr_t
virt_to_user (volatile const void *in)
{
  return in;
}

void
free_memblock (void *ptr, size_t size __attribute__ ((unused)))
{
  grub_free (ptr);
}

void *
memchr (void *s, grub_uint8_t c, grub_size_t size)
{
  for (;size && *(grub_uint8_t *)s != c; size--, s = (grub_uint8_t *)s + 1);
  if (size)
    return s;
  return NULL;
}

grub_size_t
strnlen (char *str, grub_size_t n)
{
  grub_size_t r = 0;
  while (*str && n)
    {
      str++;
      n--;
      r++;
    }
  return r;
}
