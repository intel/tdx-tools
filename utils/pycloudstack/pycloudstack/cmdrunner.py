"""
Manage command line runner thread.
"""
import os
import datetime
import logging
import subprocess
import threading

__author__ = 'cpio'

LOG = logging.getLogger(__name__)


class NativeCmdRunner(threading.Thread):

    """
    Run native command which managed by standalone thread.
    """

    def __init__(self, cmdarr, cwd=None, tty=None, shell=False, silent=False):
        threading.Thread.__init__(self)
        self._stdout = []
        self._stderr = []
        self._retcode = None
        self._cmdarr = cmdarr
        self._duration = -1
        self._is_terminate = False
        self._process = None
        self._cwd = cwd
        self._tty = tty
        self._shell = shell
        self._env = os.environ
        LOG.propagate = not silent

    @property
    def stdout(self):
        """
        Final output after running
        """
        return self._stdout

    @property
    def stderr(self):
        """
        Error output after running
        """
        return self._stderr

    @property
    def retcode(self):
        """
        Ret code for command
        """
        return self._retcode

    @property
    def duration(self):
        """
        Total execution duration
        """
        return self._duration

    @property
    def logprefix(self):
        """
        the prefix string for LOG message
        """
        return "CMD"

    @property
    def env(self):
        """
        Ret environment variables
        """
        return self._env

    @env.setter
    def env(self, new_env):
        """
        Set new environment variables
        """
        self._env = new_env

    def terminate(self):
        """
        Terminate the command process and launch thread
        """
        self._is_terminate = True
        if self._process is not None:
            LOG.debug("Terminate the process: %d", self._process.pid)
            self._process.kill()

    def runwait(self):
        """
        Run until the command executing completed
        """
        self.start()
        self.join()
        return self.retcode

    def runnowait(self):
        """
        Run command but not wait for its complete
        """
        self.start()

    def _execute(self):
        with subprocess.Popen(
            self._cmdarr, shell=self._shell, bufsize=1,
            universal_newlines=True, cwd=self._cwd, stdin=self._tty,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=self._env) as self._process:
            while self._process.returncode is None and not self._is_terminate:
                for line in self._process.stdout:
                    LOG.debug("  [%s-OUT] %s", self.logprefix, line.strip())
                    self._stdout += [line.strip(), ]
                for line in self._process.stderr:
                    LOG.debug("  [%s-ERR] %s", self.logprefix, line.strip())
                    self._stderr += [line.strip(), ]
                self._process.poll()
            self._retcode = self._process.returncode

    def run(self):
        """
        Thread's main run function
        """
        LOG.info("[%s] %s", self.logprefix, " ".join(self._cmdarr))
        start = datetime.datetime.now()
        self._execute()
        end = datetime.datetime.now()
        self._duration = end - start
        LOG.debug("[%s] Completed in %d seconds! ret=%d (%s)", self.logprefix,
                  self._duration.seconds, self.retcode, self._cmdarr[0])


class SSHCmdRunner(NativeCmdRunner):

    """
    Run SSH command
    """

    def __init__(self, cmdarr, ssh_id_key, port, user="root", ip="127.0.0.1"):
        super().__init__(cmdarr)
        os.chmod(ssh_id_key, 0o600)
        self._cmdarr = [
            "ssh", "-v", "-i", ssh_id_key,
            f"{user}@{ip}", "-p", f"{port}",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ConnectTimeout=30",
            "-o", "PreferredAuthentications=publickey",
        ] + cmdarr

    @property
    def logprefix(self):
        return "SSH"
