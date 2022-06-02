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

#ifndef _GPXE_LIST_H
#define _GPXE_LIST_H 1

#include <grub/types.h>
#include <gpxe/wrap.h>

struct list_head
{
  struct list_head *next;
  struct list_head *prev;
};

#define LIST_HEAD struct list_head

#define INIT_LIST_HEAD(x) ((x)->next = NULL)
#define LIST_HEAD_INIT(x) { .next = NULL, .prev = NULL }
#define list_empty(x) ((x)->next == NULL)

#define offsetof(type, elem) ((grub_uint8_t *) (&((type *) NULL)->elem) - (grub_uint8_t *) NULL)
#define container_of(var, type, elem) ((type *) ((grub_uint8_t *)(var) - offsetof (type, elem)))

#define list_get_next(it, lst_el, hold)				\
  container_of ((it)->lst_el.next, typeof (*hold), lst_el)

#define list_for_each_entry(it, lst, lst_el)				\
  for ((it) = container_of((lst)->next, typeof (*(it)), lst_el); 	\
       &(it)->lst_el != NULL && &(it)->lst_el != (void *) lst;		\
       (it) = list_get_next(it, lst_el, it))

#define list_for_each_entry_safe(it, next_h, lst, lst_el)		\
    for ((it) = container_of((lst)->next, typeof (*(it)), lst_el);	\
	 &(it)->lst_el != NULL && &(it)->lst_el != (void *) lst;	\
	 ((it) = container_of ((next_h), typeof (*(next_h)), lst_el)),	\
	   (next_h) = list_get_next(it, lst_el, next_h))


static inline void
list_del (struct list_head *head)
{
  if (head->next == head->prev)
    {
      head->next->prev = NULL;
      head->prev->next = NULL;
    }
  else
    {
      head->prev->next = head->next;
      head->next->prev = head->prev;
    }
}

static inline void
list_add_tail (struct list_head *head, struct list_head *new)
{
  if (list_empty (head))
    {
      head->next = head->prev = new;
      new->next = new->prev = head;
    }
  else
    {
      head->prev->next = new;
      new->prev = head->prev;
      new->next = head;
      head->prev = new;
    }
}

static inline void
list_add (struct list_head *head, struct list_head *new)
{
  if (list_empty (head))
    {
      head->next = head->prev = new;
      new->next = new->prev = head;
    }
  else
    {
      head->next->prev = new;
      new->next = head->next;
      new->prev = head;
      head->next = new;
    }
}

#endif
