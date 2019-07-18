A ScanCode scan plugin to find dwarf source info.

To start the test case, please run:
1. ./configure
2. source bin/activate
3. pip install -e plugins/scancode-dwarfdump-manylinux1_x86_64 -e plugins/scancode-dwarf
4. pytest -vvs plugins/scancode-dwarf/tests/test_dwarf.py

Note that in step3, the path depends on your OS versions, please update according to your real os enviroment.