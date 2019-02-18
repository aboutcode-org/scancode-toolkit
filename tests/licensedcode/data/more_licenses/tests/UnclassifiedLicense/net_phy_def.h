/*
*********************************************************************************************************
*                                              uC/TCP-IP
*                                      The Embedded TCP/IP Suite
*
*                          (c) Copyright 2003-2006; Micrium, Inc.; Weston, FL
*
*               All rights reserved.  Protected by international copyright laws.
*
*               uC/TCP-IP is provided in source form for FREE evaluation, for educational
*               use or peaceful research.  If you plan on using uC/TCP-IP in a commercial
*               product you need to contact Micrium to properly license its use in your
*               product.  We provide ALL the source code for your convenience and to help
*               you experience uC/TCP-IP.  The fact that the source code is provided does
*               NOT mean that you can use it without paying a licensing fee.
*
*               Network Interface Card (NIC) port files provided, as is, for FREE and do
*               NOT require any additional licensing or licensing fee.
*
*               Knowledge of the source code may NOT be used to develop a similar product.
*
*               Please help us continue to provide the Embedded community with the finest
*               software available.  Your honesty is greatly appreciated.
*********************************************************************************************************
*/

/*
*********************************************************************************************************
*
*                                   NETWORK PHYSICAL LAYER DEFINES
*
* Filename      : net_phy_def.h
* Version       : V1.88
* Programmer(s) : EHS
*********************************************************************************************************
*/

/*
*********************************************************************************************************
*                                               MODULE
*********************************************************************************************************
*/

#ifndef  NET_PHY_DEF_MODULE_PRESENT
#define  NET_PHY_DEF_MODULE_PRESENT


/*
*********************************************************************************************************
*                                     PHYSICAL LAYER DEFINITIONS
*********************************************************************************************************
*/

#define  NET_PHY_SPD_0                                     0    /* Link speed unknown, or link down                     */
#define  NET_PHY_SPD_10                                   10    /* Link speed = 10mbps                                  */
#define  NET_PHY_SPD_100                                 100    /* Link speed = 100mbps                                 */
#define  NET_PHY_SPD_1000                               1000    /* Link speed = 1000mbps                                */

#define  NET_PHY_DUPLEX_UNKNOWN                            0    /* Duplex uknown or auto-neg incomplete                 */
#define  NET_PHY_DUPLEX_HALF                               1    /* Duplex = Half Duplex                                 */
#define  NET_PHY_DUPLEX_FULL                               2    /* Duplex = Full Duplex                                 */


/*
*********************************************************************************************************
*                                     PHYSICAL LAYER ERROR CODES
*
* Note(s) : (1) Network error code '12,000' series reserved for physical layers.
*********************************************************************************************************
*/

#define  NET_PHY_ERR_NONE                              12000


/*$PAGE*/
/*
*********************************************************************************************************
*                                             MODULE END
*********************************************************************************************************
*/

#endif                                                          /* End of net phy module include.                       */

