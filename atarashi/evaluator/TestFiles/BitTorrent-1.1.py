#!/usr/bin/env python

# The contents of this file are subject to the BitTorrent Open Source License
# Version 1.1 (the License).  You may not copy or use this file, in either
# source code or executable form, except in compliance with the License.  You
# may obtain a copy of the License at http://www.bittorrent.com/license/.
#
# Software distributed under the License is distributed on an AS IS basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied.  See the License
# for the specific language governing rights and limitations under the
# License.

# Written by Uoti Urpala and Matt Chisholm

from __future__ import division

from BitTorrent.platform import install_translation
install_translation()

import sys
import itertools
import math
import os
import threading
import datetime
import random
import atexit

assert sys.version_info >= (2, 3), _("Install Python %s or greater") % '2.3'

from BitTorrent import BTFailure, INFO, WARNING, ERROR, CRITICAL, status_dict, app_name

from BitTorrent import configfile

from BitTorrent.defaultargs import get_defaults
from BitTorrent.IPC import ipc_interface
from BitTorrent.prefs import Preferences
from BitTorrent.platform import doc_root, btspawn, path_wrap, os_version, is_frozen_exe, get_startup_dir, create_shortcut, remove_shortcut
from BitTorrent import zurllib

defaults = get_defaults('bittorrent')
defaults.extend((('donated' , '', ''), # the version that the user last donated for
                 ('notified', '', ''), # the version that the user was last notified of
                 ))


ui_options = [
    'max_upload_rate'       ,
    'minport'               ,
    'maxport'               ,
    'next_torrent_time'     ,
    'next_torrent_ratio'    ,
    'last_torrent_ratio'    ,
    'seed_forever'          ,
    'seed_last_forever'     ,
    'ask_for_save'          ,
    'save_in'               ,
    'open_from'             ,
    'ip'                    ,
    'start_torrent_behavior',
    'upnp'                  ,
    ]

if os.name == 'nt':
    ui_options.extend( [
        'launch_on_startup'     ,
        'minimize_to_tray'      ,
        ])

advanced_ui_options_index = len(ui_options)

ui_options.extend([
    'min_uploads'     ,
    'max_uploads'     ,
    'max_initiate'    ,
    'max_incomplete'  ,
    'max_allow_in'    ,
    'max_files_open'  ,
    'forwarded_port'  ,
    'display_interval',
    'donated'         ,
    'notified'        ,
    ])


if is_frozen_exe:
    ui_options.append('progressbar_hack')
    defproghack = 0
    if os_version == 'XP':
        # turn on progress bar hack by default for Win XP 
        defproghack = 1
    defaults.extend((('progressbar_hack' , defproghack, ''),)) 


NAG_FREQUENCY = 3
PORT_RANGE = 5

defconfig = dict([(name, value) for (name, value, doc) in defaults])
del name, value, doc

def btgui_exit(ipc):
    ipc.stop()

class global_logger(object):
    def __init__(self, logger = None):
        self.logger = logger
    def __call__(self, severity, msg):
        if self.logger:
            self.logger(severity, msg)
        else:
            sys.stderr.write("%s: %s\n" % (status_dict[severity], msg))        

# if it's application global, why do we pass a reference to it everywhere?
global_log_func = global_logger()

if __name__ == '__main__':
    zurllib.add_unsafe_thread()
    
    try:
        config, args = configfile.parse_configuration_and_args(defaults,
                                        'bittorrent', sys.argv[1:], 0, None)
    except BTFailure, e:
        print str(e)
        sys.exit(1)

    config = Preferences().initWithDict(config)
    advanced_ui = config['advanced']

    newtorrents = args
    for opt in ('responsefile', 'url'):
        if config[opt]:
            print '"--%s"' % opt, _("deprecated, do not use")
            newtorrents.append(config[opt])

    ipc = ipc_interface(config, global_log_func)

    # this could be on the ipc object
    ipc_master = True
    try:
        ipc.create()
    except BTFailure:
        ipc_master = False

        try:
            ipc.send_command('no-op')
        except BTFailure:
            global_log_func(ERROR, _("Failed to communicate with another %s process "
                                     "but one seems to be running.") + 
                                   _(" Closing all %s windows may fix the problem.")
                                   % (app_name, app_name))
            sys.exit(1)

    # make sure we clean up the ipc when we close
    atexit.register(btgui_exit, ipc)

    # it's not obvious, but 'newtorrents' is carried on to the gui
    # __main__ if we're the IPC master
    
    if not ipc_master:
        
        if newtorrents:
            # Not sure if anything really useful could be done if
            # these send_command calls fail
            for name in newtorrents:
                ipc.send_command('start_torrent', name, config['save_as'])
            sys.exit(0)
            
        try:
            ipc.send_command('show_error', _("%s already running")%app_name)
        except BTFailure:
            global_log_func(ERROR, _("Failed to communicate with another %s process.") +
                                   _(" Closing all %s windows may fix the problem.")
                                   % app_name)
        sys.exit(1)


import gtk
import pango
import gobject
import webbrowser

assert gtk.pygtk_version >= (2, 6), _("PyGTK %s or newer required") % '2.6'

from BitTorrent import HELP_URL, DONATE_URL, SEARCH_URL, version, branch

from BitTorrent import TorrentQueue
from BitTorrent import LaunchPath
from BitTorrent import Desktop
from BitTorrent import ClientIdentifier
from BitTorrent import NewVersion

from BitTorrent.parseargs import makeHelp
from BitTorrent.TorrentQueue import RUNNING, RUN_QUEUED, QUEUED, KNOWN, ASKING_LOCATION
from BitTorrent.TrayIcon import TrayIcon
from BitTorrent.StatusLight import GtkStatusLight as StatusLight
from BitTorrent.GUI import * 


main_torrent_dnd_tip = _("drag to reorder")
torrent_menu_tip = _("right-click for menu")
torrent_tip_format = '%s:\n %s\n %s'

rate_label = ': %s'

speed_classes = {
    (   4,    5):_("dialup"           ),
    (   6,   14):_("DSL/cable 128k up"),
    (  15,   29):_("DSL/cable 256k up"),
    (  30,   91):_("DSL 768k up"      ),
    (  92,  137):_("T1"               ),
    ( 138,  182):_("T1/E1"            ),
    ( 183,  249):_("E1"               ),
    ( 250, 5446):_("T3"               ),
    (5447,18871):_("OC3"              ),
    }

def find_dir(path):
    if os.path.isdir(path):
        return path
    directory, garbage = os.path.split(path)
    while directory:
        if os.access(directory, os.F_OK) and os.access(directory, os.W_OK):
            return directory
        directory, garbage = os.path.split(directory)
        if garbage == '':
            break        
    return None

def smart_dir(path):
    path = find_dir(path)
    if path is None:
        path = Desktop.desktop
    return path

class MenuItem(gtk.MenuItem): 
    def __init__(self, label, accel_group=None, func=None):
        gtk.MenuItem.__init__(self, label)
        if func is not None:
            self.connect("activate", func)
        else:
            self.set_sensitive(False)

        if accel_group is not None:
            label = label.decode('utf-8')
            accel_index = label.find('_')
            if -1 < accel_index < len(label) - 1:
                accel_char = long(ord(label[accel_index+1]))
                accel_key  = gtk.gdk.unicode_to_keyval(accel_char)
                if accel_key != accel_char | 0x01000000:
                    self.add_accelerator("activate", accel_group, accel_key,
                                         gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        self.show()


def build_menu(menu_items, accel_group=None):
    menu = gtk.Menu()
    for label,func in menu_items:
        if label == '----':
            s = gtk.SeparatorMenuItem()
            s.show()
            menu.add(s)
        else:
            item = MenuItem(label, accel_group=accel_group, func=func)
            item.show()
            menu.add(item)
    return menu


class Validator(gtk.Entry):
    valid_chars = '1234567890'
    minimum = None
    maximum = None
    cast = int
    
    def __init__(self, option_name, config, setfunc):
        gtk.Entry.__init__(self)
        self.option_name = option_name
        self.config      = config
        self.setfunc     = setfunc

        self.set_text(str(config[option_name]))
            
        self.set_size_request(self.width,-1)
        
        self.connect('insert-text', self.text_inserted)
        self.connect('focus-out-event', self.focus_out)

    def get_value(self):
        value = None
        try:
            value = self.cast(self.get_text())
        except ValueError:
            pass
        return value

    def set_value(self, value):
        self.set_text(str(value))
        self.setfunc(self.option_name, value)        
        
    def focus_out(self, entry, widget):
        value = self.get_value()

        if value is None:
            return

        if (self.minimum is not None) and (value < self.minimum):
            value = self.minimum
        if (self.maximum is not None) and (value > self.maximum):
            value = self.maximum

        self.set_value(value)

    def text_inserted(self, entry, input, position, user_data):
        for i in input:
            if (self.valid_chars is not None) and (i not in self.valid_chars):
                self.emit_stop_by_name('insert-text')
                return True
        return False

class IPValidator(Validator):
    valid_chars = '1234567890.'
    width = 128
    cast = str

class PortValidator(Validator):
    width = 64
    minimum = 1024
    maximum = 65535

    def add_end(self, end_name):
        self.end_option_name = end_name

    def set_value(self, value):
        self.set_text(str(value))
        self.setfunc(self.option_name, value)
        self.setfunc(self.end_option_name, value+PORT_RANGE)


class PercentValidator(Validator):
    width = 48
    minimum = 0

class MinutesValidator(Validator):
    width = 48
    minimum = 1

class EnterUrlDialog(MessageDialog):
    flags = gtk.DIALOG_DESTROY_WITH_PARENT
    def __init__(self, parent):
        self.entry = gtk.Entry()
        self.entry.show()
        self.main = parent
        MessageDialog.__init__(self, parent.mainwindow,
                               _("Enter torrent URL"),
                               _("Enter the URL of a torrent file to open:"),
                               type=gtk.MESSAGE_QUESTION,
                               buttons=gtk.BUTTONS_OK_CANCEL,
                               yesfunc=lambda *args: parent.open_url(self.entry.get_text()),
                               default=gtk.RESPONSE_OK
                               )
        hbox = gtk.HBox()
        hbox.pack_start(self.entry, padding=SPACING)
        hbox.show()
        self.entry.set_activates_default(True)
        self.entry.set_flags(gtk.CAN_FOCUS)
        self.vbox.pack_start(hbox)
        self.entry.grab_focus()

    def close(self, *args):
        self.destroy()

    def destroy(self):
        MessageDialog.destroy(self)
        self.main.window_closed('enterurl')


class RateSliderBox(gtk.VBox):
    base = 10
    multiplier = 4
    max_exponent = 3.3

    def __init__(self, config, torrentqueue):
        gtk.VBox.__init__(self, homogeneous=False)
        self.config = config
        self.torrentqueue = torrentqueue

        if self.config['max_upload_rate'] < self.slider_to_rate(0):
            self.config['max_upload_rate'] = self.slider_to_rate(0)

        self.speed_classes = {
            (   4,    5):_("dialup"           ),
            (   6,   14):_("DSL/cable 128k up"),
            (  15,   29):_("DSL/cable 256k up"),
            (  30,   91):_("DSL 768k up"      ),
            (  92,  137):_("T1"               ),
            ( 138,  182):_("T1/E1"            ),
            ( 183,  249):_("E1"               ),
            ( 250, 5446):_("T3"               ),
            (5447,18871):_("OC3"              ),
            }

        biggest_size = 0
        for v in self.speed_classes.values():
            width = gtk.Label(v).size_request()[0]
            if width > biggest_size:
                biggest_size = width

        self.rate_slider_label_box = gtk.HBox(spacing=SPACING,
                                              homogeneous=True)
        
        self.rate_slider_label = gtk.Label(_("Maximum upload rate:"))
        self.rate_slider_label.set_ellipsize(pango.ELLIPSIZE_START)
        self.rate_slider_label.set_alignment(1, 0.5)
        self.rate_slider_label_box.pack_start(self.rate_slider_label,
                                              expand=True, fill=True)

        self.rate_slider_value = gtk.Label(
            self.value_to_label(self.config['max_upload_rate']))
        self.rate_slider_value.set_alignment(0, 0.5)
        self.rate_slider_value.set_size_request(biggest_size, -1)

        self.rate_slider_label_box.pack_start(self.rate_slider_value,
                                              expand=True, fill=True)

        self.rate_slider_adj = gtk.Adjustment(
            self.rate_to_slider(self.config['max_upload_rate']), 0,
            self.max_exponent, 0.01, 0.1)
        
        self.rate_slider = gtk.HScale(self.rate_slider_adj)
        self.rate_slider.set_draw_value(False)
        self.rate_slider_adj.connect('value_changed', self.set_max_upload_rate)

        self.pack_start(self.rate_slider       , expand=False, fill=False)
        self.pack_start(self.rate_slider_label_box , expand=False, fill=False)

        if False: # this shows the legend for the slider
            self.rate_slider_legend = gtk.HBox(homogeneous=True)
            for i in range(int(self.max_exponent+1)):
                label = gtk.Label(str(self.slider_to_rate(i)))
                alabel = halign(label, i/self.max_exponent)
                self.rate_slider_legend.pack_start(alabel,
                                                   expand=True, fill=True)
            self.pack_start(self.rate_slider_legend, expand=False, fill=False)


    def start(self):
        self.set_max_upload_rate(self.rate_slider_adj)

    def rate_to_slider(self, value):
        return math.log(value/self.multiplier, self.base)

    def slider_to_rate(self, value):
        return int(round(self.base**value * self.multiplier))

    def value_to_label(self, value):
        conn_type = ''
        for key, conn in self.speed_classes.items():
            min_v, max_v = key
            if min_v <= value <= max_v:
                conn_type = ' (%s)'%conn
                break
        label = str(Rate(value*1024)) + conn_type
        return label

    def set_max_upload_rate(self, adj):
        option = 'max_upload_rate'
        value = self.slider_to_rate(adj.get_value())
        self.config[option] = value
        self.torrentqueue.set_config(option, value)
        self.rate_slider_value.set_text(self.value_to_label(int(value)))


class StopStartButton(gtk.Button):
    stop_tip  = _("Temporarily stop all running torrents")
    start_tip = _("Resume downloading")

    def __init__(self, main):
        gtk.Button.__init__(self)
        self.main = main
        self.connect('clicked', self.toggle)

        self.stop_image = gtk.Image()
        self.stop_image.set_from_stock('bt-pause', gtk.ICON_SIZE_BUTTON)
        self.stop_image.show()

        self.start_image = gtk.Image()
        self.start_image.set_from_stock('bt-play', gtk.ICON_SIZE_BUTTON)
        self.start_image.show()

    def toggle(self, widget):
        self.set_paused(not self.main.config['pause'])

    def set_paused(self, paused):
        image = self.get_child()
        if paused:
            if image == self.stop_image:
                self.remove(self.stop_image)
            if image != self.start_image:
                self.add(self.start_image)
            self.main.tooltips.set_tip(self, self.start_tip)
            self.main.stop_queue()
        else:
            if image == self.start_image:
                self.remove(self.start_image)
            if image != self.stop_image:
                self.add(self.stop_image)
            self.main.tooltips.set_tip(self, self.stop_tip )
            self.main.restart_queue()


class VersionWindow(Window):
    def __init__(self, main, newversion, download_url):
        Window.__init__(self)
        self.set_title(_("New %s version available")%app_name)
        self.set_border_width(SPACING)
        self.set_resizable(False)
        self.main = main
        self.newversion = newversion
        self.download_url = download_url
        self.connect('destroy', lambda w: self.main.window_closed('version'))
        self.vbox = gtk.VBox(spacing=SPACING)
        self.hbox = gtk.HBox(spacing=SPACING)
        self.image = gtk.Image()
        self.image.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DIALOG)
        self.hbox.pack_start(self.image)
        
        self.label = gtk.Label()
        self.label.set_markup(
            (_("A newer version of %s is available.\n") % app_name) +
            (_("You are using %s, and the new version is %s.\n") % (version, newversion)) +
            (_("You can always get the latest version from \n%s") % self.download_url)
            ) 
        self.label.set_selectable(True)
        self.hbox.pack_start(self.label)
        self.vbox.pack_start(self.hbox)
        self.bbox = gtk.HBox(spacing=SPACING)

        self.closebutton = gtk.Button(_("Download _later"))
        self.closebutton.connect('clicked', self.close)

        self.newversionbutton = gtk.Button(_("Download _now"))
        self.newversionbutton.connect('clicked', self.get_newversion)

        self.bbox.pack_end(self.newversionbutton, expand=False, fill=False)
        self.bbox.pack_end(self.closebutton     , expand=False, fill=False)

        self.checkbox = gtk.CheckButton(_("_Remind me later"))
        self.checkbox.set_active(True)
        self.checkbox.connect('toggled', self.remind_toggle)
        
        self.bbox.pack_start(self.checkbox, expand=False, fill=False)

        self.vbox.pack_start(self.bbox)
        
        self.add(self.vbox)
        self.show_all()

    def remind_toggle(self, widget):
        v = self.checkbox.get_active()
        notified = ''
        if v:
            notified = ''
        else:
            notified = self.newversion
        self.main.set_config('notified', str(notified))

    def close(self, widget):
        self.destroy()

    def get_newversion(self, widget):
        if self.main.updater.can_install():
            if self.main.updater.torrentfile is None:
                self.main.visit_url(self.download_url)
            else:
                self.main.start_auto_update()
        else:
            self.main.visit_url(self.download_url)
        self.destroy()


