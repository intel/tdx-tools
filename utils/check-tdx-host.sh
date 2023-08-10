#!/bin/bash
#
# Check the TDX host status
#


COL_RED=$(tput setaf 1)
COL_GREEN=$(tput setaf 2)
COL_YELLOW=$(tput setaf 3)
COL_BLUE=$(tput setaf 4)
COL_WHITE=$(tput setaf 7)
COL_NORMAL=$(tput sgr0)
COL_URL=$COL_BLUE
COL_GUIDE=$COL_WHITE

#
# Reference URLs
#
URL_TDX_LINUX_WHITE_PAPER=https://www.intel.com/content/www/us/en/content-details/779108/whitepaper-linux-stacks-for-intel-trust-domain-extension-1-0.html
URL_INTEL_SDM=https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html

#
# Print helpers
#
print_url() {
    printf "    ${COL_URL}Link: %s\n${COL_NORMAL}" "$*"
}

print_guide() {
    printf "    ${COL_GUIDE}%s\n${COL_NORMAL}" "$*"
}

print_title() {
    printf "\n"
    printf "    ${COL_GUIDE}*** %s ***\n${COL_NORMAL}" "$*"
    printf "\n"
}

#
# Report action result fail or not, if fail, then report the detail reason
# Parameters:
#   $1  -   "OK", "FAIL" or "TBD" (to-be-determined)
#   $2  -   action string
#   $3  -   reason string if FAIL or TBD
#   $4  -   "mandatory" or "optional"
#   $5  -   "program" or "manual", default "program"
#
report_result() {
    local result=$1
    local action=$2
    local reason=$3
    local optional=$4
    local operation=$5
    if [[ $result == "OK" ]]; then
        printf '%.70s %s\n' "${action} ........................................" "${COL_GREEN}OK${COL_NORMAL}"
    else
	local text_color=$COL_RED
	if [[ $optional == "optional" ]]; then
	    text_color=$COL_YELLOW
        fi
	if [[ $operation == "manual" ]]; then
	    text_color=$COL_YELLOW
	    reason="Unable to check in program. Please check manually."
	fi
        printf '%.70s %s\n' "${action} ........................................" "${text_color}${result}${COL_NORMAL}"
        if [[ -n $reason ]]; then
            printf "    ${text_color}Reason: %s\n${COL_NORMAL}" "$reason"
        fi
    fi
}

#
# Check the command exists or not
# Parameters:
#   $1  -   the command or program
#
check_cmd() {
    if ! [ -x "$(command -v "$1")" ]; then
        echo "Error: \"$1\" is not installed." >&2
        echo "$2"
        exit 1
    fi
}

#
# Check the OS information
#
check_os() {
    local action="Check OS: The distro and version are correct (mandatory & manually)"
    local reason=""
    report_result TBD "$action" "$reason" mandatory manual
    local os_info
    os_info=$(head -2 /etc/os-release)
    print_guide "Your OS info." "$os_info"
    print_guide "Details can be found in Whitepaper: Linux* Stacks for Intel® Trust Domain Extension"
    print_url $URL_TDX_LINUX_WHITE_PAPER
    printf "\n"
}

#
# Check the TDX module's version
#
check_tdx_module() {
    local action="Check TDX Module: The version is expected (mandatory & manually)"
    local reason=""
    report_result TBD "$action" "$reason" mandatory manual
    local tdx_module_info
    # shellcheck disable=SC2012
    tdx_module_info=$(ls /sys/firmware/tdx/tdx_module | while read -r tdxattr; \
            do echo "$tdxattr": ; cat /sys/firmware/tdx/tdx_module/"$tdxattr"; echo; done)
    # shellcheck disable=SC2086
    print_guide "Your TDX Module info." $tdx_module_info
    print_guide "Details can be found in Whitepaper: Linux* Stacks for Intel® Trust Domain Extension"
    print_url $URL_TDX_LINUX_WHITE_PAPER
    printf "\n"
}

#
# TDX only support 1LM mode
#
check_bios_memory_map() {
    local action="Check BIOS: Volatile Memory should be 1LM (mandatory & manually)"
    local reason=""
    report_result TBD "$action" "$reason" mandatory manual
    print_guide "Please check your BIOS settings:"
    print_guide "    Socket Configuration -> Memory Configuration -> Memory Map"
    print_guide "        Volatile Memory (or Volatile Memory Mode) should be 1LM"
    print_guide "(Different BIOS may need different setting path)"
    printf "\n"
}

#
# Check whether the bit 11 for MSR 0x1401, 1 means MK-TME is enabled in BIOS.
#
check_bios_enabling_mktme() {
    local action="Check BIOS: TME = Enabled (mandatory)"
    local reason="The bit 1 of MSR 0x982 should be 1"
    local retval
    retval=$(sudo rdmsr -f 1:1 0x982)
    [[ "$retval" == 1 ]] && result="OK" || result="FAIL"
    report_result "$result" "$action" "$reason" mandatory
    print_guide "Details can be found in Intel SDM: Vol. 4 Model Specific Registers (MSRs)"
    print_url $URL_INTEL_SDM
    printf "\n"
}

