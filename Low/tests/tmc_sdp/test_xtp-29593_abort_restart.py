"""Test TMC-SDP Restart functionality"""
import json

import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    update_eb_pb_ids,
)
from tests.resources.test_support.common_utils.result_code import ResultCode


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29593_restart_tmc_sdp.feature",
    "TMC executes a Restart on SDP subarray when subarray completes Abort",
)
def test_tmc_sdp_restart(central_node_low):
    """
    Test case to verify TMC-SDP Restart functionality
    """
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0


@given("the telescope is in ON state")
def telescope_is_in_on_state(central_node_low, event_recorder):
    """ "A method to check if telescope in is on state."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("TMC and SDP subarray are in ABORTED ObsState")
def telescope_is_in_aborted_obsstate(
    central_node_low, event_recorder, command_input_factory
):
    "Method to move subarray in ABORTED Obsstate."
    event_recorder.subscribe_event(
        central_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    input_json = update_eb_pb_ids(assign_input_json)
    _, unique_id = central_node_low.store_resources(input_json)

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
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

    central_node_low.subarray_abort()
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@when("I command it to Restart")
def restart_is_invoked(central_node_low):
    """
    This method is to invoke Restart command on tmc subarray
    """
    central_node_low.subarray_restart()


@then("the SDP subarray transitions to ObsState EMPTY")
def sdp_subarray_is_in_empty_obsstate(central_node_low, event_recorder):
    """
    This method checks if the SDP subarray is in EMPTY obstate
    """
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )


@then("the TMC subarray transitions to ObsState EMPTY")
def tmc_subarray_is_in_empty_obsstate(central_node_low, event_recorder):
    """
    This method checks if TMC subarray is in EMPTY obsstate
    """
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
