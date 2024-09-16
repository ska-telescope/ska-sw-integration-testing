"""Test TMC-SDP Assign Release Assign functionality"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState
from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-32452_assign_release_assign_sequence.feature",
    "Validate second AssignResources command  after "
    "first successful AssignResources and ReleaseResources are executed",
)
def test_tmc_sdp_reassign_resources():
    """
    Test case to verify below sequence of events on TMC-SDP
     AssignResources,ReleaseResources,AssignResources
    """


@given(
    parsers.parse(
        "the TMC and SDP subarray {subarray_id} in the IDLE obsState"
    )
)
def telescope_is_in_idle_state(
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node,
):
    """Method to move subarray into the IDLE ObsState."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    central_node_mid.move_to_on()

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when(
    parsers.parse(
        "I release all resources assigned to TMC subarray {subarray_id}"
    )
)
def release_resources_of_subarray(
    central_node_mid, command_input_factory, subarray_id
):
    """Method to release resources from subarray."""
    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    central_node_mid.invoke_release_resources(release_input_json)


@then(
    parsers.parse(
        "TMC and SDP subarray {subarray_id} must be in EMPTY obsState"
    )
)
def check_components_in_empty_obsstate(
    central_node_mid, event_recorder, subarray_id, subarray_node
):
    """Method to check TMC Subarray SDP is in EMPTY obsstate"""
    check_subarray_instance(
        central_node_mid.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@then(
    parsers.parse(
        "AssignResources is executed with updated {input_json1} "
        "on TMC subarray {subarray_id}"
    )
)
def reassign_resources_on_subarray(
    central_node_mid, subarray_id, command_input_factory, input_json1
):
    """Execute second assign resource"""

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        input_json1, command_input_factory
    )

    central_node_mid.store_resources(assign_input_json)


@then(
    parsers.parse(
        "TMC and SDP subarray {subarray_id} transitions to IDLE obsState"
    )
)
def check_obsstate_on_subarray(
    central_node_mid, event_recorder, subarray_id, subarray_node
):
    """
    Check if TMC Subarray and SDP subarray has transitioned
    to required ObsState
    """
    check_subarray_instance(
        subarray_node.subarray_devices.get("sdp_subarray"), subarray_id
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
