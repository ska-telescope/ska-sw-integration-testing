"""Test module for TMC-SDP Scan functionality"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState

from Mid.tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29384_scan.feature",
    "TMC executes a scan on SDP subarray",
)
def test_tmc_sdp_scan():
    """
    Test case to verify TMC-SDP Scan functionality

    Glossary:
        - "central_node_mid": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
        - "subarray_node": fixture for a TMC SubarrayNode under test
    """


@given(parsers.parse("the subarray {subarray_id} obsState is READY"))
def check_subarray_is_configured(
    central_node_mid,
    subarray_node,
    command_input_factory,
    event_recorder,
    subarray_id,
):
    """Method to check tmc and sdp subarrays are in READY obsstate"""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_json = json.loads(configure_input_json)
    configure_json["tmc"]["scan_duration"] = 10.0
    central_node_mid.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(central_node_mid.sdp_master, "State")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "State"
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")

    # check telescopeState is ON, and invoke TelescopeOn() command
    if central_node_mid.telescope_state != "ON":
        central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.sdp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices["sdp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )

    # execute set of commands and bring SubarrayNode to READY obsState
    subarray_node.force_change_of_obs_state(
        "READY",
        assign_input_json=assign_input_json,
        configure_input_json=json.dumps(configure_json),
    )

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


@when(
    parsers.parse(
        "I issue scan command with scan Id {scan_id} on subarray {subarray_id}"
    )
)
def invoke_scan(
    central_node_mid,
    subarray_node,
    command_input_factory,
    scan_id,
    subarray_id,
):
    """A method to invoke Scan command"""
    input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    scan_json = json.loads(input_json)
    scan_json["scan_id"] = scan_id

    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.execute_transition("Scan", argin=json.dumps(scan_json))


@then(
    parsers.parse(
        "the subarray {subarray_id} obsState transitions to SCANNING"
    )
)
def check_subarray_obs_State(
    central_node_mid, subarray_node, subarray_id, event_recorder
):
    """Check TMC and SDP subarray obsStates"""
    central_node_mid.set_subarray_id(subarray_id)
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


@then(
    parsers.parse(
        "the sdp subarray {subarray_id} obsState "
        + "transitions to READY after the scan duration elapsed"
    )
)
def check_sdp_subarray_in_ready(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstate"""
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} obsState transitions back to READY"
    )
)
def check_tmc_subarray_obs_state(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """A method to check TMC subarray obsstate"""
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
