#ifndef _GPXE_ABFT_H
#define _GPXE_ABFT_H

/** @file
*
* AoE boot firmware table
*
*/

FILE_LICENCE ( GPL2_OR_LATER );

#include <stdint.h>
#include <gpxe/acpi.h>
#include <gpxe/if_ether.h>

/** AoE boot firmware table signature */
#define ABFT_SIG "aBFT"

/**
* AoE Boot Firmware Table (aBFT)
*/
struct abft_table {
/** ACPI header */
struct acpi_description_header acpi;
/** AoE shelf */
uint16_t shelf;
/** AoE slot */
uint8_t slot;
/** Reserved */
uint8_t reserved_a;
/** MAC address */
uint8_t mac[ETH_ALEN];
} __attribute__ (( packed ));

extern void abft_fill_data ( struct aoe_session *aoe );

#endif /* _GPXE_ABFT_H */
