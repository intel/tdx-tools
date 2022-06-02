# vim: set fileencoding=UTF-8 :
'''apport package hook for grub2

Author: Jean-Baptiste Lallement <jeanbaptiste.lallement@gmail.com>

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License, or (at your
option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
the full text of the license.
'''

from __future__ import print_function

import os
import re
import subprocess

from apport.hookutils import (
    attach_default_grub,
    attach_file,
    attach_file_if_exists,
    path_to_key,
)


def check_shell_syntax(path):
    ''' Check the syntax of a shell script '''
    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.check_call(['/bin/sh', '-n', path], stderr=devnull)
    except subprocess.CalledProcessError:
        return False
    return True


def check_shell_syntax_harder(path):
    ''' Check the syntax of a shell script '''
    try:
        # sh -n is tempting, but not good enough.  Consider this case:
        #
        #   GRUB_CMDLINE_LINUX_DEFAULT=”quiet splash nomodeset”
        #
        # The quotes are Unicode quotes, not valid in the shell and probably
        # caused by copying a line out of a web page.  This is parsed as an
        # instruction to run the 'splash' command with argument 'nomodeset”'
        # and with the GRUB_CMDLINE_LINUX_DEFAULT environment variable set
        # to '”quiet'.  'sh -n' allows this because this is a valid parse
        # and it's possible that the command 'splash' might exist, but what
        # we need to know is whether sourcing the file will fail.
        #
        # Unfortunately this test may involve executing code.  However, this
        # file is already sourced as root when running update-grub, so it
        # seems unlikely that this could do any further harm.
        with open(os.devnull, 'w') as devnull:
            subprocess.check_call(
                ['/bin/sh', '-ec', '. %s' % re.escape(path)], stderr=devnull)
    except subprocess.CalledProcessError:
        return False
    return True


def add_info(report):
    if report['ProblemType'] == 'Package':
        # To detect if root fs is a loop device
        attach_file(report, '/proc/cmdline', 'ProcCmdLine')
        attach_default_grub(report, 'EtcDefaultGrub')
        attach_file_if_exists(report, '/boot/grub/device.map', 'DeviceMap')
        try:
            grub_d = '/etc/default/grub.d'
            for name in sorted(os.listdir(grub_d)):
                if name.endswith('.cfg'):
                    key = 'EtcDefaultGrubD.' + path_to_key(name)
                    attach_file_if_exists(
                        report, os.path.join(grub_d, name), key)
        except OSError:
            pass

        invalid_grub_script = []
        if not check_shell_syntax_harder('/etc/default/grub'):
            invalid_grub_script.append('/etc/default/grub')

        # Check scripts in /etc/grub.d since some users directly change
        # configuration there
        grubdir = '/etc/grub.d'
        for f in os.listdir(grubdir):
            fullpath = os.path.join(grubdir, f)
            if f != 'README' and os.access(fullpath, os.X_OK) \
               and not check_shell_syntax(fullpath):
                invalid_grub_script.append(fullpath)
                attach_file(report, fullpath)

        # TODO: Add some UI to ask if the user modified the invalid script
        # and if he still wants to report it
        if invalid_grub_script:
            report['InvalidGrubScript'] = ' '.join(invalid_grub_script)


if __name__ == '__main__':
    r = {}
    r['ProblemType'] = 'Package'
    add_info(r)
    for k, v in r.items():
        print('%s: "%s"' % (k, v))
        print("========================================")
