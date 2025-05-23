"""Test module for Configure functionality (XTP-68817)"""

import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import (
    CSPFacade,  # CSP facade
)
from ska_integration_test_harness.facades.dishes_facade import DishesFacade
from ska_integration_test_harness.facades.sdp_facade import (
    SDPFacade,  # SDP facade
)
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.dish_mode import DishMode
from ska_integration_test_harness.inputs.pointing_state import PointingState
from ska_tango_testing.integration import TangoEventTracer
from tests.system_level_tests.conftest import (
    DISH_IDS,
    SubarrayTestContextData,
    _setup_event_subscriptions,
)
from tests.system_level_tests.utils.json_file_input_handler import (
    MyFileJSONInput,
)

TIMEOUT = 200


@pytest.mark.system_level_test_mid
@scenario(
    "system_level_tests/"
    + "xtp_66801_telescope_observational_commands.feature",
    "Configure a Mid telescope subarray for a scan using TMC",
)
def test_telescope_configure_command():
    """BDD test scenario for verifying successful execution of
    the Configure command with TMC,CSP and SDP
    devices for pairwise testing"""


#  @given("telescope is in ON state") -> conftest


@when("I issue the Configure command to subarray")
def send_configure_command(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Send the Configure command to the subarray.

    This step uses the subarray_node_facade to send a Configure command
    to the specified subarray. It uses a pre-defined JSON input file and
    sends the command without waiting for termination. The action result
    is stored in the context fixture.
    """
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    context_fixt.when_action_name = "Configure"

    json_input = MyFileJSONInput("subarray", "configure_mid")

    context_fixt.when_action_result = tmc.configure(
        json_input,
        wait_termination=False,
    )


@then("the TMC, CSP and SDP subarrays transition to CONFIGURING obsState")
def verify_configuring_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the CONFIGURING state.
    """
    assert_that(event_tracer).described_as(
        f"All three: TMC Subarray Node device "
        f"({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to CONFIGURING."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.CONFIGURING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.CONFIGURING,
        previous_value=context_fixt.starting_state,
    )
    # store current (already verified) state to use it as previous step
    # in next assertions
    context_fixt.starting_state = ObsState.CONFIGURING


@then("the TMC, CSP and SDP subarrays transition to READY obsState")
def verify_ready_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the READY state.

    This step checks that the ObsState attribute of the TMC Subarray Node,
    CSP Subarray, and SDP Subarray devices all transition from the starting
    state to the READY state. It uses the event_tracer to assert that these
    state changes occur within a specified timeout. After verification, it
    updates the starting state in the context fixture for subsequent steps.
    """
    assert_that(event_tracer).described_as(
        f"All three: TMC Subarray Node device "
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


@then("the DishMaster transitions to dishMode OPERATE and pointingState TRACK")
def check_dish_mode_and_pointing_state_after_configure(
    event_tracer: TangoEventTracer,
    dishes: DishesFacade,
):
    """Verify that each DishMaster transitions to
    OPERATE and pointingState TRACK"""
    for dish_id in DISH_IDS:
        assert_that(event_tracer).described_as(
            f"The DishMaster {dish_id} must transition to OPERATE mode"
        ).within_timeout(120).has_change_event_occurred(
            dishes.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
        ).has_change_event_occurred(
            dishes.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
        )
