"""devkit_spec.features.scope: observe declared and changed work scopes and keep creation snapshots in a registry.

``inputs`` builds a ``ScopeSet`` from a proposal or a spec bundle, ``localfs`` is the file registry, ``location``
finds the registry and the worktree's token, ``flow`` runs a worktree's creation registration and release, and
``services.collection`` is the Host's explicit observation (``devkit spec scope collect``). The purpose is detection
before parallel work runs, never exclusive ownership. Contract: ``CAP-COLL-work-scope-registry``
(``docs/capabilities/collaboration/``).
"""

from devkit_spec.features.scope.models.deadline import Deadline
from devkit_spec.features.scope.models.model import (
    Diff,
    Granularity,
    Problem,
    Record,
    ScopePath,
    ScopeSet,
    Source,
    Stage,
    SweepResult,
    Unresolved,
    Verdict,
)
from devkit_spec.features.scope.models.registry import Registry, token_hash
from devkit_spec.features.scope.repositories.localfs import (
    FlockLocker,
    LocalRegistry,
)
from devkit_spec.features.scope.repositories.location import Location, default_namespace, load_token, locate
from devkit_spec.features.scope.usecases.flow import (
    Registered,
    RegisterScopeUseCase,
    ReleaseScopeUseCase,
    Session,
    auto_register,
    creation_scope,
    open_session,
    own,
)
from devkit_spec.features.scope.usecases.inputs import from_proposal, from_spec, kind_of

__all__ = [
    "Deadline",
    "Diff",
    "FlockLocker",
    "Granularity",
    "LocalRegistry",
    "Location",
    "Problem",
    "Record",
    "RegisterScopeUseCase",
    "Registered",
    "Registry",
    "ReleaseScopeUseCase",
    "ScopePath",
    "ScopeSet",
    "Session",
    "Source",
    "Stage",
    "SweepResult",
    "Unresolved",
    "Verdict",
    "auto_register",
    "creation_scope",
    "default_namespace",
    "from_proposal",
    "from_spec",
    "kind_of",
    "load_token",
    "locate",
    "open_session",
    "own",
    "token_hash",
]
