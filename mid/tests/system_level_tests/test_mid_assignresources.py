"""Test module for AssignResources functionality (XTP-65630)"""

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import (
    CSPFacade,  # CSP facade
)
from ska_integration_test_harness.facades.sdp_facade import (
    SDPFacade,  # SDP facade
)
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from ska_integration_test_harness.facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer
from tests.system_level_tests.conftest import (
    SubarrayTestContextData,
    _setup_event_subscriptions,
)
from tests.system_level_tests.utils.json_file_input_handler import (
    MyFileJSONInput,
)

TIMEOUT = 100


@pytest.mark.skip
@pytest.mark.system_level_test_mid
@scenario(
    "system_level_tests/" + "xtp_65630_telescope_subarray_transitions.feature",
    "Assign resources to Mid subarray",
)
def test_telescope_assign_resources():
    """BDD test scenario for verifying successful execution of
    the AssignResources command with TMC,CSP and SDP
    devices for pairwise testing"""


#  @given("telescope is in ON state") -> conftest


@given("subarray is in EMPTY ObsState")
def subarray_in_empty_obsstate(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify the subarray's transition to the EMPTY state."""
    _setup_event_subscriptions(
        central_node_facade, subarray_node_facade, csp, sdp, event_tracer
    )
    context_fixt.starting_state = ObsState.EMPTY
    subarray_node_facade.force_change_of_obs_state(
        ObsState.EMPTY,
        TestHarnessInputs(),
        wait_termination=True,
    )


@when("I assign resources to the subarray")
def invoke_assignresources(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
):

    context_fixt.when_action_name = "AssignResources"
    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.assign_resources(
        json_input,
        wait_termination=False,
    )


@then("the TMC, CSP and SDP subarrays transition to IDLE obsState")
def verify_idle_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the IDLE state."""

    assert_that(event_tracer).described_as(
        f"All three: TMC Subarray Node device "
        f"({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to IDLE."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.IDLE,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.IDLE,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.IDLE,
        previous_value=context_fixt.starting_state,
    )


@then("the requested resources are assigned to subarray")
def assert_assigned_resources(subarray_node_facade):
    """
    This method asserts that the assigned resources in the subarray node
    match the expected resources "SKA001", "SKA036", "SKA063", and "SKA100".

    Args:
        subarray_node_facade: The facade object for the subarray node.
    """
    assert_that(
        subarray_node_facade.subarray_node.assignedResources
    ).described_as(
        "Wrong set of resources being assigned in subarray_node"
    ).contains_only(
        "SKA001", "SKA036", "SKA063", "SKA100"
    )
