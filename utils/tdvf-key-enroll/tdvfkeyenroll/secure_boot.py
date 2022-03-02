#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import argparse
import os
import pathlib
import shutil
import stat
import platform
import time
import subprocess
import logging
import struct
from pathlib import Path
from .VarEnroll import var_enroll, VarEnrollOps, is_guid, str2guid

def IsSecureBootConfigValid(SecureBootConfig, build_log):
    '''
    If User provide the PK/KEK/db/dbx params via command line,
    We need check whether whether the params are valid.
    PK/KEK/db/SecureBootEnable is mandatory,
    dbx is optional
    :param SecureBootConfig:
    :param build_log:
    :return:
    '''
    vars = [v for v in SecureBootConfig.keys()]
    mandatory_vars = ['PK', 'KEK', 'db', 'SecureBootEnable']
    valid = True
    for v in mandatory_vars:
        if v not in vars:
            build_log.log(LOG_ERR, "SecureBoot variable [%s] is missing" % v)
            valid = False

    return valid

def SetSecureBootConfig(SecureBootConfig, arg, guid, cert_bin_file, pkg_path, build_log):
    '''
    Set the SecureBootConfig.
    If cert_bin_file is a relative file path, then it should be relative to @pkg_path
    :param SecureBootConfig:
    :param arg:
    :param guid:
    :param cert_bin_file:
    :param pkg_path:
    :return:
    '''
    sb_var_names = {
        '-pk': 'PK',
        '-kek': 'KEK',
        '-db': 'db',
        '-dbx': 'dbx',
        '-secure_boot': 'SecureBootEnable'
    }
    if arg not in sb_var_names.keys():
        build_log.log(LOG_ERR, "Invalid SecureBoot variables[%s]" % arg)
        return False, SecureBootConfig

    if not is_guid(guid):
        build_log.log(LOG_ERR, "Invalid SecureBoot Guid[%s]" % guid)
        return False, SecureBootConfig

    if os.path.isabs(cert_bin_file):
        abs_cert_bin_file = cert_bin_file
    else:
        abs_cert_bin_file = os.path.join(pkg_path, cert_bin_file)

    if not os.path.isfile(abs_cert_bin_file):
        build_log.log(LOG_ERR, "File not exist [%s]. relative path?" % cert_bin_file)
        return False, SecureBootConfig

    var_name = sb_var_names[arg]
    SecureBootConfig[var_name] = [guid, abs_cert_bin_file]
    return True, SecureBootConfig

#
# logging level
#
LOG_DBG  = 0x1
LOG_INFO = 0x2
LOG_WARN = 0x4
LOG_ERR  = 0x8


class BuildLog(object):
    '''
    build log
    '''
    def __init__(self,log_file):
        # Define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)

        # Set a format which is simpler for console use
        console_formatter = logging.Formatter('  %(message)s')
        console.setFormatter(console_formatter) # Tell the handler to use this format

        # Define a Handler which writes INFO messages or higher to the log_file
        file_handler = logging.FileHandler(log_file,'w')
        file_format_str = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s',datefmt='%m-%d %H:%M:%S')
        file_handler.setFormatter(file_format_str)
        file_handler.setLevel(logging.DEBUG)

        self.logger = logging.getLogger(log_file)
        self.logger.addHandler(console)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)

    def close_handlers(self):
        for handler in self.logger.handlers:
            handler.close()

    def log(self, level, log):
        if level == LOG_DBG:
            self.logger.debug(log)
        elif level == LOG_INFO:
            self.logger.info(log)
        elif level == LOG_WARN:
            self.logger.warning(log)
        elif level == LOG_ERR:
            self.logger.error(log)


class VarEnrollParams:
    '''
    VarEnroll related params
    '''
    def __init__(self):
        self.info = None
        self.fd = None
        self.operation = None
        self.name = None
        self.guid = None
        self.attributes = None
        self.data_file = None
        self.output = None

