"""Test module for TMC-SDP EndScan functionality"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29457_tmc_sdp_end_scan.feature",
    "TMC executes a EndScan command on SDP subarray",
)
def test_tmc_sdp_endscan():
    """
    Test case to verify TMC-SDP EndScan functionality

    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
        - "subarray_node_low": fixture for a TMC SubarrayNode under test
    """


# @given -> ../conftest.py


@given(parsers.parse("TMC subarray {subarray_id} is in Scanning ObsState"))
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
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")

    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "scanID"
    )
    # execute set of commands and bring SubarrayNode to SCANNING obsState
    subarray_node_low.force_change_of_obs_state(
        "SCANNING",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
    )
    # scanID set from scan_low json
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "scanID",
        int("1"),
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.SCANNING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )


@when(
    parsers.parse(
        "I issue the Endscan command to the TMC subarray {subarray_id}"
    )
)
def invoke_endscan(subarray_node_low, subarray_id):
    """A method to invoke EndScan command"""
    subarray_node_low.set_subarray_id(subarray_id)
    subarray_node_low.remove_scan_data()


@then(parsers.parse("the SDP subarray transitions to ObsState READY"))
def check_sdp_subarray_obs_State(subarray_node_low, event_recorder):
    """Check sdp subarray obsState READY"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState READY"
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
