/*
 * evd-pki-pubkey.c
 *
 * EventDance, Peer-to-peer IPC library <http://eventdance.org>
 *
 * Copyright (C) 2011, Igalia S.L.
 *
 * Authors:
 *   Eduardo Lima Mitev <elima@igalia.com>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * version 3, or (at your option) any later version as published by
 * the Free Software Foundation.
 *
 * This library is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License at http://www.gnu.org/licenses/lgpl-3.0.txt
 * for more details.
 */

#include <gcrypt.h>

#include "evd-pki-pubkey.h"

#include "evd-error.h"

G_DEFINE_TYPE (EvdPkiPubkey, evd_pki_pubkey, G_TYPE_OBJECT)

#define EVD_PKI_PUBKEY_GET_PRIVATE(obj) (G_TYPE_INSTANCE_GET_PRIVATE ((obj), \
                                         EVD_TYPE_PKI_PUBKEY, \
                                         EvdPkiPubkeyPrivate))

/* private data */
struct _EvdPkiPubkeyPrivate
{
  gcry_sexp_t key_sexp;

  EvdPkiKeyType type;
};


/* properties */
enum
{
  PROP_0,
  PROP_TYPE
};

static void     evd_pki_pubkey_class_init         (EvdPkiPubkeyClass *class);
static void     evd_pki_pubkey_init               (EvdPkiPubkey *self);

static void     evd_pki_pubkey_finalize           (GObject *obj);
static void     evd_pki_pubkey_dispose            (GObject *obj);

static void     evd_pki_pubkey_get_property       (GObject    *obj,
                                                   guint       prop_id,
                                                   GValue     *value,
                                                   GParamSpec *pspec);

static void
evd_pki_pubkey_class_init (EvdPkiPubkeyClass *class)
{
  GObjectClass *obj_class;

  obj_class = G_OBJECT_CLASS (class);

  obj_class->dispose = evd_pki_pubkey_dispose;
  obj_class->finalize = evd_pki_pubkey_finalize;
  obj_class->get_property = evd_pki_pubkey_get_property;

  /* install properties */
  g_object_class_install_property (obj_class, PROP_TYPE,
                                   g_param_spec_uint ("type",
                                                      "Key type",
                                                      "The type of private key (RSA, DSA, etc)",
                                                      EVD_PKI_KEY_TYPE_UNKNOWN,
                                                      EVD_PKI_KEY_TYPE_DSA,
                                                      EVD_PKI_KEY_TYPE_UNKNOWN,
                                                      G_PARAM_READABLE |
                                                      G_PARAM_STATIC_STRINGS));

  g_type_class_add_private (obj_class, sizeof (EvdPkiPubkeyPrivate));
}

static void
evd_pki_pubkey_init (EvdPkiPubkey *self)
{
  EvdPkiPubkeyPrivate *priv;

  priv = EVD_PKI_PUBKEY_GET_PRIVATE (self);
  self->priv = priv;

  priv->key_sexp = NULL;

  self->priv->type = EVD_PKI_KEY_TYPE_UNKNOWN;
}

static void
evd_pki_pubkey_dispose (GObject *obj)
{
  G_OBJECT_CLASS (evd_pki_pubkey_parent_class)->dispose (obj);
}

static void
evd_pki_pubkey_finalize (GObject *obj)
{
  EvdPkiPubkey *self = EVD_PKI_PUBKEY (obj);

  if (self->priv->key_sexp != NULL)
    gcry_sexp_release (self->priv->key_sexp);

  G_OBJECT_CLASS (evd_pki_pubkey_parent_class)->finalize (obj);
}

static void
evd_pki_pubkey_get_property (GObject    *obj,
                             guint       prop_id,
                             GValue     *value,
                             GParamSpec *pspec)
{
  EvdPkiPubkey *self;

  self = EVD_PKI_PUBKEY (obj);

  switch (prop_id)
    {
    case PROP_TYPE:
      g_value_set_uint (value, self->priv->type);
      break;

    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (obj, prop_id, pspec);
      break;
    }
}

static void
free_gstring_wisely (gpointer data)
{
  GString *st = data;

  g_string_free (st, st->str != NULL);
}

static void
encrypt_in_thread (GSimpleAsyncResult *res,
                   GObject            *object,
                   GCancellable       *cancellable)
{
  EvdPkiPubkey *self = EVD_PKI_PUBKEY (object);;
  gcry_sexp_t data_sexp;
  gcry_sexp_t ciph_sexp;
  gcry_sexp_t token_sexp;
  gcry_error_t err;
  GError *error = NULL;
  const gchar *data;
  GString *result;
  gsize len;

  data_sexp = g_simple_async_result_get_op_res_gpointer (res);

  /* encrypt */
  err = gcry_pk_encrypt (&ciph_sexp, data_sexp, self->priv->key_sexp);
  if (err != GPG_ERR_NO_ERROR)
    {
      evd_error_build_gcrypt (err, &error);
      g_simple_async_result_set_from_error (res, error);
      g_error_free (error);
      goto out;
    }

  /* extract data */
  token_sexp = gcry_sexp_find_token (ciph_sexp, "a", 0);
  data = gcry_sexp_nth_data (token_sexp, 1, &len);
  result = g_string_new_len (data, len);
  gcry_sexp_release (ciph_sexp);
  gcry_sexp_release (token_sexp);

  g_simple_async_result_set_op_res_gpointer (res, result, free_gstring_wisely);

 out:
  g_object_unref (res);
}

