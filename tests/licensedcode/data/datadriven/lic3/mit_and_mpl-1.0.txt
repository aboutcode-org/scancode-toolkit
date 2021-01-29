/*
 * udll.cxx
 *
 * Dynamic Link Library implementation.
 *
 * Portable Windows Library
 *
 * Copyright (c) 1993-1998 Equivalence Pty. Ltd.
 *
 * The contents of this file are subject to the Mozilla Public License
 * Version 1.0 (the "License"); you may not use this file except in
 * compliance with the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS"
 * basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
 * the License for the specific language governing rights and limitations
 * under the License.
 *
 * The Original Code is Portable Windows Library.
 *
 * The Initial Developer of the Original Code is Equivalence Pty. Ltd.
 *
 * Portions are Copyright (C) 1993 Free Software Foundation, Inc.
 * All Rights Reserved.
 *
 * Contributor(s): ______________________________________.
 *
 * $Log$
 * Revision 1.1  2006/06/29 04:18:41  joegenbaclor
 * *** empty log message ***
 *
 * Revision 1.19  2005/11/30 12:47:42  csoutheren
 * Removed tabs, reformatted some code, and changed tags for Doxygen
 *
 * Revision 1.18  2005/08/04 20:10:24  csoutheren
 * Apply patch #1217596
 * Fixed problems with MacOSX Tiger
 * Thanks to Hannes Friederich
 *
 * Revision 1.17  2004/05/11 01:15:53  csoutheren
 * Included name into Unix PDynaLink implementation
 *
 * Revision 1.16  2003/09/11 00:52:13  dereksmithies
 * Full dependancy check on dynamically loading a library.
 * Thanks to Snark on #gnomemeeting for pointing this out...
 *
 * Revision 1.15  2003/07/09 11:37:13  rjongbloed
 * Fixed corrct closing of DLL (setting handle to NULL) thanks Fabrizio Ammollo
 *
 * Revision 1.14  2003/05/14 10:50:30  dereksmithies
 * Quick hack to add the function: PDynaLink::GetName().  Fix me.
 *
 * Revision 1.13  2003/05/06 06:59:12  robertj
 * Dynamic library support for MacOSX, thanks Hugo Santos
 *
 * Revision 1.12  2003/04/16 07:17:35  craigs
 * CHanged to use new #define
 *
 * Revision 1.11  2001/06/30 06:59:07  yurik
 * Jac Goudsmit from Be submit these changes 6/28. Implemented by Yuri Kiryanov
 *
 * Revision 1.10  2001/03/07 06:57:52  yurik
 * Changed email to current one
 *
 * Revision 1.9  2000/03/10 08:21:17  rogerh
 * Add correct OpenBSD support
 *
 * Revision 1.8  2000/03/09 18:41:53  rogerh
 * Workaround for OpenBSD. This breaks the functionality on OpenBSD but
 * gains us a clean compilation. We can return to this problem later.
 *
 * Revision 1.7  1999/02/22 13:26:54  robertj
 * BeOS port changes.
 *
 * Revision 1.6  1999/02/06 05:49:44  robertj
 * BeOS port effort by Yuri Kiryanov <openh323@kiryanov.com>
 *
 * Revision 1.5  1998/11/30 21:52:03  robertj
 * New directory structure.
 *
 * Revision 1.4  1998/09/24 04:12:26  robertj
 * Added open software license.
 *
 * Revision 1.3  1998/01/04 08:11:41  craigs
 * Remove Solarisism and made platform independent
 *
 * Revision 1.2  1997/10/30 12:41:22  craigs
 * Added GetExtension command
 *
 * Revision 1.1  1997/04/22 10:58:17  craigs
 * Initial revision
 *
 *
 */

#pragma implementation "dynalink.h"

#include <ptlib.h>

#ifdef P_MACOSX
#if P_MACOSX < 700

