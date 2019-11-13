# dephell_setuptools

Extract meta information from `setup.py`.

Install:

```
python3 -m pip install --user dephell_setuptools
```

CLI:

```
python3 -m dephell_setuptools ./setup.py
```

Lib:

```python
from pathlib import Path
from dephell_setuptools import read_setup

result = read_setup(path=Path('setup.py'))
```