def do_var_enroll(input_fd, output_fd, pkg_path, SecureBootConfig, build_log):
    '''
    enroll Secure Boot related variables
    :param input_fd:
    :param output_fd:
    :param pkg_path:
    :return:
    '''

    FILE_PATH = lambda file, base_dir: file if os.path.isabs(file) else os.path.join(base_dir, file)
    pk_file = FILE_PATH(SecureBootConfig['PK'][1], pkg_path)
    kek_file = FILE_PATH(SecureBootConfig['KEK'][1], pkg_path)
    db_file = FILE_PATH(SecureBootConfig['db'][1], pkg_path)
    dbx_file = FILE_PATH(SecureBootConfig['dbx'][1], pkg_path) if 'dbx' in SecureBootConfig.keys() else None
    enable_bin_file = FILE_PATH(SecureBootConfig['SecureBootEnable'][1], pkg_path)

    out_pk = input_fd + '.pk'
    out_kek = out_pk + '.kek'
    out_db = out_kek + '.db'
    out_dbx = out_db + '.dbx'
    out_sb_enable = out_dbx + '.sb'
    result = False

    while True:
        # enroll pk
        if not os.path.isfile(pk_file):
            break
        args = VarEnrollParams()
        args.__dict__.update(fd=input_fd, output=out_pk, data_file=pk_file,
                             guid=SecureBootConfig['PK'][0], name='PK', operation=VarEnrollOps.add)
        ret = var_enroll(args)
        build_log.log(LOG_DBG, "\nEnroll PK variable -- %s\n"%('Success' if ret else 'Failed'))
        if not ret:
            break

        # enroll kek
        if not os.path.isfile(kek_file):
            break
        args.__dict__.update(fd=out_pk, output=out_kek, data_file=kek_file,
                             guid=SecureBootConfig['KEK'][0], name='KEK', operation=VarEnrollOps.add)
        ret = var_enroll(args)
        build_log.log(LOG_DBG, "\nEnroll KEK variable -- %s\n" % ('Success' if ret else 'Failed'))
        if not ret:
            break

        # enroll db
        if not os.path.isfile(db_file):
            break
        args.__dict__.update(fd=out_kek, output=out_db, data_file=db_file,
                             guid=SecureBootConfig['db'][0], name='db', operation=VarEnrollOps.add)
        ret = var_enroll(args)
        build_log.log(LOG_DBG, "\nEnroll db variable -- %s\n" % ('Success' if ret else 'Failed'))
        if not ret:
            break

        # enroll dbx
        # dbx may not be enrolled
        if dbx_file:
            if not os.path.isfile(dbx_file):
                break

            args.__dict__.update(fd=out_db, output=out_dbx, data_file=dbx_file,
                                 guid=SecureBootConfig['dbx'][0], name='dbx', operation=VarEnrollOps.add)
            ret = var_enroll(args)
            build_log.log(LOG_DBG, "\nEnroll dbx variable -- %s\n" % ('Success' if ret else 'Failed'))
            if not ret:
                break
        else:
            shutil.copyfile(out_db, out_dbx)

        # enable SecureBoot
        if not os.path.isfile(enable_bin_file):
            break
        args.__dict__.update(fd=out_dbx, output=out_sb_enable, data_file=enable_bin_file,
                             name='SecureBootEnable', guid=SecureBootConfig['SecureBootEnable'][0],
                             attributes="0x3", operation=VarEnrollOps.add)
        ret = var_enroll(args)
        build_log.log(LOG_DBG, "\nEnroll SecureBootEnable variable -- %s\n" % ('Success' if ret else 'Failed'))
        if not ret:
            break

        shutil.copyfile(out_sb_enable, output_fd)
        result = True
        break

    ## then clean the tmp files
    if os.path.isfile(out_pk):
        os.remove(out_pk)
    if os.path.isfile(out_kek):
        os.remove(out_kek)
    if os.path.isfile(out_db):
        os.remove(out_db)
    if os.path.isfile(out_dbx):
        os.remove(out_dbx)
    if os.path.isfile(out_sb_enable):
        os.remove(out_sb_enable)

    build_log.log(LOG_DBG, "\n[%s] Enroll All Variables to %s\n" % ('Success' if result else 'Failed', output_fd))

    return result

