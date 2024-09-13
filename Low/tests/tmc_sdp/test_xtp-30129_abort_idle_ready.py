"""Test TMC-SDP Abort functionality in IDLE obstate"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    update_eb_pb_ids,
)
from tests.resources.test_support.common_utils.result_code import ResultCode


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-30129_abort_idle_ready.feature",
    "Use TMC command Abort to trigger SDP subarray transition"
    + " from ObsStates IDLE and READY to ObsState ABORTED",
)
def test_tmc_sdp_abort_in_given_obsstate(central_node_low):
    """
    Test case to verify TMC-SDP Abort functionality in IDLE and READY obsState
    """
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0


@given(
    parsers.parse(
        "TMC subarray {subarray_id} and SDP subarray {subarray_id} in"
        + " ObsState {obsstate}"
    )
)
def subarray_is_in_given_obsstate(
    central_node_low,
    event_recorder,
    command_input_factory,
    obsstate,
    subarray_node_low,
    subarray_id,
):
    """A method to check if telescope in is given obsSstate."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.set_subarray_id(subarray_id)
    input_json = update_eb_pb_ids(assign_input_json)

    _, unique_id = central_node_low.store_resources(input_json)

    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )

    if obsstate == "READY":
        input_json = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        _, unique_id = subarray_node_low.execute_transition(
            "Configure", input_json
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_devices["sdp_subarray"],
            "obsState",
            ObsState.READY,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.READY,
        )
        event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (
                unique_id[0],
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )


# @when -> ../conftest.py


@then("the SDP subarray transitions to ObsState ABORTED")
def sdp_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Method to check SDP subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )


@then("the subarray transitions to ObsState ABORTED")
def tmc_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Method to check if TMC subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
