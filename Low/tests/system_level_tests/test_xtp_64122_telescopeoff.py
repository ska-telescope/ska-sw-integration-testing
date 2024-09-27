"""Test module for TMC-SDP ShutDown functionality"""
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
    "../../features/system_level_tests/"
    + "xtp_64112_telescope_startup.feature",
    "Switch off the low telescope",
)
def test_off_telescope():
    """
    Test case to verify TMC-CSP Standby functionality
    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """


@when("I switch off the telescope")
def move_to_off(central_node_low: CentralNodeWrapperLow):
    """A method to put CSP to STANDBY"""
    central_node_low.move_to_off()


@then("the SDP,CSP and MCCS must be OFF")
def check_telescope_state_standby(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """A method to check CentralNode.telescopeState"""
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER OFF COMMAND: "
        "SDP devices"
        "are expected to be in State OFF",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.sdp_master,
        "State",
        DevState.OFF,
    ).has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "State",
        DevState.OFF,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER OFFCOMMAND: "
        "MCCS devices"
        "are expected to be in State OFF",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.mccs_master,
        "State",
        DevState.OFF,
    ).has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "State",
        DevState.OFF,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER OFF COMMAND: "
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
        "FAILED ASSUMPTION AFTER STANDBY COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState UNKNOWN",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.UNKNOWN,
    )
