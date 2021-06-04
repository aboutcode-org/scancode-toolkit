#ifndef lint
#ifdef SCCS
static char     sccsid[] = "@(#)sel_util.c 1.29 93/06/28";
#endif
#endif

/*
 *	(c) Copyright 1990 Sun Microsystems, Inc. Sun design patents 
 *	pending in the U.S. and foreign countries. See LEGAL NOTICE 
 *	file for terms of the license.
 */

#include <xview_private/sel_impl.h>
#include <xview_private/svr_impl.h>
#include <xview/notify.h>
#include <xview/window.h>
#include <xview/server.h>
#ifdef SVR4 
#include <stdlib.h> 
#endif SVR4

static void tvdiff();
static void FreeMultiProp();
static int	SelMatchReply();
static Sel_req_tbl *SelMatchReqTbl();

Pkg_private struct timeval *
xv_sel_cvt_xtime_to_timeval( XTime )
Time  XTime;
{
    struct  timeval  *time;
    
    time = xv_alloc( struct timeval );
    time->tv_sec = ((unsigned long) XTime )/1000;
    time->tv_usec = (((unsigned long) XTime ) % 1000) * 1000;
    return time;
}


Pkg_private Time
xv_sel_cvt_timeval_to_xtime( timeV )
struct  timeval  *timeV;
{
    return ( ( timeV->tv_sec * 1000 ) + ( timeV->tv_usec / 1000 ) );
}


Pkg_private Sel_owner_info *
xv_sel_find_selection_data( dpy, selection, xid )
Display    *dpy;
Atom       selection;
Window     xid;
{
    Sel_owner_info       *sel;
    
    if ( selCtx == 0 )
        selCtx = XUniqueContext();
    if ( XFindContext( dpy, (Window) selection, selCtx, (caddr_t *)&sel ) ) {

	sel = xv_alloc( Sel_owner_info );

	if ( sel == NULL ) {
	    return ( (Sel_owner_info *) NULL );
	}
	/* Attach the atom type informations to the display */
	sel->atomList = xv_sel_find_atom_list( dpy, xid );
	sel->dpy = dpy;
	sel->selection = selection;
	sel->xid = NULL;
	sel->status = 0;
	(void)XSaveContext( dpy, (Window)selection, selCtx, (caddr_t)sel );
    }
    return  sel;
}



Pkg_private Sel_owner_info *
xv_sel_set_selection_data( dpy, selection, sel_owner )
Display         *dpy;
Atom            selection;
Sel_owner_info  *sel_owner;
{
    if ( selCtx == 0 )
        selCtx = XUniqueContext();

    /* Attach the atom type informations to the display */
    sel_owner->atomList = xv_sel_find_atom_list( dpy, sel_owner->xid );
    sel_owner->dpy = dpy;
    sel_owner->selection = selection;
    sel_owner->status = 0;
    (void)XSaveContext( dpy,(Window)selection, selCtx,(caddr_t)sel_owner);
    return  sel_owner;
}

/*
 * REMINDER: This needs to be changed to a more efficient way of getting
 *  last event time.
*/
Xv_private Time
xv_sel_get_last_event_time( dpy, win )  
Display  *dpy;
Window   win;
{
    XEvent         event;
    XPropertyEvent *ev;
    Atom  prop = xv_sel_get_property( dpy );
    XWindowAttributes  winAttr;
    int    arg;
    int  status = xv_sel_add_prop_notify_mask( dpy, win, &winAttr );
    
    XChangeProperty( dpy, win, prop, XA_STRING, 8, PropModeReplace,
		    (unsigned char *) NULL, 0 );
    
    /* Wait for the PropertyNotify */
    arg = PropertyNotify;
    if ( !xv_sel_block_for_event( dpy, &event, 3 , xv_sel_predicate, (char *) &arg ) ) {
	xv_error(NULL,
                 ERROR_STRING,XV_MSG("xv_sel_get_last_event_time: Unable to get the last event time"),
	         ERROR_PKG,SELECTION,
                 0);
	return ( (Time) NULL );
    }

    xv_sel_free_property( dpy, prop );

    /* 
     * If we have added PropertyChangeMask to the win, reset the mask to
     * it's original state.
     */
    if ( status )
        XSelectInput( dpy, win, winAttr.your_event_mask  );

    ev = (XPropertyEvent *) &event;
    return( ev->time );
}


int
xv_sel_add_prop_notify_mask( dpy, win, winAttr )
Display           *dpy;
Window            win;
XWindowAttributes *winAttr;
{
    XGetWindowAttributes( dpy, win, winAttr );  

    /*
     * If PropertyChangeMask has already been set on the window, don't set
     * it again.
     */
    if (  winAttr->your_event_mask & PropertyChangeMask )
        return FALSE;
    
    XSelectInput( dpy, win, winAttr->your_event_mask | PropertyChangeMask );
    return TRUE;
}



/* REMEMBER TO FREE THE ALLOCATED MEM */
Pkg_private Sel_atom_list *
xv_sel_find_atom_list( dpy, xid )
Display   *dpy;
Window    xid;
{
    Sel_atom_list      *list;
    Xv_window      xvWin;
    Xv_Server      server;
    
    if ( targetCtx == 0 )
        targetCtx = XUniqueContext();
    if ( XFindContext( dpy, DefaultRootWindow(dpy), targetCtx, 
		      (caddr_t *)&list ) ) {
	list = xv_alloc( Sel_atom_list );
	if ( list == NULL ) {
	    return( (Sel_atom_list *) NULL );
	}
	/* Get XView object */
	xvWin = win_data( dpy, xid );
	server = XV_SERVER_FROM_WINDOW( xvWin );

	list->multiple = (Atom) xv_get( server, SERVER_ATOM, "MULTIPLE" );
	list->targets = (Atom) xv_get( server, SERVER_ATOM, "TARGETS" );
	list->timestamp = (Atom) xv_get( server, SERVER_ATOM, "TIMESTAMP" );
	list->file_name = (Atom) xv_get( server, SERVER_ATOM, "FILE_NAME" );
	list->string = (Atom) xv_get( server, SERVER_ATOM, "STRING" );
	list->incr = (Atom) xv_get( server, SERVER_ATOM, "INCR" );
	list->integer = (Atom) xv_get( server, SERVER_ATOM, "INTEGER" );
#ifdef OW_I18N
	list->ctext = (Atom) xv_get( server, SERVER_ATOM, "COMPOUND_TEXT" );
#endif OW_I18N
	(void)XSaveContext( dpy, DefaultRootWindow(dpy), targetCtx, 
			   (caddr_t)list );
    }
    return ( list );
}


Pkg_private Sel_prop_list *
xv_sel_get_prop_list( dpy )
Display   *dpy;
{
    Sel_prop_list      *list;
    
    if ( propCtx == 0 )
        propCtx = XUniqueContext();
    if ( XFindContext( dpy, DefaultRootWindow(dpy), propCtx, 
						(caddr_t *)&list ) ) {

	list = xv_alloc( Sel_prop_list );
	if ( list == NULL ) {
	    return ( (Sel_prop_list *) NULL );
	}

	list->prop = XInternAtom(dpy, "XV_SELECTION_0", FALSE);
	list->avail = TRUE;
	list->next = NULL;
	
	(void)XSaveContext( dpy, DefaultRootWindow(dpy), propCtx, 
					(caddr_t)list );
    }
    return ( list );
}


/* NOTE: the avail field should be reset to TRUE after a complete transaction. */
Pkg_private Atom
xv_sel_get_property( dpy )
Display  *dpy;
{
    Sel_prop_list  *cPtr;
    char       str[100];
    int          i=0;
    
    cPtr = xv_sel_get_prop_list( dpy );
    
    do {
	if ( cPtr->avail )  {
	    cPtr->avail = FALSE;
	    return ( cPtr->prop );
	}
	i++;
	if ( cPtr->next == NULL )
	    break;
	cPtr = cPtr->next;
    } while ( 1 );

    
    /* Create a new property and add it to the list */
    cPtr->next = xv_alloc( Sel_prop_list );
    if ( cPtr->next == NULL )  {
	return ( (Atom) NULL );
    }
    cPtr = cPtr->next;
    sprintf( str,"XV_SELECTION_%d", i );
    cPtr->prop = XInternAtom(dpy, str, FALSE);
    cPtr->avail = FALSE;
    cPtr->next = NULL;
    return ( cPtr->prop );
}


