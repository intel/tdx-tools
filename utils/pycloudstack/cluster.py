"""
The Cluster class is designed to manage the Kubernetes operations
"""

import logging
import time
from kubernetes.config.config_exception import ConfigException
from kubernetes.client.rest import ApiException
from kubernetes import client, config

__author__ = 'cpio'

LOG = logging.getLogger(__name__)

WAIT_INTERVAL = 2
WAIT_TIMEOUT = 660
CREATED = 'created'
DELETED = 'deleted'


# pylint: disable=too-many-public-methods
class ClusterBase:
    """
    Manage the Kubernetes operations:
    namespace: create/delete
    deployment: create/delete
    service: create/delete
    job: create/delete
    """

    def __init__(self, config_file=None):
        """
        Initalize the operator, check cluster status.
        """
        self._interval = WAIT_INTERVAL
        self._timeout = WAIT_TIMEOUT
        try:
            if config_file is None:
                config.load_kube_config()
            else:
                config.load_kube_config(config_file)
        except ConfigException:
            LOG.error("Fail to load kubernete config, might not in cluster",
                      exc_info=True)
            assert False

    @property
    def core_api(self):
        """
        https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md
        """
        return client.CoreV1Api()

    @property
    def ext_api(self):
        """
        https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md
        """
        return client.AppsV1Api()

    @property
    def batch_api(self):
        """
        https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/BatchV1Api.md
        """
        return client.BatchV1Api()

    @property
    def client(self):
        """
        https://github.com/kubernetes-client/python/
        """
        return client

    @property
    def interval(self):
        """
        interval in wait loop used to check if created/deleted successfully
        """
        return self._interval

    @interval.setter
    def interval(self, new_interval):
        if self._interval == new_interval:
            return
        if isinstance(new_interval, int) and new_interval > 0:
            self._interval = new_interval

    @property
    def timeout(self):
        """
        timeout in wait loop used to check if created/deleted successfully
        """
        return self._timeout

    @timeout.setter
    def timeout(self, new_timeout):
        if self._timeout == new_timeout:
            return
        if isinstance(new_timeout, int) and new_timeout > self.interval:
            self._timeout = new_timeout

    def wait_for_namespace(self, namespace_name,
                           expect=CREATED):
        '''
        Wait for namespace created/deleted
        '''
        interval = 0
        while interval < self.timeout:
            LOG.info("Read namespace %s, expect %s", namespace_name, expect)
            try:
                self.core_api.read_namespace(namespace_name)
                if CREATED == expect:
                    return True
            except ApiException:
                if DELETED == expect:
                    return True
            time.sleep(self.interval)
            interval += self.interval

        LOG.error("Timeout to wait for namespace %s %s", namespace_name, expect)
        return False

    def create_namespace(self, namespace_name):
        """
        Create a namespace and wait until success
        """
        try:
            resp = self.core_api.read_namespace(namespace_name)
            LOG.warning("Namespace %s already exists", namespace_name)
            if resp.status.phase != "Active":
                LOG.error("Namespace %s is not active", namespace_name)
                return False
            return True
        except ApiException:
            LOG.info("Namespace %s not found", namespace_name)

        LOG.info("Create namespace %s", namespace_name)
        body = client.V1Namespace(
            metadata=client.V1ObjectMeta(name=namespace_name)
        )
        self.core_api.create_namespace(body=body)

        return self.wait_for_namespace(
            namespace_name, expect=CREATED)

    def delete_namespace(self, namespace_name):
        """
        Delete a namespace and wait until success.
        """
        LOG.info("Delete namespace %s", namespace_name)
        self.core_api.delete_namespace(name=namespace_name)

        return self.wait_for_namespace(
            namespace_name, expect=DELETED)

    def wait_for_deployement(self, deployment_name, namespace="default",
                             expect=CREATED):
        """
        Wait for deployment created/deleted
        """
        interval = 0
        while interval < self.timeout:
            LOG.info("Read deployment %s, expect %s", deployment_name, expect)
            try:
                resp = self.ext_api.read_namespaced_deployment(
                    deployment_name, namespace)
                if CREATED == expect and \
                        resp.status.available_replicas is not None:
                    return True
            except ApiException:
                if DELETED == expect:
                    return True
            time.sleep(self.interval)
            interval += self.interval

        LOG.error("Timeout to wait for deployment %s %s", deployment_name, expect)
        return False

    def create_deployment(self, deployment_name, body, namespace="default"):
        """
        Create a deployment until success
        """
        LOG.info("Create deployment %s", deployment_name)
        self.ext_api.create_namespaced_deployment(
            body=body,
            namespace=namespace)

        return self.wait_for_deployement(
            deployment_name, namespace, expect=CREATED)

    def delete_deployment(self, deployment_name, namespace="default"):
        """
        Delete deployment until success
        """
        LOG.info("Delete deployment %s", deployment_name)
        self.ext_api.delete_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            grace_period_seconds=5)

        return self.wait_for_deployement(
            deployment_name, namespace, expect=DELETED)

    def get_service_port(self, service_name, namespace="default"):
        """
        Get service's cluster IP and port
        """
        LOG.info("Read service %s", service_name)
        resp = self.core_api.read_namespaced_service(
            service_name, namespace)
        return (resp.spec.cluster_ip, resp.spec.ports[0].port)

    def wait_for_service(self, service_name, namespace="default",
                         expect=CREATED):
        """
        Wait for service created/deleted
        """
        interval = 0
        while interval < self.timeout:
            LOG.info("Read service %s, expect %s", service_name, expect)
            try:
                self.core_api.read_namespaced_service(
                    service_name, namespace)
                if CREATED == expect:
                    return True
            except ApiException:
                if DELETED == expect:
                    return True
            time.sleep(self.interval)
            interval += self.interval

        LOG.error("Timeout to wait for service %s %s", service_name, expect)
        return False

    def create_service(self, service_name, body, namespace="default"):
        """
        Create a service until ready
        """
        LOG.info("Create service %s", service_name)
        self.core_api.create_namespaced_service(
            body=body,
            namespace=namespace)

        return self.wait_for_service(
            service_name, namespace, expect=CREATED)

    def delete_service(self, service_name, namespace="default"):
        """
        Delete a service until success
        """
        LOG.info("Delete service %s", service_name)
        self.core_api.delete_namespaced_service(
            name=service_name,
            namespace=namespace,
            grace_period_seconds=5)

        return self.wait_for_service(
            service_name, namespace, expect=DELETED)

    def wait_for_job(self, job_name, namespace="default",
                     expect=CREATED):
        """
        Read job until it ready
        """
        interval = 0
        while interval < self.timeout:
            LOG.info("Read job %s, expect %s", job_name, expect)
            try:
                resp = self.batch_api.read_namespaced_job(
                    job_name, namespace)
                if CREATED == expect:
                    if resp.status.failed is not None:
                        return False
                    if resp.status.succeeded is not None and \
                            resp.status.succeeded >= 1:
                        return True
            except ApiException:
                if DELETED == expect:
                    return True
            time.sleep(self.interval)
            interval += self.interval

        LOG.error("Timeout to wait for job %s %s", job_name, expect)
        return False

    def create_job(self, job_name, body, namespace="default"):
        """
        Create a job until success
        """
        LOG.info("Create job %s", job_name)
        self.batch_api.create_namespaced_job(
            body=body,
            namespace=namespace)

        return self.wait_for_job(
            job_name, namespace, expect=CREATED)

    def delete_job(self, job_name, namespace="default"):
        """
        Delete job until success
        """
        LOG.info("Delete job %s", job_name)
        self.batch_api.delete_namespaced_job(
            name=job_name,
            namespace=namespace,
            grace_period_seconds=5)

        return self.wait_for_job(
            job_name, namespace, expect=DELETED)

    def get_pods_by_selector(self, selector, namespace="default"):
        """
        Get the pods by label selector
        """
        LOG.info("Select pod by %s", selector)
        pods = self.core_api.list_namespaced_pod(
            namespace=namespace,
            label_selector=selector,
            limit=1,
        )
        return pods

    def get_pod_log(self, pod_name, namespace="default"):
        """
        Get pod log
        """
        LOG.info("Get pod %s log", pod_name)
        log = self.core_api.read_namespaced_pod_log(
            pod_name, namespace)
        return log

    # This method return specific status of a given node
    def get_node_ready_status(self, node_name):
        """
        Get the value of section "Ready" in the whole body of
        read_node_status, e.g. ["True"]. It means the node is ready for use.
        """
        LOG.info("Get node %s status", node_name)

        body = self.core_api.read_node_status(node_name)
        status = [s.status for s in body.status.conditions if s.type == 'Ready']
        return status


class SGXCluster(ClusterBase):
    """
    SGX cluster is designed to get SGX EPC size
    """

    def __init__(self, config_file=None):
        """
        Initialize the variables
        """
        super().__init__(config_file)
        self._sgx_epid_nodes = {}
        self._sgx_dcap_nodes = {}
        self._scan_sgx_nodes()

    def _scan_sgx_nodes(self):
        """
        Scan all SGX node within cluster
        """
        for item in self.core_api.list_node().items:
            node = self.core_api.read_node(name=item.metadata.name)
            if 'feature.node.kubernetes.io/cpu-cpuid.SGXLC' in node.metadata.labels.keys():
                if 'sgx.intel.com/enclave' in node.status.capacity.keys():
                    self._sgx_dcap_nodes[node.metadata.labels['kubernetes.io/hostname']] = node
                else:
                    self._sgx_epid_nodes[node.metadata.labels['kubernetes.io/hostname']] = node
        LOG.info("Found %d EPID devices: %s",
                 len(self._sgx_epid_nodes.keys()), str(self._sgx_epid_nodes.keys()))
        LOG.info("Found %d DCAP devices: %s",
                 len(self._sgx_dcap_nodes.keys()), str(self._sgx_dcap_nodes.keys()))

    def get_total_epc_size(self):
        """
        Calculate the total EPC size for all DCAP nodes.
        """
        total = 0
        for node in self._sgx_dcap_nodes.values():
            total += int(node.status.capacity['sgx.intel.com/epc'])
        LOG.info("Total EPC size: %d", total)
        return total

    def get_total_enclave_number(self):
        """
        Calculate the total enclave number for all DCAP devices.
        """
        total = 0
        for node in self._sgx_dcap_nodes.values():
            total += int(node.status.capacity['sgx.intel.com/enclave'])
        LOG.info("Total enclave number: %d", total)
        return total

    def get_epc_size(self, node_name):
        """
        Get EPC size for specific node
        """
        if node_name not in self._sgx_dcap_nodes:
            LOG.error(
                "Fail to find the DCAP node %s in cluster", node_name)
            return None
        node = self._sgx_dcap_nodes.keys[node_name]  # pylint: disable=E1136
        return int(node.status.capacity['sgx.intel.com/epc'])

    def get_enclave_size(self, node_name):
        """
        Get enclave number for specific node
        """
        if node_name not in self._sgx_dcap_nodes:
            LOG.error(
                "Fail to find the DCAP node %s in cluster", node_name)
            return None
        node = self._sgx_dcap_nodes.keys[node_name]  # pylint: disable=E1136
        return int(node.status.capacity['sgx.intel.com/enclave'])

    def get_total_allocated_sgx(self):
        """
        Get total allocated SGX EPC and enclave
        """
        total_epc = 0
        total_enclave = 0
        res_pods = self.core_api.list_pod_for_all_namespaces()
        for i in res_pods.items:
            for j in i.spec.containers:
                if j.resources.requests or j.resources.limits:
                    if 'sgx.intel.com/epc' in j.resources.requests.keys():
                        epc_requests = j.resources.requests['sgx.intel.com/epc']
                        # epc_limits = j.resources.limits['sgx.intel.com/epc']
                        if epc_requests.endswith('k'):
                            total_epc += int(epc_requests[:-1]) * 1024
                        else:
                            total_epc += int(epc_requests)
                    if 'sgx.intel.com/enclave' in j.resources.requests.keys():
                        enclave_requests = j.resources.requests['sgx.intel.com/enclave']
                        # enclave_limits = j.resources.limits['sgx.intel.com/enclave']
                        if enclave_requests.endswith('k'):
                            total_enclave += int(enclave_requests[:-1]) * 1024
                        else:
                            total_enclave += int(enclave_requests)
        return (total_enclave, total_epc)
