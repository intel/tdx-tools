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

#ifndef _GPXE_PCI_H
#define _GPXE_PCI_H

#include <grub/pci.h>
#include <gpxe/wrap.h>
#include <gpxe/timer.h>

static inline grub_uint8_t
inb (grub_uint16_t port)
{
  return grub_inb (GRUB_MACHINE_PCI_IO_BASE + port);
}

static inline void
outb (grub_uint8_t data, grub_uint16_t port)
{
  return grub_outb (data, GRUB_MACHINE_PCI_IO_BASE + port);
}

static inline void
outw (grub_uint16_t data, grub_uint16_t port)
{
  return grub_outw (data, GRUB_MACHINE_PCI_IO_BASE + port);
}

static inline grub_uint16_t
inw (grub_uint16_t port)
{
  return grub_inw (GRUB_MACHINE_PCI_IO_BASE + port);
}

static inline void
insw (grub_uint16_t port, grub_uint16_t *data, int count)
{
  while (count--)
    *data++ = grub_inw (GRUB_MACHINE_PCI_IO_BASE + port);
}

static inline void
outsw (grub_uint16_t port, grub_uint16_t *data, int count)
{
  while (count--)
    grub_outw (*data++, GRUB_MACHINE_PCI_IO_BASE + port);
}

static inline void
outsb (grub_uint16_t port, grub_uint8_t *data, int count)
{
  while (count--)
    grub_outb (*data++, GRUB_MACHINE_PCI_IO_BASE + port);
}

static inline void
insb (grub_uint16_t port, grub_uint8_t *data, int count)
{
  while (count--)
    *data++ = grub_inb (GRUB_MACHINE_PCI_IO_BASE + port);
}

static inline void
outl (grub_uint32_t data, grub_uint16_t port)
{
  return grub_outw (data, GRUB_MACHINE_PCI_IO_BASE + port);
}

static inline grub_uint16_t
inl (grub_uint32_t port)
{
  return grub_inw (GRUB_MACHINE_PCI_IO_BASE + port);
}

struct device_description
{
  enum {BUS_TYPE_PCI, BUS_TYPE_ISA} bus_type;
  int bus;
  int location;
  grub_uint16_t vendor;
  grub_uint16_t device;
};

struct device
{
  struct device_description desc;
  char *name;
  union
  {
    grub_pci_device_t pci_dev;
  };
};

struct pci_device
{
  struct device dev;

  grub_uint16_t ioaddr;
  grub_uint16_t vendor;
  grub_uint16_t device;

  int irq;

  void *priv;

  void *drvdata;
};

struct pci_device_id
{
  grub_pci_id_t devid;
};

#define PCI_ROM(vendor, model, short_name, long_name, num) {.devid = ((vendor) | ((model) << 16))}
#define __pci_driver

struct nic;

struct pci_driver
{
  struct pci_device_id *ids;
  grub_size_t id_count;
  int (*probe) (struct pci_device *pci, const struct pci_device_id *id);
  void (*remove) (struct pci_device *pci);
  void (*irq) (struct nic *nic, int action);
};

static inline void
pci_read_config_byte (struct pci_device *dev, grub_uint32_t reg,
		      grub_uint8_t *val)
{
  grub_pci_address_t addr;
  addr = grub_pci_make_address (dev->dev.pci_dev, reg);
  *val = grub_pci_read_byte (addr);
}

static inline void
pci_read_config_word (struct pci_device *dev, grub_uint32_t reg,
		      grub_uint16_t *val)
{
  grub_pci_address_t addr;
  addr = grub_pci_make_address (dev->dev.pci_dev, reg);
  *val = grub_pci_read_word (addr);
}

static inline void
pci_read_config_dword (struct pci_device *dev, grub_uint32_t reg,
		       grub_uint32_t *val)
{
  grub_pci_address_t addr;
  addr = grub_pci_make_address (dev->dev.pci_dev, reg);
  *val = grub_pci_read (addr);
}

static inline void
pci_write_config_byte (struct pci_device *dev, grub_uint32_t reg,
		       grub_uint8_t val)
{
  grub_pci_address_t addr;
  addr = grub_pci_make_address (dev->dev.pci_dev, reg);
  grub_pci_write_byte (addr, val);
}

static inline void
pci_write_config_word (struct pci_device *dev, grub_uint32_t reg,
		       grub_uint16_t val)
{
  grub_pci_address_t addr;
  addr = grub_pci_make_address (dev->dev.pci_dev, reg);
  grub_pci_write_word (addr, val);
}

static inline void
pci_write_config_dword (struct pci_device *dev, grub_uint32_t reg,
			grub_uint32_t val)
{
  grub_pci_address_t addr;
  addr = grub_pci_make_address (dev->dev.pci_dev, reg);
  grub_pci_write (addr, val);
}

static inline void *
pci_get_drvdata (struct pci_device *dev)
{
  return dev->drvdata;
}

static inline void
pci_set_drvdata (struct pci_device *dev, void *data)
{
  dev->drvdata = data;
}

static inline grub_uint32_t
readl (volatile void *ptr)
{
  return *(volatile grub_uint32_t *) ptr;
}

static inline void
writel (grub_uint32_t data, volatile void *ptr)
{
  *(volatile grub_uint32_t *) ptr = data;
}

static inline grub_addr_t
pci_bar_start (struct pci_device *dev, grub_uint32_t reg)
{
  grub_pci_address_t addr;
  grub_uint64_t space;

  addr = grub_pci_make_address (dev->dev.pci_dev, reg >> 2);
  space = grub_pci_read (addr);

  if ((space & GRUB_PCI_ADDR_SPACE_MASK) == GRUB_PCI_ADDR_SPACE_IO)
    return space & GRUB_PCI_ADDR_IO_MASK;

  if ((space & GRUB_PCI_ADDR_MEM_TYPE_MASK) == GRUB_PCI_ADDR_MEM_TYPE_64)
    {
      addr = grub_pci_make_address (dev->dev.pci_dev, (reg >> 2) + 1);
      space |= ((grub_uint64_t) grub_pci_read (addr)) << 32;
    }

  return space & GRUB_PCI_ADDR_MEM_MASK;
}

/* XXX: make it use grub_pci_device_map_range.  */
static inline void *
bus_to_virt (grub_uint32_t bus)
{
  return (void *) bus;
}

static inline void *
ioremap (grub_uint32_t bus, grub_size_t size __attribute__ ((unused)))
{
  return (void *) bus;
}

static inline grub_uint32_t
virt_to_bus (void *virt)
{
  return (grub_addr_t) virt;
}

void
grub_gpxe_register_pci_nic (struct pci_driver *nic);

void
grub_gpxe_unregister_pci_nic (struct pci_driver *nic);

void adjust_pci_device ( struct pci_device *pci );

#define PCI_VENDOR_ID_DAVICOM 0x0291
#define PCI_VENDOR_ID_WINBOND2 0x1050
#define PCI_VENDOR_ID_COMPEX 0x11f6
#define PCI_COMMAND GRUB_PCI_REG_COMMAND
#define PCI_REVISION_ID GRUB_PCI_REG_REVISION
#define PCI_REVISION PCI_REVISION_ID 
#define PCI_LATENCY_TIMER GRUB_PCI_REG_LAT_TIMER
#define PCI_BASE_ADDRESS_0 GRUB_PCI_REG_ADDRESS_REG0
#define PCI_BASE_ADDRESS_1 GRUB_PCI_REG_ADDRESS_REG1
#define PCI_COMMAND_IO 0x1
#define PCI_COMMAND_MEM 0x2
#define PCI_COMMAND_MASTER 0x4

#endif
