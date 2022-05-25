/*
 * Copyright (C) 2006 Michael Brown <mbrown@fensystems.co.uk>.
 *
 * Based in part on pci.c from Etherboot 5.4, by Ken Yap and David
 * Munro, in turn based on the Linux kernel's PCI implementation.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

FILE_LICENCE ( GPL2_OR_LATER );

#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <gpxe/tables.h>
#include <gpxe/device.h>
#include <gpxe/pci.h>

/**
 * Enable PCI device
 *
 * @v pci               PCI device
 *
 * Set device to be a busmaster in case BIOS neglected to do so.  Also
 * adjust PCI latency timer to a reasonable value, 32.
 */
void adjust_pci_device ( struct pci_device *pci ) {
        unsigned short new_command, pci_command;
        unsigned char pci_latency;

        pci_read_config_word ( pci, PCI_COMMAND, &pci_command );
        new_command = ( pci_command | PCI_COMMAND_MASTER |
                        PCI_COMMAND_MEM | PCI_COMMAND_IO );
        if ( pci_command != new_command ) {
                pci_write_config_word ( pci, PCI_COMMAND, new_command );
        }

        pci_read_config_byte ( pci, PCI_LATENCY_TIMER, &pci_latency);
        if ( pci_latency < 32 ) {
                pci_write_config_byte ( pci, PCI_LATENCY_TIMER, 32);
        }
}
