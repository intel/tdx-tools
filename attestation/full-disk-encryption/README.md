# Intel&reg; TDX Full Disk Encryption

Full disk encryption (FDE) is a security method for protecting sensitive
data by encrypting all data on a disk partition. FDE shall encrypt data
automatically to prevent unauthorized access.
This project is a FDE solution based on [Intel&reg; Trust Domain 
Extensions(Intel TDX)](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-trust-domain-extensions.html).

## Architecture

![](./docs/fde-arch.png)

### The workflow of fde-agent

In the early-boot stage, the `fde-agent` which resides in the `initramfs`, is invoked by `init` to mount an encrypted rootfs. The workflow of `fde-agent` is composed of four steps:

1. Retrieve variables from OVMF via `efivarfs`.
    - Variables are enrolled in the OVMF before tdvm being launched.
    - The variables can be customized. For example, there are three variables: `url`, user token and certification, which will be used to retrieve the key from remote KBS (Key Broker Service).
    - The user token contains a `keyid`.
    - The `src/ovmf_var.rs` shows how to read variables from the OVMF.

2. Retrieve the `quote`.
    - The quote is the evidence that proves the TEE is secured from the TDX.
    - The `src/td_report.rs` and `src/quote.rs` show how to get the quote.

3. Retrieve the `key` that encrypts the rootfs from the KBS.
    - The demo follows the [Remote Attestation Procedures Architecture](https://www.ietf.org/archive/id/draft-ietf-rats-architecture-22.html). The fde-agent sends the `${quote}` and `{keyid}` to the KBS to prove that it is in a TEE, then receives the `key`. The query uri is dependent on the KBS provider, it may look like: `https://${url}/key/${keyid}`.
    - The `${url}` and `${keyid}` are retrieved in the step 1.
    - The `src/key_broker.rs` show an example to connect to the KBS.

4. Decrypt the encrypted rootfs by `${key}` and mount it.
    - the `${key}` is retrieve in the step 3.
    - The `src/disk.rs` shows the detail.

## Fde-agent Build

**Warning: The default fde-agent implementation will panic because it connects to a dummy KBS. Consult your KBS provider to create a concrete fde-agent.**

The fde-agent depends on dynamic libraries `libtdx-attest.so`, which can be built from the source [SGXDataCenterAttestationPrimitives](https://github.com/intel/SGXDataCenterAttestationPrimitives.git) with tag `tdx_1.5_dcap_mvp_23q1`. Make sure the library `libtdx-attest.so` is installed in the running environment.
Install [Rust-lang](https://www.rust-lang.org/), then build the fde-agent:

```
cd attestation/full-disk-encryption
cargo build --release
```

Optionally, strip for small-size application

```
strip --strip-all target/release/fde-agent
```

## Image Build

The image building script is `attestation/full-disk-encryption/tools/image/fde-image.sh`.  The script has 6 steps:
- Create an empty image file
- Partition the image file
- Encrypt the rootfs partition
- Format partitions
- Install rootfs 
- Close devices

Read the script if you are interested in it.


