"""Test module for TMC-MCCS EndScan functionality"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.skip(reason="MCCS v0.14.0 would solve the start_time key error")
@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-31005_endscan_mccs.feature",
    "TMC executes a EndScan command on MCCS subarray",
)
def test_endscan_command():
    """BDD test scenario for verifying successful execution of the EndScan
    command with TMC and MCCS devices for pairwise testing."""


@given("the Telescope is in the ON state")
def given_a_telescope_in_on_state(
    central_node_low, subarray_node_low, event_recorder
):
    """Checks if CentralNode's telescopeState attribute value is on."""
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["mccs_subarray"].ping() > 0
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_low.mccs_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.mccs_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("the obsState of TMC subarray is Scanning")
def subarray_in_scanning_obsstate(
    central_node_low, subarray_node_low, command_input_factory, event_recorder
):
    """Checks if SubarrayNode's obsState attribute value is SCANNING"""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        subarray_node_low.mccs_subarray1, "obsState"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    assert subarray_node_low.subarray_node.obsState == ObsState.EMPTY

    central_node_low.set_subarray_id(1)
    input_str = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )

    _, unique_id = central_node_low.store_resources(input_str)

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.IDLE
    )
    event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )

    input_str = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    _, unique_id = subarray_node_low.store_configuration_data(input_str)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.READY
    )

    event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )

    input_str = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    input_str = subarray_node_low.set_scan_id(1, input_str)
    subarray_node_low.store_scan_data(input_str)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.SCANNING
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.mccs_subarray1,
        "obsState",
        ObsState.SCANNING,
        lookahead=10,
    )


@when(
    parsers.parse(
        "I issue the Endscan command to the TMC subarray with the "
        + "{subarray_id}"
    )
)
def invoke_endscan(
    subarray_node_low,
    subarray_id,
):
    """Invokes EndScan command on TMC"""
    subarray_node_low.set_subarray_id(subarray_id)
    subarray_node_low.remove_scan_data()


@then("the MCCS subarray is transitioned to ObsState READY")
def mccs_subarray_in_ready(subarray_node_low, event_recorder):
    """Checks if MCCS Subarray's obsState attribute value is READY"""

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.mccs_subarray1,
        "obsState",
        ObsState.READY,
        lookahead=20,
    )


@then("the TMC subarray is transitioned to ObsState READY")
def subarray_node_in_ready(subarray_node_low, event_recorder):
    """Checks if Subarray Node's obsState attribute value is READY"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.READY
    )
