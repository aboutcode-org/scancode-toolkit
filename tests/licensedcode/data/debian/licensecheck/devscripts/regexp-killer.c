/*
 * (c) 2013 Devscript Developers
 *
 * Initially seen in:
 *   freeswitch/libs/ldns/dnssec.c
 * the line starting with equals gets seen as potential comment fodder
 * but when the double-equals is put in the [] it breaks the regexp that is built
 */
if (foo
	    == bar
    ) {
		return baz;
	}

/* there are some other files where:

 :: people have made their comments start like this
 :: which bumps into the same issue.

*/
