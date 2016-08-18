#!/usr/bin/python2
#
# timeconfig.py: text mode timezone selection dialog
#
# Large parts of this file were taken from the anaconda
# text mode mouse configuration screen
#
# Copyright 2002, 2003 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

from snack import *
import os
import locale
from rhpl.translate import _, textdomain_codeset
from zonetab import ZoneTab

# i18n fun
locale.setlocale(locale.LC_ALL, "")
textdomain_codeset("system-config-date", locale.nl_langinfo(locale.CODESET))

class TimezoneWindow:
    def __call__(self, screen, zonetab, timezoneBackend):
        self.timezone = timezoneBackend.getTimezoneInfo()
	self.default, self.asUTC, self.asArc = self.timezone        

        bb = ButtonBar(screen, [_("OK"), _("Cancel")])
        t = TextboxReflowed(40, 
                _("Select the timezone for the system."))
        l = Listbox(8, scroll = 1, returnExit = 0)

        zones = zonetab.getEntries()
        zones.sort()
        zonelist = []

        for zone in zones:
            zonelist.append(zone.tz)

        zonelist.sort()

        for zone in zonelist:
            l.append(zone, zone)

        if self.default not in zonelist:
            self.default = "America/New_York"
            
        l.setCurrent(self.default)

        if self.asUTC == "true":
            isOn = 1
        else:
            isOn = 0

        self.c = Checkbox(_("System clock uses UTC"), isOn)

        g = GridFormHelp(screen, _("Timezone Selection"), "timezone", 1, 4)
        g.add(t, 0, 0)
        g.add(l, 0, 1, padding = (0, 1, 0, 1))
        g.add(self.c, 0, 2, padding = (0, 0, 0, 1))
        g.add(bb, 0, 3, growx = 1)

        rc = g.runOnce()

        button = bb.buttonPressed(rc)

        if button == "cancel":
            return -1
            
        choice = l.current()
        utc = self.c.selected()
        return choice, utc


def runConfig(rc):
    timezone, utc = rc
    default, asUTC, asArc = timezoneBackend.getTimezoneInfo()
    timezoneBackend.writeConfig(timezone, utc, asArc)

if os.getuid() > 0 or os.geteuid() > 0:
    print _("You must be root to run timeconfig.")
    import sys
    sys.exit(0)


import timezoneBackend
timezoneBackend = timezoneBackend.timezoneBackend()
        
screen = SnackScreen()
screen.drawRootText(0, 0, "system-config-date - (C) 2003 Red Hat, Inc.")

zonetab = ZoneTab()

rc = TimezoneWindow()(screen, zonetab, timezoneBackend)

if rc == -1:
    screen.finish()
else:
    screen.finish()
    runConfig(rc)


