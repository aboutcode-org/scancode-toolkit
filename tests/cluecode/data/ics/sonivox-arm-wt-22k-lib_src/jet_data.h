 * Contents and purpose:
 * Internal data structures and interfaces for JET
 *
 * Copyright (c) 2006 Sonic Network Inc.

 * Licensed under the Apache License, Version 2.0 (the "License");
#define JET_TAG(a,b,c,d) (\
    ( ((EAS_U32)(a) & 0xFF) << 24 ) \
    + ( ((EAS_U32)(b) & 0xFF) << 16 ) \
    + ( ((EAS_U32)(c) & 0xFF) <<  8 ) \
    + ( ((EAS_U32)(d) & 0xFF)))

#define JET_INFO_CHUNK JET_TAG('J','I','N','F')
#define JET_SMF_CHUNK JET_TAG('J','S','M','F')
#define JET_DLS_CHUNK JET_TAG('J','D','L','S')
#define INFO_JET_COPYRIGHT JET_TAG('J','C','O','P')
#define JET_APP_DATA_CHUNK JET_TAG('J','A','P','P')
