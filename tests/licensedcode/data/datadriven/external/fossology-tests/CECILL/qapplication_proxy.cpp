
/*
 *  This file is part of the Qt4Ada project, an Ada2005 binding to the Qt
 *  C++ library.
 *  © Copyright (C) Yves Bailly <kafka.fr@laposte.net> 2006
 *
 *  This version of Qt4Ada is released under the terms of the
 *  CeCILL license version 2 (http://www.cecill.info/index.en.html).
 *
 *  See the Licence_CeCILL_V2-en.txt file for details.
 *
 * -------------------------------------------------------------------------
 *
 *  Ce fichier fait partie du projet Qt4Ada, une liaison en Ada2005 vers la
 *  bibliothèque C++ Qt4.
 *  © Copyright (C) Yves Bailly <kafka.fr@laposte.net> 2006
 *
 *  Cette version de Qt4Ada est distribuée selon les termes de la license
 *  CeCILL version 2 (http://www.cecill.info/index.fr.html).
 *
 *  Voyez le fichier Licence_CeCILL_V2-fr.txt pour plus de détails.
 */

#include <iostream>
#include <QApplication>

#include "qapplication_proxy.h"

QApplication_Proxy::QApplication_Proxy(Ada_Access adaadrs,
                                       bool own,
                                       int& argc,
                                       char** argv):
   QApplication(argc, argv),
   _ada(adaadrs, own)
{
}

extern "C"
{
   QApplication_Proxy*
         QApplication_QApplication_Int_Chars(Ada_Access adaadrs,
                                             int argc,
                                             char** argv)
   {
      static int s_argc = argc;
      static char** s_argv = 0;
      if ( s_argv == 0 )
      {
         s_argv = new char* [s_argc];
         for(int i_arg = 0; i_arg < s_argc; ++i_arg)
         {
            const unsigned len = strlen(argv[i_arg]);
            s_argv[i_arg] = new char[len+1];
            memcpy(s_argv[i_arg], argv[i_arg], len+1);
            s_argv[i_arg][len] = '\0';
         }
      }
      return new QApplication_Proxy(adaadrs, false, s_argc, s_argv);
   }

   int QApplication_Static_Exec()
   {
      return QApplication::exec();
   }

   void Delete_QApplication_Proxy(QApplication_Proxy* qap)
   {
      delete qap;
   }
}

