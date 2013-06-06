/*
 * frogr-util.c -- Misc tools.
 *
 * Copyright (C) 2010-2012 Mario Sanchez Prada
 * Authors: Mario Sanchez Prada <msanchez@gnome.org>
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
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, see <http://www.gnu.org/licenses/>
 *
 * Parts of this file based on code from gst-plugins-base, licensed as
 * GPL version 2 or later (Copyright (C) <2007> Wim Taymans <wim.taymans@gmail.com>)
 */

#include "frogr-picture.h"
#include "frogr-util.h"
#include "frogr-global-defs.h"

#include <config.h>
#include <glib/gi18n.h>
#include <gtk/gtk.h>
#include <gst/gst.h>
#include <libexif/exif-byte-order.h>
#include <libexif/exif-data.h>
#include <libexif/exif-entry.h>
#include <libexif/exif-format.h>
#include <libexif/exif-loader.h>
#include <libexif/exif-tag.h>

#define CAPS "video/x-raw-rgb,width=160,pixel-aspect-ratio=1/1,bpp=(int)24,depth=(int)24,endianness=(int)4321,red_mask=(int)0xff0000, green_mask=(int)0x00ff00, blue_mask=(int)0x0000ff"

static gboolean
_spawn_command (const gchar* cmd)
{
  GError *error = NULL;

  if (!g_spawn_command_line_async (cmd, &error))
    {
      if (error)
        {
          DEBUG ("Error spawning command '%s': %s", cmd, error->message);
          g_error_free (error);
        }

      return FALSE;
    }
  return TRUE;
}

const gchar *
_get_data_dir (void)
{
#ifdef PLATFORM_MAC
  /* For MacOSX, we return the value of the environment value set by
     the wrapper script running the application */
  static gchar *xdg_data_dir = NULL;
  if (!xdg_data_dir)
    xdg_data_dir = g_strdup (g_getenv("XDG_DATA_DIRS"));
  return (const gchar *) xdg_data_dir;
#else
  /* For GNOME, we just return DATA_DIR */
  return DATA_DIR;
#endif
}

const gchar *
frogr_util_get_app_data_dir (void)
{
  static gchar *app_data_dir = NULL;
  if (!app_data_dir)
    app_data_dir = g_strdup_printf ("%s/frogr", _get_data_dir ());

  return (const gchar *) app_data_dir;
}

const gchar *
frogr_util_get_icons_dir (void)
{
  static gchar *icons_dir = NULL;
  if (!icons_dir)
    icons_dir = g_strdup_printf ("%s/icons", _get_data_dir ());

  return (const gchar *) icons_dir;
}

const gchar *
frogr_util_get_locale_dir (void)
{
  static const gchar *locale_dir = NULL;
  if (!locale_dir)
    {
#ifndef PLATFORM_MAC
      /* If not in MacOSX, we trust the defined variable better */
      locale_dir = g_strdup (FROGR_LOCALE_DIR);
#endif

      /* Fallback for MacOSX and cases where FROGR_LOCALE_DIR was not
	 defined yet because of any reason */
      if (!locale_dir)
	locale_dir = g_strdup_printf ("%s/locale", _get_data_dir ());
    }

  return (const gchar *) locale_dir;
}

gchar *
_get_uris_string_from_list (GList *uris_list)
{
  GList *current_uri = NULL;
  gchar **uris_array = NULL;
  gchar *uris_str = NULL;
  gint n_uris = 0;
  gint i = 0;

  n_uris = g_list_length (uris_list);
  if (n_uris == 0)
    return NULL;

  uris_array = g_new0 (gchar*, n_uris + 1);
  for (current_uri = uris_list; current_uri; current_uri = g_list_next (current_uri))
    uris_array[i++] = (gchar *) (current_uri->data);

  uris_str = g_strjoinv (" ", uris_array);
  g_free (uris_array);

  return uris_str;
}

static void
_open_uris_with_app_info (GList *uris_list, GAppInfo *app_info)
{
  GError *error = NULL;

  /* Early return */
  if (!uris_list)
    return;

  if (!app_info || !g_app_info_launch_uris (app_info, uris_list, NULL, &error))
    {
      /* The default app didn't succeed, so try 'gnome-open' / 'open' */
      gchar *command = NULL;
      gchar *uris = NULL;

      uris = _get_uris_string_from_list (uris_list);

#ifdef PLATFORM_MAC
      /* In MacOSX use 'open' instead of 'gnome-open' */
      command = g_strdup_printf ("open %s", uris);
#else
      command = g_strdup_printf ("gnome-open %s", uris);
#endif
      _spawn_command (command);

      if (error)
        {
          DEBUG ("Error opening URI(s) %s: %s", uris, error->message);
          g_error_free (error);
        }

      g_free (command);
      g_free (uris);
    }

  g_list_foreach (uris_list, (GFunc) g_free, NULL);
  g_list_free (uris_list);
}