def main():
    '''
    the main function
    :return:
    '''
    # the default build params
    ARCH = 'X64'
    BUILDTARGET = "DEBUG"
    BUILD_OPTIONS = ''
    SHOW_HELP = False
    FD_PATH = None
    FD_SB_OUTPUT = None
    quit = False

    parent_path = Path(__file__).absolute().parent

    # by default enable secure boot
    SecureBootConfig = {
        'SecureBootEnable': ['f0a30bc7-af08-4556-99c4-001009c93a44',
                             os.path.join(parent_path, 'SecureBootEnable.bin')]
    }

    parser = argparse.ArgumentParser(add_help=False)
    curr_path = pathlib.Path(__file__).parent.absolute()
    pkg_path = str(curr_path)
    build_log = BuildLog(os.path.join(pkg_path, "Build.log"))

    #
    # scan command line to override defaults
    #
    nm, args = parser.parse_known_args()
    argn = len(args)
    i = 0

    while i < argn:
        arg = args[i]
        i += 1

        if arg == '-fd':
            if i >= argn:
                build_log.log(LOG_ERR, 'Missing val of command -fd')
                quit = True
                break
            FD_PATH = args[i]

        elif arg == '-o':
            if i >= argn:
                build_log.log(LOG_ERR, 'Missing val of command -o')
                quit = True
                break
            FD_SB_OUTPUT = args[i]
            
        elif arg in ['-pk', '-kek', '-db', '-dbx', '-secure_boot']:
            # parse SecureBoot related params
            # SecureBoot related params has its dedicated format
            # for exampl: -pk <guid> <cert_file|bin_file>
            if i + 1 >= argn:
                build_log.log(LOG_ERR, 'Missing val of command args [%s] ?' % arg)
                quit = True
                break

            guid = args[i]
            cert_bin_file = args[i+1]
            if guid.startswith('-') or cert_bin_file.startswith('-'):
                quit = True
                break
            # set SecureBootConfig
            valid, SecureBootConfig = SetSecureBootConfig(SecureBootConfig, arg, guid, cert_bin_file, pkg_path, build_log)
            if not valid:
                build_log.log(LOG_ERR, 'Set secure boot config failed.')
                quit = True
                break

            i += 2

        elif arg == '-h':
            SHOW_HELP = True

        else:
            BUILD_OPTIONS += (" %s" % arg)

    if quit:
        return False

    #
    # check SecureBoot config valid
    #
    if len(SecureBootConfig.keys()) > 0:
        valid = IsSecureBootConfigValid(SecureBootConfig, build_log)
        if not valid:
            build_log.log(LOG_ERR, 'Check secure boot config failed.')
            return False

    ## enroll Secure Boot related variables
    input_fd = FD_PATH
    output_dir = FD_SB_OUTPUT if FD_SB_OUTPUT else os.path.dirname(os.path.abspath(input_fd))
    fd_name = os.path.basename(input_fd)
    name_ext = os.path.splitext(fd_name)
    fd_sb_name = name_ext[0] + ".sb" + name_ext[1]
    output_fd = os.path.join(output_dir, fd_sb_name)

    if not os.path.exists(input_fd):
        build_log.log(LOG_ERR, 'input %s not found' % input_fd)
        return False
    if not os.access(output_dir, os.W_OK):
        build_log.log(LOG_ERR, 'no write access to output directory %s, please specify it via -o' % output_dir)
        return False

    result = do_var_enroll(input_fd, output_fd, pkg_path, SecureBootConfig, build_log)
    if not result:
        return False

    return True

if __name__ == '__main__':
    exit(0) if main() else exit(1)
