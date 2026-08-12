from collections import defaultdict
from pathlib import Path
from commoncode.text import python_safe_name

RULES_DATA_DIR = Path(__file__).parents[2] / "src" / "licensedcode" / "data" / "rules"

def test_rule_file_names_generate_unique_python_names():
    rule_names_by_python_name = defaultdict(list)

    for rule_file in RULES_DATA_DIR.glob("*.RULE"):
        python_name = python_safe_name(rule_file.name)
        rule_names_by_python_name[python_name].append(rule_file.name)

    duplicate_names = {
        python_name: sorted(rule_names)
        for python_name, rule_names in rule_names_by_python_name.items()
        if len(rule_names) > 1
    }

    assert not duplicate_names, duplicate_names
