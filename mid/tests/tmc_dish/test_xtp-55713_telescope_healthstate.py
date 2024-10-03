"""Test case for verifying TMC TelescopeHealthState transition"""
import logging
import time

import pytest
from pytest_bdd import parsers, scenario, then, when
from ska_tango_base.control_model import HealthState
from tango.db import DbDevInfo


@pytest.mark.skip(
    reason="Dish manager doesn't transition from UNKNOWN to any other \
        state. SKB-443 raised for this bug"
)
@pytest.mark.tmc_dish
@scenario(
    "../../mid/features/tmc_dish/xtp-55713_telescope_healthstate.feature",
    "Verify CentralNode TelescopeHealthState",
)
def test_tmc_TMC_healthstate():
    """
    Test case verifying TMC TelescopeHealthState transition based on DISH-LMC
    subsystems HealthState
    """


@when(parsers.parse("the {device} health state changes to {health_state}"))
def set_simulator_devices_health_states(
    central_node_mid, event_recorder, health_state
):
    """Method to set the health state of specified simulator devices.

    Args:
        central_node_mid : A fixture for CentralNode tango device class
        event_recorder: A fixture for EventRecorder class_
        health_state (str): healthState value
    """
    # transitioning dishmanger (SKA001) healthstate to UNKNOWN by deleting
    # deleting spfrx device
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA001"], "healthState"
    )
    event_recorder.subscribe_event(
        central_node_mid.dish_leaf_node_dict["SKA001"], "healthState"
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeHealthState"
    )
    logging.info(
        "healthstate of dishmaster is before deleting spfrx  %s",
        central_node_mid.dish_master_dict["SKA001"].healthstate,
    )
    logging.info(
        "healthstate of dishln is before deleting spfrx %s",
        central_node_mid.dish_leaf_node_dict["SKA001"].healthstate,
    )
    logging.info(
        "telescopeHealthState of CN is before deleting spfrx %s",
        central_node_mid.central_node.telescopeHealthState,
    )
    central_node_mid.dish1_db.delete_device(central_node_mid.spfrx_fqdn)

    central_node_mid.spfrx1_admin_dev_proxy.RestartServer()

    logging.info(
        "healthstate of dishmaster is after deleting spfrx  %s",
        central_node_mid.dish_master_dict["SKA001"].healthstate,
    )
    logging.info(
        "healthstate of dishln is after deleting spfrx %s",
        central_node_mid.dish_leaf_node_dict["SKA001"].healthstate,
    )
    logging.info(
        "telescopeHealthState of CN is after deleting spfrx %s",
        central_node_mid.central_node.telescopeHealthState,
    )
    # Added a wait for the completion of spfrx1 device deletion from TANGO
    # database and the spfrx1 device restart
    # time.sleep(5)

    # asserting UNKNOWN healthstate for dishmaster and dishleafnode
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA001"], "healthState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA001"],
        "healthState",
        HealthState[health_state],
    ), f"Expected healthState to be \
        {HealthState[health_state]}"

    event_recorder.subscribe_event(
        central_node_mid.dish_leaf_node_dict["SKA001"], "healthState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_leaf_node_dict["SKA001"],
        "healthState",
        HealthState[health_state],
    ), f"Expected healthState to be \
        {HealthState[health_state]}"


@then(parsers.parse("the telescope health state is {telescope_health_state}"))
def check_telescope_health_state(
    central_node_mid, event_recorder, telescope_health_state
):
    """A method to check CentralNode.telescopeHealthState
    attribute change after aggregation.

    Args:
        central_node_mid : A fixture for CentralNode tango device class
        event_recorder: A fixture for EventRecorder class_
        telescope_health_state (str): telescopeHealthState value
    """
    # Subscribe to the health state event
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeHealthState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeHealthState",
        HealthState[telescope_health_state],
    ), f"Expected telescopeHealthState to be \
        {HealthState[telescope_health_state]}"

    # Add Dish device back to DB
    dev_info = DbDevInfo()
    dev_info.name = central_node_mid.spfrx_fqdn
    dev_info._class = central_node_mid.spfrx1_dev_class
    dev_info.server = central_node_mid.spfrx1_dev_server
    central_node_mid.dish1_db.add_device(dev_info)
    central_node_mid.spfrx1_admin_dev_proxy.RestartServer()

    logging.info("asserting health state at end")
    # Wait for the spfrx1 device to start and dish1
    # dishMode to be in proper state
    time.sleep(15)

    logging.info(
        "healthstate of dishmaster is after adding back spfrx %s",
        central_node_mid.dish_master_dict["SKA001"].healthstate,
    )
    logging.info(
        "healthstate of dishln is after adding back spfrx %s",
        central_node_mid.dish_leaf_node_dict["SKA001"].healthstate,
    )
    logging.info(
        "telescopeHealthState of CN is after adding back spfrx %s",
        central_node_mid.central_node.telescopeHealthState,
    )

    central_node_mid.move_to_off()
    assert central_node_mid.central_node.ping() > 0
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeHealthState",
        HealthState.OK,
    )
    # while True:
    #     # Check if the condition is met
    #     if event_recorder.has_change_event_occurred(
    #         central_node_mid.central_node,
    #         "telescopeHealthState",
    #         HealthState.OK,
    #     ):
    #         logging.info("telescopeHealthState is OK")
    #         break

    #     time.process_time()
