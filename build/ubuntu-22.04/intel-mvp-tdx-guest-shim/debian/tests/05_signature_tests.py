#
# UEFI signature validation
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

import os
import subprocess
import sys
import unittest
import tempfile

from pathlib import Path

from uefi_tests_base import UEFITestsBase


class TestSignatures(UEFITestsBase):
    """
    Validate UEFI signatures for common problems
    """
    @classmethod
    def setUpClass(klass):
        UEFITestsBase.setUpClass()


    def testInstalledGrubIsSigned(self):
        """Check that the GRUB copy we installed is correctly signed"""
        installed_grub_file = Path(self.signed_grub_path)
        self.assertTrue(installed_grub_file.exists())
        signed_out = subprocess.run(['sbverify', '--list', self.signed_grub_path],
                                    stdout=subprocess.PIPE)
        self.assertIn(b'image signature issuers:', signed_out.stdout)

    def testGrubSignatureValid(self):
        """Ensure the installed GRUB binary from packaging is signed with the expected key"""
        self.assertSignatureOK(self.canonical_ca, self.signed_grub_path)

    def testInstalledShimIsSigned(self):
        """Check that the installed shim is signed"""
        installed_shim_file = Path(self.signed_shim_path)
        self.assertTrue(installed_shim_file.exists())
        signed_out = subprocess.run(['sbverify', '--list', self.signed_shim_path],
                                    stdout=subprocess.PIPE)
        self.assertIn(b'image signature issuers:', signed_out.stdout)

    def testHaveSignedShimOnESP(self):
        """Verify that packaging has provided a signed shim"""
        signed_shim_file = Path(self.installed_shim)
        self.assertTrue(signed_shim_file.exists())

    def testSignaturesExist(self):
        """Validate that a binary has non-zero signatures"""
        unsigned_out = subprocess.run(['sbverify', '--list', self.unsigned_shim_path],
                                      stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.assertIn(b'No signature table present', unsigned_out.stderr)
        signed_out = subprocess.run(['sbverify', '--list', self.signed_shim_path],
                                    stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.assertIn(b'image signature issuers:', signed_out.stdout)

    def testSignatureIsReplayable(self):
        """Attest that signature is retrievable from a binary and can be replayed"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            subprocess.call(['sbattach',
                             '--detach', os.path.join(tmpdirname, 'sig.pkcs7'),
                             self.signed_shim_path])
            pkcs7_certs = subprocess.run(['openssl', 'pkcs7',
                                          '-inform', 'der',
                                          '-in', os.path.join(tmpdirname, 'sig.pkcs7'),
                                          '-print_certs'],
                                          stdout=subprocess.PIPE)
            with open(os.path.join(tmpdirname, 'out.crt'), 'ab+') as certstore:
                certstore.write(pkcs7_certs.stdout)
                self.assertSignatureOK(os.path.join(tmpdirname, 'out.crt'), self.signed_shim_path)


unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout, verbosity=2))
