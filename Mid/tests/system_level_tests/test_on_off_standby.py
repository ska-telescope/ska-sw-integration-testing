"""
Operational command system level test case
"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade

# from ska_integration_test_harness.facades.dish_facade import (
#     DISHFacade,
# )
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

# Constants
ASSERTIONS_TIMEOUT = 60


@pytest.mark.system_level_test_mid
@scenario(
    "../../features/system_level_tests/xtp_xxxxxx.feature",
    "ON to OFF - CMD on mid telescope",
)
def test_tmc_operational_command_flow():
    """
    Test case to verify operational commands on mid telescope
    """


@given("a mid telescope")
def given_the_sut(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
):
    """_summary_

    Args:
        event_tracer (TangoEventTracer): _description_
        central_node_facade (TMCCentralNodeFacade): _description_
        csp (CSPFacade): _description_
        sdp (SDPFacade): _description_
    """
    event_tracer.subscribe_event(
        central_node_facade.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(csp.csp_master, "State")
    event_tracer.subscribe_event(csp.csp_subarray, "State")
    event_tracer.subscribe_event(sdp.sdp_master, "State")
    event_tracer.subscribe_event(sdp.sdp_subarray, "State")

    log_events(
        {
            central_node_facade.central_node: ["telescopeState"],
            csp.csp_master: ["State"],
            csp.csp_subarray: ["State"],
        }
    )
    log_events(
        {
            central_node_facade.central_node: ["telescopeState"],
            sdp.sdp_master: ["State"],
            sdp.sdp_subarray: ["State"],
        }
    )


@when("I invoke the ON command on the telescope")
def send_telescope_on_command(
    event_tracer: TangoEventTracer, central_node_facade: TMCCentralNodeFacade
):
    """Send the TelescopeOn command to the telescope."""
    event_tracer.clear_events()
    central_node_facade.move_to_on(wait_termination=False)


@then(parsers.parse("the SDP, CSP and DISH {dish_ids} goes to STANDBY state"))
def verify_standby_state(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
):
    """The telescope and devices transition to the STANDBY state."""
    assert_that(event_tracer).described_as(
        "The telescope and CSP master should transition "
        "to the STANDBY state. "
        "CSP subarray should transition to OFF state."
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
        DevState.STANDBY,
    )
    assert_that(event_tracer).described_as(
        "The telescope and SDP master should transition "
        "to the STANDBY state. "
        "SDP subarray should transition to OFF state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.STANDBY,
    ).has_change_event_occurred(
        sdp.sdp_master,
        "State",
        DevState.STANDBY,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "State",
        DevState.STANDBY,
    )


# need to look how to assert dishes


@then(parsers.parse("the SDP, CSP and DISH {dish_ids} goes to ON state"))
def verify_on_state(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
):
    """The telescope and  devices transition to the ON state."""
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
    # need to look how to assert dishes


@when("I switch off the telescope")
def send_telescope_off_command(
    event_tracer: TangoEventTracer, central_node_facade: TMCCentralNodeFacade
):
    """Send the TelescopeOff command to the telescope."""
    event_tracer.clear_events()
    central_node_facade.move_to_off(wait_termination=False)


@then("the SDP,CSP and DISH must be OFF")
def verify_off_state(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
):
    """The telescope and  devices transition to the OFF state."""
    assert_that(event_tracer).described_as(
        "The telescope and CSP devices should transition from ON to OFF state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.OFF,
    ).has_change_event_occurred(
        csp.csp_master,
        "State",
        DevState.OFF,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "State",
        DevState.OFF,
    )
    assert_that(event_tracer).described_as(
        "The telescope and SDP devices should transition from ON to OFF state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.OFF,
    ).has_change_event_occurred(
        sdp.sdp_master,
        "State",
        DevState.OFF,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "State",
        DevState.OFF,
    )
