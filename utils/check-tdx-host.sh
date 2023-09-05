#!/bin/bash
#
# Check the TDX host status
#


COL_RED=$(tput setaf 1)
COL_MAGENTA=$(tput setaf 5)
COL_GREEN=$(tput setaf 2)
COL_YELLOW=$(tput setaf 3)
COL_BLUE=$(tput setaf 6)
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

print_section_header() {
    printf "\n"
    printf "${COL_GUIDE}%s\n${COL_NORMAL}" "$*"
    printf "%s------------------------------------------------------------------------\n%s" "${COL_GUIDE}" "${COL_NORMAL}"
}

SUPPORTED_OS[0]="Ubuntu 22.04.1 LTS"
SUPPORTED_OS[1]="Red Hat Enterprise Linux 8.7 (Ootpa)"

#
# Print the supported OSs.
#
print_supported_os_list() {
    print_guide "The following OSs are supported:"
    for i in "${SUPPORTED_OS[@]}"; do
        print_guide "    ${i}"
    done
}

#
# Check if given OS distro is supported.
#   $1  -  OS distro name under the check
#
is_os_supported() {
    local os_name=$1
    local is_supported="false"
    for i in "${SUPPORTED_OS[@]}"; do
        if [[ "${i}" == "${os_name}" ]]; then
            is_supported="true"
	    break
        fi
    done
    echo "${is_supported}"
}

#
# Report action result fail or not, if fail, then report the detail reason
# Parameters:
#   $1  -   "OK", "FAIL", "WARNING" or "TBD" (to-be-determined)
#   $2  -   action string
#   $3  -   reason string if FAIL, WARNING or TBD
#   $4  -   "required" or "optional"
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
    elif [[ $result == "WARNING" ]]; then
        printf '%.70s %s\n' "${action} ........................................" "${COL_MAGENTA}WARNING${COL_NORMAL}"
        if [[ -n $reason ]]; then
            printf "    ${COL_YELLOW}Reason: %s\n${COL_NORMAL}" "$reason"
        fi
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
    local os_name
    os_name=$(grep PRETTY_NAME /etc/os-release | sed "s/PRETTY_NAME=\"\(.*\)\"/\1/g")
    retval=$(is_os_supported "$os_name")
    [[ "$retval" == "true" ]] && result="OK" || result="FAIL"
    local action="Check OS: The distro and version are correct (required)"
    local reason="Your OS distro is not supported yet."
    report_result "$result" "$action" "$reason" required
    print_guide "Your current OS is ${os_name}."
    print_supported_os_list
    print_guide "There is no guarantee to other OS distro."
    print_guide "Details can be found in the Whitepaper: Linux* Stacks for Intel® Trust Domain Extension"
    print_url $URL_TDX_LINUX_WHITE_PAPER
    printf "\n"
}

#
# Check the TDX module's version
#
check_tdx_module() {
    if [[ -e /sys/firmware/tdx/tdx_module ]]; then
        local action="Check TDX Module: The version is expected (required & manually)"
        report_result TBD "$action" "" required manual
        local tdx_module_info
        # shellcheck disable=SC2012
        tdx_module_info=$(ls /sys/firmware/tdx/tdx_module | while read -r tdxattr; \
            do echo "$tdxattr": ; cat /sys/firmware/tdx/tdx_module/"$tdxattr"; echo; done)
        # shellcheck disable=SC2086
        print_guide "Your TDX Module info." $tdx_module_info
        print_guide "Different releases could require different versions of TDX module."
        print_guide "Please check your TDX Module info to see if that's what you need."
        print_guide "Details can be found in the Whitepaper: Linux* Stacks for Intel® Trust Domain Extension"
        print_url $URL_TDX_LINUX_WHITE_PAPER
    else
        local action="Check TDX Module: The version is expected (required)"
        report_result FAIL "$action" "TDX Module is required" required
    fi
    printf "\n"
}

#
# TDX only support 1LM mode
#
check_bios_memory_map() {
    local action="Check BIOS: Volatile Memory should be 1LM (optional & manually)"
    local reason=""
    report_result TBD "$action" "$reason" optional manual
    print_guide "Please check your BIOS settings:"
    print_guide "    Socket Configuration -> Memory Configuration -> Memory Map"
    print_guide "        Volatile Memory (or Volatile Memory Mode) should be 1LM"
    print_guide "A different BIOS might have a different path for this setting."
    print_guide "Please skip this setting if it doesn't exist in your BIOS menu."
    printf "\n"
}

