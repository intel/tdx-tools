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

#include <gpxe/pci.h>
#include <grub/misc.h>

/* Helper for grub_gpxe_register_pci_nic.  */
static int
grub_gpxe_pci_nic_init (grub_pci_device_t dev, grub_pci_id_t pciid, void *data)
{
  struct pci_driver *nic = data;
  unsigned i;

  for (i = 0; i < nic->id_count; i++)
    {
      int err;
      if (nic->ids[i].devid == pciid)
	{
	  struct pci_device *pci;
	  struct pci_device_id *id;
	  int reg;

	  grub_dprintf ("gpxe", "Attaching NIC %d:%d.%d\n",
			grub_pci_get_bus (dev),
			grub_pci_get_device (dev),
			grub_pci_get_function (dev));
	  pci = grub_malloc (sizeof (*pci));
	  if (!pci)
	    {
	      grub_print_error ();
	      grub_errno = GRUB_ERR_NONE;
	      return 0;
	    }
	  id = grub_malloc (sizeof (*id));
	  if (!id)
	    {
	      grub_free (pci);
	      grub_print_error ();
	      grub_errno = GRUB_ERR_NONE;
	      return 0;
	    }
	  id->devid = pciid;
	  pci->dev.desc.bus_type = BUS_TYPE_PCI;
	  pci->dev.desc.bus = grub_pci_get_bus (dev);
	  pci->dev.desc.location = (grub_pci_get_device (dev) << 3)
	    | grub_pci_get_function (dev);
	  pci->dev.desc.vendor = pciid & 0xffff;
	  pci->dev.desc.device = pciid >> 16;
	  pci->vendor = pciid & 0xffff;
	  pci->device = pciid >> 16;
	  pci->dev.name = grub_xasprintf ("PCI:%02x:%02x.%x",
					  grub_pci_get_bus (dev),
					  grub_pci_get_device (dev),
					  grub_pci_get_function (dev));
	  pci->dev.pci_dev = dev;
	  pci->priv = 0;
	  pci->drvdata = 0;

	  reg = GRUB_PCI_REG_ADDRESSES;
	  while (reg < GRUB_PCI_REG_CIS_POINTER)
	    {
	      grub_uint64_t space;
	      grub_pci_address_t addr;

	      addr = grub_pci_make_address (dev, reg);
	      space = grub_pci_read (addr);

	      reg += sizeof (grub_uint32_t);
	      
	      if (space == 0)
		continue;
	      
	      if ((space & GRUB_PCI_ADDR_SPACE_MASK) 
		  == GRUB_PCI_ADDR_SPACE_IO)
		{
		  pci->ioaddr = space & GRUB_PCI_ADDR_IO_MASK;
		  break;
		}

	      if ((space & GRUB_PCI_ADDR_MEM_TYPE_MASK)
		  == GRUB_PCI_ADDR_MEM_TYPE_64)
		reg += sizeof (grub_uint32_t);
	    }

	  /* No IRQ support yet.  */
	  pci->irq = 0;
	  grub_dprintf ("gpxe", "Probing NIC %d:%d.%d\n",
			grub_pci_get_bus (dev),
			grub_pci_get_device (dev),
			grub_pci_get_function (dev));
	  err = nic->probe (pci, id);
	  grub_dprintf ("gpxe", "Nic probe finished with status %d\n", err);
	}
    }
  return 0;
}

void
grub_gpxe_register_pci_nic (struct pci_driver *nic)
{
  grub_dprintf ("gpxe", "Registering nic\n");
  grub_pci_iterate (grub_gpxe_pci_nic_init, nic);
}

/* FIXME: free all resources associated with driver and detach devices.  */
void
grub_gpxe_unregister_pci_nic (struct pci_driver *nic __attribute__ ((unused)))
{
}
