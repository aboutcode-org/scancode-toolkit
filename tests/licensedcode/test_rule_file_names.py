from collections import defaultdict
from pathlib import Path

from commoncode.text import python_safe_name
from licensedcode.models import rules_data_dir


def test_rule_file_names_generate_unique_test_method_names():
    method_to_files = defaultdict(list)

    for rule_file in Path(rules_data_dir).glob("*.RULE"):
        method_name = python_safe_name(rule_file.stem)
        method_to_files[method_name].append(rule_file.name)

    duplicate_names = [
        (method_name, files)
        for method_name, files in method_to_files.items()
        if len(files) > 1
    ]

    assert not duplicate_names, f"Duplicate test method names found: {duplicate_names}"