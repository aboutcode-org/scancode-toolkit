/*
 * fsp-parser.h
 *
 * Copyright (C) 2010-2011 Mario Sanchez Prada
 * Authors: Mario Sanchez Prada <msanchez@igalia.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of version 3 of the GNU Lesser General
 * Public License as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU General Public Lesser License
 * along with this program; if not, see <http://www.gnu.org/licenses/>
 *
 */

#ifndef _FSP_PARSER_H
#define _FSP_PARSER_H

#include <glib.h>
#include <glib-object.h>

#include <flicksoup/fsp-data.h>

G_BEGIN_DECLS

#define FSP_TYPE_PARSER                         \
  (fsp_parser_get_type())
#define FSP_PARSER(obj)                                                 \
  (G_TYPE_CHECK_INSTANCE_CAST (obj, FSP_TYPE_PARSER, FspParser))
#define FSP_PARSER_CLASS(klass)                                         \
  (G_TYPE_CHECK_CLASS_CAST(klass, FSP_TYPE_PARSER, FspParserClass))
#define FSP_IS_PARSER(obj)                              \
  (G_TYPE_CHECK_INSTANCE_TYPE(obj, FSP_TYPE_PARSER))
#define FSP_IS_PARSER_CLASS(klass)                      \
  (G_TYPE_CHECK_CLASS_TYPE((klass), FSP_TYPE_PARSER))
#define FSP_PARSER_GET_CLASS(obj)                                       \
  (G_TYPE_INSTANCE_GET_CLASS ((obj), FSP_TYPE_PARSER, FspParserClass))

typedef struct _FspParser FspParser;
typedef struct _FspParserClass FspParserClass;

struct _FspParser
{
  GObject parent_instance;
};

struct _FspParserClass
{
  GObjectClass parent_class;
};

/* All the parsers should be defined like this type */
typedef
gpointer (* FspParserFunc)              (FspParser  *self,
                                   const gchar      *buffer,
                                   gulong            buf_size,
                                   GError          **error);

GType
fsp_parser_get_type              (void) G_GNUC_CONST;

FspParser *
fsp_parser_get_instance          (void);

gchar *
fsp_parser_get_frob                     (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

FspDataAuthToken *
fsp_parser_get_auth_token               (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

FspDataUploadStatus *
fsp_parser_get_upload_status            (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

gchar *
fsp_parser_get_upload_result            (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

FspDataPhotoInfo *
fsp_parser_get_photo_info               (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

GSList *
fsp_parser_get_photosets_list           (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

gpointer
fsp_parser_added_to_photoset            (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

gchar *
fsp_parser_photoset_created             (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

GSList *
fsp_parser_get_groups_list              (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

gpointer
fsp_parser_added_to_group               (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

GSList *
fsp_parser_get_tags_list                (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

gpointer
fsp_parser_set_license                  (FspParser  *self,
                                         const gchar      *buffer,
                                         gulong            buf_size,
                                         GError          **error);

G_END_DECLS

#endif