/*
Copyright (c) 2002 Peter O'Gorman <ogorman@users.sourceforge.net>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/


/* Just to prove that it isn't that hard to add Mac calls to your code :)
   This works with pretty much everything, including kde3 xemacs and the gimp,
   I'd guess that it'd work in at least 95% of cases, use this as your starting
   point, rather than the mess that is dlfcn.c, assuming that your code does not
   require ref counting or symbol lookups in dependent libraries
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <stdarg.h>
#include <limits.h>
#include <mach-o/dyld.h>

#define RTLD_LAZY       0x1
#define RTLD_NOW        0x2
#define RTLD_LOCAL      0x4
#define RTLD_GLOBAL     0x8
#define RTLD_NOLOAD     0x10
#define RTLD_NODELETE   0x80

#define ERR_STR_LEN 256

static void *dlsymIntern(void *handle, const char *symbol);

static const char *error(int setget, const char *str, ...);



/* Set and get the error string for use by dlerror */
static const char *error(int setget, const char *str, ...)
{
  static char errstr[ERR_STR_LEN];
  static int err_filled = 0;
  const char *retval;
  va_list arg;
  if (setget == 0)
  {
    va_start(arg, str);
    strncpy(errstr, "dlsimple: ", ERR_STR_LEN);
    vsnprintf(errstr + 10, ERR_STR_LEN - 10, str, arg);
    va_end(arg);
    err_filled = 1;
    retval = NULL;
  }
  else
  {
    if (!err_filled)
      retval = NULL;
    else
      retval = errstr;
    err_filled = 0;
  }
  return retval;
}

/* dlopen */
static void *dlopen(const char *path, int mode)
{
  void *module = 0;
  NSObjectFileImage ofi = 0;
  NSObjectFileImageReturnCode ofirc;
  static int (*make_private_module_public) (NSModule module) = 0;
  unsigned int flags =  NSLINKMODULE_OPTION_RETURN_ON_ERROR | NSLINKMODULE_OPTION_PRIVATE;

  /* If we got no path, the app wants the global namespace, use -1 as the marker
     in this case */
  if (!path)
    return (void *)-1;

  /* Create the object file image, works for things linked with the -bundle arg to ld */
  ofirc = NSCreateObjectFileImageFromFile(path, &ofi);
  switch (ofirc)
  {
    case NSObjectFileImageSuccess:
      /* It was okay, so use NSLinkModule to link in the image */
      if (!(mode & RTLD_LAZY)) flags += NSLINKMODULE_OPTION_BINDNOW;
      module = NSLinkModule(ofi, path,flags);
      /* Don't forget to destroy the object file image, unless you like leaks */
      NSDestroyObjectFileImage(ofi);
      /* If the mode was global, then change the module, this avoids
         multiply defined symbol errors to first load private then make
         global. Silly, isn't it. */
      if ((mode & RTLD_GLOBAL))
      {
        if (!make_private_module_public)
        {
          _dyld_func_lookup("__dyld_NSMakePrivateModulePublic", 
        (unsigned long *)&make_private_module_public);
        }
        make_private_module_public(module);
      }
      break;
    case NSObjectFileImageInappropriateFile:
      /* It may have been a dynamic library rather than a bundle, try to load it */
      module = (void *)NSAddImage(path, NSADDIMAGE_OPTION_RETURN_ON_ERROR);
      break;
    case NSObjectFileImageFailure:
      error(0,"Object file setup failure :  \"%s\"", path);
      return 0;
    case NSObjectFileImageArch:
      error(0,"No object for this architecture :  \"%s\"", path);
      return 0;
    case NSObjectFileImageFormat:
      error(0,"Bad object file format :  \"%s\"", path);
      return 0;
    case NSObjectFileImageAccess:
      error(0,"Can't read object file :  \"%s\"", path);
      return 0;    
  }
  if (!module)
    error(0, "Can not open \"%s\"", path);
  return module;
}

