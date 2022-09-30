/****************************************************************************
**
** Copyright (C) 2015 The Qt Company Ltd.
** Copyright (C) 2015 Intel Corporation
** Contact: http://www.qt.io/licensing/
**
** This file is part of the tools applications of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:LGPL21$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see http://www.qt.io/terms-conditions. For further
** information use the contact form at http://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 2.1 or version 3 as published by the Free
** Software Foundation and appearing in the file LICENSE.LGPLv21 and
** LICENSE.LGPLv3 included in the packaging of this file. Please review the
** following information to ensure the GNU Lesser General Public License
** requirements will be met: https://www.gnu.org/licenses/lgpl.html and
** http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
**
** As a special exception, The Qt Company gives you certain additional
** rights. These rights are described in The Qt Company LGPL Exception
** version 1.1, included in the file LGPL_EXCEPTION.txt in this package.
**
** $QT_END_LICENSE$
**
****************************************************************************/

// We could use QDir::homePath() + "/.qt-license", but
// that will only look in the first of $HOME,$USERPROFILE
// or $HOMEDRIVE$HOMEPATH. So, here we try'em all to be
// more forgiving for the end user..
QString Configure::firstLicensePath()
{
    QStringList allPaths;
    allPaths << "./.qt-license"
             << QString::fromLocal8Bit(getenv("HOME")) + "/.qt-license"
             << QString::fromLocal8Bit(getenv("USERPROFILE")) + "/.qt-license"
             << QString::fromLocal8Bit(getenv("HOMEDRIVE")) + QString::fromLocal8Bit(getenv("HOMEPATH")) + "/.qt-license";
    for (int i = 0; i< allPaths.count(); ++i)
        if (QFile::exists(allPaths.at(i)))
            return allPaths.at(i);
    return QString();
}

// #### somehow I get a compiler error about vc++ reaching the nesting limit without
// undefining the ansi for scoping.
#ifdef for
#undef for
#endif

void Configure::parseCmdLine()
{
    if (configCmdLine.size() && configCmdLine.at(0) == "-top-level") {
        dictionary[ "TOPLEVEL" ] = "yes";
        configCmdLine.removeAt(0);
    }

    int argCount = configCmdLine.size();
    int i = 0;
    const QStringList imageFormats = QStringList() << "gif" << "png" << "jpeg";

    if (argCount < 1) // skip rest if no arguments
        ;
    else if (configCmdLine.at(i) == "-redo") {
        dictionary[ "REDO" ] = "yes";
        configCmdLine.clear();
        reloadCmdLine();
    }

    else if (configCmdLine.at(i) == "-loadconfig") {
        ++i;
        if (i != argCount) {
            dictionary[ "REDO" ] = "yes";
            dictionary[ "CUSTOMCONFIG" ] = "_" + configCmdLine.at(i);
            configCmdLine.clear();
            reloadCmdLine();
        } else {
            dictionary[ "DONE" ] = "error";
        }
        i = 0;
    }
    argCount = configCmdLine.size();

    bool isDeviceMkspec = false;

    // Look first for XQMAKESPEC
    for (int j = 0 ; j < argCount; ++j)
    {
        if ((configCmdLine.at(j) == "-xplatform") || (configCmdLine.at(j) == "-device")) {
            isDeviceMkspec = (configCmdLine.at(j) == "-device");
            ++j;
            if (j == argCount)
                break;
            dictionary["XQMAKESPEC"] = configCmdLine.at(j);
            applySpecSpecifics();
            break;
        }
    }

void Configure::generateConfigfiles()
{
    {
        FileWriter tmpStream(buildPath + "/src/corelib/global/qconfig.h");

        tmpStream << "#define QT_VERSION_MAJOR    " << dictionary["VERSION_MAJOR"] << endl
                  << "#define QT_VERSION_MINOR    " << dictionary["VERSION_MINOR"] << endl
                  << "#define QT_VERSION_PATCH    " << dictionary["VERSION_PATCH"] << endl
                  << "#define QT_VERSION_STR      \"" << dictionary["VERSION"] << "\"\n"
                  << endl;

        if (dictionary[ "QCONFIG" ] == "full") {
            tmpStream << "/* Everything */" << endl;
        } else {
            tmpStream << "#ifndef QT_BOOTSTRAPPED" << endl;
            QFile inFile(dictionary["QCONFIG_PATH"]);
            if (inFile.open(QFile::ReadOnly)) {
                tmpStream << QTextStream(&inFile).readAll();
                inFile.close();
            }
            tmpStream << "#endif // QT_BOOTSTRAPPED" << endl;
        }
        tmpStream << endl;

        if (dictionary[ "SHARED" ] == "no") {
            tmpStream << "/* Qt was configured for a static build */" << endl
                      << "#if !defined(QT_SHARED) && !defined(QT_STATIC)" << endl
                      << "# define QT_STATIC" << endl
                      << "#endif" << endl
                      << endl;
        }
        tmpStream << "/* License information */" << endl;
        tmpStream << "#define QT_PRODUCT_LICENSEE \"" << dictionary[ "LICENSEE" ] << "\"" << endl;
        tmpStream << "#define QT_PRODUCT_LICENSE \"" << dictionary[ "EDITION" ] << "\"" << endl;
        tmpStream << endl;
        if (dictionary["BUILDDEV"] == "yes") {
            dictionary["QMAKE_INTERNAL"] = "yes";
            tmpStream << "/* Used for example to export symbols for the certain autotests*/" << endl;
            tmpStream << "#define QT_BUILD_INTERNAL" << endl;
            tmpStream << endl;
        }

        tmpStream << endl << "// Compiler sub-arch support" << endl;
        if (dictionary[ "SSE2" ] == "yes")
            tmpStream << "#define QT_COMPILER_SUPPORTS_SSE2 1" << endl;
        if (dictionary[ "SSE3" ] == "yes")
            tmpStream << "#define QT_COMPILER_SUPPORTS_SSE3 1" << endl;
        if (dictionary[ "SSSE3" ] == "yes")
            tmpStream << "#define QT_COMPILER_SUPPORTS_SSSE3 1" << endl;
        if (dictionary[ "SSE4_1" ] == "yes")
            tmpStream << "#define QT_COMPILER_SUPPORTS_SSE4_1 1" << endl;
        if (dictionary[ "SSE4_2" ] == "yes")
            tmpStream << "#define QT_COMPILER_SUPPORTS_SSE4_2 1" << endl;
        if (dictionary[ "AVX" ] == "yes")
            tmpStream << "#define QT_COMPILER_SUPPORTS_AVX 1" << endl;
        if (dictionary[ "AVX2" ] == "yes")
            tmpStream << "#define QT_COMPILER_SUPPORTS_AVX2 1" << endl;

        if (dictionary["QREAL"] != "double") {
            tmpStream << "#define QT_COORD_TYPE " << dictionary["QREAL"] << endl;
            tmpStream << "#define QT_COORD_TYPE_STRING " << dictionary["QREAL_STRING"] << endl;
        }

        tmpStream << endl << "// Compile time features" << endl;

        QStringList qconfigList;
        if (dictionary["STYLE_WINDOWS"] != "yes")     qconfigList += "QT_NO_STYLE_WINDOWS";
        if (dictionary["STYLE_FUSION"] != "yes")       qconfigList += "QT_NO_STYLE_FUSION";
        if (dictionary["STYLE_WINDOWSXP"] != "yes" && dictionary["STYLE_WINDOWSVISTA"] != "yes")
            qconfigList += "QT_NO_STYLE_WINDOWSXP";
        if (dictionary["STYLE_WINDOWSVISTA"] != "yes")   qconfigList += "QT_NO_STYLE_WINDOWSVISTA";
        if (dictionary["STYLE_WINDOWSCE"] != "yes")   qconfigList += "QT_NO_STYLE_WINDOWSCE";
        if (dictionary["STYLE_WINDOWSMOBILE"] != "yes")   qconfigList += "QT_NO_STYLE_WINDOWSMOBILE";
        if (dictionary["STYLE_GTK"] != "yes")         qconfigList += "QT_NO_STYLE_GTK";

        if (dictionary["GIF"] == "yes")              qconfigList += "QT_BUILTIN_GIF_READER=1";
        if (dictionary["PNG"] != "yes")              qconfigList += "QT_NO_IMAGEFORMAT_PNG";
        if (dictionary["JPEG"] != "yes")             qconfigList += "QT_NO_IMAGEFORMAT_JPEG";
        if (dictionary["ZLIB"] == "no") {
            qconfigList += "QT_NO_ZLIB";
            qconfigList += "QT_NO_COMPRESS";
        }

        if (dictionary["ACCESSIBILITY"] == "no")     qconfigList += "QT_NO_ACCESSIBILITY";
        if (dictionary["WIDGETS"] == "no")           qconfigList += "QT_NO_WIDGETS";
        if (dictionary["GUI"] == "no")               qconfigList += "QT_NO_GUI";
        if (dictionary["OPENGL"] == "no")            qconfigList += "QT_NO_OPENGL";
        if (dictionary["OPENVG"] == "no")            qconfigList += "QT_NO_OPENVG";
        if (dictionary["SSL"] == "no")               qconfigList += "QT_NO_SSL";
        if (dictionary["OPENSSL"] == "no")           qconfigList += "QT_NO_OPENSSL";
        if (dictionary["OPENSSL"] == "linked")       qconfigList += "QT_LINKED_OPENSSL";
        if (dictionary["DBUS"] == "no")              qconfigList += "QT_NO_DBUS";
        if (dictionary["FREETYPE"] == "no")          qconfigList += "QT_NO_FREETYPE";
        if (dictionary["HARFBUZZ"] == "no")          qconfigList += "QT_NO_HARFBUZZ";
        if (dictionary["NATIVE_GESTURES"] == "no")   qconfigList += "QT_NO_NATIVE_GESTURES";

        if (dictionary["OPENGL_ES_2"]  == "yes")     qconfigList += "QT_OPENGL_ES";
        if (dictionary["OPENGL_ES_2"]  == "yes")     qconfigList += "QT_OPENGL_ES_2";
        if (dictionary["DYNAMICGL"] == "yes")        qconfigList += "QT_OPENGL_DYNAMIC";
        if (dictionary["SQL_MYSQL"] == "yes")        qconfigList += "QT_SQL_MYSQL";
        if (dictionary["SQL_ODBC"] == "yes")         qconfigList += "QT_SQL_ODBC";
        if (dictionary["SQL_OCI"] == "yes")          qconfigList += "QT_SQL_OCI";
        if (dictionary["SQL_PSQL"] == "yes")         qconfigList += "QT_SQL_PSQL";
        if (dictionary["SQL_TDS"] == "yes")          qconfigList += "QT_SQL_TDS";
        if (dictionary["SQL_DB2"] == "yes")          qconfigList += "QT_SQL_DB2";
        if (dictionary["SQL_SQLITE"] == "yes")       qconfigList += "QT_SQL_SQLITE";
        if (dictionary["SQL_SQLITE2"] == "yes")      qconfigList += "QT_SQL_SQLITE2";
        if (dictionary["SQL_IBASE"] == "yes")        qconfigList += "QT_SQL_IBASE";

        if (dictionary["POSIX_IPC"] == "yes")
            qconfigList += "QT_POSIX_IPC";
        else if ((platform() != ANDROID) && (platform() != WINDOWS) && (platform() != WINDOWS_CE)
                    && (platform() != WINDOWS_RT))
            qconfigList << "QT_NO_SYSTEMSEMAPHORE" << "QT_NO_SHAREDMEMORY";

        if (dictionary["FONT_CONFIG"] == "no")       qconfigList += "QT_NO_FONTCONFIG";

        if (dictionary["NIS"] == "yes")
            qconfigList += "QT_NIS";
        else
            qconfigList += "QT_NO_NIS";

        if (dictionary["LARGE_FILE"] == "yes")       qconfigList += "QT_LARGEFILE_SUPPORT=64";
        if (dictionary["QT_CUPS"] == "no")           qconfigList += "QT_NO_CUPS";
        if (dictionary["QT_ICONV"] == "no")          qconfigList += "QT_NO_ICONV";
        if (dictionary["QT_EVDEV"] == "no")          qconfigList += "QT_NO_EVDEV";
        if (dictionary["QT_MTDEV"] == "no")          qconfigList += "QT_NO_MTDEV";
        if (dictionary["QT_TSLIB"] == "no")          qconfigList += "QT_NO_TSLIB";
        if (dictionary["QT_GLIB"] == "no")           qconfigList += "QT_NO_GLIB";
        if (dictionary["QT_INOTIFY"] == "no")        qconfigList += "QT_NO_INOTIFY";
        if (dictionary["QT_EVENTFD"] ==  "no")       qconfigList += "QT_NO_EVENTFD";
        if (dictionary["ATOMIC64"] == "no")          qconfigList += "QT_NO_STD_ATOMIC64";

        if (dictionary["REDUCE_EXPORTS"] == "yes")     qconfigList += "QT_VISIBILITY_AVAILABLE";
        if (dictionary["REDUCE_RELOCATIONS"] == "yes") qconfigList += "QT_REDUCE_RELOCATIONS";
        if (dictionary["QT_GETIFADDRS"] == "no")       qconfigList += "QT_NO_GETIFADDRS";

        qconfigList.sort();
        for (int i = 0; i < qconfigList.count(); ++i)
            tmpStream << addDefine(qconfigList.at(i));

        tmpStream<<"#define QT_QPA_DEFAULT_PLATFORM_NAME \"" << qpaPlatformName() << "\""<<endl;

        if (!tmpStream.flush())
            dictionary[ "DONE" ] = "error";
    }

}

QString Configure::formatConfigPath(const char *var)
{
    QString val = dictionary[var];
    if (QFileInfo(val).isRelative()) {
        QString pfx = dictionary["QT_INSTALL_PREFIX"];
        val = (val == ".") ? pfx : QDir(pfx).absoluteFilePath(val);
    }
    return QDir::toNativeSeparators(val);
}

void Configure::displayConfig()
{
    fstream sout;
    sout.open(QString(buildPath + "/config.summary").toLocal8Bit().constData(),
              ios::in | ios::out | ios::trunc);

    // Give some feedback
    sout << "Environment:" << endl;
    QString env = QString::fromLocal8Bit(getenv("INCLUDE")).replace(QRegExp("[;,]"), "\n      ");
    if (env.isEmpty())
        env = "Unset";
    sout << "    INCLUDE=\n      " << env << endl;
    env = QString::fromLocal8Bit(getenv("LIB")).replace(QRegExp("[;,]"), "\n      ");
    if (env.isEmpty())
        env = "Unset";
    sout << "    LIB=\n      " << env << endl;
    env = QString::fromLocal8Bit(getenv("PATH")).replace(QRegExp("[;,]"), "\n      ");
    if (env.isEmpty())
        env = "Unset";
    sout << "    PATH=\n      " << env << endl;

    if (dictionary[QStringLiteral("EDITION")] != QLatin1String("OpenSource")) {
        QString l1 = dictionary[ "LICENSEE" ];
        QString l2 = dictionary[ "LICENSEID" ];
        QString l3 = dictionary["EDITION"] + ' ' + "Edition";
        QString l4 = dictionary[ "EXPIRYDATE" ];
        sout << "Licensee...................." << (l1.isNull() ? "" : l1) << endl;
        sout << "License ID.................." << (l2.isNull() ? "" : l2) << endl;
        sout << "Product license............." << (l3.isNull() ? "" : l3) << endl;
        sout << "Expiry Date................." << (l4.isNull() ? "" : l4) << endl;
        sout << endl;
    }

    sout << "Configuration:" << endl;
    sout << "    " << qmakeConfig.join("\n    ") << endl;
    sout << "Qt Configuration:" << endl;
    sout << "    " << qtConfig.join("\n    ") << endl;
    sout << endl;

    if (dictionary.contains("XQMAKESPEC"))
        sout << "QMAKESPEC..................." << dictionary[ "XQMAKESPEC" ] << " (" << dictionary["QMAKESPEC_FROM"] << ")" << endl;
    else
        sout << "QMAKESPEC..................." << dictionary[ "QMAKESPEC" ] << " (" << dictionary["QMAKESPEC_FROM"] << ")" << endl;
    if (!dictionary["TARGET_OS"].isEmpty())
        sout << "Target OS..................." << dictionary["TARGET_OS"] << endl;
    sout << "Architecture................" << dictionary["QT_ARCH"]
         << ", features:" << dictionary["QT_CPU_FEATURES"] << endl;
    sout << "Host Architecture..........." << dictionary["QT_HOST_ARCH"]
         << ", features:" << dictionary["QT_HOST_CPU_FEATURES"]  << endl;
    sout << "Maketool...................." << dictionary[ "MAKE" ] << endl;
    if (dictionary[ "BUILDALL" ] == "yes") {
        sout << "Debug build................." << "yes (combined)" << endl;
        sout << "Default build..............." << dictionary[ "BUILD" ] << endl;
    } else {
        sout << "Debug......................." << (dictionary[ "BUILD" ] == "debug" ? "yes" : "no") << endl;
    }
    if (dictionary[ "BUILD" ] == "release" || dictionary[ "BUILDALL" ] == "yes")
        sout << "Force debug info............" << dictionary[ "FORCEDEBUGINFO" ] << endl;
    if (dictionary[ "BUILD" ] == "debug")
        sout << "Force optimized tools......." << dictionary[ "RELEASE_TOOLS" ] << endl;
    sout << "C++ language standard......." << dictionary[ "C++STD" ] << endl;
    sout << "Link Time Code Generation..." << dictionary[ "LTCG" ] << endl;
    sout << "Using PCH .................." << dictionary[ "PCH" ] << endl;
    sout << "Accessibility support......." << dictionary[ "ACCESSIBILITY" ] << endl;
    sout << "RTTI support................" << dictionary[ "RTTI" ] << endl;
    sout << "SSE2 support................" << dictionary[ "SSE2" ] << endl;
    sout << "SSE3 support................" << dictionary[ "SSE3" ] << endl;
    sout << "SSSE3 support..............." << dictionary[ "SSSE3" ] << endl;
    sout << "SSE4.1 support.............." << dictionary[ "SSE4_1" ] << endl;
    sout << "SSE4.2 support.............." << dictionary[ "SSE4_2" ] << endl;
    sout << "AVX support................." << dictionary[ "AVX" ] << endl;
    sout << "AVX2 support................" << dictionary[ "AVX2" ] << endl;
    sout << "NEON support................" << dictionary[ "NEON" ] << endl;
    sout << "OpenGL support.............." << dictionary[ "OPENGL" ] << endl;
    sout << "Large File support.........." << dictionary[ "LARGE_FILE" ] << endl;
    sout << "NIS support................." << dictionary[ "NIS" ] << endl;
    sout << "Iconv support..............." << dictionary[ "QT_ICONV" ] << endl;
    sout << "Evdev support..............." << dictionary[ "QT_EVDEV" ] << endl;
    sout << "Mtdev support..............." << dictionary[ "QT_MTDEV" ] << endl;
    sout << "Inotify support............." << dictionary[ "QT_INOTIFY" ] << endl;
    sout << "eventfd(7) support.........." << dictionary[ "QT_EVENTFD" ] << endl;
    sout << "Glib support................" << dictionary[ "QT_GLIB" ] << endl;
    sout << "CUPS support................" << dictionary[ "QT_CUPS" ] << endl;
    sout << "OpenVG support.............." << dictionary[ "OPENVG" ] << endl;
    sout << "SSL support................." << dictionary[ "SSL" ] << endl;
    sout << "OpenSSL support............." << dictionary[ "OPENSSL" ] << endl;
    sout << "libproxy support............" << dictionary[ "LIBPROXY" ] << endl;
    sout << "Qt D-Bus support............" << dictionary[ "DBUS" ] << endl;
    sout << "Qt Widgets module support..." << dictionary[ "WIDGETS" ] << endl;
    sout << "Qt GUI module support......." << dictionary[ "GUI" ] << endl;
    sout << "QML debugging..............." << dictionary[ "QML_DEBUG" ] << endl;
    sout << "DirectWrite support........." << dictionary[ "DIRECTWRITE" ] << endl;
    sout << "Use system proxies.........." << dictionary[ "SYSTEM_PROXIES" ] << endl;
    sout << endl;

    sout << "QPA Backends:" << endl;
    sout << "    GDI....................." << "yes" << endl;
    sout << "    Direct2D................" << dictionary[ "DIRECT2D" ] << endl;
    sout << endl;

    sout << "Third Party Libraries:" << endl;
    sout << "    ZLIB support............" << dictionary[ "ZLIB" ] << endl;
    sout << "    GIF support............." << dictionary[ "GIF" ] << endl;
    sout << "    JPEG support............" << dictionary[ "JPEG" ] << endl;
    sout << "    PNG support............." << dictionary[ "PNG" ] << endl;
    sout << "    FreeType support........" << dictionary[ "FREETYPE" ] << endl;
    sout << "    Fontconfig support......" << dictionary[ "FONT_CONFIG" ] << endl;
    sout << "    HarfBuzz support........" << dictionary[ "HARFBUZZ" ] << endl;
    sout << "    PCRE support............" << dictionary[ "PCRE" ] << endl;
    sout << "    ICU support............." << dictionary[ "ICU" ] << endl;
    if ((platform() == QNX) || (platform() == BLACKBERRY)) {
        sout << "    SLOG2 support..........." << dictionary[ "SLOG2" ] << endl;
        sout << "    IMF support............." << dictionary[ "QNX_IMF" ] << endl;
        sout << "    PPS support............." << dictionary[ "PPS" ] << endl;
        sout << "    LGMON support..........." << dictionary[ "LGMON" ] << endl;
    }
    sout << "    ANGLE..................." << dictionary[ "ANGLE" ] << endl;
    sout << "    Dynamic OpenGL.........." << dictionary[ "DYNAMICGL" ] << endl;
    sout << endl;

    sout << "Styles:" << endl;
    sout << "    Windows................." << dictionary[ "STYLE_WINDOWS" ] << endl;
    sout << "    Windows XP.............." << dictionary[ "STYLE_WINDOWSXP" ] << endl;
    sout << "    Windows Vista..........." << dictionary[ "STYLE_WINDOWSVISTA" ] << endl;
    sout << "    Fusion.................." << dictionary[ "STYLE_FUSION" ] << endl;
    sout << "    Windows CE.............." << dictionary[ "STYLE_WINDOWSCE" ] << endl;
    sout << "    Windows Mobile.........." << dictionary[ "STYLE_WINDOWSMOBILE" ] << endl;
    sout << endl;

    sout << "Sql Drivers:" << endl;
    sout << "    ODBC...................." << dictionary[ "SQL_ODBC" ] << endl;
    sout << "    MySQL..................." << dictionary[ "SQL_MYSQL" ] << endl;
    sout << "    OCI....................." << dictionary[ "SQL_OCI" ] << endl;
    sout << "    PostgreSQL.............." << dictionary[ "SQL_PSQL" ] << endl;
    sout << "    TDS....................." << dictionary[ "SQL_TDS" ] << endl;
    sout << "    DB2....................." << dictionary[ "SQL_DB2" ] << endl;
    sout << "    SQLite.................." << dictionary[ "SQL_SQLITE" ] << " (" << dictionary[ "SQL_SQLITE_LIB" ] << ")" << endl;
    sout << "    SQLite2................." << dictionary[ "SQL_SQLITE2" ] << endl;
    sout << "    InterBase..............." << dictionary[ "SQL_IBASE" ] << endl;
    sout << endl;

    sout << "Sources are in.............." << QDir::toNativeSeparators(sourcePath) << endl;
    sout << "Build is done in............" << QDir::toNativeSeparators(buildPath) << endl;
    sout << "Install prefix.............." << QDir::toNativeSeparators(dictionary["QT_INSTALL_PREFIX"]) << endl;
    sout << "Headers installed to........" << formatConfigPath("QT_REL_INSTALL_HEADERS") << endl;
    sout << "Libraries installed to......" << formatConfigPath("QT_REL_INSTALL_LIBS") << endl;
    sout << "Arch-dep. data to..........." << formatConfigPath("QT_REL_INSTALL_ARCHDATA") << endl;
    sout << "Plugins installed to........" << formatConfigPath("QT_REL_INSTALL_PLUGINS") << endl;
    sout << "Library execs installed to.." << formatConfigPath("QT_REL_INSTALL_LIBEXECS") << endl;
    sout << "QML1 imports installed to..." << formatConfigPath("QT_REL_INSTALL_IMPORTS") << endl;
    sout << "QML2 imports installed to..." << formatConfigPath("QT_REL_INSTALL_QML") << endl;
    sout << "Binaries installed to......." << formatConfigPath("QT_REL_INSTALL_BINS") << endl;
    sout << "Arch-indep. data to........." << formatConfigPath("QT_REL_INSTALL_DATA") << endl;
    sout << "Docs installed to..........." << formatConfigPath("QT_REL_INSTALL_DOCS") << endl;
    sout << "Translations installed to..." << formatConfigPath("QT_REL_INSTALL_TRANSLATIONS") << endl;
    sout << "Examples installed to......." << formatConfigPath("QT_REL_INSTALL_EXAMPLES") << endl;
    sout << "Tests installed to.........." << formatConfigPath("QT_REL_INSTALL_TESTS") << endl;

    if (dictionary.contains("XQMAKESPEC") && dictionary["XQMAKESPEC"].startsWith(QLatin1String("wince"))) {
        sout << "Using c runtime detection..." << dictionary[ "CE_CRT" ] << endl;
        sout << "Cetest support.............." << dictionary[ "CETEST" ] << endl;
        sout << "Signature..................." << dictionary[ "CE_SIGNATURE"] << endl;
        sout << endl;
    }

    if (checkAvailability("INCREDIBUILD_XGE"))
        sout << "Using IncrediBuild XGE......" << dictionary["INCREDIBUILD_XGE"] << endl;
    if (!qmakeDefines.isEmpty()) {
        sout << "Defines.....................";
        for (QStringList::Iterator defs = qmakeDefines.begin(); defs != qmakeDefines.end(); ++defs)
            sout << (*defs) << " ";
        sout << endl;
    }
    if (!qmakeIncludes.isEmpty()) {
        sout << "Include paths...............";
        for (QStringList::Iterator incs = qmakeIncludes.begin(); incs != qmakeIncludes.end(); ++incs)
            sout << (*incs) << " ";
        sout << endl;
    }
    if (!qmakeLibs.isEmpty()) {
        sout << "Additional libraries........";
        for (QStringList::Iterator libs = qmakeLibs.begin(); libs != qmakeLibs.end(); ++libs)
            sout << (*libs) << " ";
        sout << endl;
    }
    if (dictionary[ "QMAKE_INTERNAL" ] == "yes") {
        sout << "Using internal configuration." << endl;
    }
    if (dictionary[ "SHARED" ] == "no") {
        sout << "WARNING: Using static linking will disable the use of plugins." << endl;
        sout << "         Make sure you compile ALL needed modules into the library." << endl;
    }
    if (dictionary[ "OPENSSL" ] == "linked") {
        if (!opensslLibsDebug.isEmpty() || !opensslLibsRelease.isEmpty()) {
            sout << "Using OpenSSL libraries:" << endl;
            sout << "   debug  : " << opensslLibsDebug << endl;
            sout << "   release: " << opensslLibsRelease << endl;
            sout << "   both   : " << opensslLibs << endl;
        } else if (opensslLibs.isEmpty()) {
            sout << "NOTE: When linking against OpenSSL, you can override the default" << endl;
            sout << "library names through OPENSSL_LIBS and optionally OPENSSL_LIBS_DEBUG/OPENSSL_LIBS_RELEASE" << endl;
            sout << "For example:" << endl;
            sout << "    configure -openssl-linked OPENSSL_LIBS=\"-lssleay32 -llibeay32\"" << endl;
        }
    }
    if (dictionary[ "ZLIB_FORCED" ] == "yes") {
        QString which_zlib = "supplied";
        if (dictionary[ "ZLIB" ] == "system")
            which_zlib = "system";

        sout << "NOTE: The -no-zlib option was supplied but is no longer supported." << endl
             << endl
             << "Qt now requires zlib support in all builds, so the -no-zlib" << endl
             << "option was ignored. Qt will be built using the " << which_zlib
             << "zlib" << endl;
    }
    if (dictionary["OBSOLETE_ARCH_ARG"] == "yes") {
        sout << endl
             << "NOTE: The -arch option is obsolete." << endl
             << endl
             << "Qt now detects the target and host architectures based on compiler" << endl
             << "output. Qt will be built using " << dictionary["QT_ARCH"] << " for the target architecture" << endl
             << "and " << dictionary["QT_HOST_ARCH"] << " for the host architecture (note that these two" << endl
             << "will be the same unless you are cross-compiling)." << endl
             << endl;
    }
    if (dictionary["C++STD"] == "c++98") {
        sout << endl
             << "NOTE: The -no-c++11 / -c++-level c++98 option is deprecated." << endl
             << endl
             << "Qt 5.7 will require C++11 support. The options are in effect for this" << endl
             << "Qt 5.6 build, but you should update your build scripts to remove the" << endl
             << "option and, if necessary, upgrade your compiler." << endl;
    }
    if (dictionary["RELEASE_TOOLS"] == "yes" && dictionary["BUILD"] != "debug" ) {
        sout << endl
             << "NOTE:  -optimized-tools is not useful in -release mode." << endl;
    }
    if (!dictionary["PREFIX_COMPLAINTS"].isEmpty()) {
        sout << endl
             << dictionary["PREFIX_COMPLAINTS"] << endl
             << endl;
    }

    // display config.summary
    sout.seekg(0, ios::beg);
    while (sout.good()) {
        string str;
        getline(sout, str);
        cout << str << endl;
    }
}

void Configure::generateHeaders()
{
    if (dictionary["SYNCQT"] == "auto")
        dictionary["SYNCQT"] = defaultTo("SYNCQT");

    if (dictionary["SYNCQT"] == "yes") {
        if (!QStandardPaths::findExecutable(QStringLiteral("perl.exe")).isEmpty()) {
            cout << "Running syncqt..." << endl;
            QStringList args;
            args << "perl" << "-w";
            args += sourcePath + "/bin/syncqt.pl";
            args << "-version" << dictionary["VERSION"] << "-minimal" << "-module" << "QtCore";
            args += sourcePath;
            int retc = Environment::execute(args, QStringList(), QStringList());
            if (retc) {
                cout << "syncqt failed, return code " << retc << endl << endl;
                dictionary["DONE"] = "error";
            }
        } else {
            cout << "Perl not found in environment - cannot run syncqt." << endl;
            dictionary["DONE"] = "error";
        }
    }
}

void Configure::addConfStr(int group, const QString &val)
{
    confStrOffsets[group] += ' ' + QString::number(confStringOff) + ',';
    confStrings[group] += "    \"" + val + "\\0\"\n";
    confStringOff += val.length() + 1;
}

void Configure::generateQConfigCpp()
{
    QString hostSpec = dictionary["QMAKESPEC"];
    QString targSpec = dictionary.contains("XQMAKESPEC") ? dictionary["XQMAKESPEC"] : hostSpec;

    dictionary["CFG_SYSROOT"] = QDir::cleanPath(dictionary["CFG_SYSROOT"]);

    bool qipempty = false;
    if (dictionary["QT_INSTALL_PREFIX"].isEmpty())
        qipempty = true;
    else
        dictionary["QT_INSTALL_PREFIX"] = QDir::cleanPath(dictionary["QT_INSTALL_PREFIX"]);

    bool sysrootifyPrefix;
    if (dictionary["QT_EXT_PREFIX"].isEmpty()) {
        dictionary["QT_EXT_PREFIX"] = dictionary["QT_INSTALL_PREFIX"];
        sysrootifyPrefix = !dictionary["CFG_SYSROOT"].isEmpty();
    } else {
        dictionary["QT_EXT_PREFIX"] = QDir::cleanPath(dictionary["QT_EXT_PREFIX"]);
        sysrootifyPrefix = false;
    }

    bool haveHpx;
    if (dictionary["QT_HOST_PREFIX"].isEmpty()) {
        dictionary["QT_HOST_PREFIX"] = (sysrootifyPrefix ? dictionary["CFG_SYSROOT"] : QString())
                                       + dictionary["QT_INSTALL_PREFIX"];
        haveHpx = false;
    } else {
        dictionary["QT_HOST_PREFIX"] = QDir::cleanPath(dictionary["QT_HOST_PREFIX"]);
        haveHpx = true;
    }

    static const struct {
        const char *basevar, *baseoption, *var, *option;
    } varmod[] = {
        { "INSTALL_", "-prefix", "DOCS", "-docdir" },
        { "INSTALL_", "-prefix", "HEADERS", "-headerdir" },
        { "INSTALL_", "-prefix", "LIBS", "-libdir" },
        { "INSTALL_", "-prefix", "LIBEXECS", "-libexecdir" },
        { "INSTALL_", "-prefix", "BINS", "-bindir" },
        { "INSTALL_", "-prefix", "PLUGINS", "-plugindir" },
        { "INSTALL_", "-prefix", "IMPORTS", "-importdir" },
        { "INSTALL_", "-prefix", "QML", "-qmldir" },
        { "INSTALL_", "-prefix", "ARCHDATA", "-archdatadir" },
        { "INSTALL_", "-prefix", "DATA", "-datadir" },
        { "INSTALL_", "-prefix", "TRANSLATIONS", "-translationdir" },
        { "INSTALL_", "-prefix", "EXAMPLES", "-examplesdir" },
        { "INSTALL_", "-prefix", "TESTS", "-testsdir" },
        { "INSTALL_", "-prefix", "SETTINGS", "-sysconfdir" },
        { "HOST_", "-hostprefix", "BINS", "-hostbindir" },
        { "HOST_", "-hostprefix", "LIBS", "-hostlibdir" },
        { "HOST_", "-hostprefix", "DATA", "-hostdatadir" },
    };

    bool prefixReminder = false;
    for (uint i = 0; i < sizeof(varmod) / sizeof(varmod[0]); i++) {
        QString path = QDir::cleanPath(
                    dictionary[QLatin1String("QT_") + varmod[i].basevar + varmod[i].var]);
        if (path.isEmpty())
            continue;
        QString base = dictionary[QLatin1String("QT_") + varmod[i].basevar + "PREFIX"];
        if (!path.startsWith(base)) {
            if (i != 13) {
                dictionary["PREFIX_COMPLAINTS"] += QLatin1String("\n        NOTICE: ")
                        + varmod[i].option + " is not a subdirectory of " + varmod[i].baseoption + ".";
                if (i < 13 ? qipempty : !haveHpx)
                    prefixReminder = true;
            }
        } else {
            path.remove(0, base.size());
            if (path.startsWith('/'))
                path.remove(0, 1);
        }
        dictionary[QLatin1String("QT_REL_") + varmod[i].basevar + varmod[i].var]
                = path.isEmpty() ? "." : path;
    }
    if (prefixReminder) {
        dictionary["PREFIX_COMPLAINTS"]
                += "\n        Maybe you forgot to specify -prefix/-hostprefix?";
    }

    if (!qipempty) {
        // If QT_INSTALL_* have not been specified on the command line,
        // default them here, unless prefix is empty (WinCE).

        if (dictionary["QT_REL_INSTALL_HEADERS"].isEmpty())
            dictionary["QT_REL_INSTALL_HEADERS"] = "include";

        if (dictionary["QT_REL_INSTALL_LIBS"].isEmpty())
            dictionary["QT_REL_INSTALL_LIBS"] = "lib";

        if (dictionary["QT_REL_INSTALL_BINS"].isEmpty())
            dictionary["QT_REL_INSTALL_BINS"] = "bin";

        if (dictionary["QT_REL_INSTALL_ARCHDATA"].isEmpty())
            dictionary["QT_REL_INSTALL_ARCHDATA"] = ".";
        if (dictionary["QT_REL_INSTALL_ARCHDATA"] != ".")
            dictionary["QT_REL_INSTALL_ARCHDATA_PREFIX"] = dictionary["QT_REL_INSTALL_ARCHDATA"] + '/';

        if (dictionary["QT_REL_INSTALL_LIBEXECS"].isEmpty()) {
            if (targSpec.startsWith("win"))
                dictionary["QT_REL_INSTALL_LIBEXECS"] = dictionary["QT_REL_INSTALL_ARCHDATA_PREFIX"] + "bin";
            else
                dictionary["QT_REL_INSTALL_LIBEXECS"] = dictionary["QT_REL_INSTALL_ARCHDATA_PREFIX"] + "libexec";
        }

        if (dictionary["QT_REL_INSTALL_PLUGINS"].isEmpty())
            dictionary["QT_REL_INSTALL_PLUGINS"] = dictionary["QT_REL_INSTALL_ARCHDATA_PREFIX"] + "plugins";

        if (dictionary["QT_REL_INSTALL_IMPORTS"].isEmpty())
            dictionary["QT_REL_INSTALL_IMPORTS"] = dictionary["QT_REL_INSTALL_ARCHDATA_PREFIX"] + "imports";

        if (dictionary["QT_REL_INSTALL_QML"].isEmpty())
            dictionary["QT_REL_INSTALL_QML"] = dictionary["QT_REL_INSTALL_ARCHDATA_PREFIX"] + "qml";

        if (dictionary["QT_REL_INSTALL_DATA"].isEmpty())
            dictionary["QT_REL_INSTALL_DATA"] = ".";
        if (dictionary["QT_REL_INSTALL_DATA"] != ".")
            dictionary["QT_REL_INSTALL_DATA_PREFIX"] = dictionary["QT_REL_INSTALL_DATA"] + '/';

        if (dictionary["QT_REL_INSTALL_DOCS"].isEmpty())
            dictionary["QT_REL_INSTALL_DOCS"] = dictionary["QT_REL_INSTALL_DATA_PREFIX"] + "doc";

        if (dictionary["QT_REL_INSTALL_TRANSLATIONS"].isEmpty())
            dictionary["QT_REL_INSTALL_TRANSLATIONS"] = dictionary["QT_REL_INSTALL_DATA_PREFIX"] + "translations";

        if (dictionary["QT_REL_INSTALL_EXAMPLES"].isEmpty())
            dictionary["QT_REL_INSTALL_EXAMPLES"] = "examples";

        if (dictionary["QT_REL_INSTALL_TESTS"].isEmpty())
            dictionary["QT_REL_INSTALL_TESTS"] = "tests";
    }

    if (dictionary["QT_REL_HOST_BINS"].isEmpty())
        dictionary["QT_REL_HOST_BINS"] = haveHpx ? "bin" : dictionary["QT_REL_INSTALL_BINS"];

    if (dictionary["QT_REL_HOST_LIBS"].isEmpty())
        dictionary["QT_REL_HOST_LIBS"] = haveHpx ? "lib" : dictionary["QT_REL_INSTALL_LIBS"];

    if (dictionary["QT_REL_HOST_DATA"].isEmpty())
        dictionary["QT_REL_HOST_DATA"] = haveHpx ? "." : dictionary["QT_REL_INSTALL_ARCHDATA"];

    confStringOff = 0;
    addConfStr(0, dictionary["QT_REL_INSTALL_DOCS"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_HEADERS"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_LIBS"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_LIBEXECS"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_BINS"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_PLUGINS"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_IMPORTS"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_QML"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_ARCHDATA"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_DATA"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_TRANSLATIONS"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_EXAMPLES"]);
    addConfStr(0, dictionary["QT_REL_INSTALL_TESTS"]);
    addConfStr(1, dictionary["CFG_SYSROOT"]);
    addConfStr(1, dictionary["QT_REL_HOST_BINS"]);
    addConfStr(1, dictionary["QT_REL_HOST_LIBS"]);
    addConfStr(1, dictionary["QT_REL_HOST_DATA"]);
    addConfStr(1, targSpec);
    addConfStr(1, hostSpec);

    // Generate the new qconfig.cpp file
    {
        FileWriter tmpStream(buildPath + "/src/corelib/global/qconfig.cpp");
        tmpStream << "/* Licensed */" << endl
                  << "static const char qt_configure_licensee_str          [512 + 12] = \"qt_lcnsuser=" << dictionary["LICENSEE"] << "\";" << endl
                  << "static const char qt_configure_licensed_products_str [512 + 12] = \"qt_lcnsprod=" << dictionary["EDITION"] << "\";" << endl
                  << endl
                  << "/* Build date */" << endl
                  << "static const char qt_configure_installation          [11  + 12] = \"qt_instdate=2012-12-20\";" << endl
                  << endl
                  << "/* Installation Info */" << endl
                  << "static const char qt_configure_prefix_path_str       [512 + 12] = \"qt_prfxpath=" << dictionary["QT_INSTALL_PREFIX"] << "\";" << endl
                  << "#ifdef QT_BUILD_QMAKE" << endl
                  << "static const char qt_configure_ext_prefix_path_str   [512 + 12] = \"qt_epfxpath=" << dictionary["QT_EXT_PREFIX"] << "\";" << endl
                  << "static const char qt_configure_host_prefix_path_str  [512 + 12] = \"qt_hpfxpath=" << dictionary["QT_HOST_PREFIX"] << "\";" << endl
                  << "#endif" << endl
                  << endl
                  << "static const short qt_configure_str_offsets[] = {\n"
                  << "    " << confStrOffsets[0] << endl
                  << "#ifdef QT_BUILD_QMAKE\n"
                  << "    " << confStrOffsets[1] << endl
                  << "#endif\n"
                  << "};\n"
                  << "static const char qt_configure_strs[] =\n"
                  << confStrings[0] << "#ifdef QT_BUILD_QMAKE\n"
                  << confStrings[1] << "#endif\n"
                  << ";\n"
                  << endl;
        if ((platform() != WINDOWS) && (platform() != WINDOWS_CE) && (platform() != WINDOWS_RT))
            tmpStream << "#define QT_CONFIGURE_SETTINGS_PATH \"" << dictionary["QT_REL_INSTALL_SETTINGS"] << "\"" << endl;

        tmpStream << endl
                  << "#ifdef QT_BUILD_QMAKE\n"
                  << "# define QT_CONFIGURE_SYSROOTIFY_PREFIX " << (sysrootifyPrefix ? "true" : "false") << endl
                  << "#endif\n\n"
                  << "/* strlen( \"qt_lcnsxxxx\") == 12 */" << endl
                  << "#define QT_CONFIGURE_LICENSEE qt_configure_licensee_str + 12" << endl
                  << "#define QT_CONFIGURE_LICENSED_PRODUCTS qt_configure_licensed_products_str + 12" << endl
                  << endl
                  << "#define QT_CONFIGURE_PREFIX_PATH qt_configure_prefix_path_str + 12\n"
                  << "#ifdef QT_BUILD_QMAKE\n"
                  << "# define QT_CONFIGURE_EXT_PREFIX_PATH qt_configure_ext_prefix_path_str + 12\n"
                  << "# define QT_CONFIGURE_HOST_PREFIX_PATH qt_configure_host_prefix_path_str + 12\n"
                  << "#endif\n";

        if (!tmpStream.flush())
            dictionary[ "DONE" ] = "error";
    }
}


bool Configure::showLicense(QString orgLicenseFile)
{
    bool showLgpl2 = true;
    QString licenseFile = orgLicenseFile;
    QString theLicense;
    if (dictionary["EDITION"] == "OpenSource") {
        if (platform() != WINDOWS_RT
                && platform() != WINDOWS_CE
                && (platform() != ANDROID || dictionary["ANDROID_STYLE_ASSETS"] == "no")) {
            theLicense = "GNU Lesser General Public License (LGPL) version 2.1"
                         "\nor the GNU Lesser General Public License (LGPL) version 3";
        } else {
            theLicense = "GNU Lesser General Public License (LGPL) version 3";
            showLgpl2 = false;
        }
    } else {
        // the first line of the license file tells us which license it is
        QFile file(licenseFile);
        if (!file.open(QFile::ReadOnly)) {
            cout << "Failed to load LICENSE file" << endl;
            return false;
        }
        theLicense = file.readLine().trimmed();
    }

    forever {
        char accept = '?';
        cout << "You are licensed to use this software under the terms of" << endl
             << "the " << theLicense << "." << endl
             << endl;
        if (dictionary["EDITION"] == "OpenSource") {
            cout << "Type '3' to view the Lesser GNU General Public License version 3 (LGPLv3)." << endl;
            if (showLgpl2)
                cout << "Type 'L' to view the Lesser GNU General Public License version 2.1 (LGPLv2.1)." << endl;
        } else {
            cout << "Type '?' to view the " << theLicense << "." << endl;
        }
        cout << "Type 'y' to accept this license offer." << endl
             << "Type 'n' to decline this license offer." << endl
             << endl
             << "Do you accept the terms of the license?" << endl;
        cin >> accept;
        accept = tolower(accept);

        if (accept == 'y') {
            return true;
        } else if (accept == 'n') {
            return false;
        } else {
            if (dictionary["EDITION"] == "OpenSource") {
                if (accept == '3')
                    licenseFile = orgLicenseFile + "/LICENSE.LGPLv3";
                else
                    licenseFile = orgLicenseFile + "/LICENSE.LGPLv21";
            }
            // Get console line height, to fill the screen properly
            int i = 0, screenHeight = 25; // default
            CONSOLE_SCREEN_BUFFER_INFO consoleInfo;
            HANDLE stdOut = GetStdHandle(STD_OUTPUT_HANDLE);
            if (GetConsoleScreenBufferInfo(stdOut, &consoleInfo))
                screenHeight = consoleInfo.srWindow.Bottom
                             - consoleInfo.srWindow.Top
                             - 1; // Some overlap for context

            // Prompt the license content to the user
            QFile file(licenseFile);
            if (!file.open(QFile::ReadOnly)) {
                cout << "Failed to load LICENSE file" << licenseFile << endl;
                return false;
            }
            QStringList licenseContent = QString(file.readAll()).split('\n');
            while (i < licenseContent.size()) {
                cout << licenseContent.at(i) << endl;
                if (++i % screenHeight == 0) {
                    promptKeyPress();
                    cout << "\r";     // Overwrite text above
                }
            }
        }
    }
}

void Configure::readLicense()
{
    dictionary["PLATFORM NAME"] = platformName();
    dictionary["LICENSE FILE"] = sourcePath;

    bool openSource = false;
    bool hasOpenSource = QFile::exists(dictionary["LICENSE FILE"] + "/LICENSE.LGPLv3") || QFile::exists(dictionary["LICENSE FILE"] + "/LICENSE.LGPLv21");
    if (dictionary["BUILDTYPE"] == "commercial") {
        openSource = false;
    } else if (dictionary["BUILDTYPE"] == "opensource") {
        openSource = true;
    } else if (hasOpenSource) { // No Open Source? Just display the commercial license right away
        forever {
            char accept = '?';
            cout << "Which edition of Qt do you want to use ?" << endl;
            cout << "Type 'c' if you want to use the Commercial Edition." << endl;
            cout << "Type 'o' if you want to use the Open Source Edition." << endl;
            cin >> accept;
            accept = tolower(accept);

            if (accept == 'c') {
                openSource = false;
                break;
            } else if (accept == 'o') {
                openSource = true;
                break;
            }
        }
    }
    if (hasOpenSource && openSource) {
        cout << endl << "This is the " << dictionary["PLATFORM NAME"] << " Open Source Edition." << endl << endl;
        dictionary["LICENSEE"] = "Open Source";
        dictionary["EDITION"] = "OpenSource";
    } else if (openSource) {
        cout << endl << "Cannot find the GPL license files! Please download the Open Source version of the library." << endl;
        dictionary["DONE"] = "error";
    } else {
        QString tpLicense = sourcePath + "/LICENSE.PREVIEW.COMMERCIAL";
        if (QFile::exists(tpLicense)) {
            cout << endl << "This is the Qt Preview Edition." << endl << endl;

            dictionary["EDITION"] = "Preview";
            dictionary["LICENSE FILE"] = tpLicense;
        } else {
            Tools::checkLicense(dictionary, sourcePath, buildPath);
        }
    }

    if (dictionary["LICENSE_CONFIRMED"] != "yes") {
        if (!showLicense(dictionary["LICENSE FILE"])) {
            cout << "Configuration aborted since license was not accepted" << endl;
            dictionary["DONE"] = "error";
            return;
        }
    } else if (dictionary["LICHECK"].isEmpty()) { // licheck executable shows license
        cout << "You have already accepted the terms of the license." << endl << endl;
    }
}
