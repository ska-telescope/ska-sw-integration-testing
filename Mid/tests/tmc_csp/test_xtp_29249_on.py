"""Test module for TMC-CSP StartUp functionality"""
import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from tests.resources.test_harness.helpers import (
    get_master_device_simulators,
    wait_csp_master_off,
)


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29249_on.feature",
    "StartUp Telescope with TMC and CSP devices",
)
def test_tmc_csp_startup_telescope():
    """
    Test case to verify TMC-CSP StartUp functionality
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


@given("telescope state is OFF")
def check_state_devices(central_node_mid, event_recorder):
    """Set up a TMC and ensure it is in the OFF state."""
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    central_node_mid.csp_master.adminMode = 0
    wait_csp_master_off()
    csp_master_state = central_node_mid.csp_master.state()
    assert csp_master_state is DevState.OFF


@when("I start up the telescope")
def move_telescope_to_on(central_node_mid):
    """A method to turn on the telescope."""
    central_node_mid.move_to_on()


@then("the CSP must go to ON state")
def check_csp_is_on(central_node_mid, event_recorder):
    """A method to check CSP controller and CSP subarray states."""
    event_recorder.subscribe_event(central_node_mid.csp_master, "State")
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices["csp_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )


@then("telescope state is ON")
def check_telescope_state(central_node_mid, event_recorder):
    """A method to check CentralNode.telescopeState"""
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