Pkg_private void
xv_sel_free_property( dpy, prop )
Display  *dpy;
Atom   prop;
{
    Sel_prop_list  *plPtr;
    
    plPtr = xv_sel_get_prop_list( dpy );
    
    do {
	if ( plPtr->prop == prop )  {
	    plPtr->avail = TRUE;
	    break;
	}
	if ( plPtr->next == NULL )
	    break;
	plPtr = plPtr->next;
    } while ( 1 );
}

    

/*
 * Predicate function for XCheckIfEvent
 * 
 */
/*ARGSUSED*/
Pkg_private int
xv_sel_predicate( display, xevent, args )
Display        *display;
register XEvent         *xevent;
char	   *args;
{
    int  eventType;
    
    XV_BCOPY( (char *) args, (char *) &eventType, sizeof(int) ); 

    if ( (xevent->type & 0177) == eventType ) 
	return ( TRUE );

    /*
     * If we receive a SelectionRequest while waiting, handle selection request
     * to avoid a dead lock.
     */
    if ( (xevent->type & 0177) == SelectionRequest )   {
	XSelectionRequestEvent *reqEvent = (XSelectionRequestEvent *) xevent;

	if (!xv_sel_handle_selection_request(reqEvent)) {
	    Xv_window      xvWin;
	    Xv_Server      server;

	    xvWin = win_data( display, reqEvent->requestor );

	    if ( xvWin == 0 )
		server = xv_default_server;
	    else
	        server = XV_SERVER_FROM_WINDOW( xvWin );
	    
	    /*
	     * Send this request to the old selection package.
	     */
	    selection_agent_selectionrequest( server, reqEvent);	
	}
	
    }
    
    return ( FALSE );
}

/*
 * Predicate function for XCheckIfEvent
 * 
 */
/*ARGSUSED*/
Pkg_private int
xv_sel_check_selnotify( display, xevent, args )
Display        *display;
register XEvent         *xevent;
char	   *args;
{
    Sel_reply_info  reply;
    
    XV_BCOPY( (char *) args, (char *) &reply, sizeof(Sel_reply_info) ); 

    if ( (xevent->type & 0177) == SelectionNotify ) {
         XSelectionEvent *ev = (XSelectionEvent *) xevent;

#ifdef SEL_DEBUG1
  printf("REcieved SelectionNotify win = %d selection = %s property = %s target = %s\n", ev->requestor,XGetAtomName(ev->display,ev->selection),XGetAtomName(ev->display,ev->property),XGetAtomName(ev->display,ev->target));
#endif

         if ((ev->target == *reply.target))
	  return ( TRUE );
        /*
         * else 
         * fprintf(stderr, "Possible BUG case - xv_sel_check_selnotify \n");
         */
    }

    /*
     * If we receive a SelectionRequest while waiting, handle selection request
     * to avoid a dead lock.
     */
    if ( (xevent->type & 0177) == SelectionRequest )   {
	XSelectionRequestEvent *reqEvent = (XSelectionRequestEvent *) xevent;

	if (!xv_sel_handle_selection_request(reqEvent)) {
	    Xv_window      xvWin;
	    Xv_Server      server;

	    xvWin = win_data( display, reqEvent->requestor );

	    if ( xvWin == 0 )
		server = xv_default_server;
	    else
	        server = XV_SERVER_FROM_WINDOW( xvWin );
	    
	    /*
	     * Send this request to the old selection package.
	     */
	    selection_agent_selectionrequest( server, reqEvent);	
	}
	
    }
    
    return ( FALSE );
}




Pkg_private char *
xv_sel_atom_to_str( dpy, atom, xid )
Display  *dpy;
Atom     atom;
XID       xid;
{
    Xv_window xvWin;
    Xv_opaque server;

    if ( xid == 0 )
        server = xv_default_server;
    else {
	xvWin = win_data( dpy, xid );
	server = XV_SERVER_FROM_WINDOW( xvWin );
    }

    return ( (char *) xv_get( server, SERVER_ATOM_NAME, atom ));
}
    
