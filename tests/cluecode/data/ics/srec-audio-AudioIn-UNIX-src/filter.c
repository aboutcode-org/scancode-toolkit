/*---------------------------------------------------------------------------*
 *  filter.c  *
 *                                                                           *
 *  Copyright 2007, 2008 Nuance Communciations, Inc.                               *
 *                                                                           *
 *  Licensed under the Apache License, Version 2.0 (the 'License');          *
 *          Since nInput == 1, state for newest sample is still 2
 *          (otherwise, update state -= nInput-1; wrap by adding nTaps if < 0)
 *
 *      (c) Accumulate "end part" first
 *
 *           z: start with latest sample at z[pFIR->state], then advance to right
    if (pFIR->state < 0)
       pFIR->state += pFIR->nTaps;  // wrap

    // (c) Accumulate "end part"
    pz = pFIR->z + pFIR->state;
    nTaps_end = pFIR->nTaps - pFIR->state;