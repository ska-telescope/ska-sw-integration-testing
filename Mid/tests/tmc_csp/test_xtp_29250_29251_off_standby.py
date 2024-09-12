"""Test module for TMC-CSP ShutDown functionality"""
import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from tests.resources.test_harness.helpers import get_master_device_simulators


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29250_off.feature",
    "Turn Off Telescope with real TMC and CSP devices",
)
def test_tmc_csp_telescope_off():
    """
    Test case to verify TMC-CSP ShutDown functionality
    """


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29251_standby.feature",
    "Standby the Telescope with real TMC and CSP devices",
)
def test_tmc_csp_telescope_standby():
    """
    Test case to verify TMC-CSP ShutDown functionality
    """


@given(
    "a Telescope consisting of TMC, CSP, simulated DISH and simulated"
    + " SDP devices"
)
def given_the_sut(central_node_mid, simulator_factory):
    """
    Given a TMC

    Args:
        simulator_factory: fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
    """
    # Add dish 4 when SKB-266 is resolved
    (
        _,
        sdp_master_sim,
        dish_master_sim_1,
        dish_master_sim_2,
        dish_master_sim_3,
        dish_master_sim_4,
    ) = get_master_device_simulators(simulator_factory)

    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0
    assert sdp_master_sim.ping() > 0
    assert dish_master_sim_1.ping() > 0
    assert dish_master_sim_2.ping() > 0
    assert dish_master_sim_3.ping() > 0
    assert dish_master_sim_4.ping() > 0
    if central_node_mid.telescope_state != "ON":
        central_node_mid.move_to_on()


@given("telescope is in ON state")
def check_telescope_state_is_on(central_node_mid, event_recorder):
    """A method to check if telescopeState is on"""
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=15,
    )


@when("I switch off telescope")
def move_sdp_to_off(central_node_mid):
    """A method to put tmc to OFF"""
    central_node_mid.move_to_off()


@when("I standby the telescope")
def move_sdp_to_standby(central_node_mid):
    """A method to put tmc to STANDBY"""
    central_node_mid.set_standby()


@then("the CSP must go to OFF state")
def check_csp_is_off(central_node_mid, event_recorder):
    """A method to check CSP's State"""
    event_recorder.subscribe_event(central_node_mid.csp_master, "State")
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices["csp_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_master,
        "State",
        DevState.OFF,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices["csp_subarray"],
        "State",
        DevState.OFF,
    )


@then("telescope state is OFF")
def check_telescope_state_off(central_node_mid, event_recorder):
    """A method to check CentralNode.telescopeState"""
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.OFF,
    )


@then("the csp controller must go to standby state")
def check_csp_master_is_moved_to_standby(central_node_mid, event_recorder):
    """A method to check CSP controllers State"""
    event_recorder.subscribe_event(central_node_mid.csp_master, "State")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_master, "State", DevState.STANDBY, lookahead=15
    )


@then("the csp subarray must go to off state")
def check_csp_subarray_is_moved_to_off(central_node_mid, event_recorder):
    """A method to check CSP Subarray's State"""
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices["csp_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices["csp_subarray"],
        "State",
        DevState.OFF,
        lookahead=10,
    )


@then("telescope state is STANDBY")
def check_telescope_state_is_standby(central_node_mid, event_recorder):
    """A method to check CentralNode.telescopeState"""
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.STANDBY,
    )