Pkg_private Atom
xv_sel_str_to_atom( dpy, str, xid )
Display   *dpy;
char      *str;
XID       xid;
{
    Xv_window xvWin;
    Xv_opaque server;

    if ( xid == 0 )
        server = xv_default_server;
    else {
	xvWin = win_data( dpy, xid );
	server = XV_SERVER_FROM_WINDOW( xvWin );
    }
    
    return ( (Atom) xv_get( server, SERVER_ATOM, str ));
}

/*
 * REMINDER: Go over the erro codes make sure they match the spec!!
*/
/*ARGSUSED*/
Pkg_private int
xv_sel_handle_error( errCode, sel, replyInfo, target )
int   errCode;
Sel_req_info  *sel;
Sel_reply_info  *replyInfo;
Atom   target;
{
    Selection_requestor sel_req;
    
    if ( sel != NULL )
        sel_req = SEL_REQUESTOR_PUBLIC( sel );
    
    /* REMINDER: Need to remove all the printf!! */

    switch ( errCode )   {
      case SEL_BAD_PROPERTY :
#ifdef SEL_DEBUG
          printf("xv_sel_handle_error: Bad property!\n");
#endif
	  break;
      case SEL_BAD_CONVERSION :
#ifdef SEL_DEBUG
          printf("xv_sel_handle_error: Bad conversion!\n");
#endif
	  break;
      case SEL_BAD_TIME:
#ifdef SEL_DEBUG
          printf("xv_sel_handle_error: Bad time!\n");
#endif
	  break;
      case SEL_BAD_WIN_ID:
#ifdef SEL_DEBUG
          printf("xv_sel_handle_error: Bad window id!\n");
#endif
	  break;
      case SEL_TIMEDOUT:
#ifdef SEL_DEBUG
          printf("xv_sel_handle_error: Timed out!\n");
#endif
	  break;
      case SEL_PROPERTY_DELETED:
#ifdef SEL_DEBUG
          printf("xv_sel_handle_error: Expected a PropertyNotify event stat==NewValue!\n");
#endif
	  break;
      case SEL_BAD_PROPERTY_EVENT:
#ifdef SEL_DEBUG
          printf("xv_sel_handle_error: Owner received a bad PropertyNotify event !\n");
#endif
	  break;
      }

    if ( (sel != NULL) && (sel->reply_proc != NULL) )
        (*sel->reply_proc)( sel_req, target, NULL, &errCode, SEL_ERROR, 0 );
}


/*
 * xv_sel_block_for_event
 *
 * Scan the input queue for the specified event.
 * If there aren't any events in the queue, select() for them until a 
 * certain timeout period has elapsed.  Return value indicates whether the
 * specified event  was seen.
 */
Pkg_private int
xv_sel_block_for_event( display, xevent, seconds, predicate, arg )
Display        *display;
XEvent         *xevent;
int            seconds;
int            (*predicate)();
char           *arg;
{
    fd_set          rfds;
    int             result;
    struct timeval  timeout;
    struct timeval starttime, curtime, diff1, diff2;
    extern int errno;
    
    timeout.tv_sec = seconds;
    timeout.tv_usec = 0;

    (void) gettimeofday(&starttime, NULL);
    XSync( display, False );
    while (1) {
	/*
	 * Check for data on the connection.  Read it and scan it. 
	 */
	if (XCheckIfEvent(display, xevent, predicate, (char *) arg ))
            return( TRUE );

	/*
	 * We've drained the queue, so we must select for more.
	 */
	FD_ZERO( &rfds );
	FD_SET( ConnectionNumber( display ), &rfds );

	result = select( ConnectionNumber( display ) + 1, &rfds, NULL, 
			NULL, &timeout);

	if ( result == 0 ) {
	    ((XSelectionEvent *) xevent)->property = None;
	    /* REMINDER: Do we need this ^^^ here? */
#ifdef SEL_DEBUG
	    printf("Selection Timed out!\n");
#endif
	    /* we timed out without getting anything */
	    return FALSE;
	} 	    

	/*
	 * Report errors. If we were interrupted (errno == EINTR), we simply
	 * continue around the loop. We scan the input queue again.
	 */
	if (result == -1 && errno != EINTR)
	    perror("Select");

	/*
	 * Either we got interrupted or the descriptor became ready.
	 * Compute the remaining time on the timeout.
	 */
	(void) gettimeofday(&curtime, NULL);
	tvdiff(&starttime, &curtime, &diff1);
	tvdiff(&diff1, &timeout, &diff2);
	timeout = diff2;
	starttime = curtime;
	if (timeout.tv_sec < 0)
	    return False;
    }
}




/* compute t2 - t1 and return the time value in diff */
static void
tvdiff(t1, t2, diff)
    struct timeval *t1, *t2, *diff;
{
    diff->tv_sec = t2->tv_sec - t1->tv_sec;
    diff->tv_usec = t2->tv_usec - t1->tv_usec;
    if (diff->tv_usec < 0) {
	diff->tv_sec -= 1;
	diff->tv_usec += 1000000;
    }
}



Pkg_private Sel_req_tbl *
xv_sel_set_reply( reply )
Sel_reply_info  *reply;
{
    Sel_req_tbl  *reqTbl;
    Display  *dpy;
    
    if ( replyCtx == 0 )
        replyCtx = XUniqueContext();

    dpy = reply->seln->dpy;
    
    if ( XFindContext( dpy, DefaultRootWindow(dpy), replyCtx, 
		      (caddr_t *)&reqTbl )) {
	reqTbl = xv_alloc( Sel_req_tbl );
	reqTbl->done = FALSE;
	reqTbl->reply = reply;
	reqTbl->next = NULL;
	(void)XSaveContext( dpy, DefaultRootWindow(dpy),replyCtx,
			   (caddr_t *)reqTbl);
	return reqTbl;
    }
    return (Sel_req_tbl *) xv_sel_add_new_req( reqTbl, reply );
}



Pkg_private Sel_req_tbl *
xv_sel_add_new_req( reqTbl, reply )
Sel_req_tbl  *reqTbl;
Sel_reply_info *reply;
{
    Sel_req_tbl  *rPtr;

    rPtr = reqTbl;

    /*
     * If there is an slot open use it.
     */
    do {
	if ( rPtr->done )  {
	    if ( rPtr->reply != NULL )
	        XFree( (char *)rPtr->reply );
	    rPtr->reply = reply;
	    rPtr->done = FALSE;
	    return reqTbl;
	}
	if ( rPtr->next == NULL )
	    break;
	rPtr = rPtr->next;
    } while ( 1 );

    /* 
     * Create a new reply and add it to the list.
     */
    rPtr->next = xv_alloc( Sel_req_tbl );
    if ( rPtr->next == NULL )  {
	return( (Sel_req_tbl * ) NULL );
    }
    rPtr = rPtr->next;
    rPtr->reply = reply;
    rPtr->done = FALSE;
    rPtr->next = NULL;
    
    return  reqTbl;
}


    
Pkg_private Sel_reply_info *
xv_sel_get_reply( event )
XEvent *event;
{
    Sel_req_tbl  *reqTbl, *rPtr;
    Display  *dpy;

    if ( replyCtx == 0 )
        replyCtx = XUniqueContext();

    if ( event->type == SelectionNotify )
        dpy = event->xselection.display;
    else
        dpy = event->xproperty.display;

    if ( XFindContext( dpy, DefaultRootWindow(dpy), replyCtx, 
		      (caddr_t *)&reqTbl )) 
	return (Sel_reply_info *) NULL;

    rPtr = reqTbl;
    
    /*
     * Find this window's reply struct.
     */
    do {
	if ( !rPtr->done && SelMatchReply( event, rPtr->reply ) )
	    return rPtr->reply;

	if ( rPtr->next == NULL )
	    break;
	rPtr = rPtr->next;
    } while ( 1 );

    return (Sel_reply_info *) NULL;
}


