"""Test module for TMC-DISH testing"""

import logging
import os
import time

import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState
from tango.db import DbDevInfo
from tests.resources.test_harness.helpers import (
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.enum import DishMode


@pytest.mark.skip(
    reason="Issue after invocation of 2nd OFF command. OFF command is "
    + "incomplete on central node. Backlog item added for this test"
)
@pytest.mark.tmc_dish
@scenario(
    "../../features/tmc_dish/xtp-29077.feature",
    "Mid TMC Central Node robustness test with disappearing DishLMC",
)
def test_tmc_central_node_robustness():
    """
    Test case to verify TMC CentralNode Robustness
    """


LOGGER = logging.getLogger(__name__)
dish1_dev_name = os.getenv("DISH_NAME_1")


@given("a Telescope consisting of TMC, DISH, CSP and SDP")
def given_telescope(central_node_mid, simulator_factory):
    """
    Given a Telescope with TMC, Dish, CSP and SDP systems

    Args:
        - "event_recorder": fixture for EventRecorder class
    """
    csp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_MASTER_DEVICE
    )
    sdp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_MASTER_DEVICE
    )
    assert central_node_mid.central_node.ping() > 0
    assert csp_master_sim.ping() > 0
    assert sdp_master_sim.ping() > 0
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0


@given("dishes with Dish IDs 001, 036, 063, 100 are registered on the TangoDB")
def given_the_dishes_registered_in_tango_db(central_node_mid):
    """
    Given the dishes are registered in the TANGO Database
    """
    # proxy.dev_name() provides TANGO device name in small letters. Therefore
    # asserted to "mid-dish/dish-manager/ska001" instead of
    # "mid-dish/dish-manager/SKA001"
    assert (
        central_node_mid.dish_master_list[0].dev_name()
        == "mid-dish/dish-manager/ska001"
    )
    assert (
        central_node_mid.dish_master_list[1].dev_name()
        == "mid-dish/dish-manager/ska036"
    )
    assert (
        central_node_mid.dish_master_list[2].dev_name()
        == "mid-dish/dish-manager/ska063"
    )
    assert (
        central_node_mid.dish_master_list[3].dev_name()
        == "mid-dish/dish-manager/ska100"
    )


@given("dishleafnodes for dishes with IDs 001, 036, 063, 100 are available")
def check_if_dish_leaf_nodes_alive(central_node_mid):
    """A method to check if the dish leaf nodes are alive"""
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0


@given("command TelescopeOn was sent and received by the dishes")
def move_telescope_to_on_state(central_node_mid, event_recorder):
    """A method to put Telescope to ON state"""

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    # invoking TelescopeOn command
    central_node_mid.move_to_on()

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@when("communication with Dish ID 001 is lost")
def fail_to_connect_dish(central_node_mid):
    """A method to create the dish connection failure"""
    LOGGER.info(
        "dish1 admin device name is: %s", central_node_mid.dish1_admin_dev_name
    )
    LOGGER.info("dish1 device name is: %s", dish1_dev_name)

    check_dish1_info = central_node_mid.dish1_db.get_device_info(
        "mid-dish/dish-manager/SKA001"
    )
    LOGGER.info("dish1 device info is: %s", check_dish1_info)

    central_node_mid.dish1_db.delete_device(dish1_dev_name)
    central_node_mid.dish1_admin_dev_proxy.RestartServer()
    # Added a wait for the completion of dish device deletion from TANGO
    # database and the dish device restart
    time.sleep(5)


@when("command TelescopeOff is sent")
def invoke_telescope_off_command(central_node_mid, event_recorder):
    """A method to put Telescope to OFF state"""
    central_node_mid.move_to_off()

    for dish_id in ["SKA036", "SKA063", "SKA100"]:
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_LP,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_LP,
        )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.OFF,
    )
    LOGGER.info("The telescopeState is OFF")


@then("the Central Node is still running")
def check_if_central_node_running(central_node_mid):
    """Method to check if central node is still running"""
    assert central_node_mid.central_node.ping() > 0
    LOGGER.info("CentralNode is running")


@then("Dish with ID 001 comes back")
def connect_to_dish(central_node_mid, event_recorder):
    """Method to restablish the connection with the lost dish"""
    # Add Dish device back to DB
    dev_info = DbDevInfo()
    dev_info.name = dish1_dev_name
    dev_info._class = central_node_mid.dish1_dev_class
    dev_info.server = central_node_mid.dish1_dev_server
    central_node_mid.dish1_db.add_device(dev_info)

    central_node_mid.dish1_admin_dev_proxy.RestartServer()
    central_node_mid.dish1_leaf_admin_dev_proxy.RestartServer()

    # When device restart it will around 15 sec to up again
    # so wait for the dish1 dishmode attribute to be in ptoper state
    time.sleep(15)

    check_dish1_info = central_node_mid.dish1_db.get_device_info(
        "mid-dish/dish-manager/SKA001"
    )
    LOGGER.info("dish1 device info is: %s", check_dish1_info)
    check_dish1_leaf_info = central_node_mid.db.get_device_info(
        "ska_mid/tm_leaf_node/d0001"
    )
    LOGGER.info("dish1 leaf node device info is: %s", check_dish1_leaf_info)

    # Check if the dish 1 is initialised
    assert central_node_mid.dish_master_list[0].dishMode == DishMode.STANDBY_FP

    # Set kvalue on dish leaf node 1
    central_node_mid.dish_leaf_node_list[0].SetKValue(111)

    # Wait for DishLeafNode SetKValue command to be completed
    wait_and_validate_device_attribute_value(
        central_node_mid.central_node, "isDishVccConfigSet", True
    )
    wait_and_validate_device_attribute_value(
        central_node_mid.dish_leaf_node_list[0], "kValue", 111
    )

    assert central_node_mid.central_node.isDishVccConfigSet is True
    assert central_node_mid.dish_leaf_node_list[0].kValue == 111


@then("command TelescopeOff can be sent and received by the dish")
def move_telescope_to_off_state(central_node_mid):
    """A method to put Telescope to OFF state"""
    central_node_mid.move_to_off()


@then("the Central Node is still running")
def recheck_if_central_node_running(central_node_mid):
    """rechecks if central node device is running"""
    assert central_node_mid.central_node.ping() > 0


@then("the telescope is in OFF state")
def check_if_telescope_is_in_off_state(central_node_mid):
    """Verifies if telescope state is in off state"""
    for dish_id in ["SKA036", "SKA063", "SKA100"]:
        assert (
            central_node_mid.dish_master_dict[dish_id].dishMode
            == DishMode.STANDBY_LP
        )

    wait_and_validate_device_attribute_value(
        central_node_mid.dish_master_list[0],
        "dishMode",
        DishMode.STANDBY_LP,
    )
    assert central_node_mid.dish_master_list[0].dishMode == DishMode.STANDBY_LP

    wait_and_validate_device_attribute_value(
        central_node_mid.central_node,
        "telescopeState",
        DevState.OFF,
    )
    assert central_node_mid.central_node.telescopeState == DevState.OFF
