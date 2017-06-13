import pluggy

post_scan = pluggy.HookspecMarker('post_scan')
scan_proper = pluggy.HookspecMarker('scan_proper')
pre_scan = pluggy.HookspecMarker('pre_scan')

@pre_scan
def extract_archive():
    pass

@post_scan
def print_output(files_count, version, notice, scanned_files, options, input, output_file, _echo):
    pass

@scan_proper
def add_cmdline_option():
    pass
