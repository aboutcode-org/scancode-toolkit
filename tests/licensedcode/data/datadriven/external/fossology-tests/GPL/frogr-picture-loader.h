/*
 * frogr-picture-loader.h -- Asynchronous picture loader in frogr
 *
 * Copyright (C) 2009-2011 Mario Sanchez Prada
 * Authors: Mario Sanchez Prada <msanchez@igalia.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of version 3 of the GNU General Public
 * License as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public
 * License along with this program; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 *
 */

#ifndef _FROGR_PICTURE_LOADER_H
#define _FROGR_PICTURE_LOADER_H

#include "frogr-picture.h"

#include <glib.h>
#include <glib-object.h>

G_BEGIN_DECLS

#define FROGR_TYPE_PICTURE_LOADER           (frogr_picture_loader_get_type())
#define FROGR_PICTURE_LOADER(obj)           (G_TYPE_CHECK_INSTANCE_CAST(obj, FROGR_TYPE_PICTURE_LOADER, FrogrPictureLoader))
#define FROGR_PICTURE_LOADER_CLASS(klass)   (G_TYPE_CHECK_CLASS_CAST(klass, FROGR_TYPE_PICTURE_LOADER, FrogrPictureLoaderClass))
#define FROGR_IS_PICTURE_LOADER(obj)           (G_TYPE_CHECK_INSTANCE_TYPE(obj, FROGR_TYPE_PICTURE_LOADER))
#define FROGR_IS_PICTURE_LOADER_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE((klass), FROGR_TYPE_PICTURE_LOADER))
#define FROGR_PICTURE_LOADER_GET_CLASS(obj) (G_TYPE_INSTANCE_GET_CLASS ((obj), FROGR_TYPE_PICTURE_LOADER, FrogrPictureLoaderClass))

typedef struct _FrogrPictureLoader FrogrPictureLoader;
typedef struct _FrogrPictureLoaderClass FrogrPictureLoaderClass;

/* Callback to be executed after every single load */
typedef void (*FrogrPictureLoadedCallback) (GObject *source,
                                            FrogrPicture *picture);

/* Callback to be executed after all the pictures are loaded */
typedef void (*FrogrPicturesLoadedCallback) (GObject *source);

struct _FrogrPictureLoader
{
  GObject parent_instance;
};

struct _FrogrPictureLoaderClass
{
  GObjectClass parent_class;
};


GType frogr_picture_loader_get_type(void) G_GNUC_CONST;

FrogrPictureLoader *frogr_picture_loader_new (GSList *file_uris,
                                              FrogrPictureLoadedCallback picture_loaded_cb,
                                              FrogrPicturesLoadedCallback pictures_loaded_cb,
                                              gpointer object);

void frogr_picture_loader_load (FrogrPictureLoader *self);

G_END_DECLS

#endif
