import pytest
from assertpy import assert_that
from pytest_bdd import parsers, scenario, then, when
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.dishes_facade import DishesFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from ska_integration_test_harness.inputs.dish_mode import DishMode
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState

# Constants
ASSERTIONS_TIMEOUT = 60


@pytest.mark.system_level_test_mid
@scenario(
    "system_level_tests/" + "xtp_65506_on_off.feature",
    "ON to OFF - CMD on mid telescope",
)
def test_telescope_on_off_command_flow():
    """
    Test case to verify operational commands on mid telescope
    """


@pytest.mark.system_level_test_mid
@scenario(
    "system_level_tests/" + "xtp_66810_on_standby.feature",
    "ON to STANDBY - CMD on mid telescope",
)
def test_telescope_on_standby_command_flow():
    """
    Test case to verify transitioning to STANDBY on mid telescope
    """


@when(parsers.parse("I {command} the telescope"))
def send_telescope_command(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    command,
):
    """Send the command to the telescope."""
    event_tracer.clear_events()

    if command == "start up":
        central_node_facade.move_to_on(wait_termination=False)
    elif command == "switch off":
        central_node_facade.move_to_off(wait_termination=False)


@then(parsers.parse("SDP, CSP must go to {state} state"))
def verify_state(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    state,
):
    """Verify the state of the telescope and
    its devices, including subarrays."""

    # Determine expected state for the central node and CSP/SDP devices
    if state == "ON":
        expected_state = DevState.ON
        subarray_state = DevState.ON  # Subarrays should also be ON
    elif state == "OFF":
        expected_state = DevState.OFF
        subarray_state = DevState.OFF  # Subarrays should also be OFF
    elif state == "STANDBY":
        expected_state = DevState.STANDBY  # Master should go to STANDBY
        subarray_state = DevState.OFF  # Subarrays should be OFF
    else:
        raise ValueError(f"Unexpected state: {state}")

    # Verify CSP Master and Subarray state
    assert_that(event_tracer).described_as(
        f"The telescope and CSP should transition to {state} state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node, "telescopeState", expected_state
    ).has_change_event_occurred(
        csp.csp_master, "State", expected_state
    ).has_change_event_occurred(
        csp.csp_subarray, "State", subarray_state  # Check subarray state
    )

    # Verify SDP Master and Subarray state
    assert_that(event_tracer).described_as(
        f"The telescope and SDP should transition to {state} state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        sdp.sdp_master, "State", expected_state
    ).has_change_event_occurred(
        sdp.sdp_subarray, "State", subarray_state  # Check subarray state
    )


@then(parsers.parse("DishMaster must transition to {dish_mode} mode"))
def verify_dish_mode(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    dishes: DishesFacade,
    dish_mode,
):
    """Verify that each DishMaster transitions to the correct mode."""

    # Determine expected mode and telescope state based on dish_mode
    if dish_mode == "STANDBY-FP":
        # For STANDBY-FP, telescope is ON
        expected_mode = DishMode.STANDBY_FP
        expected_telescope_state = DevState.ON
    elif dish_mode == "STANDBY-LP":
        # For STANDBY-LP, telescope is OFF
        expected_mode = DishMode.STANDBY_LP
        expected_telescope_state = DevState.OFF
    elif dish_mode == "STANDBY":
        # For STANDBY, telescope is in STANDBY
        expected_mode = DishMode.STANDBY_LP
        expected_telescope_state = DevState.STANDBY
    else:
        raise ValueError(f"Unexpected dish_mode: {dish_mode}")

    # Iterate over dish IDs and verify the transition of each DishMaster
    for dish_id in ["dish_001", "dish_036", "dish_063", "dish_100"]:
        assert_that(event_tracer).described_as(
            f"The DishMaster {dish_id} must transition to {dish_mode} mode."
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            central_node_facade.central_node,
            "telescopeState",
            expected_telescope_state,
        ).has_change_event_occurred(
            dishes.dish_master_dict[dish_id],
            "dishMode",
            expected_mode,
        )
