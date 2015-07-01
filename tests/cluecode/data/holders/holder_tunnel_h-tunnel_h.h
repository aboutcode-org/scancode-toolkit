/*
 * tunnel.h --
 *
 *	Interface of the TUNNEL-MIB implementation.
 *
 * Copyright (c) 2000 Frank Strauss <strauss@ibr.cs.tu-bs.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 *
 */

#ifndef _MIBGROUP_TUNNEL_H
#define _MIBGROUP_TUNNEL_H

void init_tunnel(void);
void deinit_tunnel(void);

unsigned char *var_tunnelIfEntry(struct variable *, oid *, size_t *,
				 int, size_t *,
				 WriteMethod **write_method);

unsigned char *var_tunnelConfigEntry(struct variable *, oid *, size_t *,
				     int, size_t *,
				     WriteMethod **write_method);

#endif /* _MIBGROUP_TUNNEL_H */
