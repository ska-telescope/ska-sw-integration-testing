"""Test TMC-SDP Abort functionality in RESOURCING obsState"""
import json
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState
from tests.resources.test_harness.helpers import (
    generate_eb_pb_ids,
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../../features/tmc_sdp/xtp_29396_abort_resourcing.feature",
    "Abort assigning using TMC",
)
def test_tmc_sdp_abort_in_resourcing():
    """
    Test case to verify TMC-SDP Abort functionality in RESOURCING obsState
    """


@given(
    parsers.parse(
        "TMC subarray {subarray_id} and SDP subarray "
        + "{subarray_id} busy in assigning resources"
    )
)
def telescope_is_in_resourcing_obsstate(
    central_node_mid, event_recorder, command_input_factory, subarray_id
):
    """A method to check if telescope in is resourcing obsSstate."""
    central_node_mid.set_subarray_id(subarray_id)
    central_node_mid.move_to_on()
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_mid.sdp_master, "State")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.sdp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=15,
    )
    # Need to add a wait explicitly as the CentralNode does not receive
    # the longRunningCommandResult event on TelescopeOn command completion
    time.sleep(2)

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    input_json = json.loads(assign_input_json)
    generate_eb_pb_ids(input_json)
    central_node_mid.perform_action("AssignResources", json.dumps(input_json))

    event_recorder.subscribe_event(
        central_node_mid.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.RESOURCING,
    )


@when("I command it to Abort")
def invoke_abort(central_node_mid):
    """
    This method invokes abort command on tmc subarray.
    """

    time.sleep(0.5)
    central_node_mid.subarray_abort()


@then(
    parsers.parse(
        "the SDP subarray {subarray_id} transitions to ObsState ABORTED"
    )
)
def sdp_subarray_is_in_aborted_obsstate(
    central_node_mid, event_recorder, subarray_id
):
    """
    Method to check SDP subarray is in ABORTED obsstate
    """
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState ABORTED"
    )
)
def tmc_subarray_is_in_aborted_obsstate(
    central_node_mid, event_recorder, subarray_id
):
    """
    Method to check if TMC subarray is in ABORTED obsstate
    """
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
