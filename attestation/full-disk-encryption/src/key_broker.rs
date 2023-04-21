use anyhow::{bail, Ok, Result};
use reqwest::header::{HeaderMap, ACCEPT};
use rustls::{
    cipher_suite::TLS13_AES_256_GCM_SHA384, version::TLS13, ClientConfig, OwnedTrustAnchor,
    RootCertStore,
};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct RetrieveKeyRequest {
    pub quote: Vec<u8>, // quote
}

#[derive(Serialize, Deserialize, Debug)]
pub struct RetrieveKeyResponse {
    pub wrapped_key: String,
    pub wrapped_swk: String,
}

/// The function retreive_key_from_kbs works to retrieve the key
/// encrypting the disk. This a dummy implementation and users
/// should implement a concrete one according their KBS API.
///
/// Example, to query the KBS:
///
/// ```no_run
/// let url = format!("https://{}/key/{}", _domain_name, _id);
/// let tls_config = default_cipher_suite_with_version()?;
/// let builder = reqwest::ClientBuilder::new().use_preconfigured_tls(tls_config);
/// let client = builder.build()?;
/// let headers = default_request_headers()?;
/// let resp: RetrieveKeyResponse = client
///     .post(url)
///     .headers(headers)
///     .json(_req)
///     .send()
///     .await?
///     .json()
///     .await?;
/// Ok(resp)
/// ```
pub async fn retreive_key_from_kbs(
    _domain_name: &str,
    _keyid: String,
    _req: &RetrieveKeyRequest,
) -> Result<RetrieveKeyResponse> {
    bail!(
        "Panic: this is a dummy client of the KBS!\n \
    Please consult your KBS provider and implement it!"
    );
}

#[allow(unused)]
fn default_cipher_suite_with_version() -> Result<ClientConfig> {
    let suites = vec![TLS13_AES_256_GCM_SHA384];
    let versions = vec![&TLS13];
    let mut root_store = RootCertStore::empty();
    root_store.add_server_trust_anchors(webpki_roots::TLS_SERVER_ROOTS.0.iter().map(|ta| {
        OwnedTrustAnchor::from_subject_spki_name_constraints(
            ta.subject,
            ta.spki,
            ta.name_constraints,
        )
    }));
    let tls_config = ClientConfig::builder()
        .with_cipher_suites(&suites)
        .with_safe_default_kx_groups()
        .with_protocol_versions(&versions)
        .expect("inconsistent cipher-suite/versions selected")
        .with_root_certificates(root_store)
        .with_no_client_auth();
    Ok(tls_config)
}

#[allow(unused)]
fn default_request_headers() -> Result<HeaderMap> {
    let mut headers = HeaderMap::new();
    headers.insert(ACCEPT, "application/json".parse()?);
    Ok(headers)
}
