#!/bin/sh
#    libvirt-uri.sh - Automatically switch default libvirt URI for user
#    Copyright (C) 2015 Canonical Ltd.
#
#    Authors: Stefan Bader <stefan.bader@canonical.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

LIBVIRT_DEFAULT_URI="qemu:///system"
if [ -f /proc/xen/capabilities ]; then
	if [ "$(cat /proc/xen/capabilities)" = "control_d" ]; then
		LIBVIRT_DEFAULT_URI="xen:///"
	fi
fi

export LIBVIRT_DEFAULT_URI

