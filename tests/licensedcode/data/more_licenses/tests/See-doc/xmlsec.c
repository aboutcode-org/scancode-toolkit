/**
 * XML Security Library (http://www.aleksey.com/xmlsec).
 *
 * General functions.
 *
 * This is free software; see Copyright file in the source
 * distribution for preciese wording.
 *
 * Copyright (C) 2002-2003 Aleksey Sanin <aleksey@aleksey.com>
 */
#include "globals.h"

#include <stdlib.h>
#include <stdio.h>

#include <libxml/tree.h>

#include <xmlsec/xmlsec.h>
#include <xmlsec/xmltree.h>
#include <xmlsec/keys.h>
#include <xmlsec/transforms.h>
#include <xmlsec/app.h>
#include <xmlsec/io.h>
#include <xmlsec/xkms.h>
#include <xmlsec/errors.h>

/**
 * xmlSecInit:
 *
 * Initializes XML Security Library. The depended libraries
 * (LibXML and LibXSLT) must be initialized before.
 *
 * Returns: 0 on success or a negative value otherwise.
 */
int
xmlSecInit(void) {
    xmlSecErrorsInit();
    xmlSecIOInit();

#ifndef XMLSEC_NO_CRYPTO_DYNAMIC_LOADING
    if(xmlSecCryptoDLInit() < 0) {
        xmlSecError(XMLSEC_ERRORS_HERE,
                    NULL,
                    "xmlSecCryptoDLInit",
                    XMLSEC_ERRORS_R_XMLSEC_FAILED,
                    XMLSEC_ERRORS_NO_MESSAGE);
        return(-1);
    }
#endif /* XMLSEC_NO_CRYPTO_DYNAMIC_LOADING */

    if(xmlSecKeyDataIdsInit() < 0) {
        xmlSecError(XMLSEC_ERRORS_HERE,
                    NULL,
                    "xmlSecKeyDataIdsInit",
                    XMLSEC_ERRORS_R_XMLSEC_FAILED,
                    XMLSEC_ERRORS_NO_MESSAGE);
        return(-1);
    }

    if(xmlSecTransformIdsInit() < 0) {
        xmlSecError(XMLSEC_ERRORS_HERE,
                    NULL,
                    "xmlSecTransformIdsInit",
                    XMLSEC_ERRORS_R_XMLSEC_FAILED,
                    XMLSEC_ERRORS_NO_MESSAGE);
        return(-1);
    }

#ifndef XMLSEC_NO_XKMS
    if(xmlSecXkmsRespondWithIdsInit() < 0) {
        xmlSecError(XMLSEC_ERRORS_HERE,
                    NULL,
                    "xmlSecXkmsRespondWithIdsInit",
                    XMLSEC_ERRORS_R_XMLSEC_FAILED,
                    XMLSEC_ERRORS_NO_MESSAGE);
        return(-1);
    }
    if(xmlSecXkmsServerRequestIdsInit() < 0) {
        xmlSecError(XMLSEC_ERRORS_HERE,
                    NULL,
                    "xmlSecXkmsServerRequestIdsInit",
                    XMLSEC_ERRORS_R_XMLSEC_FAILED,
                    XMLSEC_ERRORS_NO_MESSAGE);
        return(-1);
    }
#endif /* XMLSEC_NO_XKMS */

    /* we use rand() function to generate id attributes */
    srand(time(NULL));
    return(0);
}

/**
 * xmlSecShutdown:
 *
 * Clean ups the XML Security Library.
 *
 * Returns: 0 on success or a negative value otherwise.
 */
int
xmlSecShutdown(void) {
    int res = 0;

#ifndef XMLSEC_NO_XKMS
    xmlSecXkmsServerRequestIdsShutdown();
    xmlSecXkmsRespondWithIdsShutdown();
#endif /* XMLSEC_NO_XKMS */

    xmlSecTransformIdsShutdown();
    xmlSecKeyDataIdsShutdown();

#ifndef XMLSEC_NO_CRYPTO_DYNAMIC_LOADING
    if(xmlSecCryptoDLShutdown() < 0) {
        xmlSecError(XMLSEC_ERRORS_HERE,
                    NULL,
                    "xmlSecCryptoDLShutdown",
                    XMLSEC_ERRORS_R_XMLSEC_FAILED,
                    XMLSEC_ERRORS_NO_MESSAGE);
        res = -1;
    }
#endif /* XMLSEC_NO_CRYPTO_DYNAMIC_LOADING */

    xmlSecIOShutdown();
    xmlSecErrorsShutdown();
    return(res);
}

/**
 * xmlSecCheckVersionExt:
 * @major:              the major version number.
 * @minor:              the minor version number.
 * @subminor:           the subminor version number.
 * @mode:               the version check mode.
 *
 * Checks if the loaded version of xmlsec library could be used.
 *
 * Returns: 1 if the loaded xmlsec library version is OK to use
 * 0 if it is not or a negative value if an error occurs.
 */
int
xmlSecCheckVersionExt(int major, int minor, int subminor, xmlSecCheckVersionMode mode) {
    /* we always want to have a match for major version number */
    if(major != XMLSEC_VERSION_MAJOR) {
        xmlSecError(XMLSEC_ERRORS_HERE,
                    NULL,
                    NULL,
                    XMLSEC_ERRORS_R_XMLSEC_FAILED,
                    "expected major version=%d;real major version=%d",
                    XMLSEC_VERSION_MAJOR, major);
        return(0);
    }

    switch(mode) {
    case xmlSecCheckVersionExactMatch:
        if((minor != XMLSEC_VERSION_MINOR) || (subminor != XMLSEC_VERSION_SUBMINOR)) {
            xmlSecError(XMLSEC_ERRORS_HERE,
                        NULL,
                        NULL,
                        XMLSEC_ERRORS_R_XMLSEC_FAILED,
                        "mode=exact;expected minor version=%d;real minor version=%d;expected subminor version=%d;real subminor version=%d",
                        XMLSEC_VERSION_MINOR, minor,
                        XMLSEC_VERSION_SUBMINOR, subminor);
            return(0);
        }
        break;
    case xmlSecCheckVersionABICompatible:
        if((minor < XMLSEC_VERSION_MINOR) ||
           ((minor == XMLSEC_VERSION_MINOR) &&
            (subminor < XMLSEC_VERSION_SUBMINOR))) {
            xmlSecError(XMLSEC_ERRORS_HERE,
                        NULL,
                        NULL,
                        XMLSEC_ERRORS_R_XMLSEC_FAILED,
                        "mode=abi compatible;expected minor version=%d;real minor version=%d;expected subminor version=%d;real subminor version=%d",
                        XMLSEC_VERSION_MINOR, minor,
                        XMLSEC_VERSION_SUBMINOR, subminor);
            return(0);
        }
        break;
    }

    return(1);
}


