#!/usr/bin/env python

'''
Enrolling secure boot related keys and variables
'''

import sys
import argparse
import os
import pathlib
import shutil
import logging
from pathlib import Path
from .var_enroll import var_enroll, VarEnrollOps, is_guid

# pylint: disable=consider-using-f-string

def secure_boot_config_valid(sbconfig, build_log):
    '''
    If User provide the PK/KEK/db/dbx params via command line,
    We need check whether whether the params are valid.
    PK/KEK/db/SecureBootEnable is mandatory,
    dbx is optional
    :param sbconfig:
    :param build_log:
    :return:
    '''
    mandatory_vars = ['PK', 'KEK', 'db', 'SecureBootEnable']
    valid = True
    for mandatory_var in mandatory_vars:
        if mandatory_var not in sbconfig:
            build_log.log(LOG_ERR, "SecureBoot variable [%s] is missing" % mandatory_var)
            valid = False

    return valid

def set_sbconfig(sbconfig, arg, guid, cert_bin_file, pkg_path, build_log):
    '''
    Set the sbconfig.
    If cert_bin_file is a relative file path, then it should be relative to @pkg_path
    :param sbconfig:
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
    if arg not in sb_var_names:
        build_log.log(LOG_ERR, "Invalid SecureBoot variables[%s]" % arg)
        return False, sbconfig

    if not is_guid(guid):
        build_log.log(LOG_ERR, "Invalid SecureBoot Guid[%s]" % guid)
        return False, sbconfig

    if os.path.isabs(cert_bin_file):
        abs_cert_bin_file = cert_bin_file
    else:
        abs_cert_bin_file = os.path.join(pkg_path, cert_bin_file)

    if not os.path.isfile(abs_cert_bin_file):
        build_log.log(LOG_ERR, "File not exist [%s]. relative path?" % cert_bin_file)
        return False, sbconfig

    var_name = sb_var_names[arg]
    sbconfig[var_name] = [guid, abs_cert_bin_file]
    return True, sbconfig

#
# logging level
#
LOG_DBG  = 0x1
LOG_INFO = 0x2
LOG_WARN = 0x4
LOG_ERR  = 0x8


class BuildLog():
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
        format_str = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s',
                datefmt='%m-%d %H:%M:%S')
        file_handler.setFormatter(format_str)
        file_handler.setLevel(logging.DEBUG)

        self.logger = logging.getLogger(log_file)
        self.logger.addHandler(console)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)

    def close_handlers(self):
        '''close log handlers'''
        for handler in self.logger.handlers:
            handler.close()

    def log(self, level, log):
        '''set log level'''
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
        self.input = None
        self.operation = None
        self.name = None
        self.guid = None
        self.attributes = None
        self.data_file = None
        self.output = None

def do_var_enroll(input_fd, output_fd, pkg_path, sbconfig, build_log):
    '''
    enroll Secure Boot related variables
    :param input_fd:
    :param output_fd:
    :param pkg_path:
    :return:
    '''

    # pylint: disable=unnecessary-lambda-assignment
    file_path = lambda file, base_dir: file if os.path.isabs(file) else os.path.join(base_dir, file)
    pk_file = file_path(sbconfig['PK'][1], pkg_path)
    kek_file = file_path(sbconfig['KEK'][1], pkg_path)
    db_file = file_path(sbconfig['db'][1], pkg_path)
    dbx_file = file_path(sbconfig['dbx'][1], pkg_path) if 'dbx' in sbconfig else None
    enable_bin_file = file_path(sbconfig['SecureBootEnable'][1], pkg_path)

    out_pk = input_fd + '.pk'
    out_kek = out_pk + '.kek'
    out_db = out_kek + '.db'
    out_dbx = out_db + '.dbx'
    out_sb_enable = out_dbx + '.sb'
    result = False

    # enroll pk
    args = VarEnrollParams()
    args.__dict__.update(input=input_fd, output=out_pk, data_file=pk_file,
    guid=sbconfig['PK'][0], name='PK', operation=VarEnrollOps.ADD)
    ret = var_enroll(args)
    build_log.log(LOG_DBG, "\nEnroll PK variable -- %s\n"%('Success' if ret else 'Failed'))
    if not ret:
        return ret

    # enroll kek
    args.__dict__.update(input=out_pk, output=out_kek, data_file=kek_file,
    guid=sbconfig['KEK'][0], name='KEK', operation=VarEnrollOps.ADD)
    ret = var_enroll(args)
    build_log.log(LOG_DBG, "\nEnroll KEK variable -- %s\n" % ('Success' if ret else 'Failed'))
    if not ret:
        return ret

    # enroll db
    args.__dict__.update(input=out_kek, output=out_db, data_file=db_file,
    guid=sbconfig['db'][0], name='db', operation=VarEnrollOps.ADD)
    ret = var_enroll(args)
    build_log.log(LOG_DBG, "\nEnroll db variable -- %s\n" % ('Success' if ret else 'Failed'))
    if not ret:
        return ret

    # enroll dbx
    # dbx may not be enrolled
    if dbx_file:
        args.__dict__.update(input=out_db, output=out_dbx, data_file=dbx_file,
        guid=sbconfig['dbx'][0], name='dbx', operation=VarEnrollOps.ADD)
        ret = var_enroll(args)
        build_log.log(LOG_DBG, "\nEnroll dbx variable -- %s\n" % \
                ('Success' if ret else 'Failed'))
        if not ret:
            return ret
    else:
        shutil.copyfile(out_db, out_dbx)

    # enable SecureBoot
    args.__dict__.update(input=out_dbx, output=out_sb_enable, data_file=enable_bin_file,
            name='SecureBootEnable', guid=sbconfig['SecureBootEnable'][0],
            attributes="0x3", operation=VarEnrollOps.ADD)
    ret = var_enroll(args)
    build_log.log(LOG_DBG, "\nEnroll SecureBootEnable variable -- %s\n" % \
            ('Success' if ret else 'Failed'))
    if not ret:
        return ret

    shutil.copyfile(out_sb_enable, output_fd)
    result = True

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

    build_log.log(LOG_DBG, "\n[%s] Enroll All Variables to %s\n" % \
            ('Success' if result else 'Failed', output_fd))

    return result

def print_usage():
    '''
    helper function
    '''
    usage = '''tdvf-key-enroll -fd <absolute-path-to-OVMF_VARS.fd>
    -pk <pk-key-guid> <absolute-path-to-PK.cer>
    -kek <kek-guid> <absolute-path-to-KEK.cer>
    -db <db-key-guid> <absolute-path-to-DB.cer>
    [-o outputdir]'''
    print(usage)
    sys.exit()

def main():
    '''
    the main function
    :return:
    '''
    # the default build params
    input_fd = None
    output_dir = None

    parent_path = Path(__file__).absolute().parent

    # by default enable secure boot
    sbconfig = {
        'SecureBootEnable': ['f0a30bc7-af08-4556-99c4-001009c93a44',
                             os.path.join(parent_path, 'SecureBootEnable.bin')]
    }

    parser = argparse.ArgumentParser(add_help=False)
    curr_path = pathlib.Path(__file__).parent.absolute()
    pkg_path = str(curr_path)
    build_log = BuildLog(os.path.join(pkg_path, "Build.log"))

    # scan command line to override defaults
    _, args = parser.parse_known_args()
    argn = len(args)
    i = 0

    if argn == 0:
        print_usage()

    while i < argn:
        arg = args[i]
        i += 1

        if arg == '-fd':
            input_fd = args[i]
            i += 1
        elif arg == '-o':
            output_dir = args[i]
            i += 1
        elif arg in ['-pk', '-kek', '-db', '-dbx', '-secure_boot']:
            # parse SecureBoot related params
            # SecureBoot related params has its dedicated format
            # for exampl: -pk <guid> <cert_file|bin_file>
            guid = args[i]
            cert_bin_file = args[i+1]
            valid, sbconfig = set_sbconfig(
                    sbconfig, arg, guid, cert_bin_file, pkg_path, build_log)
            if not valid:
                build_log.log(LOG_ERR, 'Set secure boot config failed.')
                return False
            i += 2
        else:
            print_usage()

    # check SecureBoot config valid
    if len(sbconfig.keys()) > 0:
        valid = secure_boot_config_valid(sbconfig, build_log)
        if not valid:
            build_log.log(LOG_ERR, 'Check secure boot config failed.')
            return False

    ## enroll Secure Boot related variables
    output_dir = output_dir if output_dir else os.path.dirname(os.path.abspath(input_fd))
    fd_name = os.path.basename(input_fd)
    name_ext = os.path.splitext(fd_name)
    fd_sb_name = name_ext[0] + ".sb" + name_ext[1]
    output_fd = os.path.join(output_dir, fd_sb_name)

    if not os.path.exists(input_fd):
        build_log.log(LOG_ERR, 'input %s not found' % input_fd)
        return False
    if not os.access(output_dir, os.W_OK):
        build_log.log(LOG_ERR, 'no write access to output directory %s' % output_dir)
        return False

    return do_var_enroll(input_fd, output_fd, pkg_path, sbconfig, build_log)

if __name__ == '__main__':
    if main():
        sys.exit()
    else:
        sys.exit(1)
