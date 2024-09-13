"""Test module for TMC-SDP Scan functionality"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29456_tmc_sdp_scan.feature",
    "TMC executes a scan on SDP subarray",
)
def test_tmc_sdp_scan():
    """
    Test case to verify TMC-SDP Scan functionality

    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
        - "subarray_node_low": fixture for a TMC SubarrayNode under test
    """


@given(parsers.parse("the subarray {subarray_id} obsState is READY"))
def check_subarray_is_configured(
    central_node_low,
    subarray_node_low,
    command_input_factory,
    event_recorder,
    subarray_id,
):
    """Method to check tmc and sdp subarray is in READY obstate"""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    subarray_node_low.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "State"
    )
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "scanID"
    )
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")

    # check telescopeState is ON, and fire TelescopeOn() command
    if central_node_low.telescope_state != "ON":
        central_node_low.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["sdp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )

    # execute set of commands and bring SubarrayNode to READY obsState
    subarray_node_low.force_change_of_obs_state(
        "READY",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
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


@when(
    parsers.parse(
        "I issue scan command with scan Id {scan_id} on subarray {subarray_id}"
    )
)
def invoke_scan(
    subarray_node_low,
    command_input_factory,
    scan_id,
    subarray_id,
    event_recorder,
):
    """A method to invoke Scan command"""
    input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    scan_json = json.loads(input_json)
    scan_json["scan_id"] = int(scan_id)

    subarray_node_low.set_subarray_id(subarray_id)
    subarray_node_low.store_scan_data(json.dumps(scan_json))

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "scanID",
        int(scan_id),
    )


@then(
    parsers.parse(
        "the subarray {subarray_id} obsState transitions to SCANNING"
    )
)
def check_subarray_obs_State(subarray_node_low, subarray_id, event_recorder):
    """Check TMC and SDP subarray obsState Scanning"""

    subarray_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
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
    subarray_node_low, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstate"""
    subarray_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} obsState transitions back to READY"
    )
)
def check_tmc_subarray_obs_state(
    subarray_node_low, event_recorder, subarray_id
):
    """A method to check TMC subarray obsstate"""
    subarray_node_low.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