/* public methods */

EvdPkiPubkey *
evd_pki_pubkey_new (void)
{
  return g_object_new (EVD_TYPE_PKI_PUBKEY, NULL);
}

EvdPkiKeyType
evd_pki_pubkey_get_key_type (EvdPkiPubkey *self)
{
  g_return_val_if_fail (EVD_IS_PKI_PUBKEY (self), -1);

  return self->priv->type;
}

gboolean
evd_pki_pubkey_import_native (EvdPkiPubkey  *self,
                              gpointer       pubkey_st,
                              GError       **error)
{
  gcry_sexp_t algo_sexp;
  gchar *algo_st;
  gboolean result = TRUE;

  g_return_val_if_fail (EVD_IS_PKI_PUBKEY (self), FALSE);
  g_return_val_if_fail (pubkey_st != NULL, FALSE);

  /* check if there are operations pending and return error if so */

  if (self->priv->key_sexp)
    {
      gcry_sexp_release (self->priv->key_sexp);
      self->priv->type = EVD_PKI_KEY_TYPE_UNKNOWN;
    }

  self->priv->key_sexp = (gcry_sexp_t) pubkey_st;

  /* detect key algorithm */
  algo_sexp = gcry_sexp_nth (self->priv->key_sexp, 1);
  algo_st = gcry_sexp_nth_string (algo_sexp, 0);
  gcry_sexp_release (algo_sexp);

  if (g_strcmp0 (algo_st, "rsa") == 0)
    self->priv->type = EVD_PKI_KEY_TYPE_RSA;
  else if (g_strcmp0 (algo_st, "dsa") == 0)
    self->priv->type = EVD_PKI_KEY_TYPE_DSA;
  else
    {
      g_set_error_literal (error,
                           G_IO_ERROR,
                           G_IO_ERROR_NOT_SUPPORTED,
                           "Key algorithm not supported");
      self->priv->key_sexp = NULL;
      result = FALSE;
    }

  gcry_free (algo_st);

  return result;
}

void
evd_pki_pubkey_encrypt (EvdPkiPubkey        *self,
                        const gchar         *data,
                        gsize                size,
                        GCancellable        *cancellable,
                        GAsyncReadyCallback  callback,
                        gpointer             user_data)
{
  gcry_sexp_t data_sexp;
  GSimpleAsyncResult *res;
  gcry_error_t err;

  g_return_if_fail (EVD_IS_PKI_PUBKEY (self));

  res = g_simple_async_result_new (G_OBJECT (self),
                                   callback,
                                   user_data,
                                   evd_pki_pubkey_decrypt);

  /* pack message into an S-expression */
  err = gcry_sexp_build (&data_sexp,
                         0,
                         "%b",
                         size,
                         data);
  if (err != GPG_ERR_NO_ERROR)
    {
      GError *error = NULL;

      evd_error_build_gcrypt (err, &error);

      g_simple_async_result_set_from_error (res, error);
      g_error_free (error);

      g_simple_async_result_complete_in_idle (res);
      g_object_unref (res);
    }
  else
    {
      g_simple_async_result_set_op_res_gpointer (res,
                                                 data_sexp,
                                                 (GDestroyNotify) gcry_sexp_release);

      /* @TODO: use a thread pool to avoid overhead */
      g_simple_async_result_run_in_thread (res,
                                           encrypt_in_thread,
                                           G_PRIORITY_DEFAULT,
                                           cancellable);
    }
}

gchar *
evd_pki_pubkey_encrypt_finish (EvdPkiPubkey  *self,
                               GAsyncResult  *result,
                               gsize         *size,
                               GError       **error)
{
  GSimpleAsyncResult *res = G_SIMPLE_ASYNC_RESULT (result);

  g_return_val_if_fail (EVD_IS_PKI_PUBKEY (self), NULL);
  g_return_val_if_fail (g_simple_async_result_is_valid (result,
                                                        G_OBJECT (self),
                                                        evd_pki_pubkey_decrypt),
                        NULL);

  if (! g_simple_async_result_propagate_error (res, error))
    {
      GString *data;
      gchar *ret;

      data = g_simple_async_result_get_op_res_gpointer (res);
      ret = data->str;
      data->str = NULL;

      if (size != NULL)
        *size = data->len;

      return ret;
    }
  else
    return NULL;
}

void
evd_pki_pubkey_decrypt (EvdPkiPubkey        *self,
                        const gchar         *data,
                        gsize                size,
                        GCancellable        *cancellable,
                        GAsyncReadyCallback  callback,
                        gpointer             user_data)
{
  evd_pki_pubkey_encrypt (self, data, size, cancellable, callback, user_data);
}

gchar *
evd_pki_pubkey_decrypt_finish (EvdPkiPubkey  *self,
                               GAsyncResult  *result,
                               gsize         *size,
                               GError       **error)
{
  return evd_pki_pubkey_encrypt_finish (self, result, size, error);
}
