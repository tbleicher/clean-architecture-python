import os
import json
from typing import Any, List


def filter_entities_by_attributes(data: dict[str, dict], attributes: dict[str, Any]):
    _set = data.values()

    for key, value in attributes.items():
        _set = [entity for entity in _set if entity[key] == value]

    return _set


def load_fixtures(fixtures_path: str) -> List[dict[str, str]]:
    if not os.path.exists(fixtures_path):
        return []

    try:
        with open(fixtures_path) as fixtures_file:
            data = json.load(fixtures_file)
            return data
    except:
        return []