class AboutWindow(object):

    def __init__(self, main, donatefunc):
        self.win = Window()
        self.win.set_title(_("About %s")%app_name)
        self.win.set_size_request(300,400)
        self.win.set_border_width(SPACING)
        self.win.set_resizable(False)
        self.win.connect('destroy', lambda w: main.window_closed('about'))
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.scroll.set_shadow_type(gtk.SHADOW_IN)

        self.outervbox = gtk.VBox()

        self.outervbox.pack_start(get_logo(96), expand=False, fill=False)

        version_str = version
        if int(version_str[2]) % 2:
            version_str = version_str + ' ' + _("Beta")

        self.outervbox.pack_start(gtk.Label(_("Version %s")%version_str), expand=False, fill=False)

        if branch is not None:
            blabel = gtk.Label('cdv client dir: %s' % branch)
            self.outervbox.pack_start(blabel, expand=False, fill=False)

        self.vbox = gtk.VBox()
        self.vbox.set_size_request(250, -1)

        for i, fn in enumerate(('credits', 'credits-l10n')):
            if i != 0:
                self.vbox.pack_start(gtk.HSeparator(), padding=SPACING,
                                     expand=False, fill=False)
            filename = os.path.join(doc_root, fn+'.txt')
            l = ''
            if not os.access(filename, os.F_OK|os.R_OK):
                l = _("Couldn't open %s") % filename
            else:
                credits_f = file(filename)
                l = credits_f.read()
                credits_f.close()
            if os.name == 'nt':
                # gtk ignores blank lines on win98
                l = l.replace('\n\n', '\n\t\n')
            label = gtk.Label(l.strip())
            label.set_line_wrap(True)
            label.set_selectable(True)
            label.set_justify(gtk.JUSTIFY_CENTER)
            label.set_size_request(250,-1)
            self.vbox.pack_start(label, expand=False, fill=False)

        self.scroll.add_with_viewport(self.vbox)

        self.outervbox.pack_start(self.scroll, padding=SPACING)

        self.donatebutton = gtk.Button(_("Donate"))
        self.donatebutton.connect('clicked', donatefunc)
        self.donatebuttonbox = gtk.HButtonBox()
        self.donatebuttonbox.pack_start(self.donatebutton,
                                        expand=False, fill=False)
        self.outervbox.pack_end(self.donatebuttonbox, expand=False, fill=False)

        self.win.add(self.outervbox)

        self.win.show_all()

    def close(self, widget):
        self.win.destroy()    


class LogWindow(object):
    def __init__(self, main, logbuffer, config):
        self.config = config
        self.main = main
        self.win = Window()
        self.win.set_title(_("%s Activity Log")%app_name)
        self.win.set_default_size(600, 200)
        self.win.set_border_width(SPACING)
            
        self.buffer = logbuffer
        self.text = gtk.TextView(self.buffer)
        self.text.set_editable(False)
        self.text.set_cursor_visible(False)
        self.text.set_wrap_mode(gtk.WRAP_WORD)

        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.scroll.set_shadow_type(gtk.SHADOW_IN)
        self.scroll.add(self.text)

        self.vbox = gtk.VBox(spacing=SPACING)
        self.vbox.pack_start(self.scroll)

        self.buttonbox = gtk.HButtonBox()
        self.buttonbox.set_spacing(SPACING)
        
        self.closebutton = gtk.Button(stock='gtk-close')
        self.closebutton.connect('clicked', self.close)
        
        self.savebutton = gtk.Button(stock='gtk-save')
        self.savebutton.connect('clicked', self.save_log_file_selection)

        self.clearbutton = gtk.Button(stock='gtk-clear')
        self.clearbutton.connect('clicked', self.clear_log)

        self.buttonbox.pack_start(self.savebutton)
        self.buttonbox.pack_start(self.closebutton)

        self.hbox2 = gtk.HBox(homogeneous=False)

        self.hbox2.pack_end(self.buttonbox, expand=False, fill=False)

        bb = gtk.HButtonBox()
        bb.pack_start(self.clearbutton)
        self.hbox2.pack_start(bb, expand=False, fill=True)

        self.vbox.pack_end(self.hbox2, expand=False, fill=True)

        self.win.add(self.vbox)        
        self.win.connect("destroy", lambda w: self.main.window_closed('log'))
        self.scroll_to_end()
        self.win.show_all()

    def scroll_to_end(self):
        mark = self.buffer.create_mark(None, self.buffer.get_end_iter())
        self.text.scroll_mark_onscreen(mark)

    def save_log_file_selection(self, *args):
        name = 'bittorrent.log'
        path = smart_dir(self.config['save_in'])
        fullname = os.path.join(path, name)
        self.main.open_window('savefile',
                              title=_("Save log in:"),
                              fullname=fullname,
                              got_location_func=self.save_log,
                              no_location_func=lambda: self.main.window_closed('savefile'))


    def save_log(self, saveas):
        self.main.window_closed('savefile')
        f = file(saveas, 'w')
        f.write(self.buffer.get_text(self.buffer.get_start_iter(),
                                     self.buffer.get_end_iter()))
        save_message = self.buffer.log_text(_("log saved"), None)
        f.write(save_message)
        f.close()

    def clear_log(self, *args):
        self.buffer.clear_log()

    def close(self, widget):
        self.win.destroy()


class LogBuffer(gtk.TextBuffer):

    def __init__(self):
        gtk.TextBuffer.__init__(self)

        tt = self.get_tag_table()

        size_tag = gtk.TextTag('small')
        size_tag.set_property('size-points', 10)
        tt.add(size_tag)

        info_tag = gtk.TextTag('info')
        info_tag.set_property('foreground', '#00a040')
        tt.add(info_tag)

        warning_tag = gtk.TextTag('warning')
        warning_tag.set_property('foreground', '#a09000')
        tt.add(warning_tag)

        error_tag = gtk.TextTag('error')
        error_tag.set_property('foreground', '#b00000')
        tt.add(error_tag)

        critical_tag = gtk.TextTag('critical')
        critical_tag.set_property('foreground', '#b00000')
        critical_tag.set_property('weight', pango.WEIGHT_BOLD)
        tt.add(critical_tag)


    def log_text(self, text, severity=CRITICAL):
        now_str = datetime.datetime.strftime(datetime.datetime.now(),
                                             '[%Y-%m-%d %H:%M:%S] ')
        self.insert_with_tags_by_name(self.get_end_iter(), now_str, 'small')
        if severity is not None:
            self.insert_with_tags_by_name(self.get_end_iter(), '%s\n'%text,
                                          'small', status_dict[severity])
        else:
            self.insert_with_tags_by_name(self.get_end_iter(),
                                          ' -- %s -- \n'%text, 'small')
            
        return now_str+text+'\n'

    def clear_log(self):
        self.set_text('')
        self.log_text(_("log cleared"), None)


class CheckButton(gtk.CheckButton): 
    def __init__(self, label, main, option_name, initial_value,
                 extra_callback=None):
        gtk.CheckButton.__init__(self, label)
        self.main = main
        self.option_name = option_name
        self.option_type = type(initial_value)
        self.set_active(bool(initial_value))
        self.extra_callback = extra_callback
        self.connect('toggled', self.callback)

    def callback(self, *args):
        self.main.config[self.option_name] = \
            self.option_type(not self.main.config[self.option_name])
        self.main.setfunc(self.option_name, self.main.config[self.option_name])
        if self.extra_callback is not None:
            self.extra_callback()


class SettingsWindow(object):

    def __init__(self, main, config, setfunc):
        self.main = main
        self.setfunc = setfunc
        self.config = config
        self.win = Window()
        self.win.connect("destroy", lambda w: main.window_closed('settings'))
        self.win.set_title(_("%s Settings")%app_name)
        self.win.set_border_width(SPACING)

        self.notebook = gtk.Notebook()

        self.vbox = gtk.VBox(spacing=SPACING)
        self.vbox.pack_start(self.notebook, expand=False, fill=False)

        # General tab
        if os.name == 'nt':
            self.cb_box = gtk.VBox(spacing=SPACING)
            self.cb_box.set_border_width(SPACING)
            self.notebook.append_page(self.cb_box, gtk.Label(_("General")))

            self.startup_checkbutton = CheckButton(
                _("Launch BitTorrent when Windows starts"), self,
                'launch_on_startup', self.config['launch_on_startup'])
            self.cb_box.pack_start(self.startup_checkbutton, expand=False, fill=False)
            self.startup_checkbutton.connect('toggled', self.launch_on_startup)

            self.minimize_checkbutton = CheckButton(
                _("Minimize to system tray"), self,
                'minimize_to_tray', self.config['minimize_to_tray'])
            self.cb_box.pack_start(self.minimize_checkbutton, expand=False, fill=False)

            # allow the user to set the progress bar text to all black
            self.progressbar_hack = CheckButton(
                _("Progress bar text is always black\n(requires restart)"),
                self, 'progressbar_hack', self.config['progressbar_hack'])

            self.cb_box.pack_start(self.progressbar_hack, expand=False, fill=False)
            # end General tab

        # Saving tab
        self.saving_box = gtk.VBox(spacing=SPACING)
        self.saving_box.set_border_width(SPACING)
        self.notebook.append_page(self.saving_box, gtk.Label(_("Saving")))

        self.dl_frame = gtk.Frame(_("Save new downloads in:"))
        self.saving_box.pack_start(self.dl_frame, expand=False, fill=False)

        self.dl_box = gtk.VBox(spacing=SPACING)
        self.dl_box.set_border_width(SPACING)
        self.dl_frame.add(self.dl_box)
        self.save_in_box = gtk.HBox(spacing=SPACING)

        self.dl_save_in = gtk.Entry()
        self.dl_save_in.set_editable(False)
        self.set_save_in(self.config['save_in'])
        self.save_in_box.pack_start(self.dl_save_in, expand=True, fill=True)

        self.dl_save_in_button = gtk.Button(_("Change..."))
        self.dl_save_in_button.connect('clicked', self.get_save_in)
        self.save_in_box.pack_start(self.dl_save_in_button, expand=False, fill=False)
        self.dl_box.pack_start(self.save_in_box, expand=False, fill=False)

        self.dl_ask_checkbutton = CheckButton(
            _("Ask where to save each new download"), self,
            'ask_for_save', self.config['ask_for_save'])

        self.dl_box.pack_start(self.dl_ask_checkbutton, expand=False, fill=False)
        # end Saving tab

        # Downloading tab
        self.downloading_box = gtk.VBox(spacing=SPACING)
        self.downloading_box.set_border_width(SPACING)
        self.notebook.append_page(self.downloading_box, gtk.Label(_("Downloading")))

        self.dnd_frame = gtk.Frame(_("When starting a new torrent:"))
        self.dnd_box = gtk.VBox(spacing=SPACING, homogeneous=True)
        self.dnd_box.set_border_width(SPACING)

        self.dnd_states = ['replace','add','ask']
        self.dnd_original_state = self.config['start_torrent_behavior']
        
        self.always_replace_radio = gtk.RadioButton(
            group=None,
            label=_("_Stop another running torrent to make room"))
        self.dnd_box.pack_start(self.always_replace_radio)
        self.always_replace_radio.state_name = self.dnd_states[0]
        
        self.always_add_radio = gtk.RadioButton(
            group=self.always_replace_radio,
            label=_("_Don't stop other running torrents"))
        self.dnd_box.pack_start(self.always_add_radio)
        self.always_add_radio.state_name = self.dnd_states[1]

        self.always_ask_radio = gtk.RadioButton(
            group=self.always_replace_radio,
            label=_("_Ask each time")
            )
        self.dnd_box.pack_start(self.always_ask_radio)
        self.always_ask_radio.state_name = self.dnd_states[2]

        self.dnd_group = self.always_replace_radio.get_group()
        for r in self.dnd_group:
            r.connect('toggled', self.start_torrent_behavior_changed)

        self.set_start_torrent_behavior(self.config['start_torrent_behavior'])
        
        self.dnd_frame.add(self.dnd_box)
        self.downloading_box.pack_start(self.dnd_frame, expand=False, fill=False)

        # Seeding tab
        self.seeding_box = gtk.VBox(spacing=SPACING)
        self.seeding_box.set_border_width(SPACING)
        self.notebook.append_page(self.seeding_box, gtk.Label(_("Seeding")))

        def colon_split(framestr):
            COLONS = (':', u'\uff1a')
            for colon in COLONS:
                if colon in framestr:
                    return framestr.split(colon)
            return '', framestr
        
        nt_framestr = _("Seed completed torrents: until share ratio reaches [_] percent, or for [_] minutes, whichever comes first.")
        nt_title, nt_rem = colon_split(nt_framestr)
        nt_msg1, nt_msg2, nt_msg4 = nt_rem.split('[_]')
        nt_msg3 = ''
        if ',' in nt_msg2:
            nt_msg2, nt_msg3 = nt_msg2.split(',')
            nt_msg2 += ','

        self.next_torrent_frame = gtk.Frame(nt_title+':')
        self.next_torrent_box   = gtk.VBox(spacing=SPACING, homogeneous=True)
        self.next_torrent_box.set_border_width(SPACING) 
        
        self.next_torrent_frame.add(self.next_torrent_box)


        self.next_torrent_ratio_box = gtk.HBox()
        self.next_torrent_ratio_box.pack_start(gtk.Label(nt_msg1),
                                               fill=False, expand=False)
        self.next_torrent_ratio_field = PercentValidator('next_torrent_ratio',
                                                         self.config, self.setfunc)
        self.next_torrent_ratio_box.pack_start(self.next_torrent_ratio_field,
                                               fill=False, expand=False)
        self.next_torrent_ratio_box.pack_start(gtk.Label(nt_msg2),
                                               fill=False, expand=False)
        self.next_torrent_box.pack_start(self.next_torrent_ratio_box)


        self.next_torrent_time_box = gtk.HBox()
        self.next_torrent_time_box.pack_start(gtk.Label(nt_msg3),
                                              fill=False, expand=False)
        self.next_torrent_time_field = MinutesValidator('next_torrent_time',
                                                        self.config, self.setfunc)
        self.next_torrent_time_box.pack_start(self.next_torrent_time_field,
                                              fill=False, expand=False)
        self.next_torrent_time_box.pack_start(gtk.Label(nt_msg4),
                                              fill=False, expand=False)
        self.next_torrent_box.pack_start(self.next_torrent_time_box)

        def seed_forever_extra():
            for field in (self.next_torrent_ratio_field,
                          self.next_torrent_time_field):
                field.set_sensitive(not self.config['seed_forever'])

        seed_forever_extra()
        self.seed_forever = CheckButton( _("Seed indefinitely"), self,
                                         'seed_forever',
                                         self.config['seed_forever'],
                                         seed_forever_extra)
        self.next_torrent_box.pack_start(self.seed_forever)
        # end next torrent seed behavior

        # begin last torrent seed behavior
        lt_framestr = _("Seed last completed torrent: until share ratio reaches [_] percent.")
        lt_title, lt_rem = colon_split(lt_framestr)
        lt_msg1, lt_msg2 = lt_rem.split('[_]')
        
        self.seeding_box.pack_start(self.next_torrent_frame, expand=False, fill=False)

        self.last_torrent_frame = gtk.Frame(lt_title+':')
        self.last_torrent_vbox = gtk.VBox(spacing=SPACING)
        self.last_torrent_vbox.set_border_width(SPACING)
        self.last_torrent_box = gtk.HBox()
        self.last_torrent_box.pack_start(gtk.Label(lt_msg1),
                                         expand=False, fill=False)
        self.last_torrent_ratio_field = PercentValidator('last_torrent_ratio',
                                                         self.config, self.setfunc)
        self.last_torrent_box.pack_start(self.last_torrent_ratio_field,
                                         fill=False, expand=False)
        self.last_torrent_box.pack_start(gtk.Label(lt_msg2),
                                         fill=False, expand=False)
        self.last_torrent_vbox.pack_start(self.last_torrent_box)
        
        def seed_last_forever_extra():
            self.last_torrent_ratio_field.set_sensitive(
                not self.config['seed_last_forever'])

        seed_last_forever_extra()

        self.seed_last_forever = CheckButton(_("Seed indefinitely"), self,
                                             'seed_last_forever',
                                             self.config['seed_last_forever'],
                                             seed_last_forever_extra)
        self.last_torrent_vbox.pack_start(self.seed_last_forever)

        self.last_torrent_frame.add(self.last_torrent_vbox)
        self.seeding_box.pack_start(self.last_torrent_frame, expand=False, fill=False)

        # Network tab
        self.network_box = gtk.VBox(spacing=SPACING)
        self.network_box.set_border_width(SPACING)
        self.notebook.append_page(self.network_box, gtk.Label(_("Network")))

        self.port_range_frame = gtk.Frame(_("Look for available port:"))        
        self.port_range_box = gtk.VBox(spacing=SPACING)
        self.port_range_box.set_border_width(SPACING)
        
        self.port_range = gtk.HBox()
        self.port_range.pack_start(gtk.Label(_("starting at port: ")),
                                   expand=False, fill=False)
        self.minport_field = PortValidator('minport', self.config, self.setfunc)
        self.minport_field.add_end('maxport')
        self.port_range.pack_start(self.minport_field, expand=False, fill=False)
        self.minport_field.settingswindow = self
        self.port_range.pack_start(gtk.Label(' (1024-65535)'),
                                   expand=False, fill=False)
        self.port_range_box.pack_start(self.port_range,
                                       expand=False, fill=False)

        self.upnp = CheckButton(_("Enable automatic port mapping")+' (_UPnP)',
                                self, 'upnp', self.config['upnp'], None)
        self.port_range_box.pack_start(self.upnp,
                                   expand=False, fill=False)

        self.port_range_frame.add(self.port_range_box)
        self.network_box.pack_start(self.port_range_frame, expand=False, fill=False)

        self.ip_frame = gtk.Frame(_("IP to report to the tracker:"))
        self.ip_box = gtk.VBox()
        self.ip_box.set_border_width(SPACING)
        self.ip_field = IPValidator('ip', self.config, self.setfunc)
        self.ip_box.pack_start(self.ip_field, expand=False, fill=False)
        label = gtk.Label(_("(Has no effect unless you are on the\nsame local network as the tracker)"))
        label.set_line_wrap(True)
        self.ip_box.pack_start(lalign(label), expand=False, fill=False)
        self.ip_frame.add(self.ip_box)
        self.network_box.pack_start(self.ip_frame, expand=False, fill=False)

        # end Network tab        

        # Language tab
        self.languagechooser = LanguageChooser()
        self.notebook.append_page(self.languagechooser, gtk.Label("Language"))
        # end Language tab

        # Advanced tab
        if advanced_ui:
            self.advanced_box = gtk.VBox(spacing=SPACING)
            self.advanced_box.set_border_width(SPACING)
            hint = gtk.Label(_("WARNING: Changing these settings can\nprevent %s from functioning correctly.")%app_name)
            self.advanced_box.pack_start(lalign(hint), expand=False, fill=False)
            self.store = gtk.ListStore(*[gobject.TYPE_STRING] * 2)
            for option in ui_options[advanced_ui_options_index:]:
                self.store.append((option, str(self.config[option])))

            self.treeview = gtk.TreeView(self.store)
            r = gtk.CellRendererText()
            column = gtk.TreeViewColumn(_("Option"), r, text=0)
            self.treeview.append_column(column)
            r = gtk.CellRendererText()
            r.set_property('editable', True)
            r.connect('edited', self.store_value_edited)
            column = gtk.TreeViewColumn(_("Value"), r, text=1)
            self.treeview.append_column(column)
            self.advanced_frame = gtk.Frame()
            self.advanced_frame.set_shadow_type(gtk.SHADOW_IN)
            self.advanced_frame.add(self.treeview)

            self.advanced_box.pack_start(self.advanced_frame, expand=False, fill=False)
            self.notebook.append_page(self.advanced_box, gtk.Label(_("Advanced")))
        

        self.win.add(self.vbox)
        self.win.show_all()


    def get_save_in(self, widget=None):
        self.file_selection = self.main.open_window('choosefolder',
                                                    title=_("Choose default download directory"),
                                                    fullname=self.config['save_in'],
                                                    got_location_func=self.set_save_in,
                                                    no_location_func=lambda: self.main.window_closed('choosefolder'))

    def set_save_in(self, save_location):
        self.main.window_closed('choosefolder')
        if os.path.isdir(save_location):
            if save_location[-1] != os.sep:
                save_location += os.sep
            self.config['save_in'] = save_location
            save_in = path_wrap(self.config['save_in'])
            self.dl_save_in.set_text(save_in)
            self.setfunc('save_in', self.config['save_in'])

    def launch_on_startup(self, *args):
        dst = os.path.join(get_startup_dir(), app_name)
        if self.config['launch_on_startup']:
            src = os.path.abspath(sys.argv[0])
            create_shortcut(src, dst, "--start_minimized")
        else:
            try:
                remove_shortcut(dst)
            except Exception, e:
                self.main.global_error(WARNING, _("Failed to remove shortcut: %s") % str(e))

    def set_start_torrent_behavior(self, state_name):
        if state_name in self.dnd_states:
            for r in self.dnd_group:
                if r.state_name == state_name:
                    r.set_active(True)
                else:
                    r.set_active(False)
        else:
            self.always_replace_radio.set_active(True)        

    def start_torrent_behavior_changed(self, radiobutton):
        if radiobutton.get_active():
            self.setfunc('start_torrent_behavior', radiobutton.state_name)

    def store_value_edited(self, cell, row, new_text):
        it = self.store.get_iter_from_string(row)
        option = ui_options[int(row)+advanced_ui_options_index]
        t = type(defconfig[option])
        try:
            if t is type(None) or t is str:
                value = new_text
            elif t is int or t is long:
                value = int(new_text)
            elif t is float:
                value = float(new_text)
            elif t is bool:
                value = value == 'True'
            else:
                raise TypeError, str(t)
        except ValueError:
            return
        self.setfunc(option, value)
        self.store.set(it, 1, str(value))

    def close(self, widget):
        self.win.destroy()


