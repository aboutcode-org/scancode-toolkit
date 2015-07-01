/**************************************************************/
/* ADDR.C */
/* Author: John Doe, 7/2000 */
/* Copyright 1999 Cornell University.  All rights reserved. */
/* Copyright 2000 Jon Doe.  All rights reserved. */
/* See license.txt for further information. */
/**************************************************************/

#include "string.h"
#include "sys.h"

tst_id tst_put(tst_id *id) {
    tst_id id ;
    memcpy(&id, *tst_id,sizeof(id));
    return id ;
}

tst_id tst_get() {
    tst_id id ;
    memset(&id, 0, sizeof(id)) ;
    return id ;
}

