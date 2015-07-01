/**************************************************************
from ticket 141
Something like

might still need to be reported on an IBM project as it would not be exclusively an IBM copyright.

When there are several copyright statements in the code, only the one that is about the company should be excluded.

Some other issues include the variety of things: For instance we can find copyrights such as:

Copyright (c) ibm technologies  2008
Copyright (c) IBM Corporation 2008
Copyright (c) Ibm Corp. 2008
Copyright (c) ibm.com 2008
Copyright (c) IBM technology 2008
Copyright (c) IBM company 2008

**************************************************************/

#include "string.h"
#include "sys.h"

tst_id tst_put(tst_id *id) {
    tst_id id ;
    memcpy(&id, *tst_id,sizeof(id));
    return id ;
}
