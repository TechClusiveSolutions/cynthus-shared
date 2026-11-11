"""The core model classes are pure data (ADR-009): no web framework, database or broker"""

import json
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[4] / 'src'

FORBIDDEN = ['fastapi', 'sqlalchemy', 'azure', 'aio_pika', 'cynthus.service', 'cynthus.messaging']


def modules_loaded_by(statement: str) -> list[str]:
    # A fresh interpreter, so nothing the other tests imported is counted
    code = f'import sys, json; sys.path.insert(0, {str(SRC)!r}); {statement}; print(json.dumps(sorted(sys.modules)))'
    output = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, check=True).stdout

    return json.loads(output)


def test_the_core_model_classes_load_without_the_runtime():
    loaded = modules_loaded_by(
        'import cynthus.core.event, cynthus.core.resource, cynthus.core.service, cynthus.core.system, cynthus.core.user'
    )

    offenders = [name for name in loaded if any(name == bad or name.startswith(bad + '.') for bad in FORBIDDEN)]

    assert offenders == []
