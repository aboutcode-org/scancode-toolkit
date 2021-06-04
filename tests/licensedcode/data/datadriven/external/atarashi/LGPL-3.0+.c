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
