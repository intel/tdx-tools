# Pckid retrieve tool service

The service is aimed to register the platform to the SGX registration server every boot time. 

## Prerequisite

The service depends on two services, `pccs.service` and `mpa_registration_tool.service`. Install them from official repo [here](https://download.01.org/intel-sgx/sgx-dcap/).

```
apt install sgx-dcap-pccs sgx-ra-service 
```

## Build & install

Build a deb package `pckid-retrieve-tool-service_1.0-1_amd64.deb`, that completes registration with the password `$PASSWD`

```
PASSWD='your_passwd'
./build $PASSWD
```

Install the package.

```
sudo dpkg -i pckid-retrieve-tool-service_1.0-1_amd64.deb
```

Remove the package.

```
sudo dpkg -i pckid-retrieve-tool-service
```

