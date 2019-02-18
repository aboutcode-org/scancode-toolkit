/*
This work is licensed under the Creative Commons Attribution 3.0 Unported License.
To view a copy of this license, visit http://creativecommons.org/licenses/by/3.0/
or send a letter to
        Creative Commons,
        171 Second Street,
        Suite 300,
        San Francisco,
        California,\
 * 
        94105,
        USA.

JTR
This file operates as the global header for <function> implementation
It is applicable to both PIC18 and PIC24.

This is the main BOSS configuration file. It is to be included 
in:

usb_stack.c
cdc.c or other CLASS file.
configwords.h
main.c
descriptors.h

In this file you can define:

ENDPOINT SIZES Applies to EP0 and other class specific endpoints
PING-PONG MODE
BUS or SELF POWERED
VID & PID
USB TRANSCEIVER MODE
USB_NUM_CONFIGURATIONS  
USB_NUM_INTERFACES      
USB_NUM_ENDPOINTS
USB_NUM_STRINGS

USB configured LED
Other misc LEDs and hardware. 

Low power request macro
*/

#ifndef __BOOT_CONFIG_H__
#define __BOOT_CONFIG_H__

#define MODELED LATBbits.LATB8
#define USBLED  LATBbits.LATB10 //Active LOW

#define  USBLEDON()   USBLED = 0

#define USB_VID (0x4d8)
#define USB_PID (0x000A)
#define USB_DEV 0x0002

#define USB_NUM_CONFIGURATIONS          1u
#define USB_NUM_INTERFACES              2u
#define USB_NUM_ENDPOINTS               3u
#define USB_NUM_STRINGS                 4u

#define MAX_EPNUM_USED                  2u

#define USB_BUS_POWERED 1
#define USB_INTERNAL_TRANSCIEVER 1
#define USB_INTERNAL_PULLUPS 1
#define USB_INTERNAL_VREG 1
#define USB_FULL_SPEED_DEVICE 1

//#define USB_INTERRUPT 1

/* PingPong Buffer Mode
 * Valid values
 * 0 - No PingPong Buffers
 * 1 - PingPong on EP0
 * 2 - PingPong on all EP
 * 3 - PingPong on all except EP0
 */
#define USB_PP_BUF_MODE 0
#define USB_EP0_BUFFER_SIZE 8u
#define CDC_BUFFER_SIZE 64u
#define CDC_NOTICE_BUFFER_SIZE 10u

/* Low Power Request
 * Optional user supplied subroutine to set the circuit
 * into low power mode during usb suspend.
 * Probably needed when bus powered as only 2.5mA should
 * be drawn from bus i suspend mode */
//#define usb_low_power_request() Nop()


#endif /* BOOT_CONFIG_H */