class FileListWindow(object):

    SET_PRIORITIES = False

    def __init__(self, metainfo, closefunc):
        self.metainfo = metainfo
        self.setfunc = None
        self.allocfunc = None
        self.win = Window()
        self.win.set_title(_('Files in "%s"') % self.metainfo.name)
        self.win.connect("destroy", closefunc)
        self.tooltips = gtk.Tooltips()

        self.filepath_to_iter = {}

        self.box1 = gtk.VBox()

        size_request = (0,0)
        if self.SET_PRIORITIES:
            self.toolbar = gtk.Toolbar()
            for label, tip, stockicon, method, arg in (
                (_("Never" ), _("Never download"   ), gtk.STOCK_DELETE, self.dosomething, -1,),
                (_("Normal"), _("Download normally"), gtk.STOCK_NEW   , self.dosomething,  0,),
                (_("First" ), _("Download first"   ),'bt-finished'    , self.dosomething, +1,),):
                self.make_tool_item(label, tip, stockicon, method, arg)
            size_request = (-1,54)
            self.box1.pack_start(self.toolbar, False)
            
        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.box1.pack_start(self.sw)
        self.win.add(self.box1)

        columns = [_("Filename"),_("Length"),_('%')]
        pre_size_list = ['M'*30, '6666 MB', '100.0', 'Download','black']
        if self.SET_PRIORITIES:
            columns.append(_("Download"))
        num_columns = len(pre_size_list)

        self.store = gtk.TreeStore(*[gobject.TYPE_STRING] * num_columns)
        self.store.append(None, pre_size_list)
        self.treeview = gtk.TreeView(self.store)
        self.treeview.set_enable_search(True)
        self.treeview.set_search_column(0)
        cs = []
        for i, name in enumerate(columns):
            r = gtk.CellRendererText()
            r.set_property('xalign', (0, 1, 1, 1)[i])
            if i == 0:
                column = gtk.TreeViewColumn(name, r, text = i, foreground = len(pre_size_list)-1)
            else:
                column = gtk.TreeViewColumn(name, r, text = i)
            column.set_resizable(True)
            self.treeview.append_column(column)
            cs.append(column)

        self.sw.add(self.treeview)
        self.treeview.set_headers_visible(False)
        self.treeview.columns_autosize()
        self.box1.show_all()
        self.treeview.realize()

        for column in cs:
            column.set_fixed_width(max(5,column.get_width()))
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.treeview.set_headers_visible(True)
        self.store.clear()

        if self.SET_PRIORITIES:
            self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        else:
            self.treeview.get_selection().set_mode(gtk.SELECTION_NONE)

        self.piecelen = self.metainfo.piece_length
        self.lengths = self.metainfo.sizes
        self.initialize_file_priorities()#[0,0])
        for name, size, priority in itertools.izip(self.metainfo.orig_files,
                                        self.metainfo.sizes, self.priorities):
            parent_name, local_name = os.path.split(name)
            parent_iter = self.recursive_add(parent_name)
            
            row = [local_name, Size(size), '?','', 'black']
            it = self.store.append(parent_iter, row)
            self.filepath_to_iter[name] = it
            
        self.treeview.expand_all()
        tvsr = self.treeview.size_request()
        vertical_padding = 18 
        size_request = [max(size_request[0],tvsr[0]),
                        (size_request[1] + tvsr[1] ) + vertical_padding]
        maximum_height = 300
        if size_request[1] > maximum_height - SCROLLBAR_WIDTH:
            size_request[1] = maximum_height
            size_request[0] = size_request[0] + SCROLLBAR_WIDTH
        self.win.set_default_size(*size_request)
                                  
        self.win.show_all()

    def recursive_add(self, fullpath):
        if fullpath == '':
            return None
        elif self.filepath_to_iter.has_key(fullpath):
            return self.filepath_to_iter[fullpath]
        else:
            parent_path, local_path = os.path.split(fullpath)
            parent_iter = self.recursive_add(parent_path)
            it = self.store.append(parent_iter,
                                   (local_path,) +
                                   ('',) * (self.store.get_n_columns()-2) +
                                   ('black',))
            self.filepath_to_iter[fullpath] = it
            return it

    def make_tool_item(self, label, tip, stockicon, method, arg): 
        icon = gtk.Image()
        icon.set_from_stock(stockicon, gtk.ICON_SIZE_SMALL_TOOLBAR)
        item = gtk.ToolButton(icon_widget=icon, label=label)
        item.set_homogeneous(True)
        item.set_tooltip(self.tooltips, tip)
        if arg is not None:
            item.connect('clicked', method, arg)
        else:
            item.connect('clicked', method)
        self.toolbar.insert(item, 0)

    def initialize_file_priorities(self):
        self.priorities = []
        for length in self.lengths:
            self.priorities.append(0)

## Uoti wrote these methods. I have no idea what this code is supposed to do.
##        --matt
##    def set_priorities(self, widget):
##        r = []
##        piece = 0
##        pos = 0
##        curprio = prevprio = 1000
##        for priority, length in itertools.izip(self.priorities, self.lengths):
##            pos += length
##            curprio = min(priority, curprio)
##            while pos >= (piece + 1) * self.piecelen:
##                if curprio != prevprio:
##                    r.extend((piece, curprio))
##                prevprio = curprio
##                if curprio == priority:
##                    piece = pos // self.piecelen
##                else:
##                    piece += 1
##                if pos == piece * self.piecelen:
##                    curprio = 1000
##                else:
##                    curprio = priority
##        if curprio != prevprio:
##            r.extend((piece, curprio))
##        self.setfunc(r)
##        it = self.store.get_iter_first()
##        for i in xrange(len(self.priorities)):
##            self.store.set_value(it, 5, "black")
##            it = self.store.iter_next(it)
##        self.origpriorities = list(self.priorities)
##
##    def initialize_file_priorities(self, piecepriorities):
##        self.priorities = []
##        piecepriorities = piecepriorities + [999999999]
##        it = iter(piecepriorities)
##        assert it.next() == 0
##        pos = piece = curprio = 0
##        for length in self.lengths:
##            pos += length
##            priority = curprio
##            while pos >= piece * self.piecelen:
##                curprio = it.next()
##                if pos > piece * self.piecelen:
##                    priority = max(priority, curprio)
##                piece = it.next()
##            self.priorities.append(priority)
##        self.origpriorities = list(self.priorities)

    def dosomething(self, widget, dowhat):
        self.treeview.get_selection().selected_foreach(self.adjustfile, dowhat)

    def adjustfile(self, treemodel, path, it, dowhat):
        length = treemodel.get(it, 1)[0]
        if length == '':
            child = treemodel.iter_children(it)
            while True:
                if child is None:
                    return
                elif not treemodel.is_ancestor(it, child):
                    return
                else:
                    self.adjustfile(treemodel, path, child, dowhat)
                child = treemodel.iter_next(child)
            
        else:
            # BUG: need to set file priorities in backend here
            if dowhat == -1:
                text, color = _("never"), 'darkgrey'
            elif dowhat == 1:
                text, color = _("first"), 'darkgreen'
            else:
                text, color = '', 'black'
            treemodel.set_value(it, 3, text )
            treemodel.set_value(it, 4, color)

    def update(self, left, allocated):
        for name, left, total, alloc in itertools.izip(
            self.metainfo.orig_files, left, self.lengths, allocated):
            it = self.filepath_to_iter[name]
            if total == 0:
                p = 1
            else:
                p = (total - left) / total
            self.store.set_value(it, 2, "%.1f" % (int(p * 1000)/10))

    def close(self):
        self.win.destroy()


