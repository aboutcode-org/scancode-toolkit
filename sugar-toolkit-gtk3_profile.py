# Copyright (C) 2006-2007, Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""User settings/configuration loading.
"""

from gi.repository import Gio
import os
import logging

from six.moves.configparser import ConfigParser

from sugar3 import env
from sugar3 import util
from sugar3.graphics.xocolor import XoColor

import getpass

_profile = None
_journal_settings = None


class Profile(object):
    """Local user's current options/profile information

    The profile is also responsible for loading the user's
    public and private ssh keys from disk.

    Attributes:

        pubkey -- public ssh key
        privkey_hash -- SHA has of the child's public key
    """

    def __init__(self, path):
        self._pubkey = None
        self._privkey_hash = None

    def _get_pubkey(self):
        if self._pubkey is None:
            self._pubkey = self._load_pubkey()
        return self._pubkey

    pubkey = property(fget=_get_pubkey)

    def _get_privkey_hash(self):
        if self._privkey_hash is None:
            self._privkey_hash = self._hash_private_key()
        return self._privkey_hash

    privkey_hash = property(fget=_get_privkey_hash)

    def is_valid(self):
        nick = get_nick_name()
        color = get_color()

        return nick != '' and \
            color != '' and \
            self.pubkey is not None and \
            self.privkey_hash is not None

    def _load_pubkey(self):
        key_path = os.path.join(env.get_profile_path(), 'owner.key.pub')

        if not os.path.exists(key_path):
            return None

        try:
            f = open(key_path, 'r')
            lines = f.readlines()
            f.close()
        except IOError:
            logging.exception('Error reading public key')
            return None

        # Support both DSA (ssh-dss) for existing keys and RSA (ssh-rsa) for new keys
        # This ensures backward compatibility with existing user profiles
        supported_key_types = ('ssh-dss ', 'ssh-rsa ')
        for line in lines:
            line = line.strip()
            for magic in supported_key_types:
                if line.startswith(magic):
                    return line[len(magic):]
        else:
            logging.error('Error parsing public key.')
            return None

    def _hash_private_key(self):
        key_path = os.path.join(env.get_profile_path(), 'owner.key')

        if not os.path.exists(key_path):
            return None

        try:
            f = open(key_path, 'r')
            lines = f.readlines()
            f.close()
        except IOError:
            logging.exception('Error reading private key')
            return None

        key = ""
        begin_found = False
        end_found = False
        for line in lines:
            line = line.strip()
            if line.startswith(('-----BEGIN DSA PRIVATE KEY-----',
                                '-----BEGIN OPENSSH PRIVATE KEY-----')):
                begin_found = True
                continue
            if line.startswith(('-----END DSA PRIVATE KEY-----',
                                '-----END OPENSSH PRIVATE KEY-----')):
                end_found = True
                continue
            key += line
        if not (len(key) and begin_found and end_found):
            logging.error('Error parsing public key.')
            return None

        # hash it
        key_hash = util.sha_data(key)
        return util.printable_hash(key_hash)

    def convert_profile(self):
        cp = ConfigParser()
        path = os.path.join(env.get_profile_path(), 'config')
        cp.read([path])

        settings = Gio.Settings('org.sugarlabs.user')
        if cp.has_option('Buddy', 'NickName'):
            name = cp.get('Buddy', 'NickName')
            # decode nickname from ascii-safe chars to unicode
            nick = name.decode('utf-8')
            settings.set_string('nick', nick)
        if cp.has_option('Buddy', 'Color'):
            color = cp.get('Buddy', 'Color')
            settings.set_string('color', color)

        if cp.has_option('Jabber', 'Server'):
            server = cp.get('Jabber', 'Server')
            settings = Gio.Settings('org.sugarlabs.collaboration')
            settings.set_string('jabber-server', server)

        if cp.has_option('Date', 'Timezone'):
            timezone = cp.get('Date', 'Timezone')
            settings = Gio.Settings('org.sugarlabs.date')
            settings.set_string('timezone', timezone)

        settings = Gio.Settings('org.sugarlabs.frame')
        if cp.has_option('Frame', 'HotCorners'):
            delay = float(cp.get('Frame', 'HotCorners'))
            settings.set_int('corner-delay', int(delay))
        if cp.has_option('Frame', 'WarmEdges'):
            delay = float(cp.get('Frame', 'WarmEdges'))
            settings.set_int('edge-delay', int(delay))

        if cp.has_option('Server', 'Backup1'):
            backup1 = cp.get('Server', 'Backup1')
            settings = Gio.Settings('org.sugarlabs')
            settings.set_string('backup-url', backup1)

        if cp.has_option('Sound', 'Volume'):
            volume = float(cp.get('Sound', 'Volume'))
            settings = Gio.Settings('org.sugarlabs.sound')
            settings.set_int('volume', int(volume))

        settings = Gio.Settings('org.sugarlabs.power')
        if cp.has_option('Power', 'AutomaticPM'):
            state = cp.get('Power', 'AutomaticPM')
            if state.lower() == 'true':
                settings.set_boolean('automatic', True)
        if cp.has_option('Power', 'ExtremePM'):
            state = cp.get('Power', 'ExtremePM')
            if state.lower() == 'true':
                settings.set_boolean('extreme', True)

        if cp.has_option('Shell', 'FavoritesLayout'):
            layout = cp.get('Shell', 'FavoritesLayout')
            settings = Gio.Settings('org.sugarlabs.desktop')
            settings.set_string('favorites-layout', layout)
        del cp
        try:
            os.unlink(path)
        except OSError:
            logging.error('Error removing old profile.')


def get_profile():
    global _profile

    if not _profile:
        path = os.path.join(env.get_profile_path(), 'config')
        _profile = Profile(path)

    return _profile


def get_nick_name():
    if 'org.sugarlabs.user' in Gio.Settings.list_schemas():
        settings = Gio.Settings('org.sugarlabs.user')
        return settings.get_string('nick')
    else:
        return getpass.getuser()


def get_color():
    if 'org.sugarlabs.user' in Gio.Settings.list_schemas():
        settings = Gio.Settings('org.sugarlabs.user')
        color = settings.get_string('color')
        return XoColor(color)
    else:
        return XoColor()


def get_pubkey():
    return get_profile().pubkey


def _get_journal_settings_boolean(name, default):
    global _journal_settings

    if not _journal_settings:
        if 'org.sugarlabs.journal' not in Gio.Settings.list_schemas():
            return default

        _journal_settings = Gio.Settings('org.sugarlabs.journal')

    if name not in _journal_settings.list_keys():
        return default

    return _journal_settings.get_boolean(name)


def get_save_as():
    return _get_journal_settings_boolean('save-as', False)
