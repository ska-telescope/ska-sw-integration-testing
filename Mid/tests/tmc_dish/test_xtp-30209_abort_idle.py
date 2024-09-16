"""Test TMC-DISH Abort functionality in IDLE obsState"""

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.enum import DishMode


@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-30209_abort_idle.feature",
    "TMC executes Abort command on DISH.LMC when TMC Subarray is in IDLE",
)
def test_tmc_dish_abort_in_idle():
    """
    Test case to verify TMC-DISH Abort functionality in IDLE obsState
    """


@given(parsers.parse("TMC subarray {subarray_id}  is in IDLE obsState"))
def subarray_is_in_idle_obsState(
    central_node_mid,
    subarray_node,
    event_recorder,
    subarray_id,
    command_input_factory,
):
    """
    A method to check if telescope in is idle obsState.

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        subarray_id (str): Subarray ID
        command_input_factory: fixture for creating input required
        for command
    """
    central_node_mid.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices.get("csp_subarray"), "obsState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    pytest.command_result = central_node_mid.store_resources(assign_input_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )


@when("I issue the Abort command to the TMC subarray")
def abort_is_invoked(subarray_node):
    """
    This method invokes abort command on tmc subarray.

    Args:
        subarray_id (str): Subarray ID
    """
    pytest.command_result = subarray_node.abort_subarray()


@then(
    parsers.parse("the DishMaster {dish_ids} remains in dishmode STANDBY-FP")
)
def check_dish_mode(central_node_mid, dish_ids):
    """
    Method to check dishMode.

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        dish_ids (str): Comma-separated IDs of DISH components.
    """
    for dish_id in dish_ids.split(","):
        assert (
            central_node_mid.dish_master_dict[dish_id].dishMode
            == DishMode.STANDBY_FP
        )
        assert (
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode
            == DishMode.STANDBY_FP
        )


@then("the TMC subarray transitions to obsState ABORTED")
def tmc_subarray_is_in_aborted_obsState(subarray_node, event_recorder):
    """
    Method to check if TMC subarray is in ABORTED obsState

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
