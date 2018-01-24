"""
This base config script gets automatically executed for all platforms via
configure.
"""

import sys


"""
Check that we run a supported OS and architecture.
"""

def unsupported(platform):
    print('Unsupported OS/platform %r.' % platform)
    print('See https://github.com/nexB/scancode-toolkit/ for supported OS/platforms.')
    print('Enter a ticket https://github.com/nexB/scancode-toolkit/issues asking for support of your OS/platform combo.')
    sys.exit(1)

if sys.maxsize > 2 ** 32:
    arch = '64'
else:
    arch = '32'

sys_platform = str(sys.platform).lower()
if 'linux' in sys_platform:
    os = 'linux'
elif'win32' in sys_platform:
    os = 'win'
elif 'darwin' in sys_platform:
    os = 'mac'
else:
    unsupported(sys_platform)


supported_combos = {
    'linux': ['32', '64'],
    'win': ['32',],
    'mac': ['64',],
}

arches = supported_combos[os]
if arch not in arches:
    unsupported(os + arch)