static int
SelMatchReply( event, reply )
XEvent *event;
Sel_reply_info *reply;
{
    if ( event->type == SelectionNotify ) {
	XSelectionEvent  *ev = (XSelectionEvent *) event;

	if (ev->requestor != reply->requestor) 
	    return FALSE;

	if ( ev->selection != reply->seln->selection )
	    return FALSE;

	if ( ( ev->target != *reply->target) &&
	    (ev->target != reply->seln->atomList->incr ) )
	    return FALSE;
    }
    else {
	XPropertyEvent *ev = (XPropertyEvent *) event;
	
	if ( ev->window != reply->requestor )
            return FALSE;

	if ( ev->state != PropertyNewValue )
            return FALSE;
    }
    
    return TRUE;
}



/*ARGSUSED*/
Pkg_private Notify_value
xv_sel_handle_sel_timeout( client, which )
Notify_client client;
int           which;
{
    Sel_reply_info  *reply = (Sel_reply_info *) client;
    Sel_req_tbl  *reqTbl;
    
    
    reqTbl = (Sel_req_tbl *) SelMatchReqTbl( reply );
    
    if ( reqTbl != NULL )  {

        if ( !reqTbl->done  )  {
	    xv_sel_handle_error( SEL_TIMEDOUT, reply->req_info, reply, 
			*reply->target );    
	    xv_sel_end_request( reply );
	}
    }
	
    return NOTIFY_DONE;
}



static Sel_req_tbl *
SelMatchReqTbl( reply )
Sel_reply_info  *reply;
{
    Sel_req_tbl  *reqTbl, *rPtr;
    Display  *dpy = reply->seln->dpy;

    if ( replyCtx == 0 )
        replyCtx = XUniqueContext();

    if ( XFindContext( dpy, DefaultRootWindow(dpy), replyCtx, 
		      (caddr_t *)&reqTbl )) 
	return FALSE;
    
    rPtr = reqTbl;
    
    /*
     * Find this window's request table.
     */
    do {
	if ( !rPtr->done && SelFindReply( reply, rPtr->reply ) ) 
	    return rPtr;
	
	if ( rPtr->next == NULL )
	    break;
	rPtr = rPtr->next;
    } while ( 1 );

    return (Sel_req_tbl *) NULL;    
}


int
xv_sel_end_request( reply )
Sel_reply_info  *reply;
{
    XWindowAttributes winAttr;
    Sel_req_tbl  *reqTbl;
    
    reqTbl = SelMatchReqTbl( reply );

    if ( reqTbl != NULL )  {

	notify_set_itimer_func( (Notify_client) reply, NOTIFY_FUNC_NULL, ITIMER_REAL, 
			       NULL, NULL); 

	/*
	 * Free all the properties that were created for the multiple
	 * request.
	 */
	FreeMultiProp( reply );

	reqTbl->done = TRUE;
	/* 
	 * If we have added PropertyChangeMask to the win, reset the mask to
	 * it's original state.
	 */
	if ( reply->status == TRUE )  {
	    XGetWindowAttributes( reply->seln->dpy, reply->requestor, &winAttr );  

	    XSelectInput(reply->seln->dpy, reply->requestor,
		     (winAttr.your_event_mask & ~(PropertyChangeMask)));
	}
	
	XDeleteContext( reply->seln->dpy, (Window) reply->seln->selection, 
		       selCtx );
	
	xv_sel_free_property( reply->seln->dpy, reqTbl->reply->property );	    

	XFree( (char *)reqTbl->reply );
	reqTbl->reply = NULL;
	return TRUE;
    }
    return FALSE;    
}




static int 
SelFindReply( r1, r2 )
Sel_reply_info  *r1;
Sel_reply_info  *r2;
{
    /*
     * Make sure it is really it!!
     */
    if ( (r1->requestor == r2->requestor) && (*r1->target == *r2->target) &&
	 (r1->property == r2->property) && (r1->format == r2->format) &&
	 (r1->time == r2->time) && (r2->length == r1->length) &&
	 (r1->seln->selection == r2->seln->selection) )
        return TRUE;
    return FALSE;
}


/*
 * Free all the properties that were created for the multiple
 * request.
 */
