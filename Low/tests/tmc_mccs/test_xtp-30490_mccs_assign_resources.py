"""Test module for TMC-mccs AssignResources functionality"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-30490_assign_resources_mccs.feature",
    "Assigning Resources to MCCS Subarray",
)
def test_assignresources_command():
    """BDD test scenario for verifying successful execution of
    the AssignResources command with TMC and mccs devices for pairwise
    testing."""


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
        subarray_node_low.subarray_devices["mccs_subarray"], "State"
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


@given("the obsState of subarray is EMPTY")
def subarray_in_empty_obsstate(subarray_node_low, event_recorder):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert subarray_node_low.subarray_node.obsState == ObsState.EMPTY


@when(
    parsers.parse(
        "I assign resources with the {subarray_id} to the subarray using TMC"
    )
)
def invoke_assignresources(
    central_node_low,
    command_input_factory,
    event_recorder,
    subarray_id,
):
    """Invokes AssignResources command on TMC"""
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    central_node_low.set_subarray_id(subarray_id)
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(input_json)
    event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@then("the MCCS subarray obsState must transition to IDLE")
def mccs_subarray_idle(subarray_node_low, event_recorder):
    """Checks if mccs Subarray's obsState attribute value is IDLE"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.IDLE,
    )


@then("the TMC subarray obsState is transitioned to IDLE")
def tmc_subarray_idle(subarray_node_low, event_recorder):
    """Checks if SubarrayNode's obsState attribute value is IDLE"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.IDLE
    )


@then(
    parsers.parse(
        "the correct resources {station_ids} are assigned to the MCCS subarray"
    )
)
def mccs_subarray_assignedresources(central_node_low, station_ids):
    """Method to check whether resources are assigned"""
    station_id = json.loads(
        central_node_low.subarray_devices["mccs_subarray"].assignedResources
    )["station_ids"]
    expected_station_ids = station_ids.replace('"', "").split(", ")
    assert station_id == expected_station_ids
