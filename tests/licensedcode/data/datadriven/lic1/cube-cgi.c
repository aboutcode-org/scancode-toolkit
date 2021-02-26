/* cube-cgi.c  modified from expl-cgi.c
 * 
 * 	Author : David Joyce,
 *		 Dept of CS/Math, Clark University,
 *		 Worcester, Mass, 01610
 *	Date:    revised Jan, 1997
 *
 */

/*
 * Copyright 1997 by David E. Joyce and Clark University
 *
 * Permission to use, copy, and distribute for non-commercial purposes,
 * is hereby granted without fee, providing that the above copyright
 * notice appear in all copies and that both the copyright notice and this
 * permission notice appear in supporting documentation.
 *
 * The software may be modified for your own purposes, but modified versions
 * may not be distributed.
 *
 * This software is provided "as is" without any expressed or implied warranty.
 *
 * The author may be contacted via email at djoyce@black.clarku.edu
 */


#include "cube-cgi.h"

sendmesg(char *url)
{
    printf("Location: %s%c%c",url,10,10);
    printf("This document is located <A HREF=\"%s\">here</A>%c",url,10);
}

main(int argc, char *argv[]) {
  cgiargs argg;
  char   *w, *v;
  int    entrycount;
  time_t now;
  char   *thetime;

  int    i,j;
  double mux, muy;
  double jcenterx, jcentery, jradiusx, jradiusy;
  double mcenterx, mcentery, mradiusx, mradiusy;
  double mcx, mcy, sum, x, y;

  int    getjulia=0, magmandel=0, magjulia=0;
  int    mandelclick=0, do_julia, do_mandel;
  int    iter;       /* iterations */
  int    height,  width;
  int    jwidthold,jheightold,mwidthold,mheightold;
  double jlx,jly,jhx,jhy, mlx,mly,mhx,mhy;
  int    style = 1, wrap = 1, escape = 1, pattern = 1;
  int    juliax = -1, juliay = -1;
  int    mandelx = -1, mandely = -1;
  double mag = 3.0;
  char   filen[11], *jfn, *jhn, *mfn, *mhn, *hfn, *hhn;
  char   *jsource,*msource,*hsource;
  int    mplane = 1, oldmplane = 1;
  FILE   *fp;


  cgiparse(argc, argv, &argg);

  for (i=0; i<=argg.m; ++i) {
    w=argg.entries[i].name;
    v=argg.entries[i].val;
 
    /* printf(" <code>%s = %s</code><br>%c",w,v,10);  */

    if      (!strcmp(w,"JULIA.x"))  {
      juliax = atoi(v);
      magjulia = 1;
    }
    else if (!strcmp(w,"JULIA.y"))  juliay = atoi(v);

    else if (!strcmp(w,"JCENTERX")) jcenterx = atof(v);
    else if (!strcmp(w,"JCENTERY")) jcentery = atof(v);
    else if (!strcmp(w,"JRADIUS"))  jradiusx = atof(v);
    else if (!strcmp(w,"JSOURCE"))  jsource = v;
    else if (!strcmp(w,"MUX"))      mux = atof(v);
    else if (!strcmp(w,"MUY"))      muy = atof(v);

    else if (!strcmp(w,"MANDEL.x")) {
      mandelx = atoi(v);
      mandelclick = 1;
    }
    else if (!strcmp(w,"MANDEL.y")) mandely = atoi(v);
    else if (!strcmp(w,"MCENTERX")) mcenterx = atof(v);
    else if (!strcmp(w,"MCENTERY")) mcentery = atof(v);
    else if (!strcmp(w,"MRADIUS"))  mradiusx = atof(v);
    else if (!strcmp(w,"MSOURCE"))  msource = v;
    else if (!strcmp(w,"MCLICKS"))  {
      if       (!strcmp(v,"GETJULIA"))  getjulia = 1;
      else if  (!strcmp(v,"MAGMANDEL")) magmandel = 1;
    }

    else if (!strcmp(w,"WIDTH"))      width = atoi(v);
    else if (!strcmp(w,"HEIGHT"))     height = atoi(v);
    else if (!strcmp(w,"JWIDTHOLD"))  jwidthold = atoi(v);
    else if (!strcmp(w,"JHEIGHTOLD")) jheightold = atoi(v);
    else if (!strcmp(w,"MWIDTHOLD"))  mwidthold = atoi(v);
    else if (!strcmp(w,"MHEIGHTOLD")) mheightold = atoi(v);
    else if (!strcmp(w,"ITER"))       iter = atoi(v);
    else if (!strcmp(w,"MAG"))        mag = atof(v);
    else if (!strcmp(w,"STYLE"))      style = atoi(v);
    else if (!strcmp(w,"ESCAPE"))     escape = atoi(v);
    else if (!strcmp(w,"PATTERN"))    pattern = atoi(v);
    else if (!strcmp(w,"WRAP"))       wrap = atoi(v);
    else if (!strcmp(w,"MPLANE"))     mplane = atoi(v);
    else if (!strcmp(w,"OLDMPLANE"))  oldmplane = atoi(v);
    else if (!strcmp(w,"HSOURCE"))    hsource = v;

    else printf("Can not parse <code>%s = %s</code><br>%c",w,v,10);
  }

  do_julia = (getjulia && mandelclick) || magjulia;
  do_mandel = magmandel && mandelclick;

  /* check and process the parameters */
  if (mag <= 0.0001) mag = 0.0001;
  if (width < 2)  width = 2;
  if (height < 2) height = 2;
  if (juliax > jwidthold)   juliax = jwidthold;
  if (juliay > jheightold)  juliay = jheightold;
  if (mandelx > mwidthold)  mandelx = mwidthold;
  if (mandely > mheightold) mandely = mheightold;


  jradiusy = jheightold*jradiusx/jwidthold;
  mradiusy = mheightold*mradiusx/mwidthold;

  if (magjulia) { 
    jcenterx = jcenterx - jradiusx + 2.0*jradiusx*juliax/jwidthold;
    jcentery = jcentery + jradiusy - 2.0*jradiusy*juliay/jheightold;
    jradiusx = jradiusx/mag;     jradiusy = height*jradiusx/width;
    jlx = jcenterx - jradiusx;   jhx = jcenterx + jradiusx;
    jly = jcentery - jradiusy;   jhy = jcentery + jradiusy;
  }
  else if (getjulia && mandelclick) {
    jradiusx = 1.5;     jradiusy = height*jradiusx/width; 
    jcenterx = 0.0;     jcentery = 0.0;
    jlx = jcenterx - jradiusx;   jhx = jcenterx + jradiusx;
    jly = jcentery - jradiusy;   jhy = jcentery + jradiusy;
    mux = mcenterx - mradiusx + 2.0*mradiusx*mandelx/mwidthold;
    muy = mcentery + mradiusy - 2.0*mradiusy*mandely/mheightold;
/*    changeplane(oldmplane, 1,  mux,  muy, &mux, &muy); */

  }
  if (do_mandel) { 
    mcenterx = mcenterx - mradiusx + 2.0*mradiusx*mandelx/mwidthold;
    mcentery = mcentery + mradiusy - 2.0*mradiusy*mandely/mheightold;
    mradiusx = mradiusx/mag;      mradiusy = height*mradiusx/width;
/*    if (mplane != oldmplane) {  
      mcx = mcenterx; mcy = mcentery;
      changeplane(oldmplane,mplane, mcx,mcy,&mcenterx,&mcentery);
      sum = 0.0;
      changeplane(oldmplane,mplane, mcx-mradiusx,mcy+mradiusy, &x,&y);
      sum += fabs(mcenterx-x);
      sum += fabs(mcentery-y)*mwidthold/mheightold;
      changeplane(oldmplane,mplane, mcx-mradiusx,mcy-mradiusy, &x,&y);
      sum += fabs(mcenterx-x);
      sum += fabs(mcentery-y)*mwidthold/mheightold;
      changeplane(oldmplane,mplane, mcx+mradiusx,mcy-mradiusy, &x,&y);
      sum += fabs(mcenterx-x);
      sum += fabs(mcentery-y)*mwidthold/mheightold;
      changeplane(oldmplane,mplane, mcx+mradiusx,mcy+mradiusy, &x,&y);
      sum += fabs(mcenterx-x);
      sum += fabs(mcentery-y)*mwidthold/mheightold;
      mradiusx = sum/8.0;         mradiusy = height*mradiusx/width;
      oldmplane = mplane;
    } */
    mlx = mcenterx - mradiusx;    mhx = mcenterx + mradiusx;
    mly = mcentery - mradiusy;    mhy = mcentery + mradiusy;
  }

  if (do_julia) {
     jwidthold = width; jheightold = height;
  }
  if (do_mandel) {
     mwidthold = width; mheightold = height;
  }

  /* Get the random number generator ready. */
  srand((int) time(0) % 542319);


  if ((fp = fopen("/home/djoyce/public_html/julia/expl.count","r"))==NULL)
         servererr("Couldn't open counter file.");
  fscanf(fp,"%d",&entrycount);
  fclose(fp);
  if ((fp = fopen("/home/djoyce/public_html/julia/expl.count","w+"))==NULL)
         servererr("Couldn't open counter file.");
  fprintf(fp,"%d\n",++entrycount);
  fclose(fp);

  now = time(NULL);
  thetime = ctime(&now);

  /* Choose file locations */
  sprintf(filen,"%02d",entrycount%50);

  jfn = malloc(strlen("/home/djoyce/public_html/julia/ztemp/") + 3 + strlen("j.gif"));
  strcpy(jfn,"/home/djoyce/public_html/julia/ztemp/");
  strcat(jfn,filen);
  strcat(jfn,"j.gif");

  jhn = malloc(strlen("http:/~djoyce/julia/ztemp/") + 3 + strlen("j.gif"));
  strcpy(jhn,"http:/~djoyce/julia/ztemp/");
  strcat(jhn,filen);
  strcat(jhn,"j.gif");

  mfn = malloc(strlen("/home/djoyce/public_html/julia/ztemp/") + 3 + strlen("m.gif"));
  strcpy(mfn,"/home/djoyce/public_html/julia/ztemp/");
  strcat(mfn,filen);
  strcat(mfn,"m.gif");

  mhn = malloc(strlen("http:/~djoyce/julia/ztemp/") + 3 + strlen("m.gif"));
  strcpy(mhn,"http:/~djoyce/julia/ztemp/");
  strcat(mhn,filen);
  strcat(mhn,"m.gif");

  hfn = malloc(strlen("/home/djoyce/public_html/julia/ztemp/") + 3 + strlen(".html"));
  strcpy(hfn,"/home/djoyce/public_html/julia/ztemp/");
  strcat(hfn,filen);
  strcat(hfn,".html");

  hhn = malloc(strlen("/~djoyce/julia/ztemp/") + 3 + strlen(".html"));
  strcpy(hhn,"/~djoyce/julia/ztemp/");
  strcat(hhn,filen);
  strcat(hhn,".html");

  if (do_julia)  jsource = jhn;
  if (do_mandel) msource = mhn;

  if ((fp = fopen(hfn,"w"))==NULL)
         servererr("Couldn't open output file.");

  fprintf(fp,"<HTML><HEAD><TITLE>Mandelbrot and Julia Set Explorer</TITLE>%c",10);
  fprintf(fp,"<link rev=\"made\" href=\"mailto:djoyce@aleph0.clarku.edu\"></HEAD><BODY>%c",10);

  fprintf(fp,"<center><H1>Mandelbrot and Julia Set Explorer</H1>%c",10);

  fprintf(fp,"For background on Julia and Mandelbrot sets, see the%c",10);
  fprintf(fp,"<a href=\"http://aleph0.clarku.edu/~djoyce/julia/julia.html\"> introduction.</a>%c",10);

  fprintf(fp,"There is <a href=\"http:/~djoyce/julia/explhelp.html\">detailed%c",10);
  fprintf(fp,"help</a> available for using this form if it isn't self evident.%c",10);

  fprintf(fp,"<hr><FORM METHOD=\"POST\" ACTION=\"http://aleph0.clarku.edu/~djoyce/cgi-bin/expl.cgi\">%c",10);

  if (strcmp(jsource,"NONE")) 
    fprintf(fp,"<p><table border=8>%c",10);
  else
    fprintf(fp,"<p><table border=12>%c",10);

  fprintf(fp,"<tr><td><INPUT TYPE=\"image\"  NAME=\"MANDEL\" SRC=\"%s\">%c",msource,10);
  if (strcmp(jsource,"NONE")) 
    fprintf(fp,"<td><INPUT TYPE=\"image\"  NAME=\"JULIA\" SRC=\"%s\">%c",jsource,10);

  fprintf(fp,"<tr><td><br><b>Mandelbrot Set</b> %c",10);
/*  if (oldmplane==2) fprintf(fp," (in the lambda plane)%c",10);
  else if (oldmplane==3) fprintf(fp," (in the 1/mu plane)%c",10);
  else if (oldmplane==4) fprintf(fp," (in the 1/(mu+.25) plane)%c",10);
  else if (oldmplane==5) fprintf(fp," (in the 1/lambda plane)%c",10);
  else if (oldmplane==6) fprintf(fp," (in the 1/(lambda-1) plane)%c",10);
  else if (oldmplane==7) fprintf(fp," (in the 1/(mu-1.40115) plane)%c",10); */
  fprintf(fp,":<br><i>x</i> in [%.8f,%.8f];<br><i>y</i> in [%.8f,%.8f].%c",mcenterx-mradiusx,
        mcenterx+mradiusx, mcentery-mradiusy,mcentery+mradiusy,10);

  if (strcmp(jsource,"NONE")) {
    fprintf(fp,"<td><br><b>Julia Set</b>:<br><i>x</i> in [%.8f,%.8f];<br><i>y</i> in [%.8f,%.8f].%c",jcenterx-jradiusx,
        jcenterx+jradiusx, jcentery-jradiusy,jcentery+jradiusy,10);
    if (muy>=0)
      fprintf(fp,"<br>mu = %.9f+%.9fi.%c",mux,muy,10);
    else
      fprintf(fp,"<br>mu = %.9f%.9fi.%c",mux,muy,10);
/*    if (mplane==2 || mplane==5 || mplane==6) {
      changeplane(1, 2,  mux,  muy, &x, &y);
      if (y>=0)
        fprintf(fp,"<br>lambda = %.9f+%.9fi.%c",x,y,10);
      else
        fprintf(fp,"<br>lambda = %.9f%.9fi.%c",x,y,10);
    } */
  }
  fprintf(fp,"</table></center><hr>%c",10);

  fprintf(fp,"<h2>Parameters</h2>%c",10);
  fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"HSOURCE\" VALUE=\"%s\">%c",hhn,10);
  fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"MCENTERX\" VALUE=\"%.14f\">%c",mcenterx,10);
  fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"MCENTERY\" VALUE=\"%.14f\">%c",mcentery,10);
  fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"MRADIUS\" VALUE=\"%.14f\">%c",mradiusx,10);
  fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"MWIDTHOLD\" VALUE=\"%d\">%c",mwidthold,10);
  fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"MHEIGHTOLD\" VALUE=\"%d\">%c",mheightold,10);
  fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"MSOURCE\" VALUE=\"%s\">%c",msource,10);
/*  fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"OLDMPLANE\" VALUE=\"%d\">%c",oldmplane,10); */

  fprintf(fp,"<p>Clicks on the Mandelbrot set image will<br>%c",10);

  fprintf(fp,"<INPUT TYPE=\"checkbox\" NAME=\"MCLICKS\" VALUE=\"GETJULIA\" %c",10);
  if (getjulia) fprintf(fp,"CHECKED%c",10);
  fprintf(fp,"> get a Julia set <br>%c",10);
  fprintf(fp,"<INPUT TYPE=\"checkbox\" NAME=\"MCLICKS\" VALUE=\"MAGMANDEL\" %c",10);
  if (magmandel) fprintf(fp,"CHECKED%c",10);
  fprintf(fp,"> magnify the Mandelbrot set%c",10);

/*  fprintf(fp,"<p>Alternate parameter plane <SELECT NAME=\"MPLANE\"><OPTION %c",10); 
  if (mplane==1) fprintf(fp,"SELECTED %c",10);
  fprintf(fp,"VALUE=1> mu <OPTION  %c",10);
  if (mplane==2) fprintf(fp,"SELECTED %c",10);
  fprintf(fp,"VALUE=2> lambda (mu = lambda^2/4-lambda/2) <OPTION %c",10);
  if (mplane==3) fprintf(fp,"SELECTED %c",10);
  fprintf(fp,"VALUE=3> 1/mu <OPTION %c",10);
  if (mplane==4) fprintf(fp,"SELECTED %c",10);
  fprintf(fp,"VALUE=4> 1/(mu+.25) <OPTION %c",10);
  if (mplane==5) fprintf(fp,"SELECTED %c",10);
  fprintf(fp,"VALUE=5> 1/lambda <OPTION %c",10);
  if (mplane==6) fprintf(fp,"SELECTED %c",10);
  fprintf(fp,"VALUE=6> 1/(lambda-1) <OPTION %c",10);
  if (mplane==7) fprintf(fp,"SELECTED %c",10);
  fprintf(fp,"VALUE=7> 1/(mu-%f) </SELECT>%c",MYERBERG,10); */

  fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"JSOURCE\" VALUE=\"%s\">%c",jsource,10);
  if (strcmp(jsource,"NONE")) {
    fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"JCENTERX\" VALUE=\"%.14f\">%c",jcenterx,10);
    fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"JCENTERY\" VALUE=\"%.14f\">%c",jcentery,10);
    fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"JRADIUS\" VALUE=\"%.14f\">%c",jradiusx,10);
    fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"JWIDTHOLD\" VALUE=\"%d\">%c",jwidthold,10);
    fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"JHEIGHTOLD\" VALUE=\"%d\">%c",jheightold,10);
    fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"MUX\" VALUE=\"%.14f\">%c",mux,10);
    fprintf(fp,"<INPUT TYPE=\"hidden\" NAME=\"MUY\" VALUE=\"%.14f\">%c",muy,10);
    fprintf(fp,"<br>Clicks on the Julia set image will magnify the Julia set.%c",10);
  }

  fprintf(fp,"<p>Image magnification factor = %c",10);
  fprintf(fp,"<INPUT NAME=\"MAG\" SIZE=7 VALUE=\"%.3f\"><br>%c",mag,10);

  fprintf(fp,"Image: width=<INPUT NAME=\"WIDTH\" SIZE=9 VALUE=\"%d\"> by%c",width,10);
  fprintf(fp,"height=<INPUT NAME=\"HEIGHT\" SIZE=9 VALUE=\"%d\"> in pixels.<br>%c",height,10);

  fprintf(fp,"Maximum number of iterations=<INPUT NAME=\"ITER\" SIZE=9 VALUE=\"%d\"><p>%c",iter,10);

  fprintf(fp,"Note that it may take a while to compute an image if you%c",10);
  fprintf(fp,"ask for a big image or a lot of iterations.%c",10);


  fprintf(fp,"<h2>Image Rendition</h2>%c",10);
  fprintf(fp,"Image colors <SELECT NAME=\"STYLE\"><OPTION VALUE=\"1\" %c",10);
  if (style==1) fprintf (fp,"SELECTED%c",10);
  fprintf(fp,"> Color images%c",10);
  fprintf(fp,"<OPTION VALUE=\"2\" %c",10);
  if (style==2) fprintf (fp,"SELECTED%c",10);
  fprintf(fp,"> Greyscale images%c",10);
  fprintf(fp,"<OPTION VALUE=\"3\" %c",10);
  if (style==3) fprintf (fp,"SELECTED%c",10);
  fprintf(fp,"> Zebra (black & white)</SELECT>%c",10);

  fprintf(fp,"Wrap through the colors<INPUT NAME=\"WRAP\" SIZE=5 VALUE=\"%d\"> times%c",wrap,10);

  fprintf(fp,"<br>Escape criteria: <SELECT NAME=\"ESCAPE\"><OPTION VALUE=\"1\" %c",10);
  if (escape==1) fprintf (fp,"SELECTED%c",10);
  fprintf(fp,"> circular (standard)<OPTION VALUE=\"2\" %c",10);
  if (escape==2) fprintf (fp,"SELECTED%c",10);
  fprintf(fp,"> square<OPTION VALUE=\"3\" %c",10);
  if (escape==3) fprintf (fp,"SELECTED%c",10);
  fprintf(fp,"> half plane</SELECT>%c",10);

  fprintf(fp,"Level pattern: <SELECT NAME=\"PATTERN\"><OPTION VALUE=\"1\" %c",10);
  if (pattern==1) fprintf (fp,"SELECTED%c",10);
  fprintf(fp,"> plain<OPTION VALUE=\"2\" %c",10);
  if (pattern==2) fprintf (fp,"SELECTED%c",10);
  fprintf(fp,"> feathered<OPTION VALUE=\"3\" %c",10);
  if (pattern==3) fprintf (fp,"SELECTED%c",10);
  fprintf(fp,"> binary</SELECT>%c",10);



  fprintf(fp,"<hr><INPUT TYPE=\"reset\" VALUE=\"Reset default values on this form\"></FORM>%c",10);

  fprintf(fp,"<a href=\"%s\">%c",msource,10);
  fprintf(fp,"Download the Mandelbrot set image</a>%c",10);


  if (strcmp(jsource,"NONE")) {
    fprintf(fp,"<br><a href=\"%s\">%c",jsource,10);
    fprintf(fp,"Download the Julia set image</a>%c",10);
  }
  fprintf(fp,"<br><a href=\"%s\"> Return to previous page</a>%c",hsource,10);
  fprintf(fp,"<br><a href=\"/~djoyce/julia/explorer.html\"> Return to the first Mandelbrot set</a>%c",10);

  fprintf(fp,"<br><a href=\"/~djoyce/julia/ztemp/\"> Index of recently created images</a><p>%c",10);

  fprintf(fp,"<hr>This is image number %d.  It was <a href=""http://aleph0.clarku.edu/~djoyce/julia/explorer.html""> produced</a>%c",entrycount,10);
  fprintf(fp,"at <a href=""http://aleph0.clarku.edu/""> Clark University</a>%c",10);
  fprintf(fp,"for %s on %s.<p>%c",getenv("REMOTE_HOST"),thetime,10);
  fprintf(fp,"<ADDRESS><A href=\"http://aleph0.clarku.edu/~djoyce/home.html\">David E. Joyce</a>%c",10);
  fprintf(fp,"(djoyce@black.clarku.edu)</ADDRESS><p>%c", 10);
  fprintf(fp,"Program created September, 1994%c",10);
  fprintf(fp,"</BODY></HTML>%c",10);

  fclose(fp);

  /* tell the server where the html file is */
  sendmesg(hhn);

  /* Compute the images and put them in files */
  if (do_julia) {
    if ((fp = fopen(jfn,"w"))==NULL)
         servererr("Couldn't open output file.");
    julia(fp, 1, 1, mux,muy, jlx,jly,jhx,jhy, 
              width,height,iter,style,wrap,escape,pattern); 
    fclose(fp);
  }
  if (do_mandel) {
    if ((fp = fopen(mfn,"w"))==NULL)
         servererr("Couldn't open output file.");
    julia(fp, 0, mux,muy, mlx,mly,mhx,mhy, 
              width,height,iter,style,wrap,escape,pattern); 
    fclose(fp);
  }

}
