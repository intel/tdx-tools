# Deploy QGS service on Docker

QGS (Quote Generation Service) implementation comes from
[DCAP](https://github.com/intel/SGXDataCenterAttestationPrimitives/tree/master/QuoteGeneration/quote_wrapper/qgs).
Currently, the package of QGS only support several distros. Using docker to deploy the QGS service can be an alternative for some unsupported distros, like RHEL9.

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

## 1. Install QGS Service

### 2.1 Build QGS Docker Image

```bash
docker build --build-arg HTTP_PROXY=$http_proxy --build-arg HTTPS_PROXY=$https_proxy -t <your registry> .
```

### 2.2 Start QGS Service

```bash
docker run -d --privileged --name qgs --restart always --net host <your registry>
```
- Check if QGS service works

```console
$ docker ps
CONTAINER ID   IMAGE      COMMAND                 CREATED         STATUS         PORTS      NAMES
90a3777d813e   qgs        "/opt/intel/tdx-qgs/…"  9 minutes ago   Up 9 minutes              qgs
```
