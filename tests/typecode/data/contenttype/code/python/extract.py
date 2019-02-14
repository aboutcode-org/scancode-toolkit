
# flake8: noqa

import os
from os.path import join, dirname, basename, exists
import shutil
import sys



def _read_file(self, file):
    import codecs
    def try_read(file, charset):
        f = codecs.open(file, "r", charset)
        return f.read(), charset
        
    try:
        return try_read(file, "utf-8")
    except:
        return try_read(file, "latin-1" )

def _write_file(file, data, charset):
    import codecs
    f = open(file, 'w', charset)
    f.write(data)
    f.close()
            
    
    
class Extractor:
    def _extract(self, file, extract_dir, extract_function):
        os.mkdir(extract_dir)
        
        try: 
            extract_function(file, extract_dir)
        except:
            # TODO critical: log errors somehow when extracting
            print 'FAILED to extract ' + file
            shutil.rmtree(extract_dir, True)
            return False
        return True

    def extract_archives(self, folder):
        '''extracts all the archives files contained in a folder or in its subfolder. 
        Leaves other files unchanged. Returns True if everything went OK, False otherwise.'''

        allok = True
        return allok

        
