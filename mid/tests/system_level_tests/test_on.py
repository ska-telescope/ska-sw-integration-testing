import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
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
    "system_level_tests/" + "xtp_65506_on.feature",
    "Starting up mid telescope",
)
def test_telescope_on_command_flow():
    """
    Test case to verify ON command on mid telescope
    """


@when("I invoke the ON command on the telescope")
def send_telescope_command(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
):
    """Send the ON command to the telescope."""
    event_tracer.clear_events()
    central_node_facade.move_to_on(wait_termination=False)


@then("the SDP and CSP to ON state")
def verify_on_state(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
):
    """The telescope and CSP devices transition to the ON state."""
    assert_that(event_tracer).described_as(
        "The telescope and CSP devices should transition " "to the ON state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.ON,
    ).has_change_event_occurred(
        csp.csp_master,
        "State",
        DevState.ON,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "State",
        DevState.ON,
    )
    assert_that(event_tracer).described_as(
        "The telescope and SDP devices should transition " "to the ON state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.ON,
    ).has_change_event_occurred(
        sdp.sdp_master,
        "State",
        DevState.ON,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "State",
        DevState.ON,
    )


@then("DishMaster must transition to STANDBY-FP mode")
def verify_dish_mode(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    dishes: DishesFacade,
):
    """Verify that each DishMaster transitions to the correct mode."""

    # Iterate over dish IDs and verify the transition of each DishMaster
    for dish_id in ["dish_001", "dish_036", "dish_063", "dish_100"]:
        assert_that(event_tracer).described_as(
            f"The DishMaster {dish_id} must transition to STANDBY-FP mode"
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            central_node_facade.central_node,
            "telescopeState",
            DevState.ON,
        ).has_change_event_occurred(
            dishes.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )
