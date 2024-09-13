"""Test module for TMC-MCCS Scan functionality"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.skip(reason="MCCS v0.14.0 would solve the start_time key error")
@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-31001_scan_mccs.feature",
    "TMC executes a scan on MCCS subarray",
)
def test_scan_command():
    """BDD test scenario for verifying successful execution of the Scan command
    with TMC and MCCS devices for pairwise testing."""


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


@given("the obsState of TMC subarray is READY")
def subarray_in_ready_obsstate(
    central_node_low, subarray_node_low, command_input_factory, event_recorder
):
    """Checks if SubarrayNode's obsState attribute value is READY"""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node_low.mccs_subarray1, "obsState"
    )
    assert subarray_node_low.subarray_node.obsState == ObsState.EMPTY

    central_node_low.set_subarray_id(1)
    input_str = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.store_resources(input_str)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.IDLE
    )

    input_str = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    subarray_node_low.store_configuration_data(input_str)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.READY
    )


@when(
    parsers.parse(
        "I issue scan command with scan Id {scan_id} on subarray with the "
        + "{subarray_id} using tmc"
    )
)
def invoke_scan(
    subarray_node_low,
    command_input_factory,
    scan_id,
    subarray_id,
):
    """Invokes Scan command on TMC"""
    subarray_node_low.set_subarray_id(subarray_id)
    input_str = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    input_str = subarray_node_low.set_scan_id(int(scan_id), input_str)
    subarray_node_low.store_scan_data(input_str)


@then("the subarray obsState is transitioned to SCANNING")
def subarray_node_in_scanning(subarray_node_low, event_recorder):
    """Checks if Subarray Node's obsState attribute value is SCANNING"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.SCANNING
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.mccs_subarray1,
        "obsState",
        ObsState.SCANNING,
        lookahead=10,
    )


@then(
    "the MCCS subarray obsState is transitioned to READY after the scan "
    + "duration elapsed"
)
def mccs_subarray_in_ready(subarray_node_low, event_recorder):
    """Checks if MCCS Subarray's obsState attribute value is READY"""

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.mccs_subarray1,
        "obsState",
        ObsState.READY,
        lookahead=20,
    )


@then("the TMC subarray obsState is transitioned back to READY")
def subarray_node_in_ready(subarray_node_low, event_recorder):
    """Checks if Subarray Node's obsState attribute value is READY"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.READY
    )
