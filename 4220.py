import json
import zipfile
from pathlib import Path

def scan_pip_cache_dir(path):
    results = {}
    for file in Path(path).iterdir():
        if file.name == "origin.json":
            with open(file) as f:
                results["origin"] = json.load(f)
        elif file.suffix == ".whl":
            with zipfile.ZipFile(file, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith("METADATA") or name.endswith("PKG-INFO"):
                        results["wheel_metadata"] = zf.read(name).decode("utf-8")
    return results
