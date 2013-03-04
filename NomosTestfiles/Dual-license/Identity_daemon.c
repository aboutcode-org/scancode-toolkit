/*
 * Identity Daemon
 *
 * Copyright (C) 2011 Texas Instruments, Inc.
 *
 * Dan Murphy (dmurphy@ti.com)
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the dual BSD / GNU General Public License version 2 as
 * published by the Free Software Foundation. When using or
 * redistributing this file, you may do so under either license.
 */

/* OS-specific headers */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <errno.h>
#include <pthread.h>
#include <dirent.h>
#include <ctype.h>

#include <utils/Log.h>
#include <cutils/properties.h>

#include "../../include/omap4_board_identity.h"

#if defined (__cplusplus)
extern "C" {
#endif /* defined (__cplusplus) */

#define ID_DEBUG 1

struct id_data_sysfs {
    int info_id;
    const char *name;
    const char *sysfs_node;
} id_sysfs[] = {
    { SOC_FAMILY, "OMAP Family ", "/sys/board_properties/soc/family"},
    { SOC_REV, "OMAP Type ", "/sys/board_properties/soc/type"},
    { SOC_TYPE, "OMAP Rev ", "/sys/board_properties/soc/revision"},
    { SOC_MAX_FREQ, "Rated Freq ", "/sys/board_properties/soc/max_freq"},
    { APPS_BOARD_REV, "Apps Board Rev ", "/sys/board_properties/board/board_rev"},
    { CPU_MAX_FREQ, "Max Freq ", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq"},
    { CPU_GOV, "Scaling Gov ", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"},
    { LINUX_VERSION, "Linux version ", "/proc/version"},
    { LINUX_CMDLINE, "cmdline ", "/proc/pvr/version"},
    { LINUX_CMDLINE, "cmdline ", "/proc/cmdline"},
    { LINUX_CPU1_STAT, "CPU1 Status ", CPU1_ONLINE},
    { LINUX_OFF_MODE, "Off Mode ", OFF_MODE},
    { WILINK_VERSION, "WiLink version ", "/sys/kernel/debug/ti-st/version"},
    { DPLL_TRIM, "DPLL Trimmed ", "/sys/board_properties/soc/dpll_trimmed"},
    { RBB_TRIM, "DPLL Trimmed ", "/sys/board_properties/soc/rbb_trimmed"},
};

struct id_data_prop {
    int info_id;
    const char *name;
    const char *prop_node;
} id_prop[] = {
    { PROP_DISPLAY_ID, "Build ID ", "ro.build.display.id"},
    { PROP_BUILD_TYPE, "Build Type ", "ro.build.type"},
    { PROP_SER_NO, "Serial Number ", "ro.serialno"},
    { PROP_BOOTLOADER, "Bootloader ", "ro.bootloader"},
    { PROP_DEBUGGABLE, "Debug ", "ro.debuggable"},
    { PROP_CRYPTO_STATE, "Crypto State ", "ro.crypto.state"},
};

struct gov_data {
    int gov_id;
    const char *name;
} gov_info[] = {
    { GOV_PERFORMANCE, "performance"},
    { GOV_HOTPLUG, "hotplug"},
    { GOV_ONDEMAND, "ondemand "},
    { GOV_INTERACTIVE, "interactive"},
    { GOV_USERSPACE, "userspace"},
    { GOV_CONSERVATIVE, "conservative"},
    { GOV_POWERSAVE, "powersave"},
};

char* get_device_identity(int id_number)
{
    char buffer[1024] = {0};
    char* buf;
    int bytes_read = 13;
    int sys_fd = -1;

    if (id_number > MAX_FIELDS) {
           buf = (char *)calloc(1, bytes_read);
           strcpy(buffer, "Not Avaiable");
           goto out;
    }

    LOGD("Reading  %i %s\n", id_number, id_sysfs[id_number].sysfs_node);
    sys_fd = open(id_sysfs[id_number].sysfs_node, O_RDONLY);
    if (sys_fd >= 0) {
            bytes_read = read(sys_fd, buffer, 1024);
            buf = (char *)calloc(1, bytes_read);
            LOGD("%s = %s", id_sysfs[id_number].name, buffer);
            close(sys_fd);
            sys_fd = -1;
    } else {
            LOGD("%s = %s", id_sysfs[id_number].name, "Not Avaialble");
            buf = (char *)calloc(1, bytes_read);
            strcpy(buffer, "Not Avaiable");
    }

out:
    memcpy(buf, buffer, bytes_read - 1);
    return buf;
}

char* get_device_property(int id_number)
{
    char prop_return[1024] = {0};
    int bytes_read = 0;

    if (id_number > MAX_PROP)
           goto out;

    bytes_read = property_get(id_prop[id_number].prop_node, prop_return, "unknown");
    LOGD("%s = %s", id_prop[id_number].name, prop_return);

out:
     return prop_return;
}

int set_governor(int governor)
{
    int ret = 0;
    int sys_fd = -1;
    int value = 1;

    if (governor > GOV_MAX)
           goto out;

    sys_fd = open(GOV_STRING, O_RDWR);
    if (sys_fd >= 0) {
           LOGD("Setting %s\n", gov_info[governor].name);
           ret = write(sys_fd, gov_info[governor].name, 12);
           if (ret < 0)
                   LOGD("ERRNO %i\n", errno);
           LOGD("Returning %i\n", ret);
           close(sys_fd);
           if (governor != GOV_HOTPLUG) {
                char buffer[20];
                sys_fd = open(CPU1_ONLINE, O_RDWR);
                LOGD("Setting CPU1 Online\n");
                int bytes = sprintf(buffer, "%d\n", value);
                ret = write(sys_fd, buffer, bytes);
                if (ret < 0)
                       LOGD("ERRNO %i\n", errno);
                LOGD("Returning %i\n", ret);
                close(sys_fd);
           }
           return ret;
    } else {
            LOGD("Cannot open %s\n", GOV_STRING);
    }

out:
    return -1;
}

int set_off_mode(int off_mode)
{
    int ret = 0;
    int sys_fd = -1;

    if (off_mode > 1)
           off_mode = 1;

    sys_fd = open(OFF_MODE, O_RDWR);
    if (sys_fd >= 0) {
           char buffer[20];
           LOGD("Setting %i\n", off_mode);
           int bytes = sprintf(buffer, "%d\n", off_mode);
           ret = write(sys_fd, buffer, bytes);
           if (ret < 0)
                   LOGD("ERRNO %i\n", errno);
           LOGD("Returning %i\n", ret);
           close(sys_fd);
           return ret;
    } else {
            LOGD("Cannot open %s\n", OFF_MODE);
    }

out:
    return -1;
}

ssize_t print_prop_identity(int id_number)
{
    char prop_return[1024] = {0};

    if (id_number > MAX_PROP)
           goto out;

    property_get(id_prop[id_number].prop_node, prop_return, "unknown");

    LOGD("%s = %s", id_prop[id_number].name, prop_return);
out:
    return 0;
}

ssize_t print_sysfs_identity(int id_number)
{
    char buffer[1024] = {0};
    int bytes_read = 0;
    int sys_fd = -1;

    if (id_number > MAX_FIELDS)
           goto out;

    sys_fd = open(id_sysfs[id_number].sysfs_node, O_RDONLY);
    if (sys_fd >= 0) {
            bytes_read = read(sys_fd, buffer, 1024);
            LOGD("%s = %s", id_sysfs[id_number].name, buffer);
            close(sys_fd);
            sys_fd = -1;
    } else {
            LOGD("%s = %s", id_sysfs[id_number].name, "Not Avaialble");
            strcpy(buffer, "Not Avaiable");
    }

out:
    return 0;
}

int main(int argc, char * argv [])
{
    int bytes_read = 0;
    int sys_fd = -1;
    int i = 0;
    int sysfs_count = MAX_FIELDS;

#if PRINT_ONLY
    for (i = 0; i < MAX_FIELDS; i++) {
         print_sysfs_identity(i);
    }

    for (i = 0; i < MAX_PROP; i++) {
         print_prop_identity(i);
    }

#else
    LOGD(" I got nothing");
#endif
    return 0;
}


#if defined (__cplusplus)
}
#endif /* defined (__cplusplus) */
