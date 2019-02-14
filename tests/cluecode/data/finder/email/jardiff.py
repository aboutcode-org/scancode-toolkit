#!/ms/dist/python/PROJ/core/2.4/bin/python
# flake8: noqa
'''
Compares API differences between two jar files

(C)opyright 2006 Jason Petrone <jp_py@demonseed.net>
All Rights Reserved

'''

__author__ = 'Jason Petrone <jp_py@demonseed.net>'
__version__ = '1.0'

import sys, os
from zipfile import ZipFile
from copy import copy
import classdiff
from StringIO import StringIO

USAGE = \
'''
Usage: %s [options] <file0.jar> <file1.jar>

Supported Options:  
  --access=v0[,v1,...]   Filter by access level(package, private, protected,
                         public, all) [default=protected,public].
  --noadded              Suppress display of new fields, classes, and methods.
  --bincompat            Only show changes that will break binary compatibility
''' % (sys.argv[0])


def jardiff(path0, path1, opts={}):
  jar0 = ZipFile(path0)
  jar1 = ZipFile(path1)
  files0 = jar0.namelist()
  files1 = set(jar1.namelist())

  removedClasses = []

  for path in files0:
    # if not path.startswith('msjava/msnet/MSNetTCPSocket.'):
    #   continue

    if not path.endswith('.class'):
      continue

    class0 = classdiff.Class(StringIO(jar0.read(path)))

    if not path in files1:
      if classdiff.checkAccess(class0, opts):
        klass = path.replace('/', '.')[:-1*(len('.class'))]
        removedClasses.append(klass)
      continue
    
    class1 = classdiff.Class(StringIO(jar1.read(path)))
    classdiff.classdiff(class0, class1, opts)
    files1.remove(path)

  removedClasses.sort()
  if removedClasses:
    print 
    print 'Removed Classes:'
    print '  '+'\n  '.join(removedClasses)
    print

  addedClasses = []
  for path in files1:
    if not path.endswith('.class'):
      continue

    class1 = classdiff.Class(StringIO(jar1.read(path)))
    if classdiff.checkAccess(class1, opts):
      addedClasses.append(class1.name.replace('/', '.'))
  addedClasses.sort()

  if addedClasses and not opts['suppress_added']:
    print 
    print 'Added Classes:'
    print '  '+'\n  '.join(addedClasses)
    print


if __name__ == '__main__':
  opts, jars = classdiff.parseCmdline(copy(sys.argv))

  if len(jars) != 2:
    print USAGE
    sys.exit(-1)
    
  jardiff(jars[0], jars[1], opts)
  

