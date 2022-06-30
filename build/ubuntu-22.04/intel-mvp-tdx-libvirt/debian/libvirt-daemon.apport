'''apport package hook for libvirt source package

(c) 2009-2011 Canonical Ltd.
Author:
Jamie Strandboge <jamie@ubuntu.com>

'''

from apport.hookutils import *
from os import path
import re

def add_info(report):
    attach_conffiles(report, 'libvirt-daemon-system')
    attach_related_packages(report, ['apparmor', 'libapparmor1',
        'libapparmor-perl', 'apparmor-utils', 'auditd', 'libaudit0'])

    # get apparmor stuff.
    attach_mac_events(report, ['/usr/lib/libvirt/virt-aa-helper',
                               '/usr/sbin/libvirtd',
                               'libvirt-.*'])

