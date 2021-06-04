/*
 * sqsh_filter.c - Filter data through an external program
 *
 * Copyright (C) 1995-1997 by Scott C. Gray
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, write to the Free Software
 * Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 * You may contact the author :
 *   e-mail:  gray@voicenet.com
 *            grays@xtend-tech.com
 *            gray@xenotropic.com
 */
#include <stdio.h>
#include "sqsh_config.h"
#include "sqsh_fd.h"
#include "sqsh_sig.h"
#include "sqsh_varbuf.h"
#include "sqsh_error.h"
#include "sqsh_filter.h"

#define BLOCK_SIZE    512     /* "Packet" size to sub-process */

/*-- Prototypes --*/
static void filter_sigflg   _ANSI_ARGS(( int, void* ));

/*-- Static Globals --*/
static int     sg_got_sigint = False;

/*
 * sqsh_filter():
 *
 * This function is used to filter a buffer pointed to by buf_ptr
 * (of length buf_len), through an external program, filter, 
 * placing the results in outbuf.  The filtering program is
 * launched as a sub-process with its stdin and stdout connected
 * directly to sqsh while it runs (so no intermediate files
 * are required).
 */
int sqsh_filter( buf_ptr, buf_len, filter, outbuf )
	char       *buf_ptr;
	int         buf_len;
	char       *filter;
	varbuf_t   *outbuf;
{
	int           nbytes;        /* Bytes written or read */
	char          line[1024];    /* Line read from input */
	int           ret;           /* Value returned by this function */
	struct pollfd fds[2];        /* Set of polling file descriptors */

	/*-- Data that needs cleaning up --*/
	int           outfd  = -1;   /* Descriptor to write to process */
	int           infd   = -1;   /* And one to read */

	/*-- Check arguments --*/
	if (buf_ptr == NULL || filter == NULL || outbuf == NULL)
	{
		sqsh_set_error( SQSH_E_BADPARAM, NULL );
		return False;
	}

	/*-- Clear output buffer --*/
	varbuf_clear( outbuf );

	/*
	 * Attempt to open the filter.  If this function succeeds, then
	 * outfd will contain a file descriptor for writing to the
	 * filtering process, and infd will contain a file descriptor
	 * for reading from the process.
	 */
	if (sqsh_popen( filter, "rw", &outfd, &infd ) == -1)
	{
		sqsh_set_error( sqsh_get_error(), "sqsh_popen: %s\n",
		                sqsh_get_errstr() );
		return False;
	}

	/*
	 * Save the current state of the signal handlers away so that
	 * we can replace them with our own copies. From this point out
	 * we need to jump to filter_fail if anything goes wrong.
	 */
	sig_save();

	/*
	 * We want to ignore SIGPIPE (we'll catch it as an error from
	 * read), but we still want to catch SIGINT, in case the
	 * user gets tired of waiting around for the filter to
	 * complete.
	 */
	sg_got_sigint = False;
	sig_install( SIGPIPE, SIG_H_IGN, NULL, 0 );
	sig_install( SIGINT, filter_sigflg, NULL, 0 );

	/*
	 * Set our pollfd array to contain the file descriptors we
	 * want to watch, and what conditions we are watching them
	 * for.
	 */
	fds[0].fd     = outfd;
	fds[0].events = POLLOUT;
	fds[1].fd     = infd;
	fds[1].events = POLLIN;

	/*
	 * Loop until we have successfully transferred everything to
	 * the filter process.
	 */
	for (;;)
	{
		if (sg_got_sigint == True)
		{
			sqsh_set_error( SQSH_E_BADSTATE, "filter interrupted" );
			goto filter_fail;
		}

		fds[0].revents = 0;
		fds[1].revents = 0;

		/*
		 * Poll the file descriptors to figure out if it is either
		 * OK to send data on outfd, or if data is ready for pro-
		 * cessing from infd.
		 */
		while ((ret = sqsh_poll( fds, 2, 0)) == -1)
		{
			if (sqsh_get_error() != EINTR || sg_got_sigint == True)
			{
				sqsh_set_error( sqsh_get_error(), "sqsh_poll: %s\n",
									 sqsh_get_errstr() );
				goto filter_fail;
			}
		}

		/*
		 * If the out-going file descriptor is ready to send, then
		 * we knock a batch of data to the filtering program.
		 */
		if (fds[0].revents & POLLOUT)
		{
			nbytes = min(BLOCK_SIZE, buf_len);

			/*
			 * Attempt to send data over the file descriptor, ignoring
			 * interrupts due to signals.
			 */
			while ((nbytes = write( outfd, buf_ptr, nbytes )) == -1)
			{
				if (errno != EINTR || sg_got_sigint == True)
				{
					sqsh_set_error( errno, "write: %s\n", strerror(errno) );
					goto filter_fail;
				}
			}

			buf_ptr += nbytes;
			buf_len -= nbytes;

			/*
			 * If we have succesfully sent everything we have to the
			 * filtering process, then we break out of our polling 
			 * loop, and just wait for data to come back from the
			 * filter, below.
			 */
			if (buf_len == 0)
			{
				break;
			}
		}

		/*
		 * If the filtering process has some data ready for us,
		 * then we want to suck it in.
		 */
		if (fds[1].revents & POLLIN)
		{
			/*
			 * Once again, we want to read from the filtering process
			 * ignoring interrupts due to incoming signals.
			 */
			while ((nbytes = read( infd, line, sizeof(line)-1 )) == -1)
			{
				if (errno != EINTR || sg_got_sigint == True)
				{
					sqsh_set_error( errno, "Error during read from filter" );
					goto filter_fail;
				}
			}

			/*
			 * If we have reached an EOF condition, then we are done
			 * (although, really, we shouldn't get EOF here since
			 * we probably aren't done sending everything we have
			 * to the filtering process.
			 */
			if (nbytes == 0)
			{
				/*
				 * If we got EOF, but we haven't finished sending everything,
				 * then we want to complain.
				 */
				if (buf_len > 0)
				{
					sqsh_set_error( SQSH_E_BADSTATE, "Unexpected EOF from filter" );
					goto filter_fail;
				}
				break;
			}

			line[nbytes] = '\0';
			varbuf_strcat( outbuf, line );
		}
	}

	/*
	 * Close our out-going file descriptor so the filtering
	 * program will get an EOF.
	 */
	sqsh_close( outfd );
	outfd = -1;

	/*
	 * At this point, we have sent everything we have to the filter
	 * so we simply want to wait for it to finish doing its thing
	 * and to send us everything it has back.
	 */
	while ((nbytes = read( infd, line, sizeof(line)-1 )) != 0)
	{
		if (nbytes == -1)
		{
			if (errno != EINTR || sg_got_sigint == True)
			{
				sqsh_set_error( errno, "read from filter: %s", strerror(errno) );
				goto filter_fail;
			}
		}
		else
		{
			line[nbytes] = '\0';
			varbuf_strcat( outbuf, line );
		}
	}
	sqsh_close( infd );
	infd = -1;

	ret = True;
	goto filter_leave;

filter_fail:
	ret = False;

filter_leave:
	sig_restore();

	if (outfd != -1)
	{
		sqsh_close( outfd );
	}

	if (infd != -1)
	{
		sqsh_close( infd );
	}

	return ret;
}

/*
 * filter_sigflg():
 *
 * Catches SIGINT signals from the user and jumps to the
 * jump-point established in sqsh_filter().
 */
static void filter_sigflg( sig, data )
	int   sig;
	void *data;
{
	sg_got_sigint = True;
}
