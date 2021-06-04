/*
  io-jpeg.c: GdkPixBuf loader for jpeg files.

  Based on io-jpeg from gdk_imlib, but not much.

  This code is licensed under the Lesser GNU
  General Public License, version 2.1.

  Author:
    Michael Zucchi <zucchi@zedzone.mmc.com.au>
*/

#include <config.h>
#include <stdio.h>
#include <glib.h>
#include <setjmp.h>
#include "gdk-pixbuf.h"
/*#include "gdk-pixbuf-io.h"*/
#include <jpeglib.h>

/* error handler data */
struct iojpeg_JPEG_error_mgr
{
	struct jpeg_error_mgr pub;
	sigjmp_buf          setjmp_buffer;
};

static void
g_JPEGFatalErrorHandler(j_common_ptr cinfo)
{
	/* FIXME:
	 * We should somehow signal what error occurred to the caller so the
	 * caller can handle the error message */
	struct iojpeg_JPEG_error_mgr *errmgr;

	errmgr = (struct iojpeg_JPEG_error_mgr *) cinfo->err;
	cinfo->err->output_message(cinfo);
	siglongjmp(errmgr->setjmp_buffer, 1);
	return;
}

GdkPixBuf *image_load(FILE *f)
{
	int w,h,i,j;
	art_u8 *pixels=NULL, *dptr;
	unsigned char *lines[4], /* Used to expand rows, via rec_outbuf_height, from
				  the header file:
				  "* Usually rec_outbuf_height will be 1 or 2, at most 4." */
		**lptr;
	struct jpeg_decompress_struct cinfo;
	struct iojpeg_JPEG_error_mgr jerr;
	GdkPixBuf *pixbuf;

	/* setup error handler */
	cinfo.err = jpeg_std_error(&(jerr.pub));
	jerr.pub.error_exit = g_JPEGFatalErrorHandler;

	if (sigsetjmp(jerr.setjmp_buffer, 1)) {
		/* Whoops there was a jpeg error */
		if (pixels != NULL)
			art_free(pixels);
		jpeg_destroy_decompress(&cinfo);
		return NULL;
	}

	/* load header, setup */
	jpeg_create_decompress(&cinfo);
	jpeg_stdio_src(&cinfo, f);
	jpeg_read_header(&cinfo, TRUE);
	jpeg_start_decompress(&cinfo);
	cinfo.do_fancy_upsampling = FALSE;
	cinfo.do_block_smoothing = FALSE;

	w = cinfo.output_width;
	h = cinfo.output_height;
	g_print("w: %d h: %d\n", w, h);

	pixels = art_alloc(h * w * 3);
	if (pixels == NULL) {
		jpeg_destroy_decompress(&cinfo);
		return NULL;
	}
	dptr = pixels;

	/* decompress all the lines, a few at a time */

	while (cinfo.output_scanline < cinfo.output_height) {
		lptr = lines;
		for (i=0;i<cinfo.rec_outbuf_height;i++) {
			*lptr++=dptr;
			dptr+=w*3;
		}
		jpeg_read_scanlines(&cinfo, lines, cinfo.rec_outbuf_height);
		if (cinfo.output_components==1) {
			/* expand grey->colour */
			/* expand from the end of the memory down, so we can use
			   the same buffer */
			for (i=cinfo.rec_outbuf_height-1;i>=0;i--) {
				unsigned char *from, *to;
				from = lines[i]+w-1;
				to = lines[i]+w*3-3;
				for (j=w-1;j>=0;j--) {
					to[0] = from[0];
					to[1] = from[0];
					to[2] = from[0];
					to-=3;
					from--;
				}
			}
		}
	}

	jpeg_finish_decompress(&cinfo);
	jpeg_destroy_decompress(&cinfo);

	/* finish off, create the pixbuf */
	pixbuf = gdk_pixbuf_new (art_pixbuf_new_rgb (pixels, w, h, (w * 3)),
				 NULL);
	if (!pixbuf)
		art_free (pixels);
	
	return pixbuf;
}

/*
 * Local variables:
 * c-basic-offset: 8
 * End:
 */
