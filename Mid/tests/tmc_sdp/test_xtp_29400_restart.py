"""Test TMC-SDP Restart functionality"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp_29400_restart.feature",
    "TMC executes a Restart on SDP subarray when subarray completes abort",
)
def test_tmc_sdp_restart(central_node_mid):
    """
    Test case to verify TMC-SDP Restart functionality
    """


@given("the telescope is in ON state")
def telescope_is_in_on_state(central_node_mid, event_recorder):
    """ "A method to check if telescope in is on state."""
    central_node_mid.move_to_on()
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(
    parsers.parse("TMC and SDP subarray {subarray_id} is in ABORTED ObsState")
)
def telescope_is_in_aborted_obsstate(
    central_node_mid, event_recorder, command_input_factory, subarray_id
):
    "Method to move subarray in ABORTED Obsstate."
    central_node_mid.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    central_node_mid.store_resources(assign_input_json)
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    central_node_mid.subarray_abort()
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@when("I command it to Restart")
def invoke_restart(central_node_mid, subarray_id):
    """
    This method is to invoke Restart command on tmc subarray
    """
    central_node_mid.set_subarray_id(subarray_id)
    central_node_mid.subarray_restart()


@then(
    parsers.parse(
        "the SDP subarray {subarray_id} transitions to ObsState EMPTY"
    )
)
def sdp_subarray_is_in_empty_obsstate(
    central_node_mid, event_recorder, subarray_id
):
    """
    This method checks if the SDP subarray is in EMPTY obstate
    """
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState EMPTY"
    )
)
def tmc_subarray_is_in_empty_obsstate(
    central_node_mid, event_recorder, subarray_id
):
    """
    This method checks if TMC subarray is in EMPTY obsstate
    """
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
