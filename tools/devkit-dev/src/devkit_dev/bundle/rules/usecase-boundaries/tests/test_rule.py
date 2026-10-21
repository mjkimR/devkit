"""Counterexamples for static transport execution boundaries."""

import sys
from pathlib import Path

from devkit_agt.features.rules.services.testing import load_rule

RULE = load_rule(__file__)
inspect_usecases = sys.modules[RULE.__module__].inspect_usecases

BASE = "from devkit_core.base.usecase import BaseUseCase as Contract\n"
VALID = (
    BASE
    + "class Run(Contract):\n def execute(self, value: str) -> str: return helper(value)\ndef helper(value): return value\n"
)


def inspect(root: Path, files: dict[str, str], extra: str = "") -> list[str]:
    config = """schema = 1
[[packages]]
namespace = "sample"
root = "src/sample"
kind = "features"
features = ["one"]
"""
    for relative, content in {".devkit/architecture.toml": config + extra, **files}.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return [message for _, _, message in inspect_usecases(root)]


def test_typed_boundary_and_internal_helpers(tmp_path: Path) -> None:
    assert not inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": VALID,
            "src/sample/features/one/cli.py": "from .usecases import Run as Operation\nOperation().execute('a')\n",
        },
    )


def test_aliased_function_through_facade_is_not_boundary(tmp_path: Path) -> None:
    found = inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": "def run(): pass\n",
            "src/sample/features/one/__init__.py": "from .usecases import run as dispatch\n",
            "src/sample/features/one/mcp.py": "import sample.features.one as api\noperation = api.dispatch\noperation()\n",
        },
    )
    assert any("execution function" in message for message in found)


def test_class_name_is_not_proof_of_contract(tmp_path: Path) -> None:
    found = inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": "class RunUseCase:\n def execute(self): pass\n",
            "src/sample/features/one/cli.py": "from .usecases import RunUseCase\nRunUseCase().execute()\n",
        },
    )
    assert any("without BaseUseCase" in message for message in found)


def test_retained_instance_and_aliased_bound_method(tmp_path: Path) -> None:
    assert not inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": VALID,
            "src/sample/features/one/mcp.py": """from .usecases import Run
class Handler:
 def __init__(self, operation: Run): self.operation = operation
 async def invoke(self):
  execute = self.operation.execute
  return execute('a')
""",
        },
    )


def test_retained_non_execute_and_service_calls_fail(tmp_path: Path) -> None:
    found = inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": VALID.replace("def helper", "def helper"),
            "src/sample/features/one/services.py": "class Service:\n def run(self): pass\n",
            "src/sample/features/one/cli.py": """from .usecases import Run
from .services import Service
class Handler:
 def __init__(self):
  self.operation = Run()
  self.service = Service()
 def invoke(self):
  self.operation.other()
  self.service.run()
""",
        },
    )
    assert sum("must invoke" in message for message in found) == 2


def test_async_contract_annotations_and_constructor_work(tmp_path: Path) -> None:
    assert not inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": BASE
            + """class Run(Contract):
 async def execute(self, value: str) -> str: return value
"""
        },
    )
    found = inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": BASE
            + """class Run(Contract):
 def __init__(self, root): root.write_text('bad')
 def execute(self, value): return value
"""
        },
    )
    assert any("annotations" in message for message in found)
    assert any("constructor" in message for message in found)


def test_exact_helper_exception_and_stale_detection(tmp_path: Path) -> None:
    files = {
        "src/sample/features/one/usecases.py": "def root(): pass\n",
        "src/sample/features/one/cli.py": "from .usecases import root\nroot()\n",
    }
    extra = """
[[usecase_exceptions]]
source = "sample.features.one.cli"
target = "sample.features.one.usecases.root"
reason = "Select transport context before executing the boundary."
"""
    assert not inspect(tmp_path, files, extra)
    files["src/sample/features/one/cli.py"] = "pass\n"
    assert any("unused usecase exception" in message for message in inspect(tmp_path, files, extra))
    assert any(
        "exact source" in message
        for message in inspect(tmp_path, files, extra.replace('usecases.root"', 'usecases.*"'))
    )


def test_instances_do_not_leak_between_transport_functions(tmp_path: Path) -> None:
    assert not inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": VALID,
            "src/sample/features/one/cli.py": """from .usecases import Run
def first():
 operation = Run()
 return operation.execute('a')
def second(operation):
 return operation.unrelated_transport_method()
""",
        },
    )


def test_dependency_factories_allowed_but_imported_operations_not(tmp_path: Path) -> None:
    found = inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": BASE
            + """import asyncio
from pathlib import Path
import subprocess
class Run(Contract):
 def __init__(self):
  self.lock = asyncio.Lock()
  self.path = Path('.')
  subprocess.run(['bad'])
 def execute(self) -> None: pass
"""
        },
    )
    assert len(found) == 1
    assert "subprocess.run" in found[0]


def test_facade_base_and_annotated_non_execute_alias(tmp_path: Path) -> None:
    found = inspect(
        tmp_path,
        {
            "src/sample/features/one/__init__.py": BASE + "Exported = Contract\n",
            "src/sample/features/one/usecases.py": "from . import Exported\nclass Run(Exported):\n def execute(self) -> None: pass\n def bypass(self) -> None: pass\n",
            "src/sample/features/one/mcp.py": "from .usecases import Run\ndef invoke(operation: Run):\n bypass = operation.bypass\n return bypass()\n",
        },
    )
    assert any("execution function" in message for message in found)


def test_nested_callback_escape_is_checked(tmp_path: Path) -> None:
    found = inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": VALID,
            "src/sample/features/one/mcp.py": """import asyncio
from .usecases import Run, helper as raw

def register():
 operation = Run()
 async def valid(): return await asyncio.to_thread(operation.execute, 'a')
 async def invalid(): return await asyncio.to_thread(raw, 'a')
 return valid, invalid
""",
        },
    )
    assert len(found) == 1
    assert "raw execution callback" in found[0]


def test_result_properties_are_values_not_callbacks(tmp_path: Path) -> None:
    assert not inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": VALID
            + """class Result:
 @property
 def notices(self): return []
""",
            "src/sample/features/one/cli.py": """from .usecases import Result
result = Result()
print(result.notices)
""",
        },
    )


def test_adapter_cannot_hide_execution_in_local_base_subclass(tmp_path: Path) -> None:
    found = inspect(tmp_path, {"src/sample/features/one/cli.py": VALID + "Run().execute('a')\n"})
    assert any("belongs in features" in message for message in found)


def test_imported_bound_execute_alias_does_not_hide_entrypoint(tmp_path: Path) -> None:
    found = inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": VALID + "run = Run().execute\n",
            "src/sample/features/one/cli.py": "from .usecases import run\nrun('a')\n",
        },
    )
    assert any("execution function" in message for message in found)


def test_lambda_execution_and_registered_callback_are_checked(tmp_path: Path) -> None:
    found = inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": VALID,
            "src/sample/features/one/mcp.py": """from .usecases import helper as raw, Run
def register():
 operation = Run()
 handler = lambda: raw('a')
 handler()
 register_tool(lambda: raw('b'))
 register_tool(lambda: operation.execute('a'))
""",
        },
    )
    assert len(found) == 2
    assert all("execution function" in message for message in found)


def test_inline_instance_receiver_requires_execute(tmp_path: Path) -> None:
    found = inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": VALID
            + """class Another(Contract):
 def execute(self) -> None: pass
 def other_method(self) -> None: pass
""",
            "src/sample/features/one/cli.py": """from .usecases import Run, Another
Run().execute('a')
Another().other_method()
""",
        },
    )
    assert len(found) == 1
    assert "must invoke BaseUseCase.execute" in found[0]
