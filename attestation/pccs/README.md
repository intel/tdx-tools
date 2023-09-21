# Deploy PCCS service on Docker

PCCS (Provisioning Certificate Caching Service) service implementation comes from
[DCAP](https://github.com/intel/SGXDataCenterAttestationPrimitives/blob/master/QuoteGeneration/pccs/README.md).
Currently, the package of PCCS only support several distros. Using docker to deploy the PCCS service can be an alternative for some unsupported distros, like RHEL9.

## 0. Install Docker

- **RHEL 9**

Before installing docker, please uninstall the podman firstly.

```bash
sudo dnf remove podman
```
And then follow the official documentation to install the docker. 

https://docs.docker.com/engine/install/centos/

- **Ubuntu22.04**

https://docs.docker.com/engine/install/ubuntu/

- Post-Installation

Add current user into docker group to get rid of the permission issue.

```bash
sudo groupadd docker
sudo usermod -a -G docker $USER
```
Log out and log back in so that your group membership is re-evaluated.

## 1. Setup PCCS necessary configurations

Obtain a provisioning API key. Goto https://sbx.api.portal.trustedservices.intel.com/provisioningcertification and click on 'Subscribe'. The API key will be used later in PCCS configuration

In the `container` directory, a default.json template file has been provided. The detailed value will be injected after executing the script.

```bash
cd container
./configure.sh
```

## 2. Install PCCS Service

### 2.1 Build PCCS Docker Image

```bash
docker build --build-arg HTTP_PROXY=$http_proxy --build-arg HTTPS_PROXY=$https_proxy -t <your registry> .
```

### 2.2 Start PCCS Service

Note: Configure the restart policy to always,which makes PCCS service to keep running after server reboot.

```bash
docker run -d --privileged -v /sys/firmware/efi/:/sys/firmware/efi/ --name pccs --restart always --net host <your registry>
```

- Check if PCCS service works

```console
$ docker ps
CONTAINER ID   IMAGE      COMMAND                 CREATED         STATUS         PORTS      NAMES
90a3777d813e   pccs       "node pccs_server.js"   9 minutes ago   Up 9 minutes   8081/tcp   pccs
```

### 2.3 Register SGX Platform

PCKIDRetrieval tool has already integrated into the PCCS docker image. Therefore, after pccs is activated, registration can be triggered directly.

```bash
docker exec -it pccs /opt/intel/sgx-pck-id-retrieval-tool/PCKIDRetrievalTool
```

### 2.4 Check PCCS Service Log

Debug the pccs service, when registration failed.

```bash
docker logs pccs
```

**NOTE: If you see message about "Platform Manifest not available" or the PCCS service complains that "Error: No cache data for this platform" in the log, you may need to perform SGX Factory Reset in BIOS and run PCKIDRetrievalTool again.**

## 3. Optional advanced operations

If the pccs docker need to be removed (Normally, we do not recommend remove the pccs docker.), please copy out the **pckcache.db** firstly.

```bash
docker cp pccs:/opt/intel/sgx-dcap-pccs/pckcache.db .
```

The **pckcache.db** can be reused when restarts pccs service in the next time.

```bash
docker run -d --privileged -v /sys/firmware/efi/:/sys/firmware/efi/ -v /path/to/pckcache.db:/opt/intel/sgx-dcap-pccs/pckcache.db --name pccs --restart always --net host <your registry>
```