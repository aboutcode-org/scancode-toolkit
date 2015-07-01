XMLPUBFUN int XMLCALL

        xmlCheckFilename                (const char *path);

/**

 * Default 'file://' protocol callbacks

 */

XMLPUBFUN int XMLCALL

        xmlFileMatch                    (const char *filename);

XMLPUBFUN void * XMLCALL

        xmlFileOpen                     (const char *filename);

XMLPUBFUN int XMLCALL

        xmlFileRead                     (void * context,

                                         char * buffer,

                                         int len);

XMLPUBFUN int XMLCALL

        xmlFileClose                    (void * context);

/**

 * Default 'http://' protocol callbacks

 */

#ifdef LIBXML_HTTP_ENABLED

XMLPUBFUN int XMLCALL

        xmlIOHTTPMatch                  (const char *filename);

XMLPUBFUN void * XMLCALL

        xmlIOHTTPOpen                   (const char *filename);

#ifdef LIBXML_OUTPUT_ENABLED

XMLPUBFUN void * XMLCALL

        xmlIOHTTPOpenW                  (const char * post_uri,

                                         int   compression );

#endif /* LIBXML_OUTPUT_ENABLED */

XMLPUBFUN int XMLCALL

        xmlIOHTTPRead                   (void * context,

                                         char * buffer,

                                         int len);

XMLPUBFUN int XMLCALL

        xmlIOHTTPClose                  (void * context);

#endif /* LIBXML_HTTP_ENABLED */

/**

 * Default 'ftp://' protocol callbacks

 */

#ifdef LIBXML_FTP_ENABLED

XMLPUBFUN int XMLCALL

        xmlIOFTPMatch                   (const char *filename);

XMLPUBFUN void * XMLCALL

        xmlIOFTPOpen                    (const char *filename);

XMLPUBFUN int XMLCALL

        xmlIOFTPRead                    (void * context,

                                         char * buffer,

                                         int len);

XMLPUBFUN int XMLCALL

        xmlIOFTPClose                   (void * context);

#endif /* LIBXML_FTP_ENABLED */

#ifdef __cplusplus

}

#endif
