import pluggy


hookspec = pluggy.HookspecMarker('post_scan')

class PrintOutput(object):

    @hookspec
    def print_output(self, files_count, version, notice, scanned_files, options, input, output_file, _echo):
        pass