static void
FreeMultiProp( reply )
Sel_reply_info  *reply;
{
    int            i;

    if ( reply->multiple ) {
        for ( i=0; i < reply->multiple; i++ )   
	    xv_sel_free_property( reply->seln->dpy, reply->atomPair[i].property );
    }
}

	 



/*ARGSUSED*/
Pkg_private int
xv_sel_check_property_event( display, xevent, args )
Display  *display;
XEvent   *xevent;
char	 *args;
{
    Sel_reply_info   reply;
    
    XV_BCOPY( (char *) args, (char *) &reply, sizeof(Sel_reply_info) ); 

    /*
     * If some other process wants to become the selection owner, let
     * it do so but continue handling the current transaction.
     */
    if ( ( xevent->type & 0177) == SelectionClear )  {
	xv_sel_handle_selection_clear( (XSelectionClearEvent * ) xevent );
	return FALSE;
    }
    
    if ( ( xevent->type & 0177) == PropertyNotify )  {
	XPropertyEvent *ev = (XPropertyEvent *) xevent;
	if ( ev->state == PropertyNewValue && ev->atom == reply.property &&
		ev->time > reply.time )
	    return ( TRUE );
    }
    return ( FALSE );
}





Xv_private void
xv_sel_set_compat_data( dpy, selection, xid, clientType )
Display  *dpy;
Atom     selection;
Window   xid;
int      clientType;
{
    Sel_cmpat_info      *cmptInfo, *infoPtr;

    if ( cmpatCtx == 0 )
        cmpatCtx = XUniqueContext();

    if (XFindContext(dpy, DefaultRootWindow(dpy), cmpatCtx, (caddr_t *)&cmptInfo)) {
	cmptInfo = xv_alloc( Sel_cmpat_info );
	if ( cmptInfo == NULL ) {
	    return;
	}
	cmptInfo->selection = selection;
	cmptInfo->owner = xid;
	cmptInfo->clientType = clientType;
	cmptInfo->next = NULL;	
	(void)XSaveContext(dpy, DefaultRootWindow(dpy), cmpatCtx, (caddr_t)cmptInfo);
	return;
    }
    infoPtr = cmptInfo;
    
    do {
	if ( (infoPtr->selection == selection) || (infoPtr->selection == NULL) ) {
	    infoPtr->selection = selection;
	    infoPtr->clientType = clientType;
	    infoPtr->owner = xid; 	    
	    return;
	}
	
	if ( infoPtr->next == NULL )
	    break;
	infoPtr = infoPtr->next;
    } while ( 1 );
    
    infoPtr->next = xv_alloc( Sel_cmpat_info );
    if ( infoPtr->next == NULL ) 
	return;
    
    infoPtr = infoPtr->next;
    infoPtr->selection = selection;
    infoPtr->clientType = clientType;
    infoPtr->owner = xid;     
    infoPtr->next = NULL;
    return;
}



Pkg_private void
xv_sel_free_compat_data( dpy, selection )
Display  *dpy;
Atom     selection;
{
    Sel_cmpat_info      *cmptInfo, *infoPtr;

    if ( cmpatCtx == 0 )
        cmpatCtx = XUniqueContext();
    if ( XFindContext(dpy, DefaultRootWindow(dpy), cmpatCtx,(caddr_t *)&cmptInfo))
	return;

    infoPtr = cmptInfo;
    
    do {
	if ( infoPtr->selection == selection ) {
	    infoPtr->selection = NULL;
	    infoPtr->owner = NULL;	    
	    infoPtr->clientType = NULL;
	    return;
	}
	if ( infoPtr->next == NULL )
	    break;
	infoPtr = infoPtr->next;
    } while ( 1 );
}


