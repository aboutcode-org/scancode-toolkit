// Netizen.cc for Blackbox - An X11 Window Manager
// Copyright (c) 1997 - 2000 Brad Hughes (bhughes@tcac.net)
//
// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the "Software"),
// to deal in the Software without restriction, including without limitation
// the rights to use, copy, modify, merge, publish, distribute, sublicense,
// and/or sell copies of the Software, and to permit persons to whom the
// Software is furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.	IN NO EVENT SHALL
// THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
// DEALINGS IN THE SOFTWARE.

#ifdef HAVE_CONFIG_H
#include "../config.h"
#endif // HAVE_CONFIG_H

#include "Netizen.hh"
#include "Screen.hh"
#include "FbAtoms.hh"

// use GNU extensions
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif // _GNU_SOURCE

using namespace fb;

Netizen::Netizen(BScreen *scr, Window win):
screen(scr), 
display(scr->getBaseDisplay()->getXDisplay()),
window(win) {
	event.type = ClientMessage;
	event.xclient.message_type = FbAtoms::instance()->getFluxboxStructureMessagesAtom();
	event.xclient.display = display;
	event.xclient.window = window;
	event.xclient.format = 32;
	event.xclient.data.l[0] = FbAtoms::instance()->getFluxboxNotifyStartupAtom();
	event.xclient.data.l[1] = event.xclient.data.l[2] =
	event.xclient.data.l[3] = event.xclient.data.l[4] = 0l;

	XSendEvent(display, window, False, NoEventMask, &event);
}


void Netizen::sendWorkspaceCount() {
 
	event.xclient.data.l[0] = FbAtoms::instance()->getFluxboxNotifyWorkspaceCountAtom();
	event.xclient.data.l[1] = screen->getCount();

	XSendEvent(display, window, False, NoEventMask, &event);
}


void Netizen::sendCurrentWorkspace() {

	event.xclient.data.l[0] = FbAtoms::instance()->getFluxboxNotifyCurrentWorkspaceAtom();
	event.xclient.data.l[1] = screen->getCurrentWorkspaceID();

	XSendEvent(display, window, False, NoEventMask, &event);
}


void Netizen::sendWindowFocus(Window w) {
	event.xclient.data.l[0] = FbAtoms::instance()->getFluxboxNotifyWindowFocusAtom();
	event.xclient.data.l[1] = w;

	XSendEvent(display, window, False, NoEventMask, &event);
}


void Netizen::sendWindowAdd(Window w, unsigned long p) {
	event.xclient.data.l[0] = FbAtoms::instance()->getFluxboxNotifyWindowAddAtom();
	event.xclient.data.l[1] = w;
	event.xclient.data.l[2] = p;

	XSendEvent(display, window, False, NoEventMask, &event);

	event.xclient.data.l[2] = 0l;
}


void Netizen::sendWindowDel(Window w) {
	event.xclient.data.l[0] = FbAtoms::instance()->getFluxboxNotifyWindowDelAtom();
	event.xclient.data.l[1] = w;

	XSendEvent(display, window, False, NoEventMask, &event);
}


void Netizen::sendWindowRaise(Window w) {
	event.xclient.data.l[0] = FbAtoms::instance()->getFluxboxNotifyWindowRaiseAtom();
	event.xclient.data.l[1] = w;

	XSendEvent(display, window, False, NoEventMask, &event);
}


void Netizen::sendWindowLower(Window w) {
	event.xclient.data.l[0] = FbAtoms::instance()->getFluxboxNotifyWindowLowerAtom();
	event.xclient.data.l[1] = w;

	XSendEvent(display, window, False, NoEventMask, &event);
}


void Netizen::sendConfigNotify(XEvent *e) {
	XSendEvent(display, window, False,
		StructureNotifyMask, e);
}
