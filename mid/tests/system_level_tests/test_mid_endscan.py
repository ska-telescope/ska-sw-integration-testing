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

TIMEOUT = 100


@pytest.mark.system_level_test_mid
@scenario(
    "../../mid/features/system_level_tests/xtp_68819_scan_endscan.feature",
    "Executes EndScan command on Mid telescope",
)
def test_telescope_endscan():
    """BDD test scenario for verifying successful execution of
    the EndScan command with TMC,CSP, SDP and DISH
    devices for pairwise testing"""


#  @given("telescope is in ON state") -> conftest


@given("subarray is in Scanning ObsState")
def subarray_in_scanning_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: TestHarnessInputs,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Ensure the subarray is in the SCANNING state."""
    _setup_event_subscriptions(
        central_node_facade, subarray_node_facade, csp, sdp, event_tracer
    )
    context_fixt.starting_state = ObsState.SCANNING
    context_fixt.expected_next_state = ObsState.READY

    subarray_node_facade.force_change_of_obs_state(
        ObsState.SCANNING,
        default_commands_inputs,
        wait_termination=True,
    )


@when("I issue the Endscan command to the subarray")
def send_end_scan_command(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """
    Send the EndScan command to the subarray.

    This step uses the subarray_node_facade to send an EndScan command to
    the specified subarray. It sends the command without waiting for
    termination and stores the action result in the context fixture.
    """
    context_fixt.when_action_name = "EndScan"

    context_fixt.when_action_result = subarray_node_facade.end_scan(
        wait_termination=False,
    )


@then("the subarray {subarray} should transition to the READY state")
def verify_ready_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the READY state.
    """
    assert_that(event_tracer).described_as(
        "All three: TMC Subarray Node device"
        f"({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to READY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.READY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.READY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.READY,
        previous_value=context_fixt.starting_state,
    )

    # override the starting state for the next step
    context_fixt.starting_state = ObsState.READY
