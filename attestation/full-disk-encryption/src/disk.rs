use cryptsetup_rs::{open, CryptDevice, LuksCryptDevice};
use log::info;

pub const KEY_LENGTH: usize = 256;

pub fn crypt_setup(root: String, name: String, key: &[u8]) {
    let mut _dev = open(root.clone())
        .expect("FDE: root deivce is not available")
        .luks2()
        .expect("FDE: Loading LUKS2 failed.");
    info!("FDE Device UUID: {}", _dev.uuid());
    info!("FDE Device cipher: {}", _dev.cipher());

    let mut _name = name.as_str();
    if _name.is_empty() {
        _name = root
            .split('/')
            .last()
            .expect("FDE: Set device name failed.");
    }
    let _ = _dev.activate(_name, key);
}
