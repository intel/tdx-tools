
"""
Manage/Customize the VM image via virt-customize tools.

"""

import os
import logging
from .cmdrunner import NativeCmdRunner


__author__ = 'cpio'

LOG = logging.getLogger(__name__)


class VMImage:

    """
    Manage VM qcow2 image
    """

    def __init__(self, filepath, part_root="/dev/sda3", part_efi="/dev/sda2"):
        assert os.path.exists(filepath)
        self._filepath = os.path.realpath(filepath)
        self._part_root = part_root
        self._part_efi = part_efi

    @property
    def filepath(self):
        """
        The file path string for VM image
        """
        return self._filepath

    def copy_in(self, localpath, remotedir):
        """
        Copy local file/directory to remote dir in rootfs partition within Image.
        """
        LOG.info("- COPY [H -> G]: %s ==> %s", localpath, remotedir)
        # Enable root remote login
        runner = NativeCmdRunner(
            ["virt-copy-in", "-a", self._filepath, localpath, remotedir])
        runner.runwait()
        assert runner.retcode == 0

    def copy_out(self, remotepath, localdir):
        """
        Copy remote file/directory to local dir in rootfs partition within Image.

        Wildcards cannot be used.
        """
        LOG.info("- COPY [H <- G]: %s <== %s", localdir, remotepath)
        runner = NativeCmdRunner(
            ["virt-copy-out", "-a", self._filepath, remotepath, localdir])
        runner.runwait()
        assert runner.retcode == 0

    def inject_root_ssh_key(self, pubkey_file=None):
        """
        Inject the test SSH public key into vm image for root account.
        After that, it can execute command within VM via SSH connection.
        """
        # Enable root remote login
        runner = NativeCmdRunner(
            ["virt-customize", "-a", self._filepath,
             "--run-command",
             "echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config"])
        runner.runwait()
        assert runner.retcode == 0

        assert pubkey_file is not None and os.path.exists(pubkey_file)

        # inject the ssh test case for root user in target VM image
        runner = NativeCmdRunner(
            ["virt-customize", "-a", str(self._filepath),
             "--ssh-inject", f"root:file:{pubkey_file}"])
        runner.runwait()
        assert runner.retcode == 0

    def clone(self, filename, filedir=None):
        """
        Clone a VM image to a new image
        """
        if filedir is None:
            filedir = os.path.dirname(self.filepath)

        new_full_path = os.path.join(filedir, filename)

        # Backing image instead of copy original image, the speed/space will be improved much
        runner = NativeCmdRunner(
            ["qemu-img", "create", "-f", "qcow2", "-F", "qcow2", "-b",
             self.filepath, new_full_path])
        assert runner.runwait() == 0

        return VMImage(new_full_path, self._part_root, self._part_efi)

    def destroy(self):
        """
        Destroy the VM image
        """
        LOG.debug("Delete file %s", self.filepath)

        # Check whether file exists
        if not os.path.exists(self.filepath):
            LOG.warning("File %s already been deleted.", self.filepath)
            return

        # Remove file if exists
        try:
            os.remove(self.filepath)
        except (OSError, IOError):
            LOG.error("Fail to delete %s", self.filepath)


def __unit_test():
    logging.basicConfig(level=logging.DEBUG)
    image = VMImage("utils/test.qcow2")
    image.copy_in("/etc/motd", "/root/")
    image.copy_out("/etc/", ".")


if __name__ == "__main__":
    __unit_test()
