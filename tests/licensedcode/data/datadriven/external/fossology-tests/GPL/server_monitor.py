#!/usr/bin/env python

# This file is part of Window-Switch.
# Copyright (c) 2009-2013 Antoine Martin <antoine@nagafix.co.uk>
# Window-Switch is released under the terms of the GNU GPL v3

import sys
import traceback

from winswitch.util.main_loop import loop_init, loop_run, loop_exit, connectUNIX, callLater
loop_init(False)

import twisted.internet.protocol
from twisted.protocols import basic

# Our imports
from winswitch.consts import DELIMITER
from winswitch.util.common import visible_command
from winswitch.util.config import get_local_server_config
from winswitch.util.file_io import get_local_server_socket
from winswitch.util.simple_logger import Logger
from winswitch.util.error_handling import display_error
from winswitch.net.protocol import ProtocolHandler
from winswitch.net.commands import SYNC_END, ADD_SERVER_COMMAND

REFRESH_DELAY = 1


show_info = None
def set_show_info_cb(method):
	global show_info
	show_info = method
def show_info_text(server):
	print("Server: %s" % server.name)
	print("Connected users: %s" % str(server.get_active_users()))
	print("Sessions: %s" % str(server.sessions))
set_show_info_cb(show_info_text)


class ServerMonitor:
	def __init__(self, refresh_delay=REFRESH_DELAY):
		Logger(self)
		server_socket = get_local_server_socket()
		factory = LocalMonitorSocketFactory(refresh_delay)
		connectUNIX(server_socket, factory, timeout=5)
		
	def start(self):
		self.log()
		# start listening
		#self.reactor.run(installSignalHandlers=0)
		loop_run()

	def __str__(self):
		return	"ServerMonitor"

	def stop(self):
		loop_exit()




class LocalMonitorSocketChannel(basic.LineReceiver):
	def __init__ (self):
		Logger(self)
		self.slog()
		self.delimiter = DELIMITER
		self.server = get_local_server_config()
		def is_connected():
			return	True
		self.handler = ProtocolHandler(self.server, self.send_message, self.disconnect, is_connected)
		self.handler.add_command_handler(SYNC_END, self.do_sync_end)
		self.handler.add_base_user_and_session_handlers(True, True)
		self.handler.add_command_handler(ADD_SERVER_COMMAND, self.handler.do_add_server_command)

	def disconnect(self, message=None):
		self.sdebug(None, message)
		self.transport.loseConnection()

	def connectionMade(self):
		self.slog()
		self.handler.send_salt()
		self.handler.send_sync("all")
		
	def connectionLost(self, reason):
		self.slog()

	def lineReceived(self, line):
		self.sdebug(None, visible_command(line))
		self.handle_command(line)

	def handle_command(self, command):
		if not self.handler:
			self.serr(None, visible_command(command), Exception("No handler set!"))
		else:
			self.sdebug(None, visible_command(command))
			return	self.handler.handle_command(command)
			#if modified: blink?
		
	def send_message(self, msg):
		self.sdebug(None, visible_command(msg))
		self.sendLine(msg)
	
	def do_sync_end(self, *args):
		self.sdebug(None, args)
		if self.factory.refresh_delay>=0:
			callLater(self.factory.refresh_delay, self.handler.send_sync)	#sync again soon
		show_info(self.server)
		

class LocalMonitorSocketFactory(twisted.internet.protocol.ClientFactory):
	# the class of the protocol to build when new connection is made
	protocol = LocalMonitorSocketChannel

	def __init__ (self, refresh_delay):
		Logger(self)
		self.sdebug(None, refresh_delay)
		self.refresh_delay = refresh_delay
		self.closing = False

	def clientConnectionLost(self, connector, reason):
		if self.closing:
			self.sdebug(None, connector, reason)
		else:
			self.serror(None, connector, reason)
		loop_exit()

	def clientConnectionFailed(self, connector, reason):
		self.serror(None, connector, reason)
		loop_exit()




def main():
	try:
		server_monitor = ServerMonitor()
		server_monitor.start()
	except Exception, e:
		print("server_monitor.main() exception")
		traceback.print_exc(file=sys.stdout)
		display_error("ServerMonitor failed to start", str(e))
		if server_monitor:
			server_monitor.stop()
		sys.exit(1)


if __name__ == "__main__":
	main()
