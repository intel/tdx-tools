# TDVF Secure Boot Key Enrolling Tools

## Overview

The tool is used for enrolling keys into TDVF to enable TDVM's secure boot.

## Build & Install

### Install via PIP

Run the following commands in order to build and install this tool.

```
make
make install
```

## Usage

Then, you can make a copy of OVMF.fd to the current directory and enroll the keys using this command:

```
tdvf-key-enroll -fd <absolute-path-to-OVMF_VARS.fd> \
-pk <pk-key-guid> <absolute-path-to-PK.cer> \
-kek <kek-guid> <absolute-path-to-KEK.cer> \
-db <db-key-guid> <absolute-path-to-DB.cer>
```

If the following information is displayed, the key has been successfully enrolled:

```
VariableFV: TimeBasedAuthenticated - Supported
EnrollVariable(add PK) - Success
Write Variable(PK) - Success

Enroll PK variable -- Success

VariableFV: TimeBasedAuthenticated - Supported
EnrollVariable(add KEK) - Success
Write Variable(KEK) - Success

Enroll KEK variable -- Success

VariableFV: TimeBasedAuthenticated - Supported
EnrollVariable(add db) - Success
Write Variable(db) - Success

Enroll db variable -- Success

VariableFV: TimeBasedAuthenticated - Supported
EnrollVariable(add dbx) - Success
Write Variable(dbx) - Success

Enroll dbx variable -- Success

VariableFV: TimeBasedAuthenticated - Supported
EnrollVariable(add SecureBootEnable) - Success
Write Variable(SecureBootEnable) - Success

Enroll SecureBootEnable variable -- Success
```
