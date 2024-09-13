"""Test module to test TMC-MCCS End functionality."""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    set_receive_address,
)
from tests.resources.test_support.common_utils.result_code import ResultCode


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-31010_end_command.feature",
    "End configure from MCCS Subarray",
)
def test_end_command():
    """
    Test case to verify TMC-MCCS observation End functionality
    """


@given("the Telescope is in the ON state")
def check_telescope_is_in_on_state(central_node_low, event_recorder) -> None:
    """Ensure telescope is in ON state."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=10,
    )


@given(parsers.parse("obsState of subarray {subarray_id} is READY"))
def move_subarray_node_to_ready_obsstate(
    central_node_low,
    subarray_node_low,
    event_recorder,
    command_input_factory,
) -> None:
    """Move TMC Subarray to READY obsstate."""
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("mccs_subarray"), "obsState"
    )
    set_receive_address(central_node_low)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )

    _, unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=10,
    )
    event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


@when(
    parsers.parse(
        "I issue the End command to the TMC subarray with the "
        + "{subarray_id}"
    )
)
def invoke_end_command(subarray_node_low, event_recorder, subarray_id) -> None:
    """Invoke End command."""
    subarray_node_low.set_subarray_id(subarray_id)
    _, unique_id = subarray_node_low.execute_transition("End")
    event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@then("the MCCS subarray is transitioned to IDLE obsState")
def check_if_mccs_subarray_moved_to_idle_obsstate(
    subarray_node_low, event_recorder
):
    """Ensure Mccs subarray is moved to IDLE obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.mccs_subarray1,
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )


@then("TMC subarray is transitioned to IDLE obsState")
def check_if_tmc_subarray_moved_to_idle_obsstate(
    subarray_node_low, event_recorder: EventRecorder
) -> None:
    """Ensure TMC Subarray is moved to IDLE obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )
