# PyYAML installation evidence

Reference: PyYAML 6.0.3 in `uv.lock`; research performed 2026-10-24.

## Eligibility and wheel inventory

The Python package requirement remains `>=3.12`; runtime YAML reads require usable `yaml.CSafeLoader`.
The following standard-ABI wheel families exist for CPython 3.12, 3.13 and 3.14:

| Wheel platform | Architectures | Minimum tag baseline |
| --- | --- | --- |
| manylinux | x86_64, aarch64, s390x | glibc 2.17 (also tagged 2.28) |
| musllinux | x86_64, aarch64 | musl 1.2 |
| macOS | x86_64; arm64 | 10.13; 11.0 |
| Windows | amd64, arm64; win32 only for 3.12/3.13 | Windows wheel tags |

Source: [PyYAML 6.0.3 release files](https://pypi.org/project/PyYAML/6.0.3/#files), also recorded in `uv.lock`.
Free-threaded 3.14 wheels exist but are outside this audited standard-ABI recommendation.
This table describes wheel availability, not devkit support. The existing CI runs Python 3.12 on Ubuntu/macOS;
its installed-consumer smoke runs on Ubuntu. Other interpreter/ABI combinations require separate verification.
Windows wheels do not remove devkit's POSIX locking limitation.

## Install behavior

Use the documented uv route with `--only-binary pyyaml` to refuse source fallback when no compatible wheel resolves.
Runtime still checks CSafeLoader because the package dependency cannot express an optional extension.
An existing pure-Python installation fails at its first YAML operation with `YAML_BINDING_UNAVAILABLE`, exit 2.
An eligible source build must expose a usable C binding; no automatic toolchain setup is added.

The upstream build can fall back to pure Python when compiling its optional extension fails.
For a deliberate source build, upstream recognizes `PYYAML_FORCE_LIBYAML=1` to require that extension.
See [PyYAML 6.0.3 setup.py](https://github.com/yaml/pyyaml/blob/6.0.3/setup.py), Distribution.ext_status,
build_ext.run and build_extensions. This research did not execute source builds or install foreign wheels.

The normal binary-wheel route does not require system development headers.
See [PyYAML parser documentation](https://pyyaml.org/wiki/PyYAMLDocumentation) for C parser selection and the
documented differences from the Python parser; its old setup.py installation example is not the recommended route.
