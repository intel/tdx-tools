"""
Session and test running activities will invoke all hooks defined in conftest.py
"""
import os
import logging
# pylint: disable=no-name-in-module,import-error
import pytest
from pycloudstack import virtxml, artifacts
from pycloudstack.vmguest import VMGuestFactory

LOG = logging.getLogger(__name__)

# Disable redefined-outer-name since it is false positive for pytest's fixture
# pylint: disable=redefined-outer-name


@pytest.fixture(scope="module")
def vm_name(request):
    """
    Customized VM name in module scope
    """
    name_marker = request.node.get_closest_marker("vm_name")
    return name_marker.args[0] if name_marker else request.node.name


@pytest.fixture(scope="module")
def vm_image(request, artifact_factory):
    """
    Customized VM image in module scope
    """
    cache_dir = request.config.cache.makedir('downloads')
    dest_dir = request.config.cache.makedir('vm-images')

    image_marker = request.node.get_closest_marker("vm_image")
    if not image_marker:
        raise ValueError("Missing vm_image marker")

    guest = request.config.getoption("--guest")
    image = image_marker.args[0] + '-' + guest
    if not image:
        raise ValueError("Invalid VM OS Image")
    # pylint: disable=unsubscriptable-object
    artobj = artifact_factory[image]
    assert artobj is not None, f"Fail to find the {image} in artifacts.yaml"
    return artobj.get(dest_dir, cache_dir)


@pytest.fixture(scope="module")
def vm_kernel(request, artifact_factory):
    """
    Customized VM kernel in module scope
    """
    cache_dir = request.config.cache.makedir('downloads')
    dest_dir = request.config.cache.makedir('vm-kernels')

    image_marker = request.node.get_closest_marker("vm_kernel")
    if not image_marker:
        raise ValueError("Missing vm_kernel marker")

    guest = request.config.getoption("--guest")
    kernel = image_marker.args[0] + '-' + guest
    if not kernel:
        raise ValueError("Invalid VM kernel")
    # pylint: disable=unsubscriptable-object
    artobj = artifact_factory[kernel]
    assert artobj is not None, f"Fail to find the {kernel} in artifacts.yaml"
    return artobj.get(dest_dir, cache_dir)


# pylint: disable=redefined-outer-name
@pytest.fixture(scope="module")
def vm_factory(request, vm_image, vm_kernel):
    """
    New mark for the vm factory to create different VM.
    """
    factoryobj = VMGuestFactory(vm_image, vm_kernel)
    yield factoryobj
    LOG.info("Delete factory instance for cleanup")
    keep_issue_vm = request.config.getoption("--keep-vm")
    factoryobj.set_keep_issue_vm(keep_issue_vm)
    factoryobj.removeall()
    del factoryobj


@pytest.fixture(autouse=True, scope="session")
def output():
    """
    Get output path
    """
    outdir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(outdir, exist_ok=True)
    virtxml.VirtXml.set_output_dir(outdir)
    return outdir


@pytest.fixture(autouse=True, scope="session")
def vm_ssh_key():
    """
    SSH key for remote running command to guest VM
    """
    return os.path.join(os.path.dirname(__file__), "vm_ssh_test_key")


@pytest.fixture(autouse=True, scope="session")
def vm_ssh_pubkey():
    """
    SSH key for remote running command to guest VM
    """
    return os.path.join(os.path.dirname(__file__), "vm_ssh_test_key.pub")


@pytest.fixture(scope="session")
def artifact_factory():
    """
    The artifact factory from artifacts.yaml
    """
    manifest_file = os.path.join(os.path.dirname(__file__), "../", "artifacts.yaml")
    fobj = artifacts.ArtifactManifest(manifest_file)
    assert fobj.load() is not None
    return artifacts.ArtifactFactory(fobj)


def pytest_addoption(parser):
    """
    The flag to keep VM without destroy for advanced debugging
    """
    parser.addoption(
        "--keep-vm", action="store_true", default=False, help="NOT destroy unhealty VMs"
    )
    parser.addoption("--guest", action="store", default="centosstream")
