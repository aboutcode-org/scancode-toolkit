# -*- coding: iso-8859-15 -*-
# -*- Mode: Python; py-ident-offset: 4 -*-
# vim:ts=4:sw=4:et

# Copyright (c) M�rio Morgado
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
PyRPM
=====

PyRPM is a pure python, simple to use, module to read information from a RPM
file.
'''

from __future__ import absolute_import


from StringIO import StringIO
import struct
import re

from . import rpmdefs

HEADER_MAGIC_NUMBER = re.compile('(\x8e\xad\xe8)')


def find_magic_number(regexp, data):
    ''' find a magic number in a buffer
    '''
    string = data.read(1)
    while 1:
        match = regexp.search(string)
        if match:
            return data.tell() - 3
        byte = data.read(1)
        if not byte:
            return None
        else:
            string += byte


class Entry(object):
    ''' RPM Header Entry
    '''
    def __init__(self, entry, store):
        self.entry = entry
        self.store = store

        self.switch = {
            rpmdefs.RPM_DATA_TYPE_CHAR:            self.__readchar,
            rpmdefs.RPM_DATA_TYPE_INT8:            self.__readint8,
            rpmdefs.RPM_DATA_TYPE_INT16:           self.__readint16,
            rpmdefs.RPM_DATA_TYPE_INT32:           self.__readint32,
            rpmdefs.RPM_DATA_TYPE_INT64:           self.__readint64,
            rpmdefs.RPM_DATA_TYPE_STRING:          self.__readstring,
            rpmdefs.RPM_DATA_TYPE_BIN:             self.__readbin,
            rpmdefs.RPM_DATA_TYPE_STRING_ARRAY:    self.__readstring,
            rpmdefs.RPM_DATA_TYPE_ASN1:            self.__readbin,
            rpmdefs.RPM_DATA_TYPE_OPENPGP:         self.__readbin,
            rpmdefs.RPM_DATA_TYPE_I18NSTRING_TYPE: self.__readstring
        }
        self.store.seek(entry[2])
        self.value = self.switch[entry[1]]()
        self.tag = entry[0]

    def __str__(self):
        return "(%s, %s)" % (self.tag, self.value,)

    def __repr__(self):
        return "(%s, %s)" % (self.tag, self.value,)

    def __readchar(self, offset=1):
        ''' store is a pointer to the store offset
        where the char should be read
        '''
        data = self.store.read(offset)
        fmt = '!' + str(offset) + 'c'
        value = struct.unpack(fmt, data)
        return value

    def __readint8(self, offset=1):
        ''' int8 = 1byte
        '''
        return self.__readchar(offset)

    def __readint16(self, offset=1):
        ''' int16 = 2bytes
        '''
        data = self.store.read(offset * 2)
        fmt = '!' + str(offset) + 'i'
        value = struct.unpack(fmt, data)
        return value

    def __readint32(self, offset=1):
        ''' int32 = 4bytes
        '''
        data = self.store.read(offset * 4)
        fmt = '!' + str(offset) + 'i'
        value = struct.unpack(fmt, data)
        return value

    def __readint64(self, offset=1):
        ''' int64 = 8bytes
        '''
        data = self.store.read(offset * 4)
        fmt = '!' + str(offset) + 'l'
        value = struct.unpack(fmt, data)
        return value

    def __readstring(self):
        ''' read a string entry
        '''
        string = ''
        while 1:
            char = self.__readchar()
            if char[0] == '\x00':  # read until '\0'
                break
            string += char[0]
        return string

    def __readbin(self):
        ''' read a binary entry
        '''
        if self.entry[0] == rpmdefs.RPMSIGTAG_MD5:
            data = self.store.read(rpmdefs.MD5_SIZE)
            value = struct.unpack('!' + rpmdefs.MD5_SIZE + 's', data)
            return value
        elif self.entry[0] == rpmdefs.RPMSIGTAG_PGP:
            data = self.store.read(rpmdefs.PGP_SIZE)
            value = struct.unpack('!' + rpmdefs.PGP_SIZE + 's', data)
            return value


class Header(object):
    ''' RPM Header Structure
    '''
    def __init__(self, header, entries, store):
        self.header = header
        self.entries = entries
        self.store = store
        self.pentries = []
        self.rentries = []
        self.__readentries()

    def __readentry(self, entry):
        ''' [4bytes][4bytes][4bytes][4bytes]
               TAG    TYPE   OFFSET  COUNT
        '''
        entryfmt = '!llll'
        entry = struct.unpack(entryfmt, entry)
        if entry[0] < rpmdefs.RPMTAG_MIN_NUMBER or\
                entry[0] > rpmdefs.RPMTAG_MAX_NUMBER:
            return None
        return entry

    def __readentries(self):
        ''' read a rpm entry
        '''
        for entry in self.entries:
            entry = self.__readentry(entry)
            if entry:
                if entry[0] in rpmdefs.RPMTAGS:
                    self.pentries.append(entry)

        for pentry in self.pentries:
            entry = Entry(pentry, self.store)
            if entry:
                self.rentries.append(entry)


class RPMError(BaseException):
    pass


class RPM(object):

    def __init__(self, rpm):
        ''' rpm - StringIO.StringIO | file
        '''
        if hasattr(rpm, 'read'):  # if it walk like a duck..
            self.rpmfile = rpm
        else:
            raise ValueError('invalid initialization: '
                             'StringIO or file expected received %s'
                                 % (type(rpm),))
        self.binary = None
        self.source = None
        self.__entries = []
        self.__headers = []

        self.__readlead()
        offset = self.__read_sigheader()
        self.__readheaders(offset)

    def __readlead(self):
        ''' reads the rpm lead section

            struct rpmlead {
               unsigned char magic[4];
               unsigned char major, minor;
               short type;
               short archnum;
               char name[66];
               short osnum;
               short signature_type;
               char reserved[16];
               } ;
        '''
        lead_fmt = '!4sBBhh66shh16s'
        data = self.rpmfile.read(96)
        value = struct.unpack(lead_fmt, data)

        magic_num = value[0]
        ptype = value[3]

        if magic_num != rpmdefs.RPM_LEAD_MAGIC_NUMBER:
            raise RPMError('wrong magic number this is not a RPM file')

        if ptype == 1:
            self.binary = False
            self.source = True
        elif ptype == 0:
            self.binary = True
            self.source = False
        else:
            raise RPMError('wrong package type this is not a RPM file')

    def __read_sigheader(self):
        ''' read signature header

            ATN: this will not return any usefull information
            besides the file offset
        '''
        start = find_magic_number(HEADER_MAGIC_NUMBER, self.rpmfile)
        if not start:
            raise RPMError('invalid RPM file, signature header not found')
        # return the offsite after the magic number
        return start + 3

    def __readheader(self, header):
        ''' reads the header-header section
        [3bytes][1byte][4bytes][4bytes][4bytes]
          MN      VER   UNUSED  IDXNUM  STSIZE
        '''
        headerfmt = '!3sc4sll'
        if not len(header) == 16:
            raise RPMError('invalid header size')

        header = struct.unpack(headerfmt, header)
        magic_num = header[0]
        if magic_num != rpmdefs.RPM_HEADER_MAGIC_NUMBER:
            raise RPMError('invalid RPM header')
        return header

    def __readheaders(self, offset):
        ''' read information headers
        '''
        # lets find the start of the header
        self.rpmfile.seek(offset)
        start = find_magic_number(HEADER_MAGIC_NUMBER, self.rpmfile)
        # go back to the begining of the header
        self.rpmfile.seek(start)
        header = self.rpmfile.read(16)
        header = self.__readheader(header)
        entries = []
        for entry in range(header[3]):
            _entry = self.rpmfile.read(16)
            entries.append(_entry)
        store = StringIO(self.rpmfile.read(header[4]))
        self.__headers.append(Header(header, entries, store))

        for header in self.__headers:
            for entry in header.rentries:
                self.__entries.append(entry)

    def __iter__(self):
        for entry in self.__entries:
            yield entry

    def __getitem__(self, item):
        for entry in self:
            if entry.tag == item:
                if entry.value and isinstance(entry.value, str):
                    return entry.value

    def name(self):
        return self[rpmdefs.RPMTAG_NAME]

    def package(self):
        name = self[rpmdefs.RPMTAG_NAME]
        version = self[rpmdefs.RPMTAG_VERSION]
        return '-'.join([name, version, ])

    def filename(self):
        package = self.package()
        release = self[rpmdefs.RPMTAG_RELEASE]
        name = '-'.join([package, release, ])
        arch = self[rpmdefs.RPMTAG_ARCH]
        if self.binary:
            return '.'.join([name, arch, 'rpm', ])
        else:
            return '.'.join([name, arch, 'src.rpm', ])

    def tags(self):
        '''returns a dict of tags, keyed by name'''
        tgs = {}
        for tagid, tagname in rpmdefs.RPMTAGS.items():
            try:
                tag = self[tagid]
                if tag == 'None' or tag == None : tag = ''
                tgs[tagname] = tag
            except:
                tgs[tagname] = ''
        return tgs
