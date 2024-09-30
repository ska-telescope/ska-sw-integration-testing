"""Test module for TMC StartUp functionality"""
import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow

TIMEOUT = 100


@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_telescope_startup.feature",
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


# @then("the SDP, CSP and MCCS goes to ON state") -> conftest


@then("the telescope go to ON state")
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
