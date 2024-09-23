"""Test module for TMC StartUp functionality"""
import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from Low.tests.resources.test_harness.central_node_low import (
    CentralNodeWrapperLow,
)
from Low.tests.resources.test_harness.helpers import (
    get_master_device_simulators,
)
from Low.tests.resources.test_harness.simulator_factory import SimulatorFactory
from Low.tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)


@pytest.mark.real_device
@scenario(
    "../../features/system_level_tests/xtp_xxxxxx_telescope_startup.feature",
    "Starting up low telescope",
)
def test_tmc_startup_telescope():
    """
    Test case to verify StartUp functionality
    """


@given("a low telescope")
def given_the_sut(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    simulator_factory: SimulatorFactory,
) -> None:
    """
    Given a TMC

    Args:
        simulator_factory: fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
    """
    (_, sdp_master_sim, _) = get_master_device_simulators(simulator_factory)

    assert central_node_low.central_node.ping() > 0
    assert central_node_low.sdp_master.ping() > 0
    assert subarray_node_low.subarray_devices["sdp_subarray"].ping() > 0
    assert sdp_master_sim.ping() > 0


@when("I invoke the ON command on the telescope")
def move_telescope_to_on(central_node_low: CentralNodeWrapperLow):
    """A method to turn on the telescope."""
    central_node_low.move_to_on()


@then("the SDP, CSP and MCCS goes to ON state")
def check_devices_is_on(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_recorder,
):
    """A method to check devices states."""
    event_recorder.subscribe_event(central_node_low.csp_master, "State")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )
    event_recorder.subscribe_event(central_node_low.sdp_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.sdp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["sdp_subarray"],
        "State",
        DevState.ON,
    )
    event_recorder.subscribe_event(central_node_low.mccs_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.mccs_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["mccs_subarray"],
        "State",
        DevState.ON,
    )


@then("the telescope goes to ON state")
def check_telescope_state(
    central_node_low: CentralNodeWrapperLow, event_recorder
):
    """A method to check CentralNode.telescopeState"""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
