import logging

import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.dishes_facade import DishesFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState

# Constants
ASSERTIONS_TIMEOUT = 60


@pytest.mark.system_level_test_mid
@scenario(
    "system_level_tests/" + "xtp_66801_telescope_operational_commands.feature",
    "Standby the mid telescope",
)
def test_telescope_standby_command_flow():
    """
    Test case to verify standby command on mid telescope
    """


@when("I invoke the STANDBY command on the telescope")
def send_telescope_command(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
):
    """Send the ON command to the telescope."""
    event_tracer.clear_events()
    central_node_facade.set_standby(wait_termination=False)


@then(
    "the Telescope consisting of SDP and CSP devices "
    "should transition to STANDBY state"
)
def verify_standby_state(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    dishes: DishesFacade,
):
    """The telescope and devices transition to the STANDBY state."""
    assert_that(event_tracer).described_as(
        "The telescope,CSP and SDP devices should transition \
            from ON to STANDBY state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.STANDBY,
    ).has_change_event_occurred(
        csp.csp_master,
        "State",
        DevState.STANDBY,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "State",
        DevState.OFF,
    ).has_change_event_occurred(
        sdp.sdp_master,
        "State",
        DevState.STANDBY,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "State",
        DevState.OFF,
    )
    for dish_id in ["dish_001", "dish_036", "dish_063", "dish_100"]:
        logging.info(
            f"DISH MODE is: " f"{dishes.dish_master_dict[dish_id].dishMode}"
        )
    assert 0