
/*
 * cidr.c - functions to process addresses in CIDR notation
 *
 * Copyright (c) Gerard Paul Java 2003
 *
 * This module contains functions that deal with CIDR address/mask notation.
 *
 * This module may be freely used for any purpose, commercial or otherwise,
 * In any product that uses this module, the following notice must appear:
 *
 *     Includes software developed by Gerard Paul Java
 *     Copyright (c) Gerard Paul Java 2003
 */

#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>

/*
 * Returns a binary subnet mask based on the number of mask bits.  The
 * dotted-decimal notation may be obtained with inet_ntoa.
 */
unsigned long cidr_get_mask(unsigned int maskbits)
{
    struct in_addr mask;

    if (maskbits == 0)
        return 0;

    inet_aton("255.255.255.255", &mask);
    mask.s_addr = htonl(mask.s_addr << (32 - maskbits));

    return mask.s_addr;
}

/*
 * Returns a subnet mask in dotted-decimal notation given the number of
 * 1-bits in the mask.
 */
char *cidr_get_quad_mask(unsigned int maskbits)
{
    struct in_addr addr;

    addr.s_addr = cidr_get_mask(maskbits);
    return inet_ntoa(addr);
}

/*
 * Returns the number of 1-bits in the given binary subnet mask in
 * network byte order.
 */
unsigned int cidr_get_maskbits(unsigned long mask)
{
    unsigned int i = 32;

    if (mask == 0)
        return 0;

    mask = ntohl(mask);
    while (mask % 2 == 0) {
        mask >>= 1;
        i--;
    }

    return i;
}

/*
 * Splits a CIDR-style address/mask string into its constituent address and
 * mask parts.  In case of absent or invalid input in the mask part, 255 is
 * returned in *maskbits (255 is invalid for an IPv4 address).
 */
void cidr_split_address(char *cidr_addr, char *addresspart,
                        unsigned int *maskbits)
{
    char maskpart[4];
    char *endptr;
    char *slashptr;

    char address_buffer[80];

    if (strchr(cidr_addr, '/') == NULL) {
        strncpy(addresspart, cidr_addr, 80);
        *maskbits = 255;
        return;
    }

    memset(address_buffer, 0, 80);
    memset(addresspart, 0, 80);
    memset(maskpart, 0, 4);

    strncpy(address_buffer, cidr_addr, 80);
    slashptr = strchr(address_buffer, '/');

    /*
     * Cut out the mask part and move past the slash
     */
    *slashptr = '\0';
    slashptr++;

    /*
     * Copy out the address and mask parts into their buffers.
     */
    strncpy(addresspart, address_buffer, 80);
    strncpy(maskpart, slashptr, 4);

    if (maskpart[0] != '\0') {
        *maskbits = strtoul(maskpart, &endptr, 10);
        if (*endptr != '\0')
            *maskbits = 255;
    } else
        *maskbits = 255;

    return;
}
