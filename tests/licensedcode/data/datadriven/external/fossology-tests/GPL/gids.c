/*****************************************************************************
 *  $Id: gids.c 913 2011-02-09 21:15:12Z chris.m.dunlap $
 *****************************************************************************
 *  Written by Chris Dunlap <cdunlap@llnl.gov>.
 *  Copyright (C) 2007-2011 Lawrence Livermore National Security, LLC.
 *  Copyright (C) 2002-2007 The Regents of the University of California.
 *  UCRL-CODE-155910.
 *
 *  This file is part of the MUNGE Uid 'N' Gid Emporium (MUNGE).
 *  For details, see <http://munge.googlecode.com/>.
 *
 *  MUNGE is free software: you can redistribute it and/or modify it under
 *  the terms of the GNU General Public License as published by the Free
 *  Software Foundation, either version 3 of the License, or (at your option)
 *  any later version.  Additionally for the MUNGE library (libmunge), you
 *  can redistribute it and/or modify it under the terms of the GNU Lesser
 *  General Public License as published by the Free Software Foundation,
 *  either version 3 of the License, or (at your option) any later version.
 *
 *  MUNGE is distributed in the hope that it will be useful, but WITHOUT
 *  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 *  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 *  and GNU Lesser General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  and GNU Lesser General Public License along with MUNGE.  If not, see
 *  <http://www.gnu.org/licenses/>.
 *****************************************************************************
 *  Refer to "gids.h" for documentation on public functions.
 *****************************************************************************/


#if HAVE_CONFIG_H
#  include "config.h"
#endif /* HAVE_CONFIG_H */

#include <sys/types.h>                  /* include before grp.h for bsd */
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <munge.h>
#include "gids.h"
#include "hash.h"
#include "log.h"
#include "munge_defs.h"
#include "timer.h"
#include "xgetgrent.h"
#include "xgetpwnam.h"


/*****************************************************************************
 *  Notes
 *****************************************************************************/
/*
 *  The gids hash contains a gids_head pointing to a singly-linked list of
 *    gids_nodes for each UID with supplementary groups.  The GIDs in each
 *    list of gids_nodes are sorted in increasing order without duplicates.
 *
 *  The use of non-reentrant passwd/group functions (ie, getpwnam & getgrent)
 *    should be ok here since they are only called in/from _gids_hash_create(),
 *    and only one instance of that routine can be running at a time within
 *    munged.  However, crashes have been traced to the use of getgrent() here
 *    (cf, <http://code.google.com/p/munge/issues/detail?id=2>) so the
 *    reentrant functions are now used.
 */


/*****************************************************************************
 *  Constants
 *****************************************************************************/

#ifndef _GIDS_DEBUG
#define _GIDS_DEBUG 0
#endif /* !_GIDS_DEBUG */


/*****************************************************************************
 *  Data Types
 *****************************************************************************/

struct gids {
    pthread_mutex_t     mutex;          /* mutex for accessing struct        */
    hash_t              hash;           /* hash of GIDs mappings             */
    int                 timer;          /* timer ID for next GIDs map update */
    int                 interval;       /* seconds between GIDs map updates  */
    int                 do_group_stat;  /* true if updates stat group file   */
    time_t              t_last_update;  /* time of last good GIDs map update */
};

struct gids_node {
    struct gids_node   *next;
    gid_t               gid;
};

struct gids_head {
    struct gids_node   *next;
    uid_t               uid;
};

struct gids_uid {
    char               *user;
    uid_t               uid;
};

typedef struct gids_node * gids_node_t;
typedef struct gids_head * gids_gid_t;
typedef struct gids_uid  * gids_uid_t;


/*****************************************************************************
 *  Prototypes
 *****************************************************************************/

static void         _gids_update (gids_t gids);
static hash_t       _gids_hash_create (void);
static int          _gids_user_to_uid (hash_t uid_hash,
                        char *user, uid_t *uid_p, char *buf, size_t buflen);
static int          _gids_hash_add (hash_t hash, uid_t uid, gid_t gid);
static gids_gid_t   _gids_head_alloc (uid_t uid);
static void         _gids_head_del (gids_gid_t g);
static gids_node_t  _gids_node_alloc (gid_t gid);
static int          _gids_node_cmp (uid_t *uid1_p, uid_t *uid2_p);
static unsigned int _gids_node_key (uid_t *uid_p);
static gids_uid_t   _gids_uid_alloc (char *user, uid_t uid);
static int          _gids_uid_cmp (char *user1, char *user2);
static void         _gids_uid_del (gids_uid_t u);

