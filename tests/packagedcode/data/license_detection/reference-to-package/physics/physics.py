#!/usr/bin/python
# Physics, a 2D Physics Playground for Kids

# Copyright (C) 2008  Alex Levenson and Brian Jordan
# Copyright (C) 2012  Daniel Francis
# Copyright (C) 2012-13  Walter Bender
# Copyright (C) 2013  Sai Vineet
# Copyright (C) 2012-13  Sugar Labs

#  This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Elements is Copyright (C) 2008, The Elements Team, <elements@linuxuser.at>

# Wiki:   http://wiki.sugarlabs.org/go/Activities/Physics
# Code:   git://git.sugarlabs.org/physics/mainline.git

import os

from gi.repository import Gtk
from gi.repository import Gdk

import pygame
from pygame.locals import MOUSEBUTTONUP

import Box2D as box2d
import myelements as elements

import tools


class PhysicsGame:

    def __init__(self, activity):
        self.activity = activity
        # Get everything set up
        self.clock = pygame.time.Clock()
        self.in_focus = True
        # Create the name --> instance map for components
        self.toolList = {}
        for c in tools.allTools:
            self.toolList[c.name] = c(self)
        self.currentTool = self.toolList[tools.allTools[0].name]
        # Set up the world (instance of Elements)
        self.box2d = box2d
        self.opening_queue = None
        self.running = True
        self.initialise = True

        self.full_pos_list = []
        self.tracked_bodies = 0

        self.trackinfo = {}

        self.box2d_fps = 50

    def set_game_fps(self, fps):
        self.box2d_fps = fps

    def switch_off_fake_pygame_cursor_cb(self, panel, event):
        self.show_fake_cursor = False

    def switch_on_fake_pygame_cursor_cb(self, panel, event):
        self.show_fake_cursor = True

    def write_file(self, path):
        # Saving to journal
        self.world.add.remove_mouseJoint()
        additional_data = {
            'trackinfo': self.trackinfo,
            'full_pos_list': self.full_pos_list,
            'tracked_bodies': self.tracked_bodies
        }
        self.world.json_save(path, additional_data, serialize=True)

    def read_file(self, path):
        # Loading from journal
        self.opening_queue = path

    def run(self):
        if self.initialise:
            self.initialise = False

            # Fake a Sugar cursor for the pyGame canvas area
            self.show_fake_cursor = True
            pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0),
                                    (0, 0, 0, 0, 0, 0, 0, 0))
            self.cursor_picture = pygame.image.load('standardcursor.png')
            self.cursor_picture.convert_alpha()
            self.canvas.connect('enter_notify_event',
                                self.switch_on_fake_pygame_cursor_cb)
            self.canvas.connect('leave_notify_event',
                                self.switch_off_fake_pygame_cursor_cb)
            self.canvas.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK |
                                   Gdk.EventMask.LEAVE_NOTIFY_MASK)

        self.screen = pygame.display.get_surface()
        self.world = elements.Elements(self.screen.get_size())
        self.world.renderer.set_surface(self.screen)
        self.world.add.ground()

        if self.opening_queue:
            path = self.opening_queue.encode('ascii', 'convert')
            if os.path.exists(path):
                self.world.json_load(path, serialized=True)
                if 'full_pos_list' in self.world.additional_vars:
                    self.full_pos_list = \
                        self.world.additional_vars['full_pos_list']
                if 'trackinfo' in self.world.additional_vars:
                    self.trackinfo = self.world.additional_vars['trackinfo']
                if 'tracked_bodies' in self.world.additional_vars:
                    self.tracked_bodies = \
                        self.world.additional_vars['tracked_bodies']

        while self.running:

            # Pump GTK messages.
            while Gtk.events_pending():
                Gtk.main_iteration()
            if not self.running:
                break

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.VIDEORESIZE:
                    pygame.display.set_mode(event.size, pygame.RESIZABLE)

                self.currentTool.handleEvents(event)

                if event.type == MOUSEBUTTONUP:
                    # if event.button == 1:
                    self.show_fake_cursor = True

            if self.in_focus:
                # Drive motors
                if self.world.run_physics:
                    bodies_present = len(self.world.world.bodies)
                    clear_all_active = self.activity.clear_all.get_sensitive()
                    if (bodies_present > 2) and clear_all_active is False:
                        self.activity.clear_all.set_sensitive(True)
                    elif (bodies_present > 2) is False and \
                            clear_all_active is True:
                        self.activity.clear_all.set_sensitive(False)

                    poslist = self.full_pos_list
                    clear_trace_active = \
                        self.activity.clear_trace.get_sensitive()
                    if poslist:
                        if not poslist[0]:
                            if clear_trace_active:
                                self.activity.clear_trace.set_sensitive(False)
                        else:
                            if clear_trace_active is False:
                                self.activity.clear_trace.set_sensitive(True)

                    for key, info in self.trackinfo.items():
                        # [host_body, tracker, color, destroyed?]
                        body = info[1]
                        if info[3] is False:  # Not destroyed the pen
                            trackdex = info[4]

                            def to_screen(pos):
                                px = self.world.meter_to_screen(
                                    pos[0])
                                py = self.world.meter_to_screen(
                                    pos[1])
                                py = self.world.renderer.get_surface() \
                                    .get_height() - py
                                return (px, py)

                            x = body.position.x
                            y = body.position.y
                            tupled_pos = to_screen((x, y))
                            posx = tupled_pos[0]
                            posy = tupled_pos[1]
                            try:
                                self.full_pos_list[trackdex].append(posx)
                                self.full_pos_list[trackdex].append(posy)
                            except IndexError:
                                self.full_pos_list.append([posx, posy])
                    '''
                    for body in self.world.world.GetBodyList():
                        if isinstance(body.userData, dict):
                            if 'rollMotor' in body.userData:
                                rollmotor = body.userData['rollMotor']
                                diff = rollmotor['targetVelocity'] - \
                                       body.GetAngularVelocity()
                                body.ApplyTorque(rollmotor['strength'] * \
                                                 diff * body.getMassData().I)
                    '''

                # Update & Draw World
                self.world.update(fps=self.box2d_fps)
                self.screen.fill((240, 240, 240))  # #f0f0f0, light-grey
                self.world.draw()

                # Draw output from tools
                self.currentTool.draw()

                # Show Sugar like cursor for UI consistancy
                if self.show_fake_cursor:
                    self.screen.blit(self.cursor_picture,
                                     pygame.mouse.get_pos())

                # Flip Display
                pygame.display.flip()

            # Stay < 30 FPS to help keep the rest of the platform responsive
            self.clock.tick(30)  # Originally 50

        return False

    def setTool(self, tool):
        self.currentTool.cancel()
        self.currentTool = self.toolList[tool]
        self.currentTool.button_activated()

    def get_activity(self):
        return self.activity
