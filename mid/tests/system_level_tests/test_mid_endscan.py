"""Test module for EndScan functionality (XTP-66801)"""

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import (
    CSPFacade,  # CSP facade
)
from ska_integration_test_harness.facades.dishes_facade import DishesFacade
from ska_integration_test_harness.facades.sdp_facade import (
    SDPFacade,  # SDP facade
)
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.pointing_state import PointingState
from ska_tango_testing.integration import TangoEventTracer
from tests.system_level_tests.conftest import (
    DISH_IDS,
    SubarrayTestContextData,
    _setup_event_subscriptions,
)

from .conftest import TestHarnessInputs

TIMEOUT = 100


@pytest.mark.system_level_test_mid
@scenario(
    "../../mid/features/system_level_tests/"
    + "xtp_66801_telescope_observational_commands.feature",
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
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
):
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    tmc.force_change_of_obs_state(
        ObsState.SCANNING,
        default_commands_inputs,
        wait_termination=True,
    )
    context_fixt.starting_state = ObsState.SCANNING

    # We haven't used force change obstate directly as we are not able to
    # verify the completion of command with longrunningcommandresult against
    # the command_id, This can be considered as an imporvement to test harness

    # context_fixt.when_action_name = "AssignResources"
    # json_input = MyFileJSONInput(
    #     "centralnode", "assign_resources_mid"
    # ).with_attribute("subarray_id", 1)

    # context_fixt.when_action_result = tmc.assign_resources(
    #     json_input,
    #     wait_termination=False,
    # )
    # assert_that(event_tracer).described_as(
    #     f"All three: TMC Subarray Node device "
    #     f"({tmc.subarray_node})"
    #     f", CSP Subarray device ({csp.csp_subarray}) "
    #     f"and SDP Subarray device ({sdp.sdp_subarray}) "
    #     "ObsState attribute values should move "
    #     f"from {str(context_fixt.starting_state)} to RESOURCING."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "obsState",
    #     ObsState.RESOURCING,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.RESOURCING,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     sdp.sdp_subarray,
    #     "obsState",
    #     ObsState.RESOURCING,
    #     previous_value=context_fixt.starting_state,
    # )

    # # override the starting state for the next step

    # context_fixt.starting_state = ObsState.RESOURCING
    # assert_that(event_tracer).described_as(
    #     f"All three: TMC Subarray Node device "
    #     f"({tmc.subarray_node})"
    #     f", CSP Subarray device ({csp.csp_subarray}) "
    #     f"and SDP Subarray device ({sdp.sdp_subarray}) "
    #     "ObsState attribute values should move "
    #     f"from {str(context_fixt.starting_state)} to IDLE."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "obsState",
    #     ObsState.IDLE,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.IDLE,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     sdp.sdp_subarray,
    #     "obsState",
    #     ObsState.IDLE,
    #     previous_value=context_fixt.starting_state,
    # )
    # assert_that(event_tracer).described_as(
    #     f"TMC Central Node ({tmc.central_node}) is "
    #     " expected to report a longRunningCommand successful completion."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.central_node,
    #     "longRunningCommandResult",
    #     get_expected_long_run_command_result(context_fixt),
    # )
    # context_fixt.starting_state = ObsState.IDLE
    # context_fixt.when_action_name = "Configure"
    # json_input = MyFileJSONInput("subarray", "configure_mid")
    # context_fixt.when_action_result = tmc.configure(
    #     json_input,
    #     wait_termination=False,
    # )
    # assert_that(event_tracer).described_as(
    #     f"All three: TMC Subarray Node device "
    #     f"({tmc.subarray_node})"
    #     f", CSP Subarray device ({csp.csp_subarray}) "
    #     f"and SDP Subarray device ({sdp.sdp_subarray}) "
    #     "ObsState attribute values should move "
    #     f"from {str(context_fixt.starting_state)} to CONFIGURING."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "obsState",
    #     ObsState.CONFIGURING,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.CONFIGURING,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     sdp.sdp_subarray,
    #     "obsState",
    #     ObsState.CONFIGURING,
    #     previous_value=context_fixt.starting_state,
    # )
    # # store current (already verified) state to use it as previous step
    # # in next assertions
    # context_fixt.starting_state = ObsState.CONFIGURING
    # assert_that(event_tracer).described_as(
    #     f"All three: TMC Subarray Node device "
    #     f"({tmc.subarray_node})"
    #     f", CSP Subarray device ({csp.csp_subarray}) "
    #     f"and SDP Subarray device ({sdp.sdp_subarray}) "
    #     "ObsState attribute values should move "
    #     f"from {str(context_fixt.starting_state)} to READY."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "obsState",
    #     ObsState.READY,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.READY,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     sdp.sdp_subarray,
    #     "obsState",
    #     ObsState.READY,
    #     previous_value=context_fixt.starting_state,
    # )
    # assert_that(event_tracer).described_as(
    #     f"TMC Subarray Node ({tmc.subarray_node}) is "
    #     " expected to report a longRunningCommand successful completion."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "longRunningCommandResult",
    #     get_expected_long_run_command_result(context_fixt),
    # )
    # context_fixt.when_action_name = "Scan"

    # json_input = MyFileJSONInput("subarray", "scan_mid")

    # context_fixt.when_action_result = tmc.scan(
    #     json_input,
    #     wait_termination=False,
    # )
    # context_fixt.starting_state = ObsState.READY
    # assert_that(event_tracer).described_as(
    #     "All three: TMC Subarray Node device"
    #     f"({tmc.subarray_node})"
    #     f", CSP Subarray device ({csp.csp_subarray}) "
    #     f"and SDP Subarray device ({sdp.sdp_subarray}) "
    #     "ObsState attribute values should move "
    #     f"from {str(context_fixt.starting_state)} to SCANNING."
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "obsState",
    #     ObsState.SCANNING,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.SCANNING,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     sdp.sdp_subarray,
    #     "obsState",
    #     ObsState.SCANNING,
    #     previous_value=context_fixt.starting_state,
    # )


@when("I issue the EndScan command to the subarray")
def send_end_scan_command(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
):
    """
    Send the EndScan command to the subarray.

    This step uses the subarray_node_facade to send an EndScan command to
    the specified subarray. It sends the command without waiting for
    termination and stores the action result in the context fixture.
    """
    context_fixt.when_action_name = "EndScan"

    context_fixt.when_action_result = tmc.end_scan(
        wait_termination=False,
    )
    context_fixt.starting_state = ObsState.SCANNING


@then("the TMC, CSP and SDP subarrays transition to ObsState READY")
def verify_ready_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the READY state.
    """
    assert_that(event_tracer).described_as(
        "All three: TMC Subarray Node device"
        f"({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to READY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
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


@then("the DishMaster transitions to pointingState TRACK")
def dish_master_transitions_to_track(
    event_tracer: TangoEventTracer,
    dishes: DishesFacade,
):
    """Verify that each DishMaster transitions to
    OPERATE and pointingState TRACK"""
    for dish_id in DISH_IDS:
        assert_that(event_tracer).described_as(
            f"The DishMaster {dish_id} must transition to pointingState TRACK"
        ).has_change_event_occurred(
            dishes.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
        )
