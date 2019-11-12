from pathlib import Path
from typing import Union


class BaseReader:
    def __init__(self, path: Union[str, Path]):
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            raise FileNotFoundError(str(path))
        if path.is_dir():
            path /= 'setup.py'
        self.path = path
