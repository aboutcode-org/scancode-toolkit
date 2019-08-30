A ScanCode scan plugin to find lkmclue source info.

To start the test case, please run:
1. ./configure
2. source bin/activate
3. pip install -e plugins/scancode-ctags-manylinux1_x86_64 -e plugins/scancode-readelf-manylinux1_x86_64 -e plugins/scancode-lkmclue
4. pytest -vvs plugins/scancode-lkmclue/tests/test_lkmclue.py
   pytest -vvs plugins/scancode-lkmclue/tests/test_elf.py

Note that in step3, the path depends on your OS versions, please update according to your real os enviroment.