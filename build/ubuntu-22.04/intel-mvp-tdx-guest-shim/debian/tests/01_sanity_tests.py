#
# UEFI Shim sanity checks for tests
#
# Copyright (C) 2019 Canonical, Ltd.
# Author: Mathieu Trudel-Lapierre <mathieu.trudel-lapierre@canonical.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import sys
import unittest

from uefi_tests_base import UEFITestsBase


class SanityTests(UEFITestsBase):
    '''
    Sanity checks for uefi tests
    '''

    def testArchitectureSuffixes(self):
        """Ensure sanity of our concept of architecture suffixes for UEFI"""
    
        machine = subprocess.check_output(['uname', '-m']).rstrip().decode('utf-8')
        if machine == 'x86_64':
            self.assertEquals('x64', self.arch_suffix)    
            self.assertEquals('x86_64-efi', self.grub_arch)    
            self.assertEquals('qemu-system-x86_64', self.qemu_arch)
        elif machine == 'aarch64':
            self.assertEquals('aa64', self.arch_suffix)    
            self.assertEquals('arm64-efi', self.grub_arch)    
            self.assertEquals('qemu-system-aarch64', self.qemu_arch)

    def testQemuAvailable(self):
        """Ensure QEMU is available for this architecture"""
        try:
            out = subprocess.run([self.qemu_arch, '-version'], stdout=None)
            out.check_returncode()
        except:
            raise UEFINotAvailable(feature="qemu", arch=self.arch_machine,
                                   details="%s failed to run" % self.qemu_arch)


unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout, verbosity=2))
