"""Test case for verifying TMC TelescopeHealthState transition based on SDP
 Controller HealthState."""
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import HealthState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import (
    centralnode,
    csp_master,
    csp_subarray1,
    dish_master1,
    sdp_master,
)
from tests.resources.test_harness.helpers import (
    get_device_simulator_with_given_name,
    wait_until_devices_operational,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.tmc_sdp_unhappy
@scenario(
    "../features/tmc_sdp/xtp_39503_health_state_unhappy_path.feature",
    "Verify TMC TelescopeHealthState transition based on SDP Controller"
    + " HealthState",
)
def test_telescope_state_sdp_controller():
    """This test case sets up a Telescope consisting of TMC-SDP, emulated CSP,
    and emulated Dish. It then changes the health state of specified simulator
    devices and checks if the telescope's health state is
    updated accordingly."""


@given("a Telescope consisting of TMC, SDP, simulated CSP and simulated Dish")
def given_telescope_setup_with_simulators(
    central_node_mid: CentralNodeWrapperMid,
    simulator_factory: SimulatorFactory,
):
    """Method to check TMC real devices and sub-system simulators

    Args:
        central_node_mid (CentralNodeWrapperMid): fixture for a
        TMC CentralNode under test
        simulator_factory (_type_):fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
    """
    simulated_devices = get_device_simulator_with_given_name(
        simulator_factory, ["csp master", "dish master1"]
    )
    csp_master_sim, dish_master_sim = simulated_devices

    devices_to_monitor = [
        centralnode,
        sdp_master,
        csp_subarray1,
        csp_master,
        dish_master1,
    ]

    assert wait_until_devices_operational(devices_to_monitor)

    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0
    assert central_node_mid.subarray_devices["csp_subarray"].ping() > 0
    assert csp_master_sim.ping() > 0
    assert dish_master_sim.ping() > 0


@when(parsers.parse("The {devices} health state changes to {health_state}"))
def set_simulator_devices_health_states(
    devices: str, health_state: str, simulator_factory: SimulatorFactory
):
    """Method to set the health state of specified simulator devices.

    Args:
        devices (list): Names of the devices whose health state will change.
        health_state (list): The new health states for the devices.
        simulator_factory (SimulatorFactory): Fixture for SimulatorFactory
          class.
    """
    # Split the devices string into individual devices
    devices_list = devices.split(",")
    health_state_list = health_state.split(",")

    sim_devices_list = get_device_simulator_with_given_name(
        simulator_factory, devices_list
    )
    for sim_device, sim_health_state_val in list(
        zip(sim_devices_list, health_state_list)
    ):
        # Check if the device is not the SDP controller
        if sim_device.dev_name not in [sdp_master]:
            sim_device.SetDirectHealthState(HealthState[sim_health_state_val])


@then(parsers.parse("the telescope health state is {telescope_health_state}"))
def check_telescope_health_state(
    central_node_mid, event_recorder, telescope_health_state
):
    """A method to check CentralNode.telescopehealthState attribute
    change after aggregation

    Args:
        central_node_mid : A fixture for CentralNode tango device class
        event_recorder: A fixture for EventRecorder class_
        telescope_health_state (str): telescopehealthState value
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeHealthState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeHealthState",
        HealthState[telescope_health_state],
    ), f"Expected telescopeHealthState to be \
        {HealthState[telescope_health_state]}"
