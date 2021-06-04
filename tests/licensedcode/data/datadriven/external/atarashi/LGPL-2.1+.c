/*
 * Copyright (C) 2006, Mr Jamie McCracken (jamiemcc@gnome.org)
 * Copyright (C) 2008, Nokia (urho.konttori@nokia.com)
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser Lesser General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
 * Boston, MA  02110-1301, USA.
 */

#include "config.h"

#include <string.h>
#include <stdlib.h>

#include <glib.h>

#include "tracker-class.h"
#include "tracker-namespace.h"
#include "tracker-ontologies.h"

#define GET_PRIV(obj) (G_TYPE_INSTANCE_GET_PRIVATE ((obj), TRACKER_TYPE_CLASS, TrackerClassPriv))

typedef struct _TrackerClassPriv TrackerClassPriv;

struct _TrackerClassPriv {
	gchar *uri;
	gchar *name;
	gint count;
	gint id;
	gboolean is_new;

	GArray *super_classes;
};

static void class_finalize     (GObject      *object);
static void class_get_property (GObject      *object,
                                guint         param_id,
                                GValue       *value,
                                GParamSpec   *pspec);
static void class_set_property (GObject      *object,
                                guint         param_id,
                                const GValue *value,
                                GParamSpec   *pspec);

enum {
	PROP_0,
	PROP_URI,
	PROP_NAME,
	PROP_COUNT,
	PROP_ID,
	PROP_IS_NEW
};
