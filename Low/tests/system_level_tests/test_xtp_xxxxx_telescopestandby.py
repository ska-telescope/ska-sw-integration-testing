"""Test module for TMC-SDP ShutDown functionality"""
import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from Low.tests.resources.test_harness.helpers import (
    get_master_device_simulators,
)


@pytest.mark.tmc_all
@scenario(
    "../../features/system_level_tests/xtp_xxxxxx_telescope_startup.feature",
    "Standby the low telescope",
)
def test_tmc_csp_standby_telescope():
    """
    Test case to verify TMC-CSP Standby functionality
    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given("an low telescope")
def given_the_sut(central_node_low, subarray_node_low, simulator_factory):
    """
    Given a TMC and CSP in ON state
    """
    (_, sdp_master_sim, _) = get_master_device_simulators(simulator_factory)

    assert central_node_low.central_node.ping() > 0
    assert central_node_low.sdp_master.ping() > 0
    assert subarray_node_low.subarray_devices["sdp_subarray"].ping() > 0
    assert sdp_master_sim.ping() > 0


@given("an Telescope consisting of SDP, CSP and MCCS that is ON")
def check_tmc_csp_state_is_on(
    central_node_low, subarray_node_low, event_recorder
):
    """A method to check CentralNode.telescopeState"""
    event_recorder.subscribe_event(central_node_low.csp_master, "State")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "State"
    )
    central_node_low.move_to_on()
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


@when("I invoke standby command on the telescope")
def move_csp_to_standby(central_node_low):
    """A method to put CSP to STANDBY"""
    central_node_low.set_standby()


@then("the telescope goes to Standby state")
def check_telescope_state_standby(central_node_low, event_recorder):
    """A method to check CentralNode.telescopeState"""
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.STANDBY,
    )
