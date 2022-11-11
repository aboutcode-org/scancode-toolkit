"""
This file is part of the 'Elements' Project
Elements is a 2D Physics API for Python (supporting Box2D2)

Copyright (C) 2008, The Elements Team, <elements@linuxuser.at>

Home:  http://elements.linuxuser.at
IRC:   #elements on irc.freenode.org

Code:  http://www.assembla.com/wiki/show/elements
       svn co http://svn2.assembla.com/svn/elements

License:  GPLv3 | See LICENSE for the full text
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from .locals import *
import Box2D as box2d


class CallbackHandler:
    # List of contact callbacks and shapes to start them - sorted by
    # type for quicker access Callbacks are saved as
    # callbacks[callback_type][[function, parameters], ...]
    callbacks = {}

    def __init__(self, parent):
        self.parent = parent

        # init callback dict to avoid those slow try
        # (especially for self.get, as it is called *often*)
        for i in range(10):
            self.callbacks[i] = []

    def add(self, callback_type, callback_handler, *args):
        """ Users can add callbacks for certain (or all) collisions

           Parameters:
             callback_type ......... CALLBACK_CONTACT
                                     (nothing else for now)
             callback_handler ...... a callback function
             args (optional) ....... a list of parameters which can be
                                     used with callbacks.get

           Return:
             callback_id ... used to remove a callback later (int)
        """
        # Create contact listener if required
        if callback_type in [CALLBACK_CONTACT_ADD,
                             CALLBACK_CONTACT_PERSIST,
                             CALLBACK_CONTACT_REMOVE]:
            if self.parent.listener is None:
                self.parent.listener = kContactListener(self.get)
                self.parent.world.SetContactListener(self.parent.listener)
                print("* ContactListener added")

        # Get callback dict for this callback_type
        c = self.callbacks[callback_type]

        # Append to the Callback Dictionary
        c.append([callback_handler, args])
        self.callbacks[callback_type] = c

        # Return Callback ID
        # ID = callback_type.callback_index (1...n)
        return "%i.%i" % (callback_type, len(c))

    def get(self, callback_type):
        return self.callbacks[callback_type]

    def start(self, callback_type, *args):
        callbacks = self.get(callback_type)
        for c in callbacks:
            callback, params = c
            callback()


class kContactListener(box2d.b2ContactListener):

    def __init__(self, get_callbacks):
        # Init the Box2D b2ContactListener
        box2d.b2ContactListener.__init__(self)

        # Function to get the current callbacks
        self.get_callbacks = get_callbacks

    def check_contact(self, contact_type, point):
        # Checks if a callback should be started with this contact point
        contacts = self.get_callbacks(contact_type)

        # Step through all callbacks for this type (eg ADD, PERSIST, REMOVE)
        for c in contacts:
            callback, bodylist = c
            if len(bodylist) == 0:
                # Without bodylist it's a universal callback (for all bodies)
                callback(point)

            else:
                # This is a callback with specified bodies
                # See if this contact involves one of the specified
                b1 = str(point.shape1.GetBody())
                b2 = str(point.shape2.GetBody())
                for s in bodylist:
                    s = str(s)
                    if b1 == s or b2 == s:
                        # Yes, that's the one :)
                        callback(point)

    def Add(self, point):
        """Called when a contact point is created"""
        self.check_contact(CALLBACK_CONTACT_ADD, point)

    def Persist(self, point):
        """Called when a contact point persists for more than a time step"""
        self.check_contact(CALLBACK_CONTACT_PERSIST, point)

    def Remove(self, point):
        """Called when a contact point is removed"""
        self.check_contact(CALLBACK_CONTACT_REMOVE, point)
