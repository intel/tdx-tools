const REPORT_MAX_STRUCT_SIZE: usize = 0x100;
const TEE_TCB_INFO_SIZE: usize = 0xef;
const RESERVED_SIZE: usize = 0x11;
const TD_INFO_SIZE: usize = 0x200;

pub struct TDReport {
    pub td_info: TDInfo,
}

impl TDReport {
    pub fn new(bytes: [u8; 1024]) -> Self {
        let offset = REPORT_MAX_STRUCT_SIZE + TEE_TCB_INFO_SIZE + RESERVED_SIZE;
        Self {
            td_info: TDInfo::new(bytes[offset..offset + TD_INFO_SIZE].to_vec()),
        }
    }
}

pub struct TDInfo {
    //member
    pub attributes: Vec<u8>,    //  0x08
    pub xfam: Vec<u8>,          //  0x08
    pub mrtd: Vec<u8>,          //  0x30
    pub mrconfigid: Vec<u8>,    //  0x30
    pub mrowner: Vec<u8>,       //  0x30
    pub mrownerconfig: Vec<u8>, //  0x30
    pub rtmr_0: Vec<u8>,        //  0x30
    pub rtmr_1: Vec<u8>,        //  0x30
    pub rtmr_2: Vec<u8>,        //  0x30
    pub rtmr_3: Vec<u8>,        //  0x30
}

impl TDInfo {
    pub fn new(bytes: Vec<u8>) -> Self {
        let mut offset: usize = 0;
        let attributes = bytes[offset..offset + 0x08].to_vec();

        offset += 0x08;
        let xfam = bytes[offset..offset + 0x08].to_vec();

        offset += 0x08;
        let mrtd = bytes[offset..offset + 0x30].to_vec();

        offset += 0x30;
        let mrconfigid = bytes[offset..offset + 0x30].to_vec();

        offset += 0x30;
        let mrowner = bytes[offset..offset + 0x30].to_vec();

        offset += 0x30;
        let mrownerconfig = bytes[offset..offset + 0x30].to_vec();

        offset += 0x30;
        let rtmr_0 = bytes[offset..offset + 0x30].to_vec();

        offset += 0x30;
        let rtmr_1 = bytes[offset..offset + 0x30].to_vec();

        offset += 0x30;
        let rtmr_2 = bytes[offset..offset + 0x30].to_vec();

        offset += 0x30;
        let rtmr_3 = bytes[offset..offset + 0x30].to_vec();

        Self {
            attributes,
            xfam,
            mrtd,
            mrconfigid,
            mrowner,
            mrownerconfig,
            rtmr_0,
            rtmr_1,
            rtmr_2,
            rtmr_3,
        }
    }

    #[allow(dead_code)]
    pub fn get_mrownerconfig(&self) -> Vec<u8> {
        self.mrownerconfig.to_vec()
    }
}
