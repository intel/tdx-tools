use crate::td_report::TDReport;
use anyhow::{anyhow, Ok, Result};

pub fn retrieve_quote() -> Result<Vec<u8>> {
    // 1. tdreport_data
    let report_data = tdx_attest_rs::tdx_report_data_t { d: [0u8; 64usize] };

    // 2.1 tdreport
    let mut tdx_report = tdx_attest_rs::tdx_report_t { d: [0; 1024usize] };
    let result = tdx_attest_rs::tdx_att_get_report(Some(&report_data), &mut tdx_report);
    if result != tdx_attest_rs::tdx_attest_error_t::TDX_ATTEST_SUCCESS {
        return Err(anyhow!("Failed to get the report."));
    }
    println!("TDX Report Retrieved!");

    // 2.2 uuid
    let _td_info = TDReport::new(tdx_report.d).td_info;

    // 3. qoute
    let mut selected_att_key_id = tdx_attest_rs::tdx_uuid_t { d: [0; 16usize] };
    let (result, quote) = tdx_attest_rs::tdx_att_get_quote(
        Some(&report_data),
        None,
        Some(&mut selected_att_key_id),
        0,
    );
    if result != tdx_attest_rs::tdx_attest_error_t::TDX_ATTEST_SUCCESS {
        return Err(anyhow!("Failed to get the quote."));
    }
    let quote_bytes = quote.expect("Failed to parse the quote");
    println!("TDX Quote Retrieved!");

    Ok(quote_bytes)
}