#
# SDM:
#   Vol. 4 Model Specific Registers (MSRs)
#     Table 2-2. IA-32 Architectural MSRs (Contd.)
#       Register Address: 982H
#       Architectural MSR Name: IA32_TME_ACTIVATE
#       Bit Fields: 31
#       Bit Description: TME Encryption Bypass Enable
#
check_bios_tme_bypass() {
    local action="Check BIOS: TME Bypass = Enabled (optional)"
    local reason="The bit 31 of MSR 0x982 should be 1"
    local retval
    retval=$(sudo rdmsr -f 31:31 0x982)
    [[ "$retval" == 1 ]] && result="OK" || result="FAIL"
    report_result "$result" "$action" "$reason" optional
    print_guide "Details can be found in Intel SDM: Vol. 4 Model Specific Registers (MSRs)"
    print_url $URL_INTEL_SDM
    printf "\n"
}

#
# Check TME-MT setting in BIOS
#
check_bios_tme_mt() {
    local action="Check BIOS: TME-MT (mandatory & manually)"
    local reason=""
    report_result TBD "$action" "$reason" mandatory manual
    print_guide "Please check your BIOS settings:"
    print_guide "    Socket Configuration -> Processor Configuration -> TME, TME-MT, TDX"
    print_guide "        Total Memory Encryption Multi-Tenant (TME-MT) should be Enable"
    print_guide "(Different BIOS may need different setting path)"
    printf "\n"
}

#
# Check whether the bit 11 for MSR 0x1401, 1 means TDX is enabled in BIOS.
#
check_bios_enabling_tdx() {
    local action="Check BIOS: TDX = Enabled (mandatory)"
    local reason="The bit 11 of MSR 1401 should be 1"
    local retval
    retval=$(sudo rdmsr -f 11:11 0x1401)
    [[ "$retval" == 1 ]] && result="OK" || result="FAIL"
    report_result "$result" "$action" "$reason" mandatory
    printf "\n"
}

#
# Check if the SEAM Loader (TDX Arbitration Mode Loader) is enabled.
#
check_bios_seam_loader() {
    local action="Check BIOS: SEAM Loader = Enabled (optional)"
    local reason=""
    report_result TBD "$action" "$reason" optional manual
    print_guide "Details can be found in Whitepaper: Linux* Stacks for Intel® Trust Domain Extension, Chapter 6.1 Override the Intel TDX SEAM module"
    print_url $URL_TDX_LINUX_WHITE_PAPER
    printf "\n"
}

#
# IA32_TME_CAPABILITY
# MK_TME_MAX_KEYS
#
check_bios_tdx_key_split() {
    local action="Check BIOS: TDX Key Split != 0 (mandatory)"
    local reason="TDX Key Split should be non-zero"
    local retval
    retval=$(sudo rdmsr -f 50:36 0x981)
    [[ "$retval" != 0 ]] && result="OK" || result="FAIL"
    report_result "$result" "$action" "$reason" mandatory
    printf "\n"
}

#
# Check whether SGX is enabled in BIOS
# NOTE: please refer https://software.intel.com/sites/default/files/managed/48/88/329298-002.pdf
#
check_bios_enabling_sgx() {
    local action="Check BIOS: SGX = Enabled (mandatory)"
    local reason="The bit 18 of MSR 0x3a should be 1"
    local retval
    retval=$(sudo rdmsr -f 18:18 0x3a)
    [[ $retval == 1 ]] && result="OK" || result="FAIL"
    report_result "$result" "$action" "$reason" mandatory
    printf "\n"
}


check_bios_sgx_reg_server() {
    local action="Check BIOS: SGX registration server (mandatory & manually)"
    local reason=""
    report_result TBD "$action" "$reason" mandatory manual
    retval=$(sudo rdmsr -f 27:27 0xce)
    [[ $retval == 1 ]] && sgx_reg_srv="SBX" || sgx_reg_srv="LIV"
    print_guide "SGX registration server is $sgx_reg_srv"
    printf "\n"
}

print_title "TDX Host Check"

check_cmd rdmsr "Please install via apt install msr-tools (Ubuntu) or dnf install msr-tools (RHEL/CentOS)"

sudo modprobe msr

check_os
check_tdx_module
check_bios_memory_map
check_bios_enabling_mktme
check_bios_tme_bypass
check_bios_tme_mt
check_bios_enabling_tdx
check_bios_seam_loader
check_bios_tdx_key_split
check_bios_enabling_sgx
check_bios_sgx_reg_server

print_guide ""
print_guide ""
print_guide "We highly recommend you to check the output info above seriously and"
print_guide "follow the corresponding guide carefully because that's the fastest way"
print_guide "for your troubleshooting. Attention to the text in red or yellow."
print_guide "That being said, if you can't resolve your problem after checking all"
print_guide "the items above, neither in program nor manually, then you can contact"
print_guide "maintainers of http://github.com/intel/tdx-tool for support with your"
print_guide "output of this script."
print_guide ""
print_guide ""
