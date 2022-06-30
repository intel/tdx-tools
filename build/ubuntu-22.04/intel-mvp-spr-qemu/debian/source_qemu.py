'''apport package hook for qemu

(c) 2009 Canonical Ltd.
'''

from apport.hookutils import *
import subprocess

def cmd_pipe(command1, command2, input = None, stderr = subprocess.STDOUT, stdin = None):
    '''Try to pipe command1 into command2.'''
    try:
        sp1 = subprocess.Popen(command1, stdin=stdin, stdout=subprocess.PIPE, stderr=stderr, close_fds=True)
        sp2 = subprocess.Popen(command2, stdin=sp1.stdout, stdout=subprocess.PIPE, stderr=stderr, close_fds=True)
    except OSError as e:
        return [127, str(e)]

    out = sp2.communicate(input)[0]
    return [sp2.returncode,out]

def add_info(report):
    attach_hardware(report)
    attach_related_packages(report, ['kvm*', '*libvirt*', 'virt-manager', 'qemu*'])
    rc,output = cmd_pipe(['ps', '-eo', 'comm,stat,euid,ruid,pid,ppid,pcpu,args'], ['egrep', '(^COMMAND|^qemu|^kvm)'])
    if rc == 0:
        report['KvmCmdLine'] = output
