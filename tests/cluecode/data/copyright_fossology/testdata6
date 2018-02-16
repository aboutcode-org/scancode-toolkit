// KDat - a tar-based DAT archiver
// Copyright (C) 1998-2000  Sean Vyain, svyain@mail.tds.net
// Copyright (C) 2001-2002  Lawrence Widman, kdat@cardiothink.com
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

#include <qpixmap.h>
#include <kglobal.h>
#include <kiconloader.h>

#include "ImageCache.h"

ImageCache::ImageCache()
{
    KIconLoader *l = KGlobal::iconLoader();
    /* 2002-01-24 FP */
    // _archive       = new QPixmap(l->iconPath("package", KIconLoader::Toolbar));
    _archive       = new QPixmap(l->iconPath("tar", KIconLoader::Small));
    /* 2002-01-24 FP */
    _backup        = new QPixmap(l->iconPath("kdat_backup", KIconLoader::Toolbar));
    _file          = new QPixmap(l->iconPath("mime_empty", KIconLoader::Small));
    _folderClosed  = new QPixmap(l->iconPath("folder_blue", KIconLoader::Small));
    _folderOpen    = new QPixmap(l->iconPath("folder_blue_open", KIconLoader::Small));
    _restore       = new QPixmap(l->iconPath("kdat_restore", KIconLoader::Toolbar));
    _selectAll     = new QPixmap(l->iconPath("kdat_select_all", KIconLoader::Toolbar));
    _selectNone    = new QPixmap(l->iconPath("kdat_select_none", KIconLoader::Toolbar));
    _selectSome    = new QPixmap(l->iconPath("kdat_select_some", KIconLoader::Toolbar));
    // 2002-01-28 FP
    // _tape          = new QPixmap(l->iconPath("kdat_archive", KIconLoader::Toolbar));
    _tape          = new QPixmap(l->iconPath("kdat", KIconLoader::Small));
    // 2002-01-28 FP
    _tapeMounted   = new QPixmap(l->iconPath("kdat_mounted", KIconLoader::Toolbar));
    _tapeUnmounted = new QPixmap(l->iconPath("kdat_unmounted", KIconLoader::Toolbar));
    _verify        = new QPixmap(l->iconPath("kdat_verify", KIconLoader::Toolbar));
}

ImageCache::~ImageCache()
{
    delete _archive;
    delete _backup;
    delete _file;
    delete _folderClosed;
    delete _folderOpen;
    delete _restore;
    delete _tape;
    delete _tapeMounted;
    delete _tapeUnmounted;
    delete _verify;
}

ImageCache* ImageCache::_instance = 0;

ImageCache* ImageCache::instance()
{
    if ( _instance == 0 ) {
        _instance = new ImageCache();
    }

    return _instance;
}

const QPixmap* ImageCache::getArchive()
{
    return _archive;
}

const QPixmap* ImageCache::getBackup()
{
    return _backup;
}

const QPixmap* ImageCache::getFile()
{
    return _file;
}

const QPixmap* ImageCache::getFolderClosed()
{
    return _folderClosed;
}

const QPixmap* ImageCache::getFolderOpen()
{
    return _folderOpen;
}

const QPixmap* ImageCache::getRestore()
{
    return _restore;
}

const QPixmap* ImageCache::getSelectAll()
{
    return _selectAll;
}

const QPixmap* ImageCache::getSelectNone()
{
    return _selectNone;
}

const QPixmap* ImageCache::getSelectSome()
{
    return _selectSome;
}

const QPixmap* ImageCache::getTape()
{
    return _tape;
}

const QPixmap* ImageCache::getTapeMounted()
{
    return _tapeMounted;
}

const QPixmap* ImageCache::getTapeUnmounted()
{
    return _tapeUnmounted;
}

const QPixmap* ImageCache::getVerify()
{
    return _verify;
}