class PeerListWindow(object):

    def __init__(self, torrent_name, closefunc):
        self.win = Window()
        self.win.connect("destroy", closefunc)
        self.win.set_title( _('Peers for "%s"')%torrent_name)
        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.sw.set_shadow_type(gtk.SHADOW_IN)
        self.win.add(self.sw)

        column_header = [_("IP address"), _("Client"), _("Connection"), _("KB/s down"), _("KB/s up"), _("MB downloaded"), _("MB uploaded"), _("% complete"), _("KB/s est. peer download")]
        pre_size_list = ['666.666.666.666', 'TorrentStorm 1.3', 'bad peer', 66666, 66666, '1666.66', '1666.66', '100.0', 6666]
        numeric_cols = [3,4,5,6,7,8]
        store_types = [gobject.TYPE_STRING]*3  + [gobject.TYPE_INT]*2 + [gobject.TYPE_STRING]*3 + [gobject.TYPE_INT]
        
        if advanced_ui:
            column_header[2:2] = [_("Peer ID")]
            pre_size_list[2:2] = ['-AZ2104-']
            store_types[2:2]   = [gobject.TYPE_STRING]
            column_header[5:5] = [_("Interested"),_("Choked"),_("Snubbed")]
            pre_size_list[5:5] = ['*','*','*']
            store_types[5:5]   = [gobject.TYPE_STRING]*3
            column_header[9:9] = [_("Interested"),_("Choked"),_("Optimistic upload")]
            pre_size_list[9:9] = ['*','*','*']
            store_types[9:9]   = [gobject.TYPE_STRING]*3
            numeric_cols = [4,8,12,13,14,15]

        num_columns = len(column_header)
        self.store = gtk.ListStore(*store_types)
        self.store.append(pre_size_list)

        def makesortfunc(sort_func):
            def sortfunc(treemodel, iter1, iter2, column):
                a_str = treemodel.get_value(iter1, column)
                b_str = treemodel.get_value(iter2, column)
                if a_str is not None and b_str is not None:
                    return sort_func(a_str,b_str)
                else:
                    return 0
            return sortfunc

        def ip_sort(a_str,b_str):
            for a,b in zip(a_str.split('.'), b_str.split('.')):
                if a == b:
                    continue
                if len(a) == len(b):
                    return cmp(a,b)
                return cmp(int(a), int(b))
            return 0

        def float_sort(a_str,b_str):
            a,b = 0,0
            try: a = float(a_str)
            except ValueError: pass
            try: b = float(b_str)
            except ValueError: pass
            return cmp(a,b)

        self.store.set_sort_func(0, makesortfunc(ip_sort), 0)
        for i in range(2,5):
            self.store.set_sort_func(num_columns-i, makesortfunc(float_sort), num_columns-i)
        
        self.treeview = gtk.TreeView(self.store)
        cs = []
        for i, name in enumerate(column_header):
            r = gtk.CellRendererText()
            if i in numeric_cols:
                r.set_property('xalign', 1)
            column = gtk.TreeViewColumn(name, r, text = i)
            column.set_resizable(True)
            column.set_min_width(5)
            column.set_sort_column_id(i)
            self.treeview.append_column(column)
            cs.append(column)
        self.treeview.set_rules_hint(True)
        self.sw.add(self.treeview)
        self.treeview.set_headers_visible(False)
        self.treeview.columns_autosize()
        self.sw.show_all()
        self.treeview.realize()
        for column in cs:
            column.set_fixed_width(column.get_width())
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.treeview.set_headers_visible(True)
        self.store.clear()
        self.treeview.get_selection().set_mode(gtk.SELECTION_NONE)
        width = self.treeview.size_request()[0]
        self.win.set_default_size(width+SCROLLBAR_WIDTH, 300)
        self.win.show_all()
        self.prev = []


    def update(self, peers, bad_peers):
        fields = []

        def p_bool(value): return value and '*' or ''

        for peer in peers:
            field = []
            field.append(peer['ip']) 

            client, version = ClientIdentifier.identify_client(peer['id']) 
            field.append(client + ' ' + version)

            if advanced_ui:
                field.append(zurllib.quote(peer['id'])) 
                
            field.append(peer['initiation'] == 'R' and _("remote") or _("local"))
            dl = peer['download']
            ul = peer['upload']

            for l in (dl, ul):
                rate = l[1]
                if rate > 100:
                    field.append(int(round(rate/(2**10)))) 
                else:
                    field.append(0)
                if advanced_ui:
                    field.append(p_bool(l[2]))
                    field.append(p_bool(l[3]))
                    if len(l) > 4:
                        field.append(p_bool(l[4]))
                    else:
                        field.append(p_bool(peer['is_optimistic_unchoke']))

            field.append('%.2f'%round(dl[0] / 2**20, 2))
            field.append('%.2f'%round(ul[0] / 2**20, 2))
            field.append('%.1f'%round(int(peer['completed']*1000)/10, 1))

            field.append(int(peer['speed']//(2**10)))

            fields.append(field)

        for (ip, (is_banned, stats)) in bad_peers.iteritems():
            field = []
            field.append(ip)

            client, version = ClientIdentifier.identify_client(stats.peerid)
            field.append(client + ' ' + version)

            if advanced_ui:
                field.append(zurllib.quote(stats.peerid))

            field.append(_("bad peer"))

            # the sortable peer list won't take strings in these fields
            field.append(0) 

            if advanced_ui:
                field.extend([0] * 7) # upRate, * fields
            else:
                field.extend([0] * 1) # upRate
                
            field.append(_("%d ok") % stats.numgood)
            field.append(_("%d bad") % len(stats.bad))
            if is_banned: # completion
                field.append(_("banned"))
            else:
                field.append(_("ok"))
            field.append(0) # peer dl rate
            fields.append(field)

        if self.store.get_sort_column_id() < 0:
            # ListStore is unsorted, it might be faster to set only modified fields
            it = self.store.get_iter_first()
            for old, new in itertools.izip(self.prev, fields):
                if old != new:
                    for i, value in enumerate(new):
                        if value != old[i]:
                            self.store.set_value(it, i, value)
                it = self.store.iter_next(it)
            for i in range(len(fields), len(self.prev)):
                self.store.remove(it)
            for i in range(len(self.prev), len(fields)):
                self.store.append(fields[i])
            self.prev = fields
        else:
            # ListStore is sorted, no reason not to to reset all fields
            self.store.clear()
            for field in fields:
                self.store.append(field)
            
        

    def close(self):
        self.win.destroy()


class TorrentInfoWindow(object):

    def __init__(self, torrent_box, closefunc):
        self.win = Window()
        self.torrent_box = torrent_box
        name = self.torrent_box.metainfo.name
        self.win.set_title(_('Info for "%s"')%name)
        self.win.set_size_request(-1,-1)
        self.win.set_border_width(SPACING)
        self.win.set_resizable(False)
        self.win.connect('destroy', closefunc)
        self.vbox = gtk.VBox(spacing=SPACING)

        self.table = gtk.Table(rows=4, columns=3, homogeneous=False)
        self.table.set_row_spacings(SPACING)
        self.table.set_col_spacings(SPACING)
        y = 0

        def add_item(key, val, y):
            self.table.attach(ralign(gtk.Label(key)), 0, 1, y, y+1)
            v = gtk.Label(val)
            v.set_selectable(True)
            self.table.attach(lalign(v), 1, 2, y, y+1)

        add_item(_("Torrent name:"), name, y)
        y+=1

        announce = ''
        if self.torrent_box.metainfo.is_trackerless:
            announce = _("(trackerless torrent)")
        else:
            announce = self.torrent_box.metainfo.announce
        add_item(_("Announce url:"), announce, y)
        y+=1

        size = Size(self.torrent_box.metainfo.total_bytes)
        num_files = _(", in one file")
        if self.torrent_box.is_batch:
            num_files = _(", in %d files") % len(self.torrent_box.metainfo.sizes)
        add_item(_("Total size:"),  str(size)+num_files, y)
        y+=1

        if advanced_ui:
            pl = self.torrent_box.metainfo.piece_length
            count, lastlen = divmod(size, pl)
            sizedetail = '%d x %d + %d = %d' % (count, pl, lastlen, int(size))
            add_item(_("Pieces:"), sizedetail, y)
            y+=1
            add_item(_("Info hash:"), self.torrent_box.infohash.encode('hex'), y)
            y+=1

        path = self.torrent_box.dlpath
        filename = ''
        if path is None:
            path = ''
        else:
            if not self.torrent_box.is_batch:
                path,filename = os.path.split(self.torrent_box.dlpath)
            if path[-1] != os.sep:
                path += os.sep
            path = path_wrap(path)
        add_item(_("Save in:"), path, y)
        y+=1

        if not self.torrent_box.is_batch:
            add_item(_("File name:"), path_wrap(filename), y)
            y+=1

        self.vbox.pack_start(self.table)        

        if self.torrent_box.metainfo.comment not in (None, ''):
            commentbuffer = gtk.TextBuffer()
            commentbuffer.set_text(self.torrent_box.metainfo.comment)
            commenttext = gtk.TextView(commentbuffer)
            commenttext.set_editable(False)
            commenttext.set_cursor_visible(False)
            commenttext.set_wrap_mode(gtk.WRAP_WORD)
            commentscroll = gtk.ScrolledWindow()
            commentscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
            commentscroll.set_shadow_type(gtk.SHADOW_IN)
            commentscroll.add(commenttext)
            self.vbox.pack_start(commentscroll)

        self.vbox.pack_start(gtk.HSeparator(), expand=False, fill=False)

        self.hbox = gtk.HBox(spacing=SPACING)
        lbbox = gtk.HButtonBox()
        rbbox = gtk.HButtonBox()
        lbbox.set_spacing(SPACING)

        if LaunchPath.can_launch_files:
            opendirbutton = IconButton(_("_Open directory"), stock=gtk.STOCK_OPEN)
            opendirbutton.connect('clicked', self.torrent_box.open_dir)
            lbbox.pack_start(opendirbutton, expand=False, fill=False)
            opendirbutton.set_sensitive(self.torrent_box.can_open_dir())

        filelistbutton = IconButton(_("Show _file list"), stock='gtk-index')
        if self.torrent_box.is_batch:
            filelistbutton.connect('clicked', self.torrent_box.open_filelist)
        else:
            filelistbutton.set_sensitive(False)
        lbbox.pack_start(filelistbutton, expand=False, fill=False)

        closebutton = gtk.Button(stock='gtk-close')
        closebutton.connect('clicked', lambda w: self.close())
        rbbox.pack_end(closebutton, expand=False, fill=False)

        self.hbox.pack_start(lbbox, expand=False, fill=False)
        self.hbox.pack_end(  rbbox, expand=False, fill=False)

        self.vbox.pack_end(self.hbox, expand=False, fill=False)

        self.win.add(self.vbox)
        
        self.win.show_all()

    def close(self):
        self.win.destroy()


class TorrentBox(gtk.EventBox):
    torrent_tip_format = '%s:\n %s\n %s'
    
    def __init__(self, infohash, metainfo, dlpath, completion, main):
        gtk.EventBox.__init__(self)
        self.infohash = infohash
        self.metainfo = metainfo
        self.completion = completion
        self.main = main

        self.main_torrent_dnd_tip = _("drag to reorder")
        self.torrent_menu_tip = _("right-click for menu")

        self.set_save_location(dlpath)

        self.uptotal   = self.main.torrents[self.infohash].uptotal
        self.downtotal = self.main.torrents[self.infohash].downtotal
        if self.downtotal > 0:
            self.up_down_ratio = self.uptotal / self.metainfo.total_bytes
        else:
            self.up_down_ratio = None

        self.infowindow = None
        self.filelistwindow = None
        self.is_batch = metainfo.is_batch
        self.menu = None
        self.menu_handler = None

        self.vbox = gtk.VBox(homogeneous=False, spacing=SPACING)
        self.label = gtk.Label()
        self.set_name()
        
        self.vbox.pack_start(lalign(self.label), expand=False, fill=False)

        self.hbox = gtk.HBox(homogeneous=False, spacing=SPACING)

        self.icon = gtk.Image()
        self.icon.set_size_request(-1, 29)

        self.iconbox = gtk.VBox()
        self.iconevbox = gtk.EventBox()        
        self.iconevbox.add(self.icon)
        self.iconbox.pack_start(self.iconevbox, expand=False, fill=False)
        self.hbox.pack_start(self.iconbox, expand=False, fill=False)
        
        self.vbox.pack_start(self.hbox)
        
        self.infobox = gtk.VBox(homogeneous=False)

        self.progressbarbox = gtk.HBox(homogeneous=False, spacing=SPACING)
        self.progressbar = gtk.ProgressBar()

        self.reset_progressbar_color()
        
        if self.completion is not None:
            self.progressbar.set_fraction(self.completion)
            if self.completion >= 1:
                done_label = self.make_done_label()
                self.progressbar.set_text(done_label)
            else:
                self.progressbar.set_text('%.1f%%'%(self.completion*100))
        else:
            self.progressbar.set_text('?')
            
        self.progressbarbox.pack_start(self.progressbar,
                                       expand=True, fill=True)

        self.buttonevbox = gtk.EventBox()
        self.buttonbox = gtk.HBox(homogeneous=True, spacing=SPACING)

        self.infobutton = gtk.Button()
        self.infoimage = gtk.Image()
        self.infoimage.set_from_stock('bt-info', gtk.ICON_SIZE_BUTTON)
        self.infobutton.add(self.infoimage)
        self.infobutton.connect('clicked', self.open_info)
        self.main.tooltips.set_tip(self.infobutton,
                                   _("Torrent info"))

        self.buttonbox.pack_start(self.infobutton, expand=True)

        self.cancelbutton = gtk.Button()
        self.cancelimage = gtk.Image()
        if self.completion is not None and self.completion >= 1:
            self.cancelimage.set_from_stock('bt-remove', gtk.ICON_SIZE_BUTTON)
            self.main.tooltips.set_tip(self.cancelbutton,
                                       _("Remove torrent"))
        else:
            self.cancelimage.set_from_stock('bt-abort', gtk.ICON_SIZE_BUTTON)
            self.main.tooltips.set_tip(self.cancelbutton,
                                       _("Abort torrent"))
            
        self.cancelbutton.add(self.cancelimage)
        # not using 'clicked' because we want to check for CTRL key
        self.cancelbutton.connect('button-release-event', self.confirm_remove)
        
        self.buttonbox.pack_start(self.cancelbutton, expand=True, fill=False)
        self.buttonevbox.add(self.buttonbox)

        vbuttonbox = gtk.VBox(homogeneous=False)
        vbuttonbox.pack_start(self.buttonevbox, expand=False, fill=False)
        self.hbox.pack_end(vbuttonbox, expand=False, fill=False)

        self.infobox.pack_start(self.progressbarbox, expand=False, fill=False)

        self.hbox.pack_start(self.infobox, expand=True, fill=True)
        self.add( self.vbox )

        self.drag_source_set(gtk.gdk.BUTTON1_MASK,
                             TARGET_ALL,
                             gtk.gdk.ACTION_MOVE|gtk.gdk.ACTION_COPY)
        self.connect('drag_data_get', self.drag_data_get)

        self.connect('drag_begin' , self.drag_begin )
        self.connect('drag_end'   , self.drag_end   )
        self.cursor_handler_id = self.connect('enter_notify_event', self.change_cursors)


    def set_save_location(self, dlpath):
        self.dlpath = dlpath
        updater_infohash = self.main.updater.infohash
        if updater_infohash == self.infohash:
            my_installer_dir = os.path.split(self.dlpath)[0]
            if self.main.updater.installer_dir != my_installer_dir:
                self.main.updater.set_installer_dir(my_installer_dir)


    def reset_progressbar_color(self):
        # Hack around broken GTK-Wimp theme:
        # make progress bar text always black
        # see task #694
        if is_frozen_exe and self.main.config['progressbar_hack']:
            style = self.progressbar.get_style().copy()
            black = style.black
            self.progressbar.modify_fg(gtk.STATE_PRELIGHT, black)
        

    def change_cursors(self, *args):
        # BUG: this is in a handler that is disconnected because the
        # window attributes are None until after show_all() is called
        self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
        self.buttonevbox.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
        self.disconnect(self.cursor_handler_id)
        

    def drag_data_get(self, widget, context, selection, targetType, eventTime):
        selection.set(selection.target, 8, self.infohash)

    def drag_begin(self, *args):
        pass

    def drag_end(self, *args):
        self.main.drag_end()

    def make_done_label(self, statistics=None):
        s = ''
        if statistics and statistics['timeEst'] is not None:
            s = _(", will seed for %s") % Duration(statistics['timeEst'])
        elif statistics:
            s = _(", will seed indefinitely.")

        if self.up_down_ratio is not None:
            done_label = _("Done, share ratio: %d%%") % \
                         (self.up_down_ratio*100) + s
        elif statistics is not None:
            done_label = _("Done, %s uploaded") % \
                         Size(statistics['upTotal']) + s
        else:
            done_label = _("Done")

        return done_label
        

    def set_name(self):
        self.label.set_text(self.metainfo.name)
        self.label.set_ellipsize(pango.ELLIPSIZE_END)

    def make_menu(self, extra_menu_items=[]):
        if self.menu_handler:
            self.disconnect(self.menu_handler)

        ## Basic Info
        menu_items = [ MenuItem(_("Torrent _info"   ), func=self.open_info), ]
        open_dir_func = None
        if LaunchPath.can_launch_files and self.can_open_dir():
            open_dir_func = self.open_dir
        menu_items.append( MenuItem(_("_Open directory" ), func=open_dir_func) )
        filelistfunc = None
        if self.is_batch:
            filelistfunc = self.open_filelist
        menu_items.append(MenuItem(_("_File list"), func=filelistfunc))
        if self.torrent_state == RUNNING:
            menu_items.append(MenuItem(_("_Peer list"), func=self.open_peerlist))
        ## end Basic Info

        menu_items.append(gtk.SeparatorMenuItem())

        ## Settings
        # change save location
        change_save_location_func = None
        if self.torrent_state != RUNNING and self.completion <= 0:
            change_save_location_func = self.change_save_location
        menu_items.append(MenuItem(_("_Change location"),
                                   func=change_save_location_func))
        # seed forever item
        self.seed_forever_item = gtk.CheckMenuItem(_("_Seed indefinitely"))
        self.reset_seed_forever()
        def sft(widget, *args):
            active = widget.get_active()
            infohash = self.infohash
            for option in ('seed_forever', 'seed_last_forever'):
                self.main.torrentqueue.set_config(option, active, infohash)
                self.main.torrentqueue.set_config(option, active, infohash)
        self.seed_forever_item.connect('toggled', sft)
        menu_items.append(self.seed_forever_item)
        ## end Settings

        menu_items.append(gtk.SeparatorMenuItem())

        ## Queue state dependent items
        if self.torrent_state == KNOWN:
            menu_items.append( MenuItem(_("Re_start"), func=self.move_to_end   ))
        elif self.torrent_state == QUEUED:
            #Here's where we'll put the "Start hash check" menu item
            menu_items.append(MenuItem(_("Download _now"), func=self.start))            
        elif self.torrent_state in (RUNNING, RUN_QUEUED):
            # no items for here
            pass

        ## Completion dependent items
        if self.completion is not None and self.completion >= 1:
            if self.torrent_state != KNOWN:
                menu_items.append(MenuItem(_("_Finish"), func=self.finish))
            menu_items.append( MenuItem(_("_Remove" ), func=self.confirm_remove))
        else:
            if self.torrent_state in (RUNNING, RUN_QUEUED):
                menu_items.append(MenuItem(_("Download _later"), func=self.move_to_end))
            else:
                #Here's where we'll put the "Seed _later" menu item
                pass
            menu_items.append(MenuItem(_("_Abort" ), func=self.confirm_remove))

        ## build the menu
        self.menu = gtk.Menu()

        for i in menu_items:
            i.show()
            self.menu.add(i)

        self.menu_handler = self.connect_object("event", self.show_menu, self.menu)

    def reset_seed_forever(self):
        sfb = False
        d = self.main.torrents[self.infohash].config.getDict()
        if d.has_key('seed_forever'):
            sfb = d['seed_forever']
        self.seed_forever_item.set_active(bool(sfb))        

    def change_save_location(self, widget=None):
        self.main.change_save_location(self.infohash)

    def open_info(self, widget=None):
        if self.infowindow is None:
            self.infowindow = TorrentInfoWindow(self, self.infoclosed)
    
    def infoclosed(self, widget=None):
        self.infowindow = None

    def close_info(self):
        if self.infowindow is not None:
            self.infowindow.close()

    def open_filelist(self, widget):
        if not self.is_batch:
            return
        if self.filelistwindow is None:
            self.filelistwindow = FileListWindow(self.metainfo,
                                                 self.filelistclosed)
            self.main.torrentqueue.check_completion(self.infohash, True)

    def filelistclosed(self, widget):
        self.filelistwindow = None

    def close_filelist(self):
        if self.filelistwindow is not None:
            self.filelistwindow.close()

    def close_child_windows(self):
        self.close_info()
        self.close_filelist()

    def destroy(self):
        if self.menu is not None:
            self.menu.destroy()
        self.menu = None
        gtk.EventBox.destroy(self)

    def show_menu(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            widget.popup(None, None, None, event.button, event.time)
            return True
        return False

    def _short_path(self, dlpath):
        path_length = 40
        sep = '...'
        ret = os.path.split(dlpath)[0]
        if len(ret) > path_length+len(sep):
            return ret[:int(path_length/2)]+sep+ret[-int(path_length/2):]
        else:
            return ret

    def get_path_to_open(self):
        path = self.dlpath
        if not self.is_batch:
            path = os.path.split(self.dlpath)[0]
        return path

    def can_open_dir(self):
        return os.access(self.get_path_to_open(), os.F_OK|os.R_OK)
        
    def open_dir(self, widget):
        LaunchPath.launchdir(self.get_path_to_open())

    def confirm_remove(self, widget, event=None):
        if event is not None and event.get_state() & gtk.gdk.CONTROL_MASK:
            self.remove()
        else:
            message = _('Are you sure you want to remove "%s"?') % self.metainfo.name
            if self.completion >= 1:
                if self.up_down_ratio is not None:
                    message = _("Your share ratio for this torrent is %d%%. ")%(self.up_down_ratio*100) + message
                else:
                    message = _("You have uploaded %s to this torrent. ")%(Size(self.uptotal)) + message

            d = MessageDialog(self.main.mainwindow,
                              _("Remove this torrent?"),
                              message, 
                              type=gtk.MESSAGE_QUESTION,
                              buttons=gtk.BUTTONS_OK_CANCEL,
                              yesfunc=self.remove,
                              default=gtk.RESPONSE_OK,
                              )

    def remove(self):
        self.main.torrentqueue.remove_torrent(self.infohash)


class KnownTorrentBox(TorrentBox):

    torrent_state = KNOWN

    def __init__(self, infohash, metainfo, dlpath, completion, main):
        TorrentBox.__init__(self, infohash, metainfo, dlpath, completion, main)

        status_tip = ''
        if completion >= 1:
            self.icon.set_from_stock('bt-finished', gtk.ICON_SIZE_LARGE_TOOLBAR)
            status_tip = _("Finished")
            known_torrent_dnd_tip = _("drag into list to seed")
        else:
            self.icon.set_from_stock('bt-broken', gtk.ICON_SIZE_LARGE_TOOLBAR)
            status_tip = _("Failed")
            known_torrent_dnd_tip = _("drag into list to resume")

        self.main.tooltips.set_tip(self.iconevbox,
                                   self.torrent_tip_format % (status_tip,
                                                              known_torrent_dnd_tip,
                                                              self.torrent_menu_tip))
        self.make_menu()
        self.show_all()

    def move_to_end(self, widget):
        self.main.change_torrent_state(self.infohash, QUEUED)
        

class DroppableTorrentBox(TorrentBox):

    def __init__(self, infohash, metainfo, dlpath, completion, main):
        TorrentBox.__init__(self, infohash, metainfo, dlpath, completion, main)

        self.drag_dest_set(gtk.DEST_DEFAULT_DROP,
                           TARGET_ALL,
                           gtk.gdk.ACTION_MOVE|gtk.gdk.ACTION_COPY)

        self.connect('drag_data_received', self.drag_data_received)
        self.connect('drag_motion', self.drag_motion)
        self.index = None

    def drag_data_received(self, widget, context, x, y, selection, targetType, time):
        if targetType == BT_TARGET_TYPE:
            half_height = self.size_request()[1] // 2
            where = cmp(y, half_height)
            if where == 0: where = 1
            self.parent.put_infohash_at_child(selection.data, self, where)
        else:
            self.main.accept_dropped_file(widget, context, x, y, selection, targetType, time)
        
    def drag_motion(self, widget, context, x, y, time):
        self.get_current_index()
        half_height = self.size_request()[1] // 2
        if y < half_height: 
            self.parent.highlight_before_index(self.index)
        else:
            self.parent.highlight_after_index(self.index)
        return False

    def drag_end(self, *args):
        self.parent.highlight_child()
        TorrentBox.drag_end(self, *args)

    def get_current_index(self):
        self.index = self.parent.get_index_from_child(self)


class QueuedTorrentBox(DroppableTorrentBox):
    icon_name = 'bt-queued'
    torrent_state = QUEUED

    def __init__(self, infohash, metainfo, dlpath, completion, main):
        DroppableTorrentBox.__init__(self, infohash, metainfo, dlpath, completion, main)

        self.state_name = _("Waiting")
        self.main.tooltips.set_tip(self.iconevbox,
                                   self.torrent_tip_format % (self.state_name,
                                                              self.main_torrent_dnd_tip,
                                                              self.torrent_menu_tip))

        self.icon.set_from_stock(self.icon_name, gtk.ICON_SIZE_LARGE_TOOLBAR)
        self.make_menu()
        self.show_all()

    def start(self, widget):
        self.main.runbox.put_infohash_last(self.infohash)

    def finish(self, widget):
        self.main.change_torrent_state(self.infohash, KNOWN)


class PausedTorrentBox(DroppableTorrentBox):
    icon_name = 'bt-paused'
    torrent_state = RUN_QUEUED

    def __init__(self, infohash, metainfo, dlpath, completion, main):
        DroppableTorrentBox.__init__(self, infohash, metainfo, dlpath, completion, main)

        self.state_name = _("Paused")
        self.main.tooltips.set_tip(self.iconevbox,
                                   self.torrent_tip_format % (self.state_name,
                                                              self.main_torrent_dnd_tip,
                                                              self.torrent_menu_tip))

        self.icon.set_from_stock(self.icon_name, gtk.ICON_SIZE_LARGE_TOOLBAR)
        self.make_menu()
        self.show_all()

    def move_to_end(self, widget):
        self.main.change_torrent_state(self.infohash, QUEUED)

    def finish(self, widget):
        self.main.change_torrent_state(self.infohash, KNOWN)

    def update_status(self, statistics):
        # in case the TorrentQueue thread calls widget.update_status()
        # before the GUI has changed the torrent widget to a
        # RunningTorrentBox
        pass


class RunningTorrentBox(PausedTorrentBox):
    torrent_state = RUNNING

    def __init__(self, infohash, metainfo, dlpath, completion, main):
        DroppableTorrentBox.__init__(self, infohash, metainfo, dlpath, completion, main)

        self.main.tooltips.set_tip(self.iconevbox,
                                   self.torrent_tip_format % (_("Running"),
                                                              self.main_torrent_dnd_tip,
                                                              self.torrent_menu_tip))

        self.seed = False
        self.peerlistwindow = None
        self.update_peer_list_flag = 0

        self.icon.set_from_stock('bt-running', gtk.ICON_SIZE_LARGE_TOOLBAR)

        self.rate_label_box = gtk.HBox(homogeneous=True)

        self.up_rate   = gtk.Label()
        self.down_rate = gtk.Label()
        self.rate_label_box.pack_start(lalign(self.up_rate  ),
                                       expand=True, fill=True)
        self.rate_label_box.pack_start(lalign(self.down_rate),
                                       expand=True, fill=True)

        self.infobox.pack_start(self.rate_label_box)        

        if advanced_ui:
            self.extrabox = gtk.VBox(homogeneous=False)
            #self.extrabox = self.vbox
            
            self.up_curr    = FancyLabel(_("Current up: %s"  ), 0)
            self.down_curr  = FancyLabel(_("Current down: %s"), 0)
            self.curr_box   = gtk.HBox(homogeneous=True)
            self.curr_box.pack_start(lalign(self.up_curr  ), expand=True, fill=True)
            self.curr_box.pack_start(lalign(self.down_curr), expand=True, fill=True)
            self.extrabox.pack_start(self.curr_box)
            
            self.up_prev    = FancyLabel(_("Previous up: %s"  ), 0)
            self.down_prev  = FancyLabel(_("Previous down: %s"), 0)
            self.prev_box   = gtk.HBox(homogeneous=True)
            self.prev_box.pack_start(lalign(self.up_prev  ), expand=True, fill=True)
            self.prev_box.pack_start(lalign(self.down_prev), expand=True, fill=True)
            self.extrabox.pack_start(self.prev_box)

            self.share_ratio = FancyLabel(_("Share ratio: %0.02f%%"), 0)
            self.extrabox.pack_start(lalign(self.share_ratio))

            self.peer_info = FancyLabel(_("%s peers, %s seeds. Totals from "
                                          "tracker: %s"), 0, 0, 'NA')
            self.extrabox.pack_start(lalign(self.peer_info))

            self.dist_copies = FancyLabel(_("Distributed copies: %d; Next: %s"), 0, '')
            self.extrabox.pack_start(lalign(self.dist_copies))

            self.piece_info = FancyLabel(_("Pieces: %d total, %d complete, "
                                           "%d partial, %d active (%d empty)"), *(0,)*5)
            self.extrabox.pack_start(lalign(self.piece_info))

            self.bad_info = FancyLabel(_("%d bad pieces + %s in discarded requests"), 0, 0)
            self.extrabox.pack_start(lalign(self.bad_info))

            # extra info
            
            pl = self.metainfo.piece_length
            tl = self.metainfo.total_bytes
            count, lastlen = divmod(tl, pl)
            self.piece_count = count + (lastlen > 0)

            self.infobox.pack_end(self.extrabox, expand=False, fill=False)

        self.make_menu()
        self.show_all() 


    def change_to_completed(self):
        self.completion = 1.0
        self.cancelimage.set_from_stock('bt-remove', gtk.ICON_SIZE_BUTTON)
        self.main.tooltips.set_tip(self.cancelbutton,
                                   _("Remove torrent"))

        updater_infohash = self.main.updater.infohash
        if updater_infohash == self.infohash:
            self.main.updater.start_install()

        self.make_menu()

    def close_child_windows(self):
        TorrentBox.close_child_windows(self)
        self.close_peerlist()

    def open_filelist(self, widget):
        if not self.is_batch:
            return
        if self.filelistwindow is None:
            self.filelistwindow = FileListWindow(self.metainfo,
                                                 self.filelistclosed)
            self.main.make_statusrequest()

    def open_peerlist(self, widget):
        if self.peerlistwindow is None:
            self.peerlistwindow = PeerListWindow(self.metainfo.name,
                                                 self.peerlistclosed)
            self.main.make_statusrequest()

    def peerlistclosed(self, widget):
        self.peerlistwindow = None
        self.update_peer_list_flag = 0

    def close_peerlist(self):
        if self.peerlistwindow is not None:
            self.peerlistwindow.close()

    rate_label = ': %s'
    eta_label = '?'
    done_label = _("Done")
    progress_bar_label = _("%.1f%% done, %s remaining")
    down_rate_label = _("Download rate")
    up_rate_label = _("Upload rate"  )
    
    def update_status(self, statistics):
        fractionDone = statistics.get('fractionDone')
        activity = statistics.get('activity')

        self.main.set_title(torrentName=self.metainfo.name,
                            fractionDone=fractionDone)

        dt = self.downtotal
        if statistics.has_key('downTotal'):
            dt += statistics['downTotal']

        ut = self.uptotal
        if statistics.has_key('upTotal'):
            ut += statistics['upTotal']

        if dt > 0:
            self.up_down_ratio = ut / self.metainfo.total_bytes

        done_label = self.done_label
        eta_label = self.eta_label
        if 'numPeers' in statistics:
            eta = statistics.get('timeEst')
            if eta is not None:
                eta_label = Duration(eta)
            if fractionDone == 1:
                done_label = self.make_done_label(statistics)

        if fractionDone == 1:
            self.progressbar.set_fraction(1)
            self.progressbar.set_text(done_label)
            self.reset_seed_forever()
            if not self.completion >= 1:
                self.change_to_completed()
        else:
            self.progressbar.set_fraction(fractionDone)
            progress_bar_label = self.progress_bar_label % \
                                 (int(fractionDone*1000)/10, eta_label) 
            self.progressbar.set_text(progress_bar_label)
            

        if 'numPeers' not in statistics:
            return

        self.down_rate.set_text(self.down_rate_label+self.rate_label %
                                Rate(statistics['downRate']))
        self.up_rate.set_text  (self.up_rate_label+self.rate_label %
                                Rate(statistics['upRate']))

        if advanced_ui:
            if self.up_down_ratio is not None:
                self.share_ratio.set_value(self.up_down_ratio*100)

            num_seeds = statistics['numSeeds']
            if self.seed:
                num_seeds = statistics['numOldSeeds'] = 0 # !@# XXX

            if statistics['trackerPeers'] is not None:
                totals = '%d/%d' % (statistics['trackerPeers'],
                                    statistics['trackerSeeds'])
            else:
                totals = _("NA")
            self.peer_info.set_value(statistics['numPeers'], num_seeds, totals)

            self.up_curr.set_value(str(Size(statistics['upTotal'])))
            self.down_curr.set_value(str(Size(statistics['downTotal'])))

            self.up_prev.set_value(str(Size(self.uptotal)))
            self.down_prev.set_value(str(Size(self.downtotal)))

            # refresh extra info
            self.piece_info.set_value(self.piece_count,
                                      statistics['storage_numcomplete'],
                                      statistics['storage_dirty'],
                                      statistics['storage_active'],
                                      statistics['storage_new'] )

            self.dist_copies.set_value( statistics['numCopies'], ', '.join(["%d:%.1f%%" % (a, int(b*1000)/10) for a, b in zip(itertools.count(int(statistics['numCopies']+1)), statistics['numCopyList'])]))

            self.bad_info.set_value(statistics['storage_numflunked'], Size(statistics['discarded']))
        
        if self.peerlistwindow is not None:
            if self.update_peer_list_flag == 0:
                spew = statistics.get('spew')
                if spew is not None:
                    self.peerlistwindow.update(spew, statistics['bad_peers'])
            self.update_peer_list_flag = (self.update_peer_list_flag + 1) % 4
        if self.filelistwindow is not None:
            if 'files_left' in statistics:
                self.filelistwindow.update(statistics['files_left'],
                                           statistics['files_allocated'])


class DroppableHSeparator(PaddedHSeparator):

    def __init__(self, box, spacing=SPACING):
        PaddedHSeparator.__init__(self, spacing)
        self.box = box
        self.main = box.main

        self.drag_dest_set(gtk.DEST_DEFAULT_DROP,
                           TARGET_ALL,
                           gtk.gdk.ACTION_MOVE|gtk.gdk.ACTION_COPY)

        self.connect('drag_data_received', self.drag_data_received)
        self.connect('drag_motion'       , self.drag_motion       )

    def drag_highlight(self):
        self.sep.drag_highlight()
        self.main.add_unhighlight_handle()

    def drag_unhighlight(self):
        self.sep.drag_unhighlight()

    def drag_data_received(self, widget, context, x, y, selection, targetType, time):
        if targetType == BT_TARGET_TYPE:
            self.box.drop_on_separator(self, selection.data)
        else:
            self.main.accept_dropped_file(widget, context, x, y, selection, targetType, time)

    def drag_motion(self, wid, context, x, y, time):
        self.drag_highlight()
        return False


class DroppableBox(HSeparatedBox):
    def __init__(self, main, spacing=0):
        HSeparatedBox.__init__(self, spacing=spacing)
        self.main = main
        self.drag_dest_set(gtk.DEST_DEFAULT_DROP,
                           TARGET_ALL,
                           gtk.gdk.ACTION_MOVE|gtk.gdk.ACTION_COPY)
        self.connect('drag_data_received', self.drag_data_received)
        self.connect('drag_motion', self.drag_motion)

    def drag_motion(self, widget, context, x, y, time):
        return False

    def drag_data_received(self, widget, context, x, y, selection, targetType, time):
        pass


class KnownBox(DroppableBox):

    def __init__(self, main, spacing=0):
        DroppableBox.__init__(self, main, spacing=spacing)
        self.drag_dest_set(gtk.DEST_DEFAULT_DROP,
                           TARGET_ALL,
                           gtk.gdk.ACTION_MOVE|gtk.gdk.ACTION_COPY)

    def pack_start(self, widget, *args, **kwargs):
        old_len = len(self.get_children())
        DroppableBox.pack_start(self, widget, *args, **kwargs)
        if old_len <= 0:
            self.main.maximize_known_pane()
        self.main.knownscroll.scroll_to_bottom()

    def remove(self, widget):
        DroppableBox.remove(self, widget)
        new_len = len(self.get_children())
        if new_len == 0:
            self.main.maximize_known_pane()

    def drag_data_received(self, widget, context, x, y, selection, targetType, time):
        if targetType == BT_TARGET_TYPE:
            infohash = selection.data
            self.main.finish(infohash)
        else:
            self.main.accept_dropped_file(widget, context, x, y, selection, targetType, time)

    def drag_motion(self, widget, context, x, y, time):
        self.main.drag_highlight(widget=self)
    
    def drag_highlight(self):
        self.main.knownscroll.drag_highlight()
        self.main.add_unhighlight_handle()

    def drag_unhighlight(self):
        self.main.knownscroll.drag_unhighlight()


class RunningAndQueueBox(gtk.VBox):

    def __init__(self, main, **kwargs):
        gtk.VBox.__init__(self, **kwargs)
        self.main = main

    def drop_on_separator(self, sep, infohash):
        self.main.change_torrent_state(infohash, QUEUED, 0)

    def highlight_between(self):
        self.drag_highlight()

    def drag_highlight(self):
        self.get_children()[1].drag_highlight()

    def drag_unhighlight(self):
        self.get_children()[1].drag_unhighlight()
        

class SpacerBox(DroppableBox):
    
    def drag_data_received(self, widget, context, x, y, selection, targetType, time):
        if targetType == BT_TARGET_TYPE:
            infohash = selection.data
            self.main.queuebox.put_infohash_last(infohash)
        else:
            self.main.accept_dropped_file(widget, context, x, y, selection, targetType, time)
            
        return True

BEFORE = -1
AFTER  =  1

class ReorderableBox(DroppableBox):

    def new_separator(self):
        return DroppableHSeparator(self)

    def __init__(self, main):
        DroppableBox.__init__(self, main)
        self.main = main

        self.drag_dest_set(gtk.DEST_DEFAULT_DROP,
                           TARGET_ALL,
                           gtk.gdk.ACTION_MOVE|gtk.gdk.ACTION_COPY)

        self.connect('drag_data_received', self.drag_data_received)
        self.connect('drag_motion'       , self.drag_motion)

    def drag_data_received(self, widget, context, x, y, selection, targetType, time):
        
        if targetType == BT_TARGET_TYPE:
            half_height = self.size_request()[1] // 2
            if y < half_height:
                self.put_infohash_first(selection.data)
            else:
                self.put_infohash_last(selection.data)
        else:
            self.main.accept_dropped_file(widget, context, x, y, selection, targetType, time)
        return True

    def drag_motion(self, widget, context, x, y, time):
        return False

    def drag_highlight(self):
        final = self.get_children()[-1]
        final.drag_highlight()
        self.main.add_unhighlight_handle()

    def drag_unhighlight(self): 
        self.highlight_child(index=None)
        self.parent.drag_unhighlight()

    def highlight_before_index(self, index):
        self.drag_unhighlight()
        children = self._get_children()
        if index > 0:
            children[index*2 - 1].drag_highlight()
        else:
            self.highlight_at_top()

    def highlight_after_index(self, index):
        self.drag_unhighlight()
        children = self._get_children()
        if index*2 < len(children)-1:
            children[index*2 + 1].drag_highlight()
        else:
            self.highlight_at_bottom()

    def highlight_child(self, index=None):
        for i, child in enumerate(self._get_children()):
            if index is not None and i == index*2:
                child.drag_highlight()
            else:
                child.drag_unhighlight()


    def drop_on_separator(self, sep, infohash):
        children = self._get_children()
        for i, child in enumerate(children):
            if child == sep:
                reference_child = children[i-1]
                self.put_infohash_at_child(infohash, reference_child, AFTER)
                break


    def get_queue(self):
        queue = []
        c = self.get_children()
        for t in c:
            queue.append(t.infohash)
        return queue

    def put_infohash_first(self, infohash):
        self.highlight_child()
        children = self.get_children()
        if len(children) > 1 and infohash == children[0].infohash:
            return
        
        self.put_infohash_at_index(infohash, 0)

    def put_infohash_last(self, infohash):
        self.highlight_child()
        children = self.get_children()
        end = len(children)
        if len(children) > 1 and infohash == children[end-1].infohash:
            return

        self.put_infohash_at_index(infohash, end)

    def put_infohash_at_child(self, infohash, reference_child, where):
        self.highlight_child()
        if infohash == reference_child.infohash:
            return
        
        target_index = self.get_index_from_child(reference_child)
        if where == AFTER:
            target_index += 1
        self.put_infohash_at_index(infohash, target_index)

    def get_index_from_child(self, child):
        c = self.get_children()
        ret = -1
        try:
            ret = c.index(child)
        except ValueError:
            pass
        return ret

    def highlight_at_top(self):
        raise NotImplementedError

    def highlight_at_bottom(self):
        raise NotImplementedError

    def put_infohash_at_index(self, infohash, end):
        raise NotImplementedError

class RunningBox(ReorderableBox):

    def put_infohash_at_index(self, infohash, target_index):
        #print 'RunningBox.put_infohash_at_index', infohash.encode('hex')[:8], target_index

        l = self.get_queue()
        replaced = None
        if l:
            replaced = l[-1]
        self.main.confirm_replace_running_torrent(infohash, replaced,
                                                  target_index)

    def highlight_at_top(self):
        pass
        # BUG: Don't know how I will indicate in the UI that the top of the list is highlighted

    def highlight_at_bottom(self):
        self.parent.highlight_between()


class QueuedBox(ReorderableBox):

    def put_infohash_at_index(self, infohash, target_index):
        #print 'want to put', infohash.encode('hex'), 'at', target_index
        self.main.change_torrent_state(infohash, QUEUED, target_index)

    def highlight_at_top(self):
        self.parent.highlight_between()

    def highlight_at_bottom(self):
        pass
        # BUG: Don't know how I will indicate in the UI that the bottom of the list is highlighted



class Struct(object):
    pass


class SearchField(gtk.Entry):
    def __init__(self, default_text, visit_url_func):
        gtk.Entry.__init__(self)
        self.default_text = default_text
        self.visit_url_func = visit_url_func
        self.set_text(self.default_text)
        self.set_size_request(150, -1)

        # default gtk Entry dnd processing is broken on linux!
        #  - default Motion handling causes asyncs
        #  - there's no way to filter the default text dnd
        # see the parent window for a very painful work-around
        self.drag_dest_unset()
        
        self.connect('key-press-event', self.check_for_enter)
        self.connect('button-press-event', self.begin_edit)
        self.search_completion = gtk.EntryCompletion()
        self.search_completion.set_text_column(0)
        self.search_store = gtk.ListStore(gobject.TYPE_STRING)
        self.search_completion.set_model(self.search_store)
        self.set_completion(self.search_completion)
        self.reset_text()
        self.timeout_id = None

    def begin_edit(self, *args):
        if self.get_text() == self.default_text:
            self.set_text('')

    def check_for_enter(self, widget, event):
        if event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
            self.search()

    def reset_text(self):
        self.set_text(self.default_text)

    def search(self, *args):
        search_term = self.get_text()
        if search_term and search_term != self.default_text:
            self.search_store.append([search_term])
            search_url = SEARCH_URL % {'query' :zurllib.quote(search_term),
                                       'client':'M-%s'%version.replace('.','-')}
            
            self.timeout_id = gobject.timeout_add(2000, self.resensitize)
            self.set_sensitive(False)
            self.visit_url_func(search_url, callback=self.resensitize)
        else:
            self.reset_text()
            self.select_region(0, -1)
            self.grab_focus()

    def resensitize(self):
        self.set_sensitive(True)
        self.reset_text()
        if self.timeout_id is not None:
            gobject.source_remove(self.timeout_id)
            self.timeout_id = None


class DownloadInfoFrame(object):

    def __init__(self, config, torrentqueue):
        self.config = config
        if self.config['save_in'] == '':
           self.config['save_in'] = smart_dir('')
        
        self.torrentqueue = torrentqueue
        self.torrents = {}
        self.running_torrents = {}
        self.lists = {}
        self.update_handle = None
        self.unhighlight_handle = None
        self.custom_size = False
        self.child_windows = {}
        self.postponed_save_windows = []
        self.helpwindow     = None
        self.errordialog    = None

        self.mainwindow = Window(gtk.WINDOW_TOPLEVEL)

        #tray icon
        self.trayicon = TrayIcon(not self.config['start_minimized'],
                                 toggle_func=self.toggle_shown,
                                 quit_func=self.quit)
        self.traythread = threading.Thread(target=self.trayicon.enable,
                                           args=())
        self.traythread.setDaemon(True)

        if os.name == "nt":
            # gtk has no way to check this?
            self.iconized = False
            self.mainwindow.connect('window-state-event', self.window_event) 

        if self.config['start_minimized']:
            self.mainwindow.iconify()
       
        gtk.threads_enter()

        self.mainwindow.set_border_width(0)

        self.set_seen_remote_connections(False)
        self.set_seen_connections(False)

        self.mainwindow.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                      TARGET_EXTERNAL,
                                      gtk.gdk.ACTION_MOVE|gtk.gdk.ACTION_COPY)

        self.mainwindow.connect('drag_leave'        , self.drag_leave         )
        self.mainwindow.connect('drag_data_received', self.accept_dropped_file)

        self.mainwindow.set_size_request(WINDOW_WIDTH, -1)

        self.mainwindow.connect('destroy', self.cancel)

        self.mainwindow.connect('size-allocate', self.size_was_allocated)

        self.accel_group = gtk.AccelGroup()

        self.mainwindow.add_accel_group(self.accel_group)

        #self.accel_group.connect(ord('W'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED,
        #                         lambda *args: self.mainwindow.destroy())

        self.tooltips = gtk.Tooltips()

        self.logbuffer = LogBuffer()
        self.log_text(_("%s started")%app_name, severity=None)

        self.box1 = gtk.VBox(homogeneous=False, spacing=0)

        self.box2 = gtk.VBox(homogeneous=False, spacing=0)
        self.box2.set_border_width(SPACING)

        self.menubar = gtk.MenuBar()
        self.box1.pack_start(self.menubar, expand=False, fill=False)

        self.ssbutton = StopStartButton(self)

        # keystrokes used: A D F H L N O P Q S U X (E)

        quit_menu_label = _("_Quit")
        if os.name == 'nt':
            quit_menu_label = _("E_xit")
        
        file_menu_items = ((_("_Open torrent file"), self.select_torrent_to_open),
                           (_("Open torrent _URL"), self.enter_url_to_open),
                           (_("Make _new torrent" ), self.make_new_torrent),

                           ('----'          , None),
                           (_("_Pause/Play"), self.ssbutton.toggle),
                           ('----'          , None),
                           (quit_menu_label , lambda w: self.mainwindow.destroy()),
                           )
        view_menu_items = ((_("Show/Hide _finished torrents"), self.toggle_known),
                           # BUG: if you reorder this menu, see def set_custom_size() first
                           (_("_Resize window to fit"), lambda w: self.resize_to_fit()),
                           ('----'             , None),
                           (_("_Log")          , lambda w: self.open_window('log')),
                           # 'View log of all download activity',
                           #('----'            , None),
                           (_("_Settings")     , lambda w: self.open_window('settings')),
                           #'Change download behavior and network settings',
                           )
        help_menu_items = ((_("_Help")         , self.open_help),
                           #(_("_Help Window") , lambda w: self.open_window('help')),
                           (_("_About")         , lambda w: self.open_window('about')),
                           (_("_Donate")        , lambda w: self.donate()),
                           #(_("Rais_e")        , lambda w: self.raiseerror()), 
                           )
        
        self.filemenu = gtk.MenuItem(_("_File"))

        self.filemenu.set_submenu(build_menu(file_menu_items, self.accel_group))
        self.filemenu.show()

        self.viewmenu = gtk.MenuItem(_("_View"))
        self.viewmenu.set_submenu(build_menu(view_menu_items, self.accel_group))
        self.viewmenu.show()

        self.helpmenu = gtk.MenuItem(_("_Help"))
        self.helpmenu.set_submenu(build_menu(help_menu_items, self.accel_group))
        self.helpmenu.show()

        if os.name != 'nt':
            self.helpmenu.set_right_justified(True)

        self.menubar.append(self.filemenu)
        self.menubar.append(self.viewmenu)
        self.menubar.append(self.helpmenu)
        
        self.menubar.show()

        self.header = gtk.HBox(homogeneous=False)

        self.box1.pack_start(self.box2, expand=False, fill=False)

        # control box: rate slider, start-stop button, search widget, status light
        self.controlbox = gtk.HBox(homogeneous=False)

        controlbox_padding = SPACING//2

        # stop-start button
        self.controlbox.pack_start(malign(self.ssbutton),
                                   expand=False, fill=False)

        # rate slider
        self.rate_slider_box = RateSliderBox(self.config, self.torrentqueue)
        self.controlbox.pack_start(self.rate_slider_box,
                                   expand=True, fill=True,
                                   padding=controlbox_padding)

        self.controlbox.pack_start(gtk.VSeparator(), expand=False, fill=False,
                                   padding=controlbox_padding)

        # search box 
        self.search_field = SearchField(_("Search for torrents"), self.visit_url)
        sfa = gtk.Alignment(xalign=0, yalign=0.5, xscale=1, yscale=0)
        sfa.add(self.search_field)
        self.controlbox.pack_start(sfa,
                                   expand=False, fill=False, padding=controlbox_padding)

        # separator
        self.controlbox.pack_start(gtk.VSeparator(), expand=False, fill=False,
                                   padding=controlbox_padding)

        # status light
        self.status_light = StatusLight(self)

        self.controlbox.pack_start(malign(self.status_light),
                                   expand=False, fill=False)

        self.box2.pack_start(self.controlbox,
                             expand=False, fill=False, padding=0)
        # end control box

        self.paned = gtk.VPaned()

        self.knownscroll = ScrolledWindow()
        self.knownscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.knownscroll.set_shadow_type(gtk.SHADOW_NONE)
        self.knownscroll.set_size_request(-1, SPACING)

        self.knownbox = KnownBox(self)
        self.knownbox.set_border_width(SPACING)

        self.knownscroll.add_with_viewport(self.knownbox)
        self.paned.pack1(self.knownscroll, resize=False, shrink=True)

        
        self.mainscroll = AutoScrollingWindow()
        self.mainscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.mainscroll.set_shadow_type(gtk.SHADOW_NONE)
        self.mainscroll.set_size_request(-1, SPACING)

        self.scrollbox = RunningAndQueueBox(self, homogeneous=False)
        self.scrollbox.set_border_width(SPACING)
        
        self.runbox = RunningBox(self)
        self.scrollbox.pack_start(self.runbox, expand=False, fill=False)

        self.scrollbox.pack_start(DroppableHSeparator(self.scrollbox), expand=False, fill=False)

        self.queuebox = QueuedBox(self)
        self.scrollbox.pack_start(self.queuebox, expand=False, fill=False)

        self.scrollbox.pack_start(SpacerBox(self), expand=True, fill=True) 

        self.mainscroll.add_with_viewport(self.scrollbox)

        self.paned.pack2(self.mainscroll, resize=True, shrink=False)

        self.box1.pack_start(self.paned)

        self.box1.show_all()

        self.mainwindow.add(self.box1)

        self.set_title()
        self.set_size()
        
        self.mainwindow.show()
        
        self.paned.set_position(0)
        self.search_field.grab_focus()

        self.updater = NewVersion.Updater(
            gtk_wrap, 
            self.new_version, 
            self.torrentqueue.start_new_torrent,
            self.confirm_install_new_version   ,
            self.global_error                  ,
            self.config['new_version']         ,
            self.config['current_version']     )

        self.nag()
        
        gtk.threads_leave()

    def window_event(self, widget, event, *args):
        if event.changed_mask == gtk.gdk.WINDOW_STATE_ICONIFIED:
            if self.config['minimize_to_tray']:
                if self.iconized == False:
                    self.mainwindow.hide()
            self.trayicon.set_toggle_state(self.iconized)
            self.iconized = not self.iconized

    def drag_leave(self, *args):
        self.drag_end()

    def make_new_torrent(self, widget=None):
        btspawn(self.torrentqueue, 'maketorrent')

    def accept_dropped_file(self, widget, context, x, y, selection,
                            targetType, time):
        if targetType == EXTERNAL_FILE_TYPE:
            d = selection.data.strip()
            file_uris = d.split('\r\n')
            for file_uri in file_uris:
                # this catches non-url entries, I've seen "\x00" at the end of lists
                if file_uri.find(':/') != -1:
                    file_name = zurllib.url2pathname(file_uri)
                    file_name = file_name[7:]
                    if os.name == 'nt':
                        file_name = file_name.strip('\\')
                    self.open_torrent( file_name )
        elif targetType == EXTERNAL_STRING_TYPE:

            data = selection.data.strip()

            # size must be > 0,0 for the intersection code to register it
            drop_rect = gtk.gdk.Rectangle(x, y, 1, 1)
            if ((self.search_field.intersect(drop_rect) is not None) and
                (not data.lower().endswith(".torrent"))):

                client_point = self.mainwindow.translate_coordinates(self.search_field, x, y)
                layout_offset = self.search_field.get_layout_offsets()
                point = []
                # subtract (not add) the offset, because we're hit-testing the layout, not the widget
                point.append(client_point[0] - layout_offset[0])
                point.append(client_point[1] - layout_offset[1])
                # ha ha ha. pango is so ridiculous
                point[0] *= pango.SCALE
                point[1] *= pango.SCALE
                layout = self.search_field.get_layout()
                position = layout.xy_to_index(*point)
                self.search_field.insert_text(data, position[0])
            else:                    
                self.open_url(data)

    def drag_highlight(self, widget=None):
        widgets = (self.knownbox, self.runbox, self.queuebox) 
        for w in widgets:
            if w != widget:
                w.drag_unhighlight()
        for w in widgets:
            if w == widget:
                w.drag_highlight()
                self.add_unhighlight_handle()

    def drag_end(self):
        self.drag_highlight(widget=None)
        self.mainscroll.stop_scrolling()

    def set_title(self, torrentName=None, fractionDone=None):
        title = app_name
        trunc = '...'
        sep = ': '

        if self.config['pause']:
            title += sep+_("(stopped)")
        elif len(self.running_torrents) == 1 and torrentName and \
               fractionDone is not None:
            maxlen = WINDOW_TITLE_LENGTH - len(app_name) - len(trunc) - len(sep)
            if len(torrentName) > maxlen:
                torrentName = torrentName[:maxlen] + trunc
            title = '%s%s%0.1f%%%s%s'% (app_name,
                                            sep,
                                            (int(fractionDone*1000)/10),
                                            sep,
                                            torrentName)
        elif len(self.running_torrents) > 1:
            title += sep+_("(multiple)")

        if self.mainwindow.get_title() != title:
            self.mainwindow.set_title(title)
        if self.trayicon.get_tooltip() != title:
            self.trayicon.set_tooltip(title)

    def _guess_size(self):
        paned_height = self.scrollbox.size_request()[1]
        if hasattr(self.paned, 'style_get_property'):
            paned_height += self.paned.style_get_property('handle-size')
        else:
            paned_height += 5
        paned_height += self.paned.get_position()
        paned_height += 4 # fudge factor, probably from scrolled window beveling ?
        paned_height = max(paned_height, MIN_MULTI_PANE_HEIGHT)

        new_height = self.menubar.size_request()[1] + \
                     self.box2.size_request()[1] + \
                     paned_height
        new_height = min(new_height, MAX_WINDOW_HEIGHT)
        new_width = max(self.scrollbox.size_request()[0] + SCROLLBAR_WIDTH, WINDOW_WIDTH)
        return new_width, new_height

    def set_size(self):
        if not self.custom_size:
            self.mainwindow.resize(*self._guess_size())

    def size_was_allocated(self, *args):
        current_size = self.mainwindow.get_size()
        target_size = self._guess_size()
        if current_size == target_size:
            self.set_custom_size(False)
        else:
            self.set_custom_size(True)

    def resize_to_fit(self):
        self.set_custom_size(False)
        self.set_size()

    def set_custom_size(self, val):
        self.custom_size = val
        # BUG this is a hack:
        self.viewmenu.get_submenu().get_children()[1].set_sensitive(val)

    # BUG need to add handler on resize event to keep track of
    # old_position when pane is hidden manually
    def split_pane(self):
        pos = self.paned.get_position()
        if pos > 0:
            self.paned.old_position = pos
            self.paned.set_position(0)
        else:
            if hasattr(self.paned, 'old_position'):
                self.paned.set_position(self.paned.old_position)
            else:
                self.maximize_known_pane()

    def maximize_known_pane(self):
        self.set_pane_position(self.knownbox.size_request()[1])        

    def set_pane_position(self, pane_position):
            pane_position = min(MAX_WINDOW_HEIGHT//2, pane_position)
            self.paned.set_position(pane_position)

    def toggle_known(self, widget=None):
        self.split_pane()

    def open_window(self, window_name, *args, **kwargs):
        if os.name == 'nt':
            self.mainwindow.present()
        savewidget = SaveFileSelection
        if window_name == 'savedir':
            savewidget = CreateFolderSelection
            window_name = 'savefile'
        if self.child_windows.has_key(window_name):
            if window_name == 'savefile':
                kwargs['show'] = False
                self.postponed_save_windows.append(savewidget(self, **kwargs))
            return

        if window_name == 'log'       :
            self.child_windows[window_name] = LogWindow(self, self.logbuffer, self.config)
        elif window_name == 'about'   :
            self.child_windows[window_name] = AboutWindow(self, lambda w: self.donate())
        elif window_name == 'help'    :
            self.child_windows[window_name] = HelpWindow(self, makeHelp('bittorrent', defaults))
        elif window_name == 'settings':
            self.child_windows[window_name] = SettingsWindow(self, self.config, self.set_config)
        elif window_name == 'version' :
            self.child_windows[window_name] = VersionWindow(self, *args)
        elif window_name == 'openfile':
            self.child_windows[window_name] = OpenFileSelection(self, **kwargs)
        elif window_name == 'savefile':
            self.child_windows[window_name] = savewidget(self, **kwargs)
        elif window_name == 'choosefolder':
            self.child_windows[window_name] = ChooseFolderSelection(self, **kwargs)            
        elif window_name == 'enterurl':
            self.child_windows[window_name] = EnterUrlDialog(self, **kwargs)

        return self.child_windows[window_name]

    def window_closed(self, window_name):
        if self.child_windows.has_key(window_name):
            del self.child_windows[window_name]
        if window_name == 'savefile' and self.postponed_save_windows:
            newwin = self.postponed_save_windows.pop(-1)
            newwin.show()
            self.child_windows['savefile'] = newwin
    
    def close_window(self, window_name):
        self.child_windows[window_name].close(None)

    def new_version(self, newversion, download_url):
        if not self.config['notified'] or \
               newversion != NewVersion.Version.from_str(self.config['notified']):
            if not self.torrents.has_key(self.updater.infohash):
                self.open_window('version', newversion, download_url)
            else:
                dlpath = os.path.split(self.torrents[self.updater.infohash].dlpath)[0]
                self.updater.set_installer_dir(dlpath)
                self.updater.start_install()

    def check_version(self):
        self.updater.check() 

    def start_auto_update(self):
        if not self.torrents.has_key(self.updater.infohash):
            self.updater.download()
        else:
            self.global_error(INFO, _("Already downloading %s installer") % self.updater.version)

    def confirm_install_new_version(self):
        MessageDialog(self.mainwindow,
                      _("Install new %s now?")%app_name,
                      _("Do you want to quit %s and install the new version, "
                        "%s, now?")%(app_name,self.updater.version),
                      type=gtk.MESSAGE_QUESTION,
                      buttons=gtk.BUTTONS_YES_NO,
                      yesfunc=self.install_new_version,
                      nofunc=None,
                      default=gtk.RESPONSE_YES
                      )

    def install_new_version(self):
        self.updater.launch_installer(self.torrentqueue)
        self.cancel()
        

    def open_help(self,widget):
        if self.helpwindow is None:
            msg = (_("%s help is at \n%s\nWould you like to go there now?")%
                  (app_name, HELP_URL))
            self.helpwindow = MessageDialog(self.mainwindow,
                                            _("Visit help web page?"),
                                            msg,
                                            type=gtk.MESSAGE_QUESTION,
                                            buttons=gtk.BUTTONS_OK_CANCEL,
                                            yesfunc=self.visit_help,
                                            nofunc =self.help_closed,
                                            default=gtk.RESPONSE_OK
                                            )

    def visit_help(self):
        self.visit_url(HELP_URL)
        self.help_closed()
        
    def close_help(self):
        self.helpwindow.close()

    def help_closed(self, widget=None):
        self.helpwindow = None


    def set_config(self, option, value):
        self.config[option] = value
        if option == 'display_interval':
            self.init_updates()
        self.torrentqueue.set_config(option, value)


    def confirm_remove_finished_torrents(self,widget):
        count = 0
        for infohash, t in self.torrents.iteritems():
            if t.state == KNOWN and t.completion >= 1:
                count += 1
        if count:
            if self.paned.get_position() == 0:
                self.toggle_known()
            msg = ''
            if count == 1:
                msg = _("There is one finished torrent in the list. ") + \
                      _("Do you want to remove it?")
            else:
                msg = _("There are %d finished torrents in the list. ") % count +\
                      _("Do you want to remove all of them?")
            MessageDialog(self.mainwindow,
                          _("Remove all finished torrents?"),
                          msg,
                          type=gtk.MESSAGE_QUESTION,
                          buttons=gtk.BUTTONS_OK_CANCEL,
                          yesfunc=self.remove_finished_torrents,
                          default=gtk.RESPONSE_OK)
        else:
            MessageDialog(self.mainwindow,
                          _("No finished torrents"),
                          _("There are no finished torrents to remove."),
                          type=gtk.MESSAGE_INFO,
                          default=gtk.RESPONSE_OK)

    def remove_finished_torrents(self):
        for infohash, t in self.torrents.iteritems():
            if t.state == KNOWN and t.completion >= 1:
                self.torrentqueue.remove_torrent(infohash)
        if self.paned.get_position() > 0:
            self.toggle_known()

    def cancel(self, widget=None):
        for window_name in self.child_windows.keys():
            self.close_window(window_name)
        
        if self.errordialog is not None:
            self.errordialog.destroy()
            self.errors_closed()

        for t in self.torrents.itervalues():
            if t.widget is not None:
                t.widget.close_child_windows()

        self.torrentqueue.set_done()
        gtk.main_quit()

    # Currently called if the user started bittorrent from a terminal
    # and presses ctrl-c there, or if the user quits BitTorrent from
    # the tray icon (on windows)   
    def quit(self):
        self.mainwindow.destroy()

    def make_statusrequest(self):
        if self.config['pause']:
            return True
        for infohash, t in self.running_torrents.iteritems():
            self.torrentqueue.request_status(infohash, t.widget.peerlistwindow
                             is not None, t.widget.filelistwindow is not None)
        if not len(self.running_torrents):
            self.status_light.send_message('empty')
        return True

    def enter_url_to_open(self, widget): 
        self.open_window('enterurl')

    def open_url(self, url):
        self.torrentqueue.start_new_torrent_by_name(url)

    def select_torrent_to_open(self, widget):
        open_location = self.config['open_from']
        if not open_location:
            open_location = self.config['save_in']
        path = smart_dir(open_location) 
        self.open_window('openfile',
                         title=_("Open torrent:"),
                         fullname=path,
                         got_location_func=self.open_torrent,
                         no_location_func=lambda: self.window_closed('openfile'))


    def open_torrent(self, name):
        self.window_closed('openfile')
        open_location = os.path.split(name)[0]
        if open_location[-1] != os.sep:
            open_location += os.sep
        self.set_config('open_from',  open_location)

        self.torrentqueue.start_new_torrent_by_name(name)

    def change_save_location(self, infohash):
        def no_location():
            self.window_closed('savefile')

        t = self.torrents[infohash]
        metainfo = t.metainfo
        
        selector = self.open_window(metainfo.is_batch and 'savedir' or \
                                                          'savefile',
                      title=_("Change save location for ") + metainfo.name,
                      fullname=t.dlpath,
                      got_location_func = \
                            lambda fn: self.got_changed_location(infohash, fn),
                      no_location_func=no_location)

    def got_changed_location(self, infohash, fullpath):
        self.window_closed('savefile')
        self.torrentqueue.set_save_location(infohash, fullpath)

    def save_location(self, infohash, metainfo):
        name = metainfo.name_fs

        if self.config['save_as'] and \
               os.access(os.path.split(self.config['save_as'])[0], os.W_OK):
            path = self.config['save_as']
            self.got_location(infohash, path, store_in_config=False)
            self.config['save_as'] = ''
            return

        path = smart_dir(self.config['save_in'])

        fullname = os.path.join(path, name)

        if not self.config['ask_for_save']:
            if os.access(fullname, os.F_OK):
                message = MessageDialog(self.mainwindow,
                                        _("File exists!"),
                                        _('"%s" already exists. '
                                          "Do you want to choose a different file name?") % path_wrap(name),
                                        buttons=gtk.BUTTONS_YES_NO,
                                        nofunc= lambda : self.got_location(infohash, fullname),
                                        yesfunc=lambda : self.get_save_location(infohash, metainfo, fullname),
                                        default=gtk.RESPONSE_NO)

            else:
                self.got_location(infohash, fullname)
        else:
            self.get_save_location(infohash, metainfo, fullname)

    def get_save_location(self, infohash, metainfo, fullname):
        def no_location():
            self.window_closed('savefile')
            self.torrentqueue.remove_torrent(infohash)

        selector = self.open_window(metainfo.is_batch and 'savedir' or \
                                                          'savefile',
                                    title=_("Save location for ") + metainfo.name,
                                    fullname=fullname,
                                    got_location_func = lambda fn: \
                                              self.got_location(infohash, fn),
                                    no_location_func=no_location)
        
        self.torrents[infohash].widget = selector

    def got_location(self, infohash, fullpath, store_in_config=True):
        self.window_closed('savefile')
        self.torrents[infohash].widget = None
        save_in = os.path.split(fullpath)[0]

        metainfo = self.torrents[infohash].metainfo
        if metainfo.is_batch:
            bottom_dirs, top_dir_name = os.path.split(save_in)
            if metainfo.name_fs == top_dir_name:

                message = MessageDialog(self.mainwindow, _("Directory exists!"),
                                        _('"%s" already exists.'\
                                          " Do you intend to create an identical,"\
                                          " duplicate directory inside the existing"\
                                          " directory?")%path_wrap(save_in),
                                        buttons=gtk.BUTTONS_YES_NO,
                                        nofunc =lambda : self.got_location(infohash, save_in ),
                                        yesfunc=lambda : self._got_location(infohash, save_in, fullpath, store_in_config=store_in_config),
                                        default=gtk.RESPONSE_NO,
                                        )
                return
        self._got_location(infohash, save_in, fullpath, store_in_config=store_in_config)

    def _got_location(self, infohash, save_in, fullpath, store_in_config=True):
        if store_in_config:
            if save_in[-1] != os.sep:
                save_in += os.sep
            self.set_config('save_in', save_in)
        self.torrents[infohash].dlpath = fullpath
        self.torrentqueue.set_save_location(infohash, fullpath)

    def add_unhighlight_handle(self):
        if self.unhighlight_handle is not None:
            gobject.source_remove(self.unhighlight_handle)
            
        self.unhighlight_handle = gobject.timeout_add(2000,
                                                      self.unhighlight_after_a_while,
                                                      priority=gobject.PRIORITY_LOW)

    def unhighlight_after_a_while(self):
        self.drag_highlight()
        gobject.source_remove(self.unhighlight_handle)
        self.unhighlight_handle = None
        return False

    def init_updates(self):
        if self.update_handle is not None:
            gobject.source_remove(self.update_handle)
        self.update_handle = gobject.timeout_add(
            int(self.config['display_interval'] * 1000),
            self.make_statusrequest)

    def remove_torrent_widget(self, infohash):
        t = self.torrents[infohash]
        self.lists[t.state].remove(infohash)
        if t.state == RUNNING:
            del self.running_torrents[infohash]
            self.set_title()
        if t.state == ASKING_LOCATION:
            if t.widget is not None:
                t.widget.destroy()
            return

        if t.state in (KNOWN, RUNNING, QUEUED):
            t.widget.close_child_windows()

        if t.state == RUNNING:
            self.runbox.remove(t.widget)
        elif t.state == QUEUED:
            self.queuebox.remove(t.widget)
        elif t.state == KNOWN:
            self.knownbox.remove(t.widget)
            
        t.widget.destroy()

        self.set_size()

    def create_torrent_widget(self, infohash, queuepos=None):
        t = self.torrents[infohash]
        l = self.lists.setdefault(t.state, [])
        if queuepos is None:
            l.append(infohash)
        else:
            l.insert(queuepos, infohash)
        if t.state == ASKING_LOCATION:
            self.save_location(infohash, t.metainfo)
            self.nag()
            return
        elif t.state == RUNNING:
            self.running_torrents[infohash] = t
            if not self.config['pause']:
                t.widget = RunningTorrentBox(infohash, t.metainfo, t.dlpath,
                                             t.completion, self)
            else:
                t.widget = PausedTorrentBox(infohash, t.metainfo, t.dlpath,
                                             t.completion, self)
            box = self.runbox
        elif t.state == QUEUED:
            t.widget = QueuedTorrentBox(infohash, t.metainfo, t.dlpath,
                                        t.completion, self)
            box = self.queuebox
        elif t.state == KNOWN:
            t.widget = KnownTorrentBox(infohash, t.metainfo, t.dlpath,
                                       t.completion, self)
            box = self.knownbox
        box.pack_start(t.widget, expand=False, fill=False)
        if queuepos is not None:
            box.reorder_child(t.widget, queuepos)

        self.set_size()

    def log_text(self, text, severity=ERROR):
        self.logbuffer.log_text(text, severity)
        if self.child_windows.has_key('log'):
            self.child_windows['log'].scroll_to_end()

    def _error(self, severity, err_str):
        err_str = err_str.decode('utf-8', 'replace').encode('utf-8')
        err_str = err_str.strip()
        if severity >= ERROR:
            self.error_modal(err_str)
        self.log_text(err_str, severity)

    def error(self, infohash, severity, text):
        if self.torrents.has_key(infohash):
            name = self.torrents[infohash].metainfo.name
            err_str = '"%s" : %s'%(name,text)
            self._error(severity, err_str)
        else:
            ihex = infohash.encode('hex')
            err_str = '"%s" : %s'%(ihex,text)
            self._error(severity, err_str)
            self._error(WARNING, 'Previous error raised for invalid infohash: "%s"' % ihex)

    def global_error(self, severity, text):
        err_str = _("(global message) : %s")%text
        self._error(severity, err_str)

    def error_modal(self, text):
        if self.child_windows.has_key('log'):
            return

        title = _("%s Error") % app_name
        
        if self.errordialog is not None:
            if not self.errordialog.multi:
                self.errordialog.destroy()
                self.errordialog = MessageDialog(self.mainwindow, title, 
                                                 _("Multiple errors have occurred. "
                                                   "Click OK to view the error log."),
                                                 buttons=gtk.BUTTONS_OK_CANCEL,
                                                 yesfunc=self.multiple_errors_yes,
                                                 nofunc=self.errors_closed,
                                                 default=gtk.RESPONSE_OK
                                                 )
                self.errordialog.multi = True
            else:
                # already showing the multi error dialog, so do nothing
                pass
        else:
            self.errordialog = MessageDialog(self.mainwindow, title, text,
                                             yesfunc=self.errors_closed,
                                             default=gtk.RESPONSE_OK)
            self.errordialog.multi = False


    def multiple_errors_yes(self):
        self.errors_closed()
        self.open_window('log')

    def errors_closed(self):
        self.errordialog = None

    def open_log(self):
        self.open_window('log')

    def stop_queue(self):
        self.set_config('pause', True)
        self.set_title()
        self.status_light.send_message('stop')
        self.set_seen_remote_connections(False)
        self.set_seen_connections(False)
        q = list(self.runbox.get_queue())
        for infohash in q:
            t = self.torrents[infohash]
            self.remove_torrent_widget(infohash)
            self.create_torrent_widget(infohash)

    def restart_queue(self):
        self.set_config('pause', False)
        q = list(self.runbox.get_queue())
        for infohash in q:
            t = self.torrents[infohash]
            self.remove_torrent_widget(infohash)
            self.create_torrent_widget(infohash)
        self.start_status_light()

    def start_status_light(self):
        if len(self.running_torrents):
            self.status_light.send_message('start')
        else:
            self.status_light.send_message('empty')

    def update_status(self, torrent, statistics):
        if self.config['pause']:
            self.status_light.send_message('start')
            return

        if self.seen_remote_connections:
            self.status_light.send_message('seen_remote_peers')
        elif self.seen_connections:
            self.status_light.send_message('seen_peers')
        else:
            self.start_status_light()
        
        self.running_torrents[torrent].widget.update_status(statistics)
        if statistics.get('numPeers'):
            self.set_seen_connections(seen=True)
        if (not self.seen_remote_connections and
            statistics.get('ever_got_incoming')):
            self.set_seen_remote_connections(seen=True)
        if self.updater is not None:
            updater_infohash = self.updater.infohash
            if self.torrents.has_key(updater_infohash):
                updater_torrent = self.torrents[updater_infohash]
                if updater_torrent.state == QUEUED:
                    self.change_torrent_state(updater_infohash, RUNNING,
                                              index=0, replaced=0,
                                              force_running=True)

    def set_seen_remote_connections(self, seen=False):
        if seen:
            self.status_light.send_message('seen_remote_peers')
        self.seen_remote_connections = seen

    def set_seen_connections(self, seen=False):
        if seen:
            self.status_light.send_message('seen_peers')
        self.seen_connections = seen

    def new_displayed_torrent(self, infohash, metainfo, dlpath, state, config,
                              completion=None, uptotal=0, downtotal=0):
        t = Struct()
        t.metainfo = metainfo
        t.dlpath = dlpath
        t.state = state
        t.config = config
        t.completion = completion
        t.uptotal = uptotal
        t.downtotal = downtotal
        t.widget = None
        self.torrents[infohash] = t
        self.create_torrent_widget(infohash)

    def torrent_state_changed(self, infohash, dlpath, state, completion,
                              uptotal, downtotal, queuepos=None):
        t = self.torrents[infohash]
        self.remove_torrent_widget(infohash)
        t.dlpath = dlpath
        t.state = state
        t.completion = completion
        t.uptotal = uptotal
        t.downtotal = downtotal
        self.create_torrent_widget(infohash, queuepos)

    def reorder_torrent(self, infohash, queuepos):
        self.remove_torrent_widget(infohash)
        self.create_torrent_widget(infohash, queuepos)

    def update_completion(self, infohash, completion, files_left=None,
                          files_allocated=None):
        t = self.torrents[infohash]
        if files_left is not None and t.widget.filelistwindow is not None:
            t.widget.filelistwindow.update(files_left, files_allocated)

    def removed_torrent(self, infohash):
        self.remove_torrent_widget(infohash)
        del self.torrents[infohash]

    def change_torrent_state(self, infohash, newstate, index=None,
                             replaced=None, force_running=False):
        t = self.torrents[infohash]
        pred = succ = None
        if index is not None:
            l = self.lists.setdefault(newstate, [])
            if index > 0:
                pred = l[index - 1]
            if index < len(l):
                succ = l[index]
        self.torrentqueue.change_torrent_state(infohash, t.state, newstate,
                                         pred, succ, replaced, force_running)

    def finish(self, infohash):
        t = self.torrents[infohash]
        if t is None or t.state == KNOWN:
            return
        self.change_torrent_state(infohash, KNOWN)

    def confirm_replace_running_torrent(self, infohash, replaced, index):
        replace_func = lambda *args: self.change_torrent_state(infohash,
                                RUNNING, index, replaced)
        add_func     = lambda *args: self.change_torrent_state(infohash,
                                RUNNING, index, force_running=True)
        moved_torrent = self.torrents[infohash]

        if moved_torrent.state == RUNNING:
            self.change_torrent_state(infohash, RUNNING, index)
            return

        if self.config['start_torrent_behavior'] == 'replace':
            replace_func()
            return
        elif self.config['start_torrent_behavior'] == 'add':
            add_func()
            return
        
        moved_torrent_name = moved_torrent.metainfo.name
        confirm = MessageDialog(self.mainwindow,
                                _("Stop running torrent?"),
                                _('You are about to start "%s". Do you want to stop another running torrent as well?')%(moved_torrent_name),
                                type=gtk.MESSAGE_QUESTION,
                                buttons=gtk.BUTTONS_YES_NO,
                                yesfunc=replace_func,
                                nofunc=add_func,
                                default=gtk.RESPONSE_YES)

    def nag(self):
        if ((self.config['donated'] != version) and
            #(random.random() * NAG_FREQUENCY) < 1) and
            False):
            title = _("Have you donated?")
            message = _("Welcome to the new version of %s. Have you donated?")%app_name
            self.nagwindow = MessageDialog(self.mainwindow,
                                           title,
                                           message,
                                           type=gtk.MESSAGE_QUESTION,
                                           buttons=gtk.BUTTONS_YES_NO,
                                           yesfunc=self.nag_yes, nofunc=self.nag_no,
                                           default=gtk.RESPONSE_NO)
            
    def nag_no(self):
        self.donate()

    def nag_yes(self):
        self.set_config('donated', version)
        MessageDialog(self.mainwindow,
                      _("Thanks!"),
                      _("Thanks for donating! To donate again, "
                        'select "Donate" from the "Help" menu.'),
                      type=gtk.MESSAGE_INFO,
                      default=gtk.RESPONSE_OK
                      )

    def donate(self):
        self.visit_url(DONATE_URL)


    def visit_url(self, url, callback=None):
        t = threading.Thread(target=self._visit_url,
                             args=(url,callback))
        t.setDaemon(True)
        t.start()

    def _visit_url(self, url, callback=None):
        webbrowser.open(url)
        if callback:
            gtk_wrap(callback)

    def toggle_shown(self):
        if self.config['minimize_to_tray']:
            if self.mainwindow.get_property('visible'):
                self.mainwindow.hide()
            else:
                self.mainwindow.show_all()
        else:
            if not self.iconized:
                self.mainwindow.iconify()
            else:
                self.mainwindow.deiconify()
                

    def raiseerror(self, *args):
        raise ValueError('test traceback behavior')

#this class provides a thin layer around the loop so that the main window
#doesn't have to run it. It protects againstexceptions in mainwindow creation
#preventing the loop from starting (and causing "The grey screen of BT")
class MainLoop:
    def __init__(self):
        self.mainwindow = None
        self.started = 0
        
        gtk.threads_init()

    def set_mainwindow(self, mainwindow):
        self.mainwindow = mainwindow

    def run(self):
        self.mainwindow.traythread.start()
        gtk.threads_enter()        

        if self.mainwindow:
            self.mainwindow.ssbutton.set_paused(self.mainwindow.config['pause'])
            self.mainwindow.rate_slider_box.start()
            self.mainwindow.init_updates()

        try:
            #the main loop has been started
            self.started = 1
            gtk.main() 
        except KeyboardInterrupt:
            gtk.threads_leave()
            if self.mainwindow:
                self.mainwindow.torrentqueue.set_done()
            raise
        
        gtk.threads_leave()

    def quit(self):
        if self.mainwindow: 
            self.mainwindow.quit()
        

def btgui_exit_gtk(mainloop):
    # if the main loop has never run, we have to run it to flush blocking threads
    # if it has run, running it a second time will cause duplicate-destruction problems
    if not mainloop.started:
        # queue up a command to close the gui
        gobject.idle_add(lock_wrap, mainloop.quit)
        # run the main loop so we process all queued commands, then quit
        mainloop.run()

if __name__ == '__main__':

    mainloop = MainLoop()

    # make sure we start the gtk loop once before we close
    atexit.register(btgui_exit_gtk, mainloop)

    torrentqueue = TorrentQueue.TorrentQueue(config, ui_options, ipc)
    d = DownloadInfoFrame(config,TorrentQueue.ThreadWrappedQueue(torrentqueue))

    mainloop.set_mainwindow(d)
    global_log_func.logger = d.global_error
    
    startflag = threading.Event()
    dlthread = threading.Thread(target = torrentqueue.run,
                                args = (d, gtk_wrap, startflag))
    dlthread.setDaemon(False)
    dlthread.start()
    startflag.wait()
    # the wait may have been terminated because of an error
    if torrentqueue.initialized == -1:
        raise BTFailure(_("Could not start the TorrentQueue, see above for errors."))
    
    torrentqueue.rawserver.install_sigint_handler()
    for name in newtorrents:
        d.torrentqueue.start_new_torrent_by_name(name)

    try:
        mainloop.run()
    except KeyboardInterrupt:
        # the gtk main loop is closed in MainLoop
        sys.exit(1)
    d.trayicon.disable()
    
