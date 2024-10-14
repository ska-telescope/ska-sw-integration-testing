import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
from ska_integration_test_harness.facades.csp_facade import CSPFacade
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


@then("the telescope go to STANDBY state")
def verify_standby_state(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
):
    """The telescope and devices transition to the STANDBY state."""

    devices = [
        {
            "name": "CSP",
            "subarray": csp.csp_subarray,
            "master": csp.csp_master,
            "subarray_state": DevState.OFF,
            "master_state": DevState.STANDBY,
        },
        {
            "name": "SDP",
            "subarray": sdp.sdp_subarray,
            "master": sdp.sdp_master,
            "subarray_state": DevState.OFF,
            "master_state": DevState.STANDBY,
        },
    ]

    # Testing for CSP and SDP devices transitioning to their respective states
    for device in devices:
        # Assert subarray transition first
        assert_that(event_tracer).described_as(
            f"{device['name']} subarray should transition to OFF state."
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            device["subarray"],
            "State",
            device["subarray_state"],
        )

        # Assert master transition next
        assert_that(event_tracer).described_as(
            f"{device['name']} master should transition to STANDBY state."
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            device["master"],
            "State",
            device["master_state"],
        )

    # After all CSP and SDP components are verified,
    # check the central node last
    assert_that(event_tracer).described_as(
        "The telescope and CSP/SDP devices should \
            transition to the correct states."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.STANDBY,
    )
