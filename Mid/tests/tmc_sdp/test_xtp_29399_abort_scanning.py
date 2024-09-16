"""Test TMC-SDP Abort functionality in Scanning obstate"""
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp_29399_abort_scanning.feature",
    "Abort scanning SDP using TMC",
)
def test_tmc_sdp_abort_in_scanning():
    """
    Test case to verify TMC-SDP Abort functionality in SCANNING obsState
    """


@given(
    parsers.parse("TMC subarray {subarray_id} and SDP subarray busy scanning")
)
def subarray_is_in_scanning_obsstate(
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_node,
    subarray_id,
):
    """ "A method to check if telescope in is SCANNING obsSstate."""
    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.set_subarray_id(subarray_id)
    central_node_mid.move_to_on()
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    # Need to add a wait explicitly as the CentralNode does not receive
    # the longRunningCommandResult event on TelescopeOn command completion
    time.sleep(2)

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    central_node_mid.store_resources(assign_input_json)
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
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
    configure_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.store_configuration_data(configure_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
    scan_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    subarray_node.store_scan_data(scan_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.SCANNING,
    )


@when("I command it to Abort")
def invoke_abort(subarray_node):
    """
    This method invokes abort command on tmc subarray
    """
    subarray_node.abort_subarray()


@then(
    parsers.parse(
        "the SDP subarray {subarray_id} transitions to ObsState ABORTED"
    )
)
def sdp_subarray_is_in_aborted_obsstate(
    subarray_node, event_recorder, subarray_id
):
    """
    Method to check SDP subarray is in ABORTED obsstate
    """
    subarray_node.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState ABORTED"
    )
)
def tmc_subarray_is_in_aborted_obsstate(
    subarray_node, event_recorder, subarray_id
):
    """
    Method to check if TMC subarray is in ABORTED obsstate
    """
    subarray_node.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
