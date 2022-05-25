#ifndef _GPXE_FEATURES_H
#define _GPXE_FEATURES_H

#include <stdint.h>
#include <gpxe/tables.h>
#include <gpxe/dhcp.h>

/** @file
 *
 * Feature list
 *
 */

FILE_LICENCE ( GPL2_OR_LATER );

/**
 * @defgroup featurecat Feature categories
 * @{
 */

#define FEATURE_PROTOCOL		01 /**< Network protocols */
#define FEATURE_IMAGE			02 /**< Image formats */
#define FEATURE_MISC			03 /**< Miscellaneous */

/** @} */

/**
 * @defgroup dhcpfeatures DHCP feature option tags
 *
 * DHCP feature option tags are Etherboot encapsulated options in the
 * range 0x10-0x7f.
 *
 * @{
 */

#define DHCP_EB_FEATURE_PXE_EXT		0x10 /**< PXE API extensions */
#define DHCP_EB_FEATURE_ISCSI		0x11 /**< iSCSI protocol */
#define DHCP_EB_FEATURE_AOE		0x12 /**< AoE protocol */
#define DHCP_EB_FEATURE_HTTP		0x13 /**< HTTP protocol */
#define DHCP_EB_FEATURE_HTTPS		0x14 /**< HTTPS protocol */
#define DHCP_EB_FEATURE_TFTP		0x15 /**< TFTP protocol */
#define DHCP_EB_FEATURE_FTP		0x16 /**< FTP protocol */
#define DHCP_EB_FEATURE_DNS		0x17 /**< DNS protocol */
#define DHCP_EB_FEATURE_BZIMAGE		0x18 /**< bzImage format */
#define DHCP_EB_FEATURE_MULTIBOOT	0x19 /**< Multiboot format */
#define DHCP_EB_FEATURE_SLAM		0x1a /**< SLAM protocol */
#define DHCP_EB_FEATURE_SRP		0x1b /**< SRP protocol */
#define DHCP_EB_FEATURE_NBI		0x20 /**< NBI format */
#define DHCP_EB_FEATURE_PXE		0x21 /**< PXE format */
#define DHCP_EB_FEATURE_ELF		0x22 /**< ELF format */
#define DHCP_EB_FEATURE_COMBOOT		0x23 /**< COMBOOT format */
#define DHCP_EB_FEATURE_EFI		0x24 /**< EFI format */

/** @} */


/** Construct a DHCP feature table entry */
#define DHCP_FEATURE( feature_opt, ... )
/** Construct a named feature */
#define FEATURE_NAME( category, text ) 

/** Declare a feature */
#define FEATURE( category, text, feature_opt, version )

/** Declare the version number feature */
#define FEATURE_VERSION( ... )

#endif /* _GPXE_FEATURES_H */
