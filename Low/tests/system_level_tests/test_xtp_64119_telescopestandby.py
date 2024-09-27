"""Test module for TMC-SDP ShutDown functionality"""
import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow

TIMEOUT = 100


@pytest.mark.system_level_tests
@scenario(
    "./../../features/system_level_tests/"
    + "xtp_64112_telescope_startup.feature",
    "Standby the low telescope",
)
def test_standby_telescope():
    """
    Test case to verify TMC-CSP Standby functionality
    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """


@when("I invoke STANDBY command on the telescope")
def move_to_standby(central_node_low: CentralNodeWrapperLow):
    """A method to put telescope to STANDBY"""
    central_node_low.set_standby()


@then("the telescope goes to STANDBY state")
def check_telescope_state_standby(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """A method to check CentralNode.telescopeState"""
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER STANDBY COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState STANDBY",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.STANDBY,
    )
