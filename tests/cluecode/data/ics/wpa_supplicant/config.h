/*
 * WPA Supplicant / Configuration file structures
 * Copyright (c) 2003-2005, Jouni Malinen <j@w1.fi>
 *
 * This program is free software; you can redistribute it and/or modify
#ifndef CONFIG_NO_STDOUT_DEBUG
void wpa_config_debug_dump_networks(struct wpa_config *config);
#else /* CONFIG_NO_STDOUT_DEBUG */
#define wpa_config_debug_dump_networks(c) do { } while (0)
#endif /* CONFIG_NO_STDOUT_DEBUG */
