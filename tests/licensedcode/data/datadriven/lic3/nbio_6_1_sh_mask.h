/*
 * Copyright (C) 2017  Advanced Micro Devices, Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE COPYRIGHT HOLDER(S) BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
 * AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
#ifndef _nbio_6_1_SH_MASK_HEADER
#define _nbio_6_1_SH_MASK_HEADER


// addressBlock: nbio_pcie_pswuscfg0_cfgdecp
//PSWUSCFG0_VENDOR_ID
#define PSWUSCFG0_VENDOR_ID__VENDOR_ID__SHIFT                                                                 0x0
#define PSWUSCFG0_VENDOR_ID__VENDOR_ID_MASK                                                                   0xFFFFL
//PSWUSCFG0_DEVICE_ID
#define PSWUSCFG0_DEVICE_ID__DEVICE_ID__SHIFT                                                                 0x0
#define PSWUSCFG0_DEVICE_ID__DEVICE_ID_MASK                                                                   0xFFFFL
//PSWUSCFG0_COMMAND
#define PSWUSCFG0_COMMAND__IO_ACCESS_EN__SHIFT                                                                0x0
#define PSWUSCFG0_COMMAND__MEM_ACCESS_EN__SHIFT                                                               0x1
#define PSWUSCFG0_COMMAND__BUS_MASTER_EN__SHIFT                                                               0x2
#define PSWUSCFG0_COMMAND__SPECIAL_CYCLE_EN__SHIFT                                                            0x3
#define PSWUSCFG0_COMMAND__MEM_WRITE_INVALIDATE_EN__SHIFT                                                     0x4
#define PSWUSCFG0_COMMAND__PAL_SNOOP_EN__SHIFT                                                                0x5
#define PSWUSCFG0_COMMAND__PARITY_ERROR_RESPONSE__SHIFT                                                       0x6
#define PSWUSCFG0_COMMAND__AD_STEPPING__SHIFT                                                                 0x7
#define PSWUSCFG0_COMMAND__SERR_EN__SHIFT                                                                     0x8
#define PSWUSCFG0_COMMAND__FAST_B2B_EN__SHIFT                                                                 0x9
#define PSWUSCFG0_COMMAND__INT_DIS__SHIFT                                                                     0xa
#define PSWUSCFG0_COMMAND__IO_ACCESS_EN_MASK                                                                  0x0001L
#define PSWUSCFG0_COMMAND__MEM_ACCESS_EN_MASK                                                                 0x0002L
#define PSWUSCFG0_COMMAND__BUS_MASTER_EN_MASK                                                                 0x0004L
#define PSWUSCFG0_COMMAND__SPECIAL_CYCLE_EN_MASK                                                              0x0008L
#define PSWUSCFG0_COMMAND__MEM_WRITE_INVALIDATE_EN_MASK                                                       0x0010L
#define PSWUSCFG0_COMMAND__PAL_SNOOP_EN_MASK                                                                  0x0020L
#define PSWUSCFG0_COMMAND__PARITY_ERROR_RESPONSE_MASK                                                         0x0040L
#define PSWUSCFG0_COMMAND__AD_STEPPING_MASK                                                                   0x0080L
#define PSWUSCFG0_COMMAND__SERR_EN_MASK                                                                       0x0100L
#define PSWUSCFG0_COMMAND__FAST_B2B_EN_MASK                                                                   0x0200L
#define PSWUSCFG0_COMMAND__INT_DIS_MASK                                                                       0x0400L
//PSWUSCFG0_STATUS
#define PSWUSCFG0_STATUS__INT_STATUS__SHIFT                                                                   0x3
#define PSWUSCFG0_STATUS__CAP_LIST__SHIFT                                                                     0x4
#define PSWUSCFG0_STATUS__PCI_66_EN__SHIFT                                                                    0x5
#define PSWUSCFG0_STATUS__FAST_BACK_CAPABLE__SHIFT                                                            0x7
#define PSWUSCFG0_STATUS__MASTER_DATA_PARITY_ERROR__SHIFT                                                     0x8
#define PSWUSCFG0_STATUS__DEVSEL_TIMING__SHIFT                                                                0x9
#define PSWUSCFG0_STATUS__SIGNAL_TARGET_ABORT__SHIFT                                                          0xb
#define PSWUSCFG0_STATUS__RECEIVED_TARGET_ABORT__SHIFT                                                        0xc
#define PSWUSCFG0_STATUS__RECEIVED_MASTER_ABORT__SHIFT                                                        0xd
#define PSWUSCFG0_STATUS__SIGNALED_SYSTEM_ERROR__SHIFT                                                        0xe
#define PSWUSCFG0_STATUS__PARITY_ERROR_DETECTED__SHIFT                                                        0xf
#define PSWUSCFG0_STATUS__INT_STATUS_MASK                                                                     0x0008L
#define PSWUSCFG0_STATUS__CAP_LIST_MASK                                                                       0x0010L
#define PSWUSCFG0_STATUS__PCI_66_EN_MASK                                                                      0x0020L
#define PSWUSCFG0_STATUS__FAST_BACK_CAPABLE_MASK                                                              0x0080L
#define PSWUSCFG0_STATUS__MASTER_DATA_PARITY_ERROR_MASK                                                       0x0100L
#define PSWUSCFG0_STATUS__DEVSEL_TIMING_MASK                                                                  0x0600L
#define PSWUSCFG0_STATUS__SIGNAL_TARGET_ABORT_MASK                                                            0x0800L
#define PSWUSCFG0_STATUS__RECEIVED_TARGET_ABORT_MASK                                                          0x1000L
#define PSWUSCFG0_STATUS__RECEIVED_MASTER_ABORT_MASK                                                          0x2000L
#define PSWUSCFG0_STATUS__SIGNALED_SYSTEM_ERROR_MASK                                                          0x4000L
#define PSWUSCFG0_STATUS__PARITY_ERROR_DETECTED_MASK                                                          0x8000L
//PSWUSCFG0_REVISION_ID
#define PSWUSCFG0_REVISION_ID__MINOR_REV_ID__SHIFT                                                            0x0
#define PSWUSCFG0_REVISION_ID__MAJOR_REV_ID__SHIFT                                                            0x4
#define PSWUSCFG0_REVISION_ID__MINOR_REV_ID_MASK                                                              0x0FL
#define PSWUSCFG0_REVISION_ID__MAJOR_REV_ID_MASK                                                              0xF0L
//PSWUSCFG0_PROG_INTERFACE
#define PSWUSCFG0_PROG_INTERFACE__PROG_INTERFACE__SHIFT                                                       0x0
#define PSWUSCFG0_PROG_INTERFACE__PROG_INTERFACE_MASK                                                         0xFFL
//PSWUSCFG0_SUB_CLASS
#define PSWUSCFG0_SUB_CLASS__SUB_CLASS__SHIFT                                                                 0x0
#define PSWUSCFG0_SUB_CLASS__SUB_CLASS_MASK                                                                   0xFFL
//PSWUSCFG0_BASE_CLASS
#define PSWUSCFG0_BASE_CLASS__BASE_CLASS__SHIFT                                                               0x0
#define PSWUSCFG0_BASE_CLASS__BASE_CLASS_MASK                                                                 0xFFL
//PSWUSCFG0_CACHE_LINE
#define PSWUSCFG0_CACHE_LINE__CACHE_LINE_SIZE__SHIFT                                                          0x0
#define PSWUSCFG0_CACHE_LINE__CACHE_LINE_SIZE_MASK                                                            0xFFL
//PSWUSCFG0_LATENCY
#define PSWUSCFG0_LATENCY__LATENCY_TIMER__SHIFT                                                               0x0
#define PSWUSCFG0_LATENCY__LATENCY_TIMER_MASK                                                                 0xFFL
//PSWUSCFG0_HEADER
#define PSWUSCFG0_HEADER__HEADER_TYPE__SHIFT                                                                  0x0
#define PSWUSCFG0_HEADER__DEVICE_TYPE__SHIFT                                                                  0x7
#define PSWUSCFG0_HEADER__HEADER_TYPE_MASK                                                                    0x7FL
#define PSWUSCFG0_HEADER__DEVICE_TYPE_MASK                                                                    0x80L
//PSWUSCFG0_BIST
#define PSWUSCFG0_BIST__BIST_COMP__SHIFT                                                                      0x0
#define PSWUSCFG0_BIST__BIST_STRT__SHIFT                                                                      0x6
#define PSWUSCFG0_BIST__BIST_CAP__SHIFT                                                                       0x7
#define PSWUSCFG0_BIST__BIST_COMP_MASK                                                                        0x0FL
#define PSWUSCFG0_BIST__BIST_STRT_MASK                                                                        0x40L
#define PSWUSCFG0_BIST__BIST_CAP_MASK                                                                         0x80L
//PSWUSCFG0_SUB_BUS_NUMBER_LATENCY
#define PSWUSCFG0_SUB_BUS_NUMBER_LATENCY__PRIMARY_BUS__SHIFT                                                  0x0
#define PSWUSCFG0_SUB_BUS_NUMBER_LATENCY__SECONDARY_BUS__SHIFT                                                0x8
#define PSWUSCFG0_SUB_BUS_NUMBER_LATENCY__SUB_BUS_NUM__SHIFT                                                  0x10
#define PSWUSCFG0_SUB_BUS_NUMBER_LATENCY__SECONDARY_LATENCY_TIMER__SHIFT                                      0x18
#define PSWUSCFG0_SUB_BUS_NUMBER_LATENCY__PRIMARY_BUS_MASK                                                    0x000000FFL
#define PSWUSCFG0_SUB_BUS_NUMBER_LATENCY__SECONDARY_BUS_MASK                                                  0x0000FF00L
#define PSWUSCFG0_SUB_BUS_NUMBER_LATENCY__SUB_BUS_NUM_MASK                                                    0x00FF0000L
#define PSWUSCFG0_SUB_BUS_NUMBER_LATENCY__SECONDARY_LATENCY_TIMER_MASK                                        0xFF000000L
//PSWUSCFG0_IO_BASE_LIMIT
#define PSWUSCFG0_IO_BASE_LIMIT__IO_BASE_TYPE__SHIFT                                                          0x0
#define PSWUSCFG0_IO_BASE_LIMIT__IO_BASE__SHIFT                                                               0x4
#define PSWUSCFG0_IO_BASE_LIMIT__IO_LIMIT_TYPE__SHIFT                                                         0x8
#define PSWUSCFG0_IO_BASE_LIMIT__IO_LIMIT__SHIFT                                                              0xc
#define PSWUSCFG0_IO_BASE_LIMIT__IO_BASE_TYPE_MASK                                                            0x000FL
#define PSWUSCFG0_IO_BASE_LIMIT__IO_BASE_MASK                                                                 0x00F0L
#define PSWUSCFG0_IO_BASE_LIMIT__IO_LIMIT_TYPE_MASK                                                           0x0F00L
#define PSWUSCFG0_IO_BASE_LIMIT__IO_LIMIT_MASK                                                                0xF000L
//PSWUSCFG0_SECONDARY_STATUS
#define PSWUSCFG0_SECONDARY_STATUS__CAP_LIST__SHIFT                                                           0x4
#define PSWUSCFG0_SECONDARY_STATUS__PCI_66_EN__SHIFT                                                          0x5
#define PSWUSCFG0_SECONDARY_STATUS__FAST_BACK_CAPABLE__SHIFT                                                  0x7
#define PSWUSCFG0_SECONDARY_STATUS__MASTER_DATA_PARITY_ERROR__SHIFT                                           0x8
#define PSWUSCFG0_SECONDARY_STATUS__DEVSEL_TIMING__SHIFT                                                      0x9
#define PSWUSCFG0_SECONDARY_STATUS__SIGNAL_TARGET_ABORT__SHIFT                                                0xb
#define PSWUSCFG0_SECONDARY_STATUS__RECEIVED_TARGET_ABORT__SHIFT                                              0xc
#define PSWUSCFG0_SECONDARY_STATUS__RECEIVED_MASTER_ABORT__SHIFT                                              0xd
#define PSWUSCFG0_SECONDARY_STATUS__RECEIVED_SYSTEM_ERROR__SHIFT                                              0xe
#define PSWUSCFG0_SECONDARY_STATUS__PARITY_ERROR_DETECTED__SHIFT                                              0xf
#define PSWUSCFG0_SECONDARY_STATUS__CAP_LIST_MASK                                                             0x0010L
#define PSWUSCFG0_SECONDARY_STATUS__PCI_66_EN_MASK                                                            0x0020L
#define PSWUSCFG0_SECONDARY_STATUS__FAST_BACK_CAPABLE_MASK                                                    0x0080L
#define PSWUSCFG0_SECONDARY_STATUS__MASTER_DATA_PARITY_ERROR_MASK                                             0x0100L
#define PSWUSCFG0_SECONDARY_STATUS__DEVSEL_TIMING_MASK                                                        0x0600L
#define PSWUSCFG0_SECONDARY_STATUS__SIGNAL_TARGET_ABORT_MASK                                                  0x0800L
#define PSWUSCFG0_SECONDARY_STATUS__RECEIVED_TARGET_ABORT_MASK                                                0x1000L
#define PSWUSCFG0_SECONDARY_STATUS__RECEIVED_MASTER_ABORT_MASK                                                0x2000L
#define PSWUSCFG0_SECONDARY_STATUS__RECEIVED_SYSTEM_ERROR_MASK                                                0x4000L
#define PSWUSCFG0_SECONDARY_STATUS__PARITY_ERROR_DETECTED_MASK                                                0x8000L
//PSWUSCFG0_MEM_BASE_LIMIT
#define PSWUSCFG0_MEM_BASE_LIMIT__MEM_BASE_TYPE__SHIFT                                                        0x0
#define PSWUSCFG0_MEM_BASE_LIMIT__MEM_BASE_31_20__SHIFT                                                       0x4
#define PSWUSCFG0_MEM_BASE_LIMIT__MEM_LIMIT_TYPE__SHIFT                                                       0x10
#define PSWUSCFG0_MEM_BASE_LIMIT__MEM_LIMIT_31_20__SHIFT                                                      0x14
#define PSWUSCFG0_MEM_BASE_LIMIT__MEM_BASE_TYPE_MASK                                                          0x0000000FL
#define PSWUSCFG0_MEM_BASE_LIMIT__MEM_BASE_31_20_MASK                                                         0x0000FFF0L
#define PSWUSCFG0_MEM_BASE_LIMIT__MEM_LIMIT_TYPE_MASK                                                         0x000F0000L
#define PSWUSCFG0_MEM_BASE_LIMIT__MEM_LIMIT_31_20_MASK                                                        0xFFF00000L
//PSWUSCFG0_PREF_BASE_LIMIT