#if _GIDS_DEBUG
static void _gids_dump_gid_hash (hash_t gid_hash);
static void _gids_dump_gid_node (gids_gid_t g, uid_t *uid_p, void *null);
static void _gids_dump_uid_hash (hash_t uid_hash);
static void _gids_dump_uid_node (gids_uid_t u, char *user, void *null);
#endif /* _GIDS_DEBUG */


/*****************************************************************************
 *  Public Functions
 *****************************************************************************/

gids_t
gids_create (int interval, int do_group_stat)
{
    gids_t gids;

    /*  If the GIDs update interval is negative, disable the GIDs mapping.
     */
    if (interval < 0) {
        log_msg (LOG_INFO, "Disabled supplementary group mapping");
        return (NULL);
    }
    if (!(gids = malloc (sizeof (*gids)))) {
        log_errno (EMUNGE_NO_MEMORY, LOG_ERR,
            "Unable to allocate gids struct");
    }
    if ((errno = pthread_mutex_init (&gids->mutex, NULL)) != 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to init gids mutex");
    }
    gids->hash = NULL;
    gids->timer = 0;
    gids->interval = interval;
    gids->do_group_stat = do_group_stat;
    gids->t_last_update = 0;
    gids_update (gids);

    if (interval == 0) {
        log_msg (LOG_INFO, "Disabled updates to supplementary group mapping");
    }
    else {
        log_msg (LOG_INFO,
            "Updating supplementary group mapping every %d second%s",
            interval, (interval == 1) ? "" : "s");
    }
    log_msg (LOG_INFO, "%s supplementary group mtime check of \"%s\"",
        (do_group_stat ? "Enabled" : "Disabled"), GIDS_GROUP_FILE);

    return (gids);
}


void
gids_destroy (gids_t gids)
{
    hash_t h;

    if (!gids) {
        return;
    }
    if ((errno = pthread_mutex_lock (&gids->mutex)) != 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to lock gids mutex");
    }
    if (gids->timer > 0) {
        timer_cancel (gids->timer);
        gids->timer = 0;
    }
    h = gids->hash;
    gids->hash = NULL;

    if ((errno = pthread_mutex_unlock (&gids->mutex)) != 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to unlock gids mutex");
    }
    hash_destroy (h);

    if ((errno = pthread_mutex_destroy (&gids->mutex)) != 0) {
        log_msg (LOG_ERR, "Unable to destroy gids mutex: %s",
            strerror (errno));
    }
    free (gids);
    return;
}


void
gids_update (gids_t gids)
{
    if (!gids) {
        return;
    }
    if ((errno = pthread_mutex_lock (&gids->mutex)) != 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to lock gids mutex");
    }
    /*  Cancel a pending update before scheduling a new one.
     */
    if (gids->timer > 0) {
        timer_cancel (gids->timer);
    }
    /*  Compute the GIDs mapping in the background by setting an expired timer.
     */
    gids->timer = timer_set_relative ((callback_f) _gids_update, gids, 0);
    if (gids->timer < 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to set gids update timer");
    }
    /*  Reset the do_group_stat flag in case it had been disabled on error
     *    (ie, set to -1).
     */
    gids->do_group_stat = !! gids->do_group_stat;

    if ((errno = pthread_mutex_unlock (&gids->mutex)) != 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to unlock gids mutex");
    }
    return;
}


int
gids_is_member (gids_t gids, uid_t uid, gid_t gid)
{
    int         is_member = 0;
    gids_gid_t  g;
    gids_node_t node;

    if (!gids) {
        return (0);
    }
    if ((errno = pthread_mutex_lock (&gids->mutex)) != 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to lock gids mutex");
    }
    if ((gids->hash) && (g = hash_find (gids->hash, &uid))) {
        assert (g->uid == uid);
        for (node = g->next; node && node->gid <= gid; node = node->next) {
            if (node->gid == gid) {
                is_member = 1;
                break;
            }
        }
    }
    if ((errno = pthread_mutex_unlock (&gids->mutex)) != 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to unlock gids mutex");
    }
    return (is_member);
}


/*****************************************************************************
 *  Private Functions
 *****************************************************************************/

