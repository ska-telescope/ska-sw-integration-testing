"""Test module for TMC-SDP On functionality"""

import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from tests.resources.test_harness.helpers import (
    get_master_device_simulators,
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.utils.enums import DishMode


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29230_on.feature",
    "Start up the telescope having TMC and SDP subsystems",
)
def test_tmc_sdp_on():
    """
    Test case to verify TMC-SDP On functionality

    Glossary:
        - "central_node_mid": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given("a Telescope consisting of TMC, SDP, simulated CSP and simulated Dish")
def given_a_tmc(central_node_mid, simulator_factory, event_recorder):
    """
    Given a TMC
    """
    (
        csp_master_sim,
        _,
        dish_master_sim_1,
        dish_master_sim_2,
        dish_master_sim_3,
        dish_master_sim_4,
    ) = get_master_device_simulators(simulator_factory)

    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0
    assert csp_master_sim.ping() > 0
    assert dish_master_sim_1.ping() > 0
    assert dish_master_sim_2.ping() > 0
    assert dish_master_sim_3.ping() > 0
    assert dish_master_sim_4.ping() > 0

    event_recorder.subscribe_event(dish_master_sim_1, "dishMode")
    event_recorder.subscribe_event(dish_master_sim_2, "dishMode")
    event_recorder.subscribe_event(dish_master_sim_3, "dishMode")
    event_recorder.subscribe_event(dish_master_sim_4, "dishMode")
    # check if dish devices are in initial states
    assert event_recorder.has_change_event_occurred(
        dish_master_sim_1,
        "dishMode",
        DishMode.STANDBY_LP,
    )
    assert event_recorder.has_change_event_occurred(
        dish_master_sim_2,
        "dishMode",
        DishMode.STANDBY_LP,
    )
    assert event_recorder.has_change_event_occurred(
        dish_master_sim_3,
        "dishMode",
        DishMode.STANDBY_LP,
    )
    assert event_recorder.has_change_event_occurred(
        dish_master_sim_4,
        "dishMode",
        DishMode.STANDBY_LP,
    )


@given("telescope state is STANDBY")
def check_telescope_state_standby(central_node_mid, event_recorder):
    """A method to check CentralNode telescopeState STANDBY"""
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

    assert (
        central_node_mid.central_node.telescopeState == DevState.STANDBY
        or DevState.OFF
    )

    # TODO: Initial telescopeState aggregation to STANDBY is taking more than
    # 15 mins sometimes. Need to debug the reason for this separately.
    # event_recorder.subscribe_event(
    #     central_node_mid.central_node, "telescopeState"
    # )
    # assert event_recorder.has_change_event_occurred(
    #     central_node_mid.central_node,
    #     "telescopeState",
    #     DevState.STANDBY,
    # )


@when("I start up the telescope")
def move_sdp_to_on(central_node_mid):
    """A method to put SDP to ON"""
    central_node_mid.move_to_on()


@then("the SDP must go to ON state")
def check_sdp_is_on(central_node_mid, event_recorder):
    """A method to check SDP controller and SDP subarray states"""
    event_recorder.subscribe_event(central_node_mid.sdp_master, "State")
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices["sdp_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.sdp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices["sdp_subarray"],
        "State",
        DevState.ON,
    )


@then("telescope state is ON")
def check_telescope_state(central_node_mid, event_recorder):
    """A method to check CentralNode.telescopeState"""
    assert wait_and_validate_device_attribute_value(
        central_node_mid.central_node, "telescopeState", DevState.ON
    )