Pkg_private void   
xv_sel_send_old_pkg_sel_clear( dpy, selection, xid, time )
Display  *dpy;
Atom     selection;
Window   xid;
Time     time;
{
    Sel_cmpat_info      *cmpatInfo, *infoPtr;
			   
    if ( cmpatCtx == 0 )
        cmpatCtx = XUniqueContext();
    if ( XFindContext(dpy, DefaultRootWindow(dpy), cmpatCtx,(caddr_t *)&cmpatInfo))
	return;
    
    infoPtr = cmpatInfo;
    do {
	if ( (infoPtr->selection == selection) && 
	    (infoPtr->clientType == OLD_SEL_CLIENT) ) {
	    Xv_window             xvWin;
	    Xv_Server             server;
	    Seln_agent_info       *agent;
	    XSelectionClearEvent  clrEvent;
	    Seln_holder           holder;
	    Seln_request          *response;
	    
	    clrEvent.display = dpy;
	    clrEvent.window = infoPtr->owner;
	    clrEvent.selection = selection;	    
	    clrEvent.time = time;

	    xvWin = win_data( dpy, xid );
	    server = XV_SERVER_FROM_WINDOW( xvWin );

	    holder = selection_inquire( server, SELN_PRIMARY );
	    response = selection_ask( server, &holder, SELN_REQ_YIELD, NULL, 0 );

	    agent = (Seln_agent_info *) xv_get(server, (Attr_attribute)XV_KEY_DATA, 
				   SELN_AGENT_INFO);	    
	    seln_give_up_selection( server,
			    selection_to_rank( selection, agent));

	    selection_agent_clear( server, &clrEvent );
	    
	    break;
	}
	if ( infoPtr->next == NULL )
	    break;
	
	infoPtr = infoPtr->next;
    }while (1);
}



Xv_private int
xv_seln_handle_req( cmpatInfo, dpy, sel, target, prop, req, time)
Sel_cmpat_info  *cmpatInfo;
Display         *dpy;
Atom            sel;
Atom            target;
Atom            prop;
Window          req;
Time            time;
{
    XSelectionRequestEvent  reqEvent;
    Sel_cmpat_info   *infoPtr;

    if ( cmpatInfo == (Sel_cmpat_info *) NULL )
	return FALSE;

    infoPtr = cmpatInfo;
    do {
	if ( infoPtr->selection != sel ) {
	    if ( infoPtr->next == NULL )
		return FALSE;
	    infoPtr = infoPtr->next;
	} else {
	    /*
	     * We found the local selection owner data!!
	     */
    	    reqEvent.display = dpy;
    	    reqEvent.owner = infoPtr->owner;
    	    reqEvent.requestor = req;
    	    reqEvent.selection = infoPtr->selection;
    	    reqEvent.target = target;
    	    reqEvent.property = prop;
    	    reqEvent.time = time;
	    break;
	}
    } while( 1 );

    /*
     * Note that selection data transfer will fail if the request is:
     * MULTIPLE or INCR.
     * This routine is compatibility proc to solve the communication
     * problem between the old selection package and the new one.
     * This routine and all the refrences to it can be deleted after
     * textsw starts using the new selection package.
     */
     xv_sel_handle_selection_request( &reqEvent );
     return TRUE;
}



Pkg_private Sel_cmpat_info  *
xv_sel_get_compat_data( dpy )
Display   *dpy;
{
    Sel_cmpat_info  *cmpatInfo;

    if ( XFindContext( dpy, DefaultRootWindow(dpy), cmpatCtx, 
			(caddr_t *)&cmpatInfo ))
	return( (Sel_cmpat_info *) NULL );
    return( (Sel_cmpat_info *) cmpatInfo );
    
}



Xv_private void
xv_sel_send_old_owner_sel_clear( dpy, selection, xid, time )
Display  *dpy;
Atom     selection;
Window   xid;
Time     time;
{
    Sel_cmpat_info      *cmpatInfo, *infoPtr;

    if ( cmpatCtx == 0 )
        cmpatCtx = XUniqueContext();
    if ( XFindContext(dpy, DefaultRootWindow(dpy), cmpatCtx,(caddr_t *)&cmpatInfo))
	return;

    infoPtr = cmpatInfo;
    do {
	if ( (infoPtr->selection == selection) && (infoPtr->owner != xid) ) {
	    XSelectionClearEvent  clrEvent;
	    
	    clrEvent.display = dpy;
	    clrEvent.window = infoPtr->owner;
	    clrEvent.selection = selection;	    
	    clrEvent.time = time;

	    xv_sel_handle_selection_clear( &clrEvent );
	}
	if ( infoPtr->next == NULL )
	    break;
	infoPtr = infoPtr->next;
    }while (1);
}

    