static void
_gids_update (gids_t gids)
{
/*  Updates the GIDs mapping [gids] if needed.
 */
    int             do_group_stat;
    time_t          t_last_update;
    time_t          t_now;
    int             do_update = 1;
    hash_t          hash = NULL;

    assert (gids != NULL);

    if ((errno = pthread_mutex_lock (&gids->mutex)) != 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to lock gids mutex");
    }
    do_group_stat = gids->do_group_stat;
    t_last_update = gids->t_last_update;

    if ((errno = pthread_mutex_unlock (&gids->mutex)) != 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to unlock gids mutex");
    }
    if (time (&t_now) == (time_t) -1) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to query current time");
    }
    if (do_group_stat > 0) {

        struct stat  st;

        /*  On stat() error, disable future stat()s until reset via SIGHUP.
         */
        if (stat (GIDS_GROUP_FILE, &st) < 0) {
            do_group_stat = -2;
            log_msg (LOG_ERR, "Unable to stat \"%s\": %s",
                GIDS_GROUP_FILE, strerror (errno));
        }
        else if (st.st_mtime <= t_last_update) {
            do_update = 0;
        }
    }
    /*  Update the GIDs mapping.
     */
    if (do_update) {
        hash = _gids_hash_create ();
    }
    if ((errno = pthread_mutex_lock (&gids->mutex)) != 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to lock gids mutex");
    }
    /*  Replace the old GIDs mapping if the update was successful.
     */
    if (hash) {

        hash_t hash_bak = gids->hash;
        gids->hash = hash;
        hash = hash_bak;

        gids->t_last_update = t_now;
    }
    /*  Change the GIDs do_group_stat flag only when the stat() first fails.
     *    This is done by setting the local flag to -2 on error, but storing -1
     *    in the GIDs struct when the mutex is next acquired.  By doing this, a
     *    SIGHUP triggered during _gids_hash_update() can still reset the flag.
     */
    if (do_group_stat < -1) {
        gids->do_group_stat = -1;
    }
    /*  Enable subsequent updating of the GIDs mapping only if the update
     *    interval is positive.
     */
    gids->timer = 0;
    if (gids->interval > 0) {
        gids->timer = timer_set_relative (
                (callback_f) _gids_update, gids, gids->interval * 1000);
        if (gids->timer < 0) {
            log_errno (EMUNGE_SNAFU, LOG_ERR,
                "Unable to reset gids update timer");
        }
    }
    if ((errno = pthread_mutex_unlock (&gids->mutex)) != 0) {
        log_errno (EMUNGE_SNAFU, LOG_ERR, "Unable to unlock gids mutex");
    }
    /*  Clean up.
     */
    if (hash) {
        hash_destroy (hash);
    }
    return;
}


