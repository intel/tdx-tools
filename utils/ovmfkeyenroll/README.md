A tool to enroll secure boot keys in OVMF_VARS.fd

## Build & Install

```
python3 -m pip install --upgrade build
python3 -m build
python3 -m pip install dist/ovmfkeyenroll-*.whl
```

## Usage

You can copy OVMF_VAR.fd to current path.

This is to enroll PK, KEK and DB keys and generate OVMF_VAR.sb.fd:

```
ovmfkeyenroll -fd $PWD/OVMF_VARS.fd \
-pk <pk-key-guid> <absolute-path-to-PK.cer> \
-kek <kek-guid> <absolute-path-to-KEK.cer> \
-db <db-key-guid> <absolute-path-to-DB.cer>
```

The keys have been successfully enrolled:

```
VariableFV: TimeBasedAuthenticated - Supported
Var Store: add PK - Success
Write Variable(PK) - Success

Enroll PK variable -- Success

VariableFV: TimeBasedAuthenticated - Supported
Var Store: add KEK - Success
Write Variable(KEK) - Success

Enroll KEK variable -- Success

VariableFV: TimeBasedAuthenticated - Supported
Var Store: add db - Success
Write Variable(db) - Success

Enroll db variable -- Success

VariableFV: TimeBasedAuthenticated - Supported
Var Store: add SecureBootEnable - Success
Write Variable(SecureBootEnable) - Success

Enroll SecureBootEnable variable -- Success
```
