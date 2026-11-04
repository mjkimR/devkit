"""Generic integration never infers a Unit from a branch or invents session claims."""

from inspect import signature

from devkit_agt.features.integration import IntegrationContext, IntegrationService


def test_generic_integration_has_no_task_or_claims_contract():
    assert set(signature(IntegrationService.prepare).parameters) == {"self", "branch", "route"}
    assert set(signature(IntegrationContext).parameters) == {"finish", "network", "result_sha"}