static hash_t
_gids_hash_create (void)
{
/*  Returns a new hash containing the new GIDs mapping, or NULL on error.
 */
    hash_t          gid_hash = NULL;
    hash_t          uid_hash = NULL;
    struct timeval  t_start;
    struct timeval  t_stop;
    int             do_group_db_close = 0;
    struct group    gr;
    char           *gr_buf_ptr = NULL;
    int             gr_buf_len;
    char           *pw_buf_ptr = NULL;
    int             pw_buf_len;
    char          **user_p;
    uid_t           uid;
    int             n_users;
    double          n_seconds;

    gid_hash = hash_create (GIDS_HASH_SIZE, (hash_key_f) _gids_node_key,
            (hash_cmp_f) _gids_node_cmp, (hash_del_f) _gids_head_del);

    if (!gid_hash) {
        log_msg (LOG_ERR, "Unable to allocate gids hash -- out of memory");
        goto err;
    }
    uid_hash = hash_create (UIDS_HASH_SIZE, (hash_key_f) hash_key_string,
            (hash_cmp_f) _gids_uid_cmp, (hash_del_f) _gids_uid_del);

    if (!uid_hash) {
        log_msg (LOG_ERR, "Unable to allocate uids hash -- out of memory");
        goto err;
    }
    if (gettimeofday (&t_start, NULL) < 0) {
        log_msg (LOG_ERR, "Unable to query current time");
        goto err;
    }
    /*  Allocate memory for both the xgetgrent() and xgetpwnam() buffers here.
     *    The xgetpwnam() buffer will be passed to _gids_user_to_uid() where it
     *    is used, but allocating it here allows the same buffer to be reused
     *    throughout a given GIDs creation cycle.
     */
    if (xgetgrent_buf_create (&gr_buf_ptr, &gr_buf_len) < 0) {
        log_msg (LOG_ERR, "Unable to allocate group entry buffer");
        goto err;
    }
    if (xgetpwnam_buf_create (&pw_buf_ptr, &pw_buf_len) < 0) {
        log_msg (LOG_ERR, "Unable to allocate password entry buffer");
        goto err;
    }
    xgetgrent_init ();
    do_group_db_close = 1;

    while (1) {
        if (xgetgrent (&gr, gr_buf_ptr, gr_buf_len) < 0) {
            if (errno == ENOENT)
                break;
            if (errno == EINTR)
                continue;
            log_msg (LOG_ERR, "Unable to query group info: %s",
                    strerror (errno));
            goto err;
        }
        /*  gr_mem is a null-terminated array of pointers to the user names
         *    belonging to the group.
         */
        for (user_p = gr.gr_mem; user_p && *user_p; user_p++) {
            int rv = _gids_user_to_uid (uid_hash, *user_p, &uid,
                    pw_buf_ptr, pw_buf_len);
            if (rv == 0) {
                if (_gids_hash_add (gid_hash, uid, gr.gr_gid) < 0) {
                    goto err;
                }
            }
        }
    }
    xgetgrent_fini ();
    xgetgrent_buf_destroy (gr_buf_ptr);

    if (gettimeofday (&t_stop, NULL) < 0) {
        log_msg (LOG_ERR, "Unable to query current time");
        goto err;
    }

#if _GIDS_DEBUG
    _gids_dump_uid_hash (uid_hash);
    _gids_dump_gid_hash (gid_hash);
#endif /* _GIDS_DEBUG */

    n_users = hash_count (gid_hash);
    n_seconds = (t_stop.tv_sec - t_start.tv_sec)
        + ((t_stop.tv_usec - t_start.tv_usec) / 1e6);
    log_msg (LOG_INFO,
        "Found %d user%s with supplementary groups in %0.3f seconds",
        n_users, ((n_users == 1) ? "" : "s"), n_seconds);

    hash_destroy (uid_hash);
    return (gid_hash);

err:
    if (do_group_db_close) {
        xgetgrent_fini ();
    }
    if (pw_buf_ptr != NULL) {
        xgetpwnam_buf_destroy (pw_buf_ptr);
    }
    if (gr_buf_ptr != NULL) {
        xgetgrent_buf_destroy (gr_buf_ptr);
    }
    if (uid_hash != NULL) {
        hash_destroy (uid_hash);
    }
    if (gid_hash != NULL) {
        hash_destroy (gid_hash);
    }
    return (NULL);
}


static int
_gids_user_to_uid (hash_t uid_hash, char *user, uid_t *uid_p,
                   char *buf, size_t buflen)
{
/*  Returns 0 on success, setting [*uid_p] (if non-NULL) to the UID associated
 *    with [user]; o/w, returns -1.
 */
    gids_uid_t     u;
    uid_t          uid;
    struct passwd  pw;

    if ((u = hash_find (uid_hash, user))) {
        uid = u->uid;
    }
    else if (xgetpwnam (user, &pw, buf, buflen) == 0) {
        uid = pw.pw_uid;
        if (!(u = _gids_uid_alloc (user, uid))) {
            log_msg (LOG_WARNING,
                "Unable to allocate uid node for %s/%d -- out of memory",
                user, uid);
        }
        else if (!hash_insert (uid_hash, u->user, u)) {
            log_msg (LOG_WARNING,
                "Unable to insert uid node for %s/%d into hash", user, uid);
            _gids_uid_del (u);
        }
    }
    else {
        log_msg (LOG_INFO,
            "Unable to query password file entry for \"%s\"", user);
        return (-1);
    }

    if (uid_p != NULL) {
        *uid_p = uid;
    }
    return (0);
}


