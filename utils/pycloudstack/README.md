
# PyCloudStack (Unified Cloud Stack Operator Framework)

## 1. Overview

PyCloudStack abstracts the common objects/operations/resources for diverse cloud
architectures like hypervisor stack based on libvirt or direct qemu command,
container stack orchestrated by kubernetes or direct docker command, and the running
or remote IaaS host.

It can be used to create advance deployment CI/CD operator via python plugin for
ansible, end-to-end validation framework with customized the components/configurations
in full vertical stack.

The architecture diagram is as follows:

![](https://github.com/intel/tdx-tools/blob/main/doc/pycloudstack.png)

## 2. Getting Start

### Install from pypi

```
pip3 install pycloudstack
```

### Install from source
```
cd ~/pycloudstack
pip3 install --user --upgrade .
```

## 3. Examples

### Example 1: Operate VM via Libvirt

```
from pycloudstack.vmguest import VMGuestFactory
from pycloudstack.vmparam import VM_STATE_SHUTDOWN, VM_STATE_RUNNING, \
    VM_STATE_PAUSE, VM_TYPE_TD

vm_factory = VMGuestFactory(vm_image, vm_kernel)

LOG.info("Create TD guest")
inst = vm_factory.new_vm(VM_TYPE_TD, auto_start=True)
inst.wait_for_ssh_ready()

LOG.info("Suspend TD guest")
inst.suspend()
ret = inst.wait_for_state(VM_STATE_PAUSE)
assert ret, "Suspend timeout"

LOG.info("Resume TD guest")
inst.resume()
ret = inst.wait_for_state(VM_STATE_RUNNING)
assert ret, "Resume timeout"
```

## Example 2: Operate VM via Qemu (QMP)

```
from gpl.vmmqmp import VMMQemu
from pycloudstack.vmparam import VM_TYPE_TD, VM_TYPE_LEGACY,

vm_factory = VMGuestFactory(vm_image, vm_kernel)
inst = vm_factory.new_vm(vm_instance_type, vm_class=VMMQemu,
                         auto_start=True)
inst.wait_for_ssh_ready()
```

## Example 3: Operate Kubenetes Cluster

```
from pycloudstack.cluster import SGXCluster

DEPLOYMENT_TEMPLATE='''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: %(name)s
spec:
  selector:
    matchLabels:
      app: testapp-redis-gsc-sgx
  template:
    metadata:
      labels:
        app: testapp-redis-gsc-sgx
    spec:
      containers:
      - name: redis-gsc-sgx
        image: gar-registry.caas.intel.com/cpio/gsc-centos8-redis:latest
        ports:
          - containerPort: 6379
        env:
        - name: GSC
          value: %(gsc)s
        resources:
          limits:
            sgx.intel.com/enclave: '1'
            sgx.intel.com/epc: '524288000'
'''
SERVICE_TEMPLATE='''
apiVersion: v1
kind: Service
metadata:
  name: %(name)s
spec:
  ports:
  - port: 6379
    protocol: TCP
  selector:
    app: testapp-redis-gsc-sgx
  type: NodePort
'''

cluster_instance = SGXCluster()
deploy_name = 'deployment-redis-gsc-sgx-' + str(uuid.uuid4())
cluster_instance.create_deployment(
        deploy_name,
        yaml.safe_load(DEPLOYMENT_TEMPLATE % {"name":deploy_name, "gsc":gsc}),
        TEST_NAMESPACE)

svc_name = 'svc-redis-gsc-sgx-' + str(uuid.uuid4())
cluster_instance.create_service(
        svc_name,
        yaml.safe_load(SERVICE_TEMPLATE % {"name":svc_name}),
        TEST_NAMESPACE)
cluster_instance.delete_service(svc_name, TEST_NAMESPACE)
cluster_instance.delete_deployment(deploy_name, TEST_NAMESPACE)

```