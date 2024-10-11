"""Test module for Assign and Release resources functionality (XTP-65630)"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
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
from tests.system_level_tests.utils.my_file_json_input import MyFileJSONInput

TIMEOUT = 100


@pytest.mark.system_level_test_mid
@scenario(
    "../../mid/features/system_level_tests/xtp_65630_assign_release.feature",
    "Assign and Release resources to Mid subarray",
)
def test_telescope_assign_release_resources():
    """BDD test scenario for verifying successful execution of
    the AssignResources and ReleaseResources commands with TMC, CSP, and SDP
    devices for pairwise testing"""


@given("a mid telescope")
def setup_mid_telescope(
    event_tracer: TangoEventTracer, central_node_facade: TMCCentralNodeFacade
):
    """Setup the mid telescope in ON state."""
    event_tracer.clear_events()
    central_node_facade.move_to_on(wait_termination=True)


@given("the subarray is in EMPTY ObsState")
def setup_subarray_in_empty_obsstate(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Ensure subarray starts in EMPTY ObsState."""
    _setup_event_subscriptions(
        central_node_facade, subarray_node_facade, csp, sdp, event_tracer
    )
    context_fixt.starting_state = ObsState.EMPTY
    subarray_node_facade.force_change_of_obs_state(
        ObsState.EMPTY, TestHarnessInputs(), wait_termination=True
    )


@when(parsers.parse("I {command} the subarray"))
def invoke_subarray_command(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
    command: str,
):
    """Invoke the assign or release resources command based on parameter."""
    context_fixt.when_action_name = command
    json_input = MyFileJSONInput(
        "centralnode", f"{command.lower()}_resources_mid"
    ).with_attribute("subarray_id", 1)

    if command == "assign resources":
        context_fixt.when_action_result = central_node_facade.assign_resources(
            json_input, wait_termination=True
        )
    elif command == "release resources":
        context_fixt.when_action_result = (
            central_node_facade.release_resources(
                json_input, wait_termination=False
            )
        )


@then(parsers.parse("SDP, CSP must go to {state} ObsState"))
def verify_subsystems_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    state: ObsState,
    event_tracer: TangoEventTracer,
):
    """Verify that CSP and SDP subarrays transition to the specified state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        f"should move to {state} ObsState."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        state,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        state,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        state,
        previous_value=context_fixt.starting_state,
    )
    context_fixt.starting_state = state


@then(parsers.parse("the Mid subarray must be in {final_obs_state} ObsState"))
def verify_mid_subarray_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    final_obs_state: ObsState,
    event_tracer: TangoEventTracer,
):
    """
    Verify that the mid subarray transitions to the specified final state.
    """
    assert_that(event_tracer).described_as(
        f"The Mid subarray should move to {final_obs_state} ObsState."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        final_obs_state,
        previous_value=context_fixt.starting_state,
    )
    context_fixt.starting_state = final_obs_state
