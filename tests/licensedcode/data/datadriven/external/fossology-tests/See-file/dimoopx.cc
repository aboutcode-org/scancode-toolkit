/*
 *
 *  Copyright (C) 1996-2010, OFFIS e.V.
 *  All rights reserved.  See COPYRIGHT file for details.
 *
 *  This software and supporting documentation were developed by
 *
 *    OFFIS e.V.
 *    R&D Division Health
 *    Escherweg 2
 *    D-26121 Oldenburg, Germany
 *
 *
 *  Module:  dcmimgle
 *
 *  Author:  Joerg Riesmeier
 *
 *  Purpose: DicomMonoOutputPixel (Source)
 *
 *  Last Update:      $Author: joergr $
 *  Update Date:      $Date: 2010-10-14 13:14:18 $
 *  CVS/RCS Revision: $Revision: 1.9 $
 *  Status:           $State: Exp $
 *
 *  CVS/RCS Log at end of file
 *
 */


#include "dcmtk/config/osconfig.h"

#include "dcmtk/dcmimgle/dimoopx.h"
#include "dcmtk/dcmimgle/dimopx.h"


/*----------------*
 *  constructors  *
 *----------------*/

DiMonoOutputPixel::DiMonoOutputPixel(const DiMonoPixel *pixel,
                                     const unsigned long size,
                                     const unsigned long frame,
                                     const unsigned long max)
  : Count(0),
    FrameSize(size),
    UsedValues(NULL),
    MaxValue(max)
{
    if (pixel != NULL)
    {
        if (pixel->getCount() > frame * size)
            Count = pixel->getCount() - frame * size;       // number of pixels remaining for this 'frame'
    }
    if (Count > FrameSize)
        Count = FrameSize;                                  // cut off at frame 'size'
}


/*--------------*
 *  destructor  *
 *--------------*/

DiMonoOutputPixel::~DiMonoOutputPixel()
{
    delete[] UsedValues;
}


/**********************************/


int DiMonoOutputPixel::isUnused(const unsigned long value)
{
    if (UsedValues == NULL)
        determineUsedValues();                  // create on demand
    if (UsedValues != NULL)
    {
        if (value <= MaxValue)
            return OFstatic_cast(int, UsedValues[value] == 0);
        return 2;                               // out of range
    }
    return 0;
}


/*
 *
 * CVS/RCS Log:
 * $Log: dimoopx.cc,v $
 * Revision 1.9  2010-10-14 13:14:18  joergr
 * Updated copyright header. Added reference to COPYRIGHT file.
 *
 * Revision 1.8  2005/12/08 15:43:01  meichel
 * Changed include path schema for all DCMTK header files
 *
 * Revision 1.7  2003/12/08 14:55:04  joergr
 * Adapted type casts to new-style typecast operators defined in ofcast.h.
 *
 * Revision 1.6  2001/06/01 15:49:58  meichel
 * Updated copyright header
 *
 * Revision 1.5  2000/03/08 16:24:31  meichel
 * Updated copyright header.
 *
 * Revision 1.4  1999/07/23 13:45:39  joergr
 * Enhanced handling of corrupted pixel data (wrong length).
 *
 * Revision 1.3  1999/02/11 16:53:35  joergr
 * Added routine to check whether particular grayscale values are unused in
 * the output data.
 * Removed unused parameter / member variable.
 *
 * Revision 1.2  1999/01/20 14:54:30  joergr
 * Replaced invocation of getCount() by member variable Count where possible.
 *
 * Revision 1.1  1998/11/27 16:15:02  joergr
 * Added copyright message.
 *
 * Revision 1.3  1998/05/11 14:52:33  joergr
 * Added CVS/RCS header to each file.
 *
 *
 */
