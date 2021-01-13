/*
 *   Copyright (C) 2010 Peter Grasch <peter.grasch@bedahr.org>
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License version 2,
 *   or (at your option) any later version, as published by the Free
 *   Software Foundation
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details
 *
 *   You should have received a copy of the GNU General Public
 *   License along with this program; if not, write to the
 *   Free Software Foundation, Inc.,
 *   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */


#ifndef SIMON_DIALOGBOUNDVALUES_H_4B4956DCAE204C49977297D20CB81F09
#define SIMON_DIALOGBOUNDVALUES_H_4B4956DCAE204C49977297D20CB81F09

#include "simondialogengine_export.h"
#include <QList>
#include <QString>
#include <QDomElement>
#include <QAbstractItemModel>

class BoundValue;

class SIMONDIALOGENGINE_EXPORT DialogBoundValues : public QAbstractItemModel
{
  private:
    QList<BoundValue*> boundValues;

  public:
    DialogBoundValues();
    Qt::ItemFlags flags(const QModelIndex &index) const;
    QVariant headerData(int, Qt::Orientation orientation,
                      int role = Qt::DisplayRole) const;
    QObject* parent() { return QObject::parent(); }
    QModelIndex parent(const QModelIndex &index) const;
    int rowCount(const QModelIndex &parent = QModelIndex()) const;

    QModelIndex index(int row, int column,const QModelIndex &parent = QModelIndex()) const;
    virtual QVariant data(const QModelIndex &index, int role) const;
    virtual int columnCount(const QModelIndex &parent = QModelIndex()) const;

    static DialogBoundValues* createInstance(const QDomElement& elem);
    QDomElement serialize(QDomDocument *doc);
    bool deSerialize(const QDomElement& elem);

    bool addBoundValue(BoundValue *value);
    bool removeBoundValue(BoundValue *value);

    //BoundValue* getBoundValue(const QString& name);
    QVariant getBoundValue(const QString& name);
    
    ~DialogBoundValues();
    
    void setArguments(const QStringList& arguments);
};

#endif


