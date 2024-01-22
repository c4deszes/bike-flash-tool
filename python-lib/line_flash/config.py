from dataclasses_json import dataclass_json
from dataclasses import dataclass

import json

@dataclass_json
@dataclass
class ConfigEntry:
    node: str
    serial: int
    file: str

def load_config(path: str) -> list:
    with open(path, 'r') as f:
        data = json.load(f)

    output = []
    for a in data:
        output.append(ConfigEntry(a['node'], int(a['serial'], base=0), a['file']))

    return output