void
frogr_util_open_uri (const gchar *uri)
{
  GAppInfo *app_info = NULL;
  GList *uris_list = NULL;

  /* Early return */
  if (!uri)
    return;

#ifndef PLATFORM_MAC
  /* Supported network URIs */
  if (g_str_has_prefix (uri, "http:") || g_str_has_prefix (uri, "https:"))
    app_info = g_app_info_get_default_for_uri_scheme ("http");

  /* Supported help URIs */
  if (g_str_has_prefix (uri, "ghelp:"))
    app_info = g_app_info_get_default_for_uri_scheme ("ghelp");
#endif

  uris_list = g_list_append (uris_list, g_strdup (uri));
  _open_uris_with_app_info (uris_list, app_info);
}

void
frogr_util_open_pictures_in_viewer (GSList *pictures)
{
  GAppInfo *app_info = NULL;
  GList *uris_list = NULL;
  GSList *current_pic = NULL;
  FrogrPicture *picture = NULL;

  /* Early return */
  if (!pictures)
    return;

  for (current_pic = pictures; current_pic; current_pic = g_slist_next (current_pic))
    {
      picture = FROGR_PICTURE (current_pic->data);
      uris_list = g_list_append (uris_list, g_strdup (frogr_picture_get_fileuri (picture)));
    }

  /* We currently choose the application based in the mime type of the
     first picture. This is very basic, but probably good enough for now */
  picture = FROGR_PICTURE (pictures->data);
  if (frogr_picture_is_video (picture))
    app_info = g_app_info_get_default_for_type ("video/mpeg", TRUE);
  else
    app_info = g_app_info_get_default_for_type ("image/jpg", TRUE);

  /* uris_list will be freed inside of the function */
  _open_uris_with_app_info (uris_list, app_info);
}

static void
_show_message_dialog (GtkWindow *parent, const gchar *message, GtkMessageType type)
{
  /* Show alert */
  GtkWidget *dialog =
    gtk_message_dialog_new (parent,
                            GTK_DIALOG_MODAL,
                            type,
                            GTK_BUTTONS_CLOSE,
                            "%s", message);
  gtk_window_set_title (GTK_WINDOW (dialog), APP_SHORTNAME);

  g_signal_connect (G_OBJECT (dialog), "response",
                    G_CALLBACK (gtk_widget_destroy), dialog);

  gtk_widget_show_all (dialog);
}

void
frogr_util_show_info_dialog (GtkWindow *parent, const gchar *message)
{
  _show_message_dialog (parent, message, GTK_MESSAGE_INFO);
}

void
frogr_util_show_warning_dialog (GtkWindow *parent, const gchar *message)
{
  _show_message_dialog (parent, message, GTK_MESSAGE_WARNING);
}

void
frogr_util_show_error_dialog (GtkWindow *parent, const gchar *message)
{
  _show_message_dialog (parent, message, GTK_MESSAGE_ERROR);
}

static GdkPixbuf *
_get_corrected_pixbuf (GdkPixbuf *pixbuf, gint max_width, gint max_height)
{
  GdkPixbuf *scaled_pixbuf = NULL;
  GdkPixbuf *rotated_pixbuf;
  const gchar *orientation;
  gint width;
  gint height;

  g_return_val_if_fail (max_width > 0, NULL);
  g_return_val_if_fail (max_height > 0, NULL);

  /* Look for the right side to reduce */
  width = gdk_pixbuf_get_width (pixbuf);
  height = gdk_pixbuf_get_height (pixbuf);

  DEBUG ("Original size: %dx%d\n", width, height);

  if (width > max_width)
    {
      height = (float)height * max_width / width;
      width = max_width;
    }

  if (height > max_height)
    {
      width = (float)width * max_height / height;
      height = max_height;
    }

  DEBUG ("Scaled size: %dx%d\n", width, height);

  /* Scale the pixbuf to its best size */
  scaled_pixbuf = gdk_pixbuf_scale_simple (pixbuf, width, height,
                                           GDK_INTERP_BILINEAR);

  /* Correct orientation if needed */
  orientation = gdk_pixbuf_get_option (pixbuf, "orientation");

  /* No orientation defined or 0 degrees rotation: we're done */
  if (!orientation || !g_strcmp0 (orientation, "1"))
    return scaled_pixbuf;

  DEBUG ("File orientation for file: %s", orientation);
  rotated_pixbuf = NULL;

  /* Rotated 90 degrees */
  if (!g_strcmp0 (orientation, "8"))
    rotated_pixbuf = gdk_pixbuf_rotate_simple (scaled_pixbuf,
                                               GDK_PIXBUF_ROTATE_COUNTERCLOCKWISE);
  /* Rotated 180 degrees */
  if (!g_strcmp0 (orientation, "3"))
    rotated_pixbuf = gdk_pixbuf_rotate_simple (scaled_pixbuf,
                                               GDK_PIXBUF_ROTATE_UPSIDEDOWN);
  /* Rotated 270 degrees */
  if (!g_strcmp0 (orientation, "6"))
    rotated_pixbuf = gdk_pixbuf_rotate_simple (scaled_pixbuf,
                                               GDK_PIXBUF_ROTATE_CLOCKWISE);
  if (rotated_pixbuf)
    {
      g_object_unref (scaled_pixbuf);
      return rotated_pixbuf;
    }

  /* No rotation was applied, return the scaled pixbuf */
  return scaled_pixbuf;
}

static GdkPixbuf *
_get_pixbuf_from_image_contents (const guchar *contents, gsize length, GError **out_error)
{
  GdkPixbufLoader *pixbuf_loader = NULL;
  GdkPixbuf *pixbuf = NULL;
  GError *error = NULL;

  pixbuf_loader = gdk_pixbuf_loader_new ();
  if (gdk_pixbuf_loader_write (pixbuf_loader,
                               (const guchar *)contents,
                               length,
                               &error))
    {
      gdk_pixbuf_loader_close (pixbuf_loader, NULL);
      pixbuf = gdk_pixbuf_loader_get_pixbuf (pixbuf_loader);
    }

  if (error)
    {
      DEBUG ("Error loading pixbuf: %s", error->message);
      g_propagate_error (out_error, error);
    }

  /* Keep the pixbuf before destroying the loader */
  if (pixbuf)
    g_object_ref (pixbuf);
  g_object_unref (pixbuf_loader);

  return pixbuf;
}

/* The following function is based in GStreamer's snapshot example,
   from gst-plugins-base, licensed as GPL version 2 or later
   (Copyright (C) <2007> Wim Taymans <wim.taymans@gmail.com>) */
static GdkPixbuf *
_get_pixbuf_from_video_file (GFile *file, GError **out_error)
{
  GdkPixbuf *pixbuf = NULL;
  GstElement *pipeline, *sink;
  GstBuffer *buffer;
  GstFormat format;
  GstStateChangeReturn ret;
  gchar *file_uri;
  gchar *descr;
  gint width, height;
  gint64 duration, position;
  GError *error = NULL;
  gboolean res;

  /* create a new pipeline */
  file_uri = g_file_get_uri (file);
  descr = g_strdup_printf ("uridecodebin uri=%s ! ffmpegcolorspace ! videoscale ! "
                           " appsink name=sink caps=\"" CAPS "\"", file_uri);
  g_free (file_uri);

  pipeline = gst_parse_launch (descr, &error);
  g_free (descr);

  if (error != NULL) {
    DEBUG ("Could not construct pipeline: %s\n", error->message);
    g_propagate_error (out_error, error);
    return NULL;
  }

  /* get sink */
  sink = gst_bin_get_by_name (GST_BIN (pipeline), "sink");

  /* set to PAUSED to make the first frame arrive in the sink */
  ret = gst_element_set_state (pipeline, GST_STATE_PAUSED);
  switch (ret) {
    case GST_STATE_CHANGE_FAILURE:
      DEBUG ("failed to play the file\n");
      return NULL;
    case GST_STATE_CHANGE_NO_PREROLL:
      /* for live sources, we need to set the pipeline to PLAYING before we can
       * receive a buffer. We don't do that yet */
      DEBUG ("live sources not supported yet\n");
      return NULL;
    default:
      break;
  }

  /* This can block for up to 5 seconds. If your machine is really overloaded,
   * it might time out before the pipeline prerolled and we generate an error. A
   * better way is to run a mainloop and catch errors there. */
  ret = gst_element_get_state (pipeline, NULL, NULL, 5 * GST_SECOND);
  if (ret == GST_STATE_CHANGE_FAILURE) {
    DEBUG ("failed to play the file\n");
    return NULL;
  }

  /* get the duration */
  format = GST_FORMAT_TIME;
  gst_element_query_duration (pipeline, &format, &duration);

  if (duration != -1)
    /* we have a duration, seek to 50% */
    position = duration * 0.5;
  else
    /* no duration, seek to 1 second, this could EOS */
    position = 1 * GST_SECOND;

  /* seek to the a position in the file. Most files have a black first frame so
   * by seeking to somewhere else we have a bigger chance of getting something
   * more interesting. */
  gst_element_seek_simple (pipeline, GST_FORMAT_TIME,
      GST_SEEK_FLAG_KEY_UNIT | GST_SEEK_FLAG_FLUSH, position);

  /* get the preroll buffer from appsink, this block untils appsink really prerolls */
  g_signal_emit_by_name (sink, "pull-preroll", &buffer, NULL);

  /* if we have a buffer now, convert it to a pixbuf. It's possible that we
   * don't have a buffer because we went EOS right away or had an error. */
  if (buffer) {
    GstCaps *caps;
    GstStructure *s;

    /* get the snapshot buffer format now. We set the caps on the appsink so
     * that it can only be an rgb buffer. The only thing we have not specified
     * on the caps is the height, which is dependant on the pixel-aspect-ratio
     * of the source material */
    caps = GST_BUFFER_CAPS (buffer);
    if (!caps) {
      DEBUG ("could not get snapshot format\n");
      return NULL;
    }
    s = gst_caps_get_structure (caps, 0);

    /* we need to get the final caps on the buffer to get the size */
    res = gst_structure_get_int (s, "width", &width);
    res |= gst_structure_get_int (s, "height", &height);
    if (!res) {
      DEBUG ("could not get snapshot dimension\n");
      return NULL;
    }

    /* create pixmap from buffer and save, gstreamer video buffers have a stride
     * that is rounded up to the nearest multiple of 4 */
    pixbuf = gdk_pixbuf_new_from_data (GST_BUFFER_DATA (buffer),
        GDK_COLORSPACE_RGB, FALSE, 8, width, height,
        GST_ROUND_UP_4 (width * 3), NULL, NULL);

  } else {
    DEBUG ("could not make snapshot\n");
  }

  /* cleanup and exit */
  gst_element_set_state (pipeline, GST_STATE_NULL);
  gst_object_unref (pipeline);

  return pixbuf;
}

GdkPixbuf *
frogr_util_get_pixbuf_for_video_file (GFile *file, gint max_width, gint max_height, GError **error)
{
  GdkPixbuf *pixbuf = NULL;

  pixbuf = _get_pixbuf_from_video_file (file, error);
  if (pixbuf)
    {
      GdkPixbuf *c_pixbuf = NULL;
      c_pixbuf = _get_corrected_pixbuf (pixbuf, max_width, max_height);
      g_object_unref (pixbuf);
      pixbuf = c_pixbuf;
    }

  return pixbuf;
}

GdkPixbuf *
frogr_util_get_pixbuf_from_image_contents (const guchar *contents, gsize length, gint max_width, gint max_height, GError **error)
{
  GdkPixbuf *pixbuf = NULL;

  pixbuf = _get_pixbuf_from_image_contents (contents, length, error);
  if (pixbuf)
    {
      GdkPixbuf *c_pixbuf = NULL;
      c_pixbuf = _get_corrected_pixbuf (pixbuf, max_width, max_height);
      g_object_unref (pixbuf);
      pixbuf = c_pixbuf;
    }

  return pixbuf;
}

gchar *
frogr_util_get_datasize_string (gulong datasize)
{
  gchar *result = NULL;

  if (datasize != G_MAXULONG)
    {
      gfloat datasize_float = G_MAXFLOAT;
      gchar *unit_str = NULL;
      int n_divisions = 0;

      datasize_float = datasize;
      while (datasize_float > 1000.0 && n_divisions < 3)
        {
          datasize_float /= 1024;
          n_divisions++;
        }

      switch (n_divisions)
        {
        case 0:
          unit_str = g_strdup ("KB");
          break;
        case 1:
          unit_str = g_strdup ("MB");
          break;
        case 2:
          unit_str = g_strdup ("GB");
          break;
        default:
          unit_str = NULL;;
        }

      if (unit_str)
        {
          result = g_strdup_printf ("%.1f %s", datasize_float, unit_str);
          g_free (unit_str);
        }
    }

  return result;
}

const gchar * const *
frogr_util_get_supported_mimetypes (void)
{
  static const gchar *supported_mimetypes[] = {
    "image/jpg",
    "image/jpeg",
    "image/png",
    "image/bmp",
    "image/gif",
    "video/mpeg",
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/ogg",
    "video/x-ms-wmv",
    "video/3gpp",
    "video/m2ts",
    "video/avchd-stream",
    "video/mp2t",
    "video/vnd.dlna.mpeg-tts",
    "application/ogg",
    NULL
  };

  return supported_mimetypes;
}