static int
_gids_hash_add (hash_t hash, uid_t uid, gid_t gid)
{
/*  Adds supplementary group [gid] for user [uid] to the GIDs mapping [gids].
 *  Returns 1 if the entry was added, 0 if the entry already exists,
 *    or -1 on error.
 */
    gids_gid_t   g;
    gids_node_t  node;
    gids_node_t *node_p;

    if (!(g = hash_find (hash, &uid))) {
        if (!(g = _gids_head_alloc (uid))) {
            log_msg (LOG_ERR, "Unable to allocate gids node -- out of memory");
            return (-1);
        }
        if (!hash_insert (hash, &g->uid, g)) {
            log_msg (LOG_ERR, "Unable to insert gids node into hash");
            _gids_head_del (g);
            return (-1);
        }
    }
    assert (g->uid == uid);

    node_p = &g->next;
    while ((*node_p) && ((*node_p)->gid < gid)) {
        node_p = &(*node_p)->next;
    }
    if ((*node_p) && ((*node_p)->gid == gid)) {
        return (0);
    }
    if (!(node = _gids_node_alloc (gid))) {
        log_msg (LOG_ERR, "Unable to allocate gids node -- out of memory");
        return (-1);
    }
    node->next = *node_p;
    *node_p = node;
    return (1);
}


static gids_gid_t
_gids_head_alloc (uid_t uid)
{
/*  Returns an allocated GIDs head for [uid], or NULL on error.
 */
    gids_gid_t g;

    if (!(g = malloc (sizeof (*g)))) {
        return (NULL);
    }
    g->next = NULL;
    g->uid = uid;
    return (g);
}


static void
_gids_head_del (gids_gid_t g)
{
/*  De-allocates the GIDs head [g] and node chain.
 */
    gids_node_t node, node_tmp;

    if (!g) {
        return;
    }
    node = g->next;
    free (g);
    while (node) {
        node_tmp = node;
        node = node->next;
        free (node_tmp);
    }
    return;
}


static gids_node_t
_gids_node_alloc (gid_t gid)
{
/*  Returns an allocated GIDs node for [gid], or NULL on error.
 */
    gids_node_t node;

    if (!(node = malloc (sizeof (*node)))) {
        return (NULL);
    }
    node->next = NULL;
    node->gid = gid;
    return (node);
}


static int
_gids_node_cmp (uid_t *uid1_p, uid_t *uid2_p)
{
/*  Used by the hash routines to compare hash keys [uid1_p] and [uid2_p].
 */
    return (!(*uid1_p == *uid2_p));
}


static unsigned int
_gids_node_key (uid_t *uid_p)
{
/*  Used by the hash routines to convert [uid_p] into a hash key.
 */
    return (*uid_p);
}


static gids_uid_t
_gids_uid_alloc (char *user, uid_t uid)
{
/*  Returns an allocated UID node mapping [user] to [uid], or NULL on error.
 */
    gids_uid_t u;

    if ((user == NULL) || (*user == '\0')) {
        return (NULL);
    }
    if (!(u = malloc (sizeof (*u)))) {
        return (NULL);
    }
    if (!(u->user = strdup (user))) {
        free (u);
        return (NULL);
    }
    u->uid = uid;
    return (u);
}


static int
_gids_uid_cmp (char *user1, char *user2)
{
/*  Used by the hash routines to compare UID node hash keys
 *    [user1] and [user2].
 */
    return (strcmp (user1, user2));
}


static void
_gids_uid_del (gids_uid_t u)
{
/*  De-allocates the UID node [u].
 */
    if (!u) {
        return;
    }
    if (u->user) {
        free (u->user);
    }
    free (u);
    return;
}


/*****************************************************************************
 *  Debug Functions
 *****************************************************************************/

#if _GIDS_DEBUG

static void
_gids_dump_gid_hash (hash_t gid_hash)
{
    int n;

    n = hash_count (gid_hash);
    printf ("* GIDs Dump (%d UID%s):\n", n, ((n == 1) ? "" : "s"));
    hash_for_each (gid_hash, (hash_arg_f) _gids_dump_gid_node, NULL);
    return;
}


static void
_gids_dump_gid_node (gids_gid_t g, uid_t *uid_p, void *null)
{
    gids_node_t node;

    assert (g->uid == *uid_p);

    printf (" %5d:", g->uid);
    for (node = g->next; node; node = node->next) {
        printf (" %d", node->gid);
    }
    printf ("\n");
    return;
}


static void
_gids_dump_uid_hash (hash_t uid_hash)
{
    int n;

    n = hash_count (uid_hash);
    printf ("* UID Dump (%d user%s):\n", n, ((n == 1) ? "" : "s"));
    hash_for_each (uid_hash, (hash_arg_f) _gids_dump_uid_node, NULL);
    return;
}


static void
_gids_dump_uid_node (gids_uid_t u, char *user, void *null)
{
    assert (u->user == user);

    printf (" %5d: %s\n", u->uid, u->user);
    return;
}

#endif /* _GIDS_DEBUG */
