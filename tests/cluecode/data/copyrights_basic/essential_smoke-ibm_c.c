/**************************************************************
from ticket 141
Something like


Copyright IBM and others (c) 2008

Copyright Eclipse, IBM and others (c) 2008

might still need to be reported on an IBM project as it would not be exclusively an IBM copyright.
When there are several copyright statements in the code, only the one that is about the company should be excluded.
Some other issues include the variety of things: For instance we can find copyrights such as:


**************************************************************/

#include "string.h"
#include "sys.h"

tst_id tst_put(tst_id *id) {
    tst_id id ;
    memcpy(&id, *tst_id,sizeof(id));
    return id ;
}