#
# Check whether the bit 11 for MSR 0x1401, 1 means MK-TME is enabled in BIOS.
#
check_bios_enabling_mktme() {
    local action="Check BIOS: TME = Enabled (required)"
    local reason="The bit 1 of MSR 0x982 should be 1"
    local retval
    retval=$(sudo rdmsr -f 1:1 0x982)
    [[ "$retval" == 1 ]] && result="OK" || result="FAIL"
    report_result "$result" "$action" "$reason" required
    print_guide "Details can be found in the Intel SDM: Vol. 4 Model Specific Registers (MSRs)"
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
    [[ "$retval" == 1 ]] && result="OK" || result="TBD"
    report_result "$result" "$action" "$reason" optional
    if [[ "$retval" != 1 ]]; then
        print_guide "The TME Bypass has not been enabled now."
    fi
    print_guide "It's better to enable TME Bypass for traditional non-confidential workloads."
    print_guide "Details can be found in the Intel SDM: Vol. 4 Model Specific Registers (MSRs)"
    print_url $URL_INTEL_SDM
    printf "\n"
}

#
# Check TME-MT/TME-MK setting in BIOS
#
check_bios_tme_mt() {
    local action="Check BIOS: TME-MT/TME-MK (required & manually)"
    local reason="The bit 1 of MSR 0x982 should be 1"
    local retval
    retval=$(sudo rdmsr -f 1:1 0x982)
    [[ "$retval" == 1 ]] && result="OK" || result="FAIL"
    report_result "$result" "$action" "$reason" required
    print_guide "Please check your BIOS settings:"
    print_guide "    Socket Configuration -> Processor Configuration -> TME, TME-MT, TDX"
    print_guide "        Total Memory Encryption Multi-Tenant (TME-MT) should be Enable"
    print_guide "A different BIOS might have a different path for this setting."
    print_url $URL_INTEL_SDM
    printf "\n"
}

#
# Check whether the bit 11 for MSR 0x1401, 1 means TDX is enabled in BIOS.
#
check_bios_enabling_tdx() {
    local action="Check BIOS: TDX = Enabled (required)"
    local reason="The bit 11 of MSR 1401 should be 1"
    local retval
    retval=$(sudo rdmsr -f 11:11 0x1401)
    [[ "$retval" == 1 ]] && result="OK" || result="FAIL"
    report_result "$result" "$action" "$reason" required
    printf "\n"
}

#
# Check if the SEAM Loader (TDX Arbitration Mode Loader) is enabled.
#
check_bios_seam_loader() {
    local action="Check BIOS: SEAM Loader = Enabled (optional)"
    local reason=""
    report_result TBD "$action" "$reason" optional manual
    print_guide "Details can be found in the Whitepaper: Linux* Stacks for Intel® Trust Domain Extension, Chapter 6.1 Override the Intel TDX SEAM module"
    print_url $URL_TDX_LINUX_WHITE_PAPER
    printf "\n"
}

#
# IA32_TME_CAPABILITY
# MK_TME_MAX_KEYS
#
check_bios_tdx_key_split() {
    local action="Check BIOS: TDX Key Split != 0 (required)"
    local reason="TDX Key Split should be non-zero"
    local retval
    retval=$(sudo rdmsr -f 50:36 0x981)
    [[ "$retval" != 0 ]] && result="OK" || result="FAIL"
    report_result "$result" "$action" "$reason" required
    printf "\n"
}

#
# Check whether SGX is enabled in BIOS
# NOTE: please refer https://software.intel.com/sites/default/files/managed/48/88/329298-002.pdf
#
check_bios_enabling_sgx() {
    local action="Check BIOS: SGX = Enabled (required)"
    local reason="The bit 18 of MSR 0x3a should be 1"
    local retval
    retval=$(sudo rdmsr -f 18:18 0x3a)
    [[ $retval == 1 ]] && result="OK" || result="FAIL"
    report_result "$result" "$action" "$reason" required
    printf "\n"
}


check_bios_sgx_reg_server() {
    local action="Check BIOS: SGX registration server (required & manually)"
    local reason=""
    report_result TBD "$action" "$reason" required manual
    retval=$(sudo rdmsr -f 27:27 0xce)
    [[ $retval == 1 ]] && sgx_reg_srv="SBX" || sgx_reg_srv="LIV"
    print_guide "SGX registration server is $sgx_reg_srv"
    printf "\n"
}

print_title "TDX Host Check"

check_cmd rdmsr "Please install via apt install msr-tools (Ubuntu) or dnf install msr-tools (RHEL/CentOS)"

sudo modprobe msr

print_section_header "Required Features & Settings:"
check_os
check_tdx_module
check_bios_enabling_mktme
check_bios_tme_mt
check_bios_enabling_tdx
check_bios_tdx_key_split
check_bios_enabling_sgx
check_bios_sgx_reg_server

print_section_header "Optional Features & Settings:"
check_bios_memory_map
check_bios_tme_bypass
check_bios_seam_loader

print_section_header "NOTICE:"
print_guide "We highly recommend you to check the output info above seriously and"
print_guide "follow the corresponding guide carefully because that's the fastest way"
print_guide "for your troubleshooting. Attention to the text in red or yellow."
print_guide "That being said, if you can't resolve your problem after checking all"
print_guide "the items above, neither in program nor manually, then you can contact"
print_guide "maintainers of http://github.com/intel/tdx-tool for support with your"
print_guide "output of this script."
print_guide ""
print_guide ""
