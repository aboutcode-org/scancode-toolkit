/*-
 * Copyright (c) 2009, 2010, 2011
 *	Thorsten Glaser <tg@mirbsd.org>
 *
 * Provided that these terms and disclaimer and all copyright notices
 * are retained or reproduced in an accompanying document, permission
 * is granted to deal in this work without restriction, including un-
 * limited rights to use, publicly perform, distribute, sell, modify,
 * merge, give away, or sublicence.
 *
 * This work is provided "AS IS" and WITHOUT WARRANTY of any kind, to
 * the utmost extent permitted by applicable law, neither express nor
 * implied; without malicious intent or gross negligence. In no event
 * may a licensor, author or contributor be held liable for indirect,
 * direct, other damage, loss, or other issues arising in any way out
 * of dealing in the work, even if advised of the possibility of such
 * damage or existence of a defect, except proven that it results out
 * of said person's immediate fault when using the work as intended.
 */

#include "sh.h"

__RCSID("$MirOS: src/bin/mksh/lalloc.c,v 1.19 2011/09/07 15:24:16 tg Exp $");

/* build with CPPFLAGS+= -DUSE_REALLOC_MALLOC=0 on ancient systems */
#if defined(USE_REALLOC_MALLOC) && (USE_REALLOC_MALLOC == 0)
#define remalloc(p,n)	((p) == NULL ? malloc_osi(n) : realloc_osi((p), (n)))
#else
#define remalloc(p,n)	realloc_osi((p), (n))
#endif

#define ALLOC_ISUNALIGNED(p) (((ptrdiff_t)(p)) % ALLOC_SIZE)

static ALLOC_ITEM *findptr(ALLOC_ITEM **, char *, Area *);

void
ainit(Area *ap)
{
	/* area pointer is an ALLOC_ITEM, just the head of the list */
	ap->next = NULL;
}

static ALLOC_ITEM *
findptr(ALLOC_ITEM **lpp, char *ptr, Area *ap)
{
	void *lp;

#ifndef MKSH_SMALL
	if (ALLOC_ISUNALIGNED(ptr))
		goto fail;
#endif
	/* get address of ALLOC_ITEM from user item */
	/*
	 * note: the alignment of "ptr" to ALLOC_SIZE is checked
	 * above; the "void *" gets us rid of a gcc 2.95 warning
	 */
	*lpp = (lp = ptr - ALLOC_SIZE);
	/* search for allocation item in group list */
	while (ap->next != lp)
		if ((ap = ap->next) == NULL) {
#ifndef MKSH_SMALL
 fail:
#endif
#ifdef DEBUG
			internal_warningf("rogue pointer %zX in ap %zX",
			    (size_t)ptr, (size_t)ap);
			/* try to get a coredump */
			abort();
#else
			internal_errorf("rogue pointer %zX", (size_t)ptr);
#endif
		}
	return (ap);
}

void *
aresize2(void *ptr, size_t fac1, size_t fac2, Area *ap)
{
	if (notoktomul(fac1, fac2))
		internal_errorf(Tintovfl, fac1, '*', fac2);
	return (aresize(ptr, fac1 * fac2, ap));
}

void *
aresize(void *ptr, size_t numb, Area *ap)
{
	ALLOC_ITEM *lp = NULL;

	/* resizing (true) or newly allocating? */
	if (ptr != NULL) {
		ALLOC_ITEM *pp;

		pp = findptr(&lp, ptr, ap);
		pp->next = lp->next;
	}

	if (notoktoadd(numb, ALLOC_SIZE) ||
	    (lp = remalloc(lp, numb + ALLOC_SIZE)) == NULL
#ifndef MKSH_SMALL
	    || ALLOC_ISUNALIGNED(lp)
#endif
	    )
		internal_errorf(Toomem, (unsigned long)numb);
	/* this only works because Area is an ALLOC_ITEM */
	lp->next = ap->next;
	ap->next = lp;
	/* return user item address */
	return ((char *)lp + ALLOC_SIZE);
}

void
afree(void *ptr, Area *ap)
{
	if (ptr != NULL) {
		ALLOC_ITEM *lp, *pp;

		pp = findptr(&lp, ptr, ap);
		/* unhook */
		pp->next = lp->next;
		/* now free ALLOC_ITEM */
		free_osimalloc(lp);
	}
}

void
afreeall(Area *ap)
{
	ALLOC_ITEM *lp;

	/* traverse group (linked list) */
	while ((lp = ap->next) != NULL) {
		/* make next ALLOC_ITEM head of list */
		ap->next = lp->next;
		/* free old head */
		free_osimalloc(lp);
	}
}
