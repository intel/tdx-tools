"""
Manage docker registry and container images.
"""

import logging
import docker
from docker.errors import APIError

__author__ = 'cpio'

LOG = logging.getLogger(__name__)


class Registry:
    """
    Common functions for registry operation like login, pull, run.
    """

    def __init__(self, username="dummy", token="dummy", address="registry-1.docker.io"):
        """Initialize the variables"""
        self._docker = docker.from_env()
        self._username = username
        self._token = token
        self._address = address
        self._is_login = False

    @property
    def username(self):
        """username for docker login"""
        return self._username

    @property
    def token(self):
        """token for docker login"""
        return self._token

    def login(self):
        """Login to the docker registry"""
        LOG.info("Login registry %s with user %s",
                 self._address, self.username)
        ret = self._docker.login(
            username=self.username,
            password=self.token,
            registry=self._address
        )
        assert ret["Status"] == "Login Succeeded"
        LOG.info("Successful login")
        self._is_login = True

    def pull(self, image_name):
        """Pull the image from docker registry"""
        try:
            self._docker.images.pull(self._get_container_path(image_name))
        except APIError:
            LOG.error("Fail to pull image: %s", self._get_container_path(image_name),
                      exc_info=True)
            return False
        return True

    def _get_container_path(self, image_name):
        """Concat the address and the image name"""
        return self._address + "/" + image_name

    def run(self, image_name, environment=None, ports=None, devices=None, detach=True,
            refresh=True, login=False, **kwargs):
        """Run image with parameters on docker"""
        environment = {} if environment is None else environment
        ports = {} if ports is None else ports
        devices = [] if devices is None else devices

        if login and not self._is_login:
            self.login()
        if refresh:
            assert self.pull(image_name)
        inst = self._docker.containers.run(
            self._get_container_path(image_name),
            environment=environment,
            ports=ports,
            devices=devices,
            detach=detach,
            **kwargs)
        return inst
