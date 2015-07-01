#
# btt_plot.py: Generate matplotlib plots for BTT generate data files
#
#  (C) Copyright 2009 Hewlett-Packard Development Company, L.P.
#
#  This program is free software; you can redistribute it and/or modify
	elif type == 'q2d':
		title_str = 'Queue (Q) To Issue (D) Average Latencies'
	elif type == 'd2c':
		title_str = 'Issue (D) To Complete (C) Average Latencies'
	elif type == 'q2c':
		title_str = 'Queue (Q) To Complete (C) Average Latencies'

	title = fig.text(.5, .95, title_str, horizontalalignment='center')