"""Test module for TMC StartUp functionality"""
import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)

TIMEOUT = 100


@pytest.mark.system_level_tests
@scenario(
    "../Low/features/system_level_tests/"
    + "xtp_64112_telescope_startup.feature",
    "Starting up low telescope",
)
def test_tmc_startup_telescope():
    """
    Test case to verify StartUp functionality
    """


@when("I invoke the ON command on the telescope")
def move_telescope_to_on(central_node_low: CentralNodeWrapperLow):
    """A method to turn on the telescope."""
    central_node_low.move_to_on()


@then("the SDP, CSP and MCCS goes to ON state")
def check_devices_is_on(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """A method to check devices states."""

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "CSP devices"
        "are expected to be in State ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.csp_master,
        "State",
        DevState.ON,
    ).has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "SDP devices"
        "are expected to be in State ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.sdp_master,
        "State",
        DevState.ON,
    ).has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "State",
        DevState.ON,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "MCCS devices"
        "are expected to be in State ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.mccs_master,
        "State",
        DevState.ON,
    ).has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "State",
        DevState.ON,
    )


@then("the telescope goes to ON state")
def check_telescope_state(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """A method to check CentralNode.telescopeState"""

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