/* dlsymIntern is used by dlsym to find the symbol */
static void *dlsymIntern(void *handle, const char *symbol)
{
  NSSymbol *nssym = 0;
  /* If the handle is -1, if is the app global context */
  if (handle == (void *)-1)
  {
    /* Global context, use NSLookupAndBindSymbol */
    if (NSIsSymbolNameDefined(symbol))
    {
      nssym = NSLookupAndBindSymbol(symbol);
    }

  }
  /* Now see if the handle is a struch mach_header* or not, use NSLookupSymbol in image
     for libraries, and NSLookupSymbolInModule for bundles */
  else
  {
    /* Check for both possible magic numbers depending on x86/ppc byte order */
    if ((((struct mach_header *)handle)->magic == MH_MAGIC) ||
      (((struct mach_header *)handle)->magic == MH_CIGAM))
    {
      if (NSIsSymbolNameDefinedInImage((struct mach_header *)handle, symbol))
      {
        nssym = NSLookupSymbolInImage((struct mach_header *)handle,
                        symbol,
                        NSLOOKUPSYMBOLINIMAGE_OPTION_BIND
                        | NSLOOKUPSYMBOLINIMAGE_OPTION_RETURN_ON_ERROR);
      }

    }
    else
    {
      nssym = NSLookupSymbolInModule(handle, symbol);
    }
  }
  if (!nssym)
  {
    error(0, "Symbol \"%s\" Not found", symbol);
    return NULL;
  }
  return NSAddressOfSymbol(nssym);
}

static const char *dlerror(void)
{
  return error(1, (char *)NULL);
}

static int dlclose(void *handle)
{
  if ((((struct mach_header *)handle)->magic == MH_MAGIC) ||
    (((struct mach_header *)handle)->magic == MH_CIGAM))
  {
    error(0, "Can't remove dynamic libraries on darwin");
    return 0;
  }
  if (!NSUnLinkModule(handle, 0))
  {
    error(0, "unable to unlink module %s", NSNameOfModule(handle));
    return 1;
  }
  return 0;
}


/* dlsym, prepend the underscore and call dlsymIntern */
static void *dlsym(void *handle, const char *symbol)
{
  static char undersym[257];  /* Saves calls to malloc(3) */
  int sym_len = strlen(symbol);
  void *value = NULL;
  char *malloc_sym = NULL;

  if (sym_len < 256)
  {
    snprintf(undersym, 256, "_%s", symbol);
    value = dlsymIntern(handle, undersym);
  }
  else
  {
    malloc_sym = malloc(sym_len + 2);
    if (malloc_sym)
    {
      sprintf(malloc_sym, "_%s", symbol);
      value = dlsymIntern(handle, malloc_sym);
      free(malloc_sym);
    }
    else
    {
      error(0, "Unable to allocate memory");
    }
  }
  return value;
}

#else

// The functionality implemented above ships directly with MacOSX 10.3 and later
#include <dlfcn.h>

#endif // P_MACOSX < 700

#endif // P_MACOSX

#ifndef  P_DYNALINK

#warning "No implementation for dynamic library functions"

#else

PDynaLink::PDynaLink()
{
  dllHandle = NULL;
}

PDynaLink::PDynaLink(const PString & _name)
  : name(_name)
{
  dllHandle = NULL;
  Open(_name);
}

PDynaLink::~PDynaLink()
{
  Close();
}

PString PDynaLink::GetExtension()
{
  return PString(".so");
}

BOOL PDynaLink::Open(const PString & _name)
{
  Close();

  name = _name;

#if defined(P_OPENBSD)
  dllHandle = dlopen((char *)(const char *)name, RTLD_NOW);
#else
  dllHandle = dlopen((const char *)name, RTLD_NOW);
#endif

  return IsLoaded();
}

void PDynaLink::Close()
{
  if (dllHandle != NULL) {
    dlclose(dllHandle);
    dllHandle = NULL;
  }
  name.MakeEmpty();
}

BOOL PDynaLink::IsLoaded() const
{
  return dllHandle != NULL;
}

PString PDynaLink::GetName(BOOL full) const
{
  if (!IsLoaded())
    return "";

  PString str = name;
  PINDEX pos = str.FindLast('/');
  if (pos != P_MAX_INDEX)
    str = str.Mid(pos+1);
  pos = str.FindLast(".so");
  if (pos != P_MAX_INDEX)
    str = str.Left(pos);

  return str;
}


BOOL PDynaLink::GetFunction(PINDEX, Function &)
{
  return FALSE;
}

BOOL PDynaLink::GetFunction(const PString & fn, Function & func)
{
  if (dllHandle == NULL)
    return FALSE;

#if defined(P_OPENBSD)
  void * p = dlsym(dllHandle, (char *)(const char *)fn);
#else
  void * p = dlsym(dllHandle, (const char *)fn);
#endif

  if (p == NULL)
    return FALSE;

  func = (Function &)p;
  return TRUE;
}

#endif

// End of file

