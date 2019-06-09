#
# Regular cron jobs for the scancode-toolkit package
#
0 4	* * *	root	[ -x /usr/bin/scancode-toolkit_maintenance ] && /usr/bin/scancode-toolkit_maintenance
