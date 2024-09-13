"""Test module for TMC- ReleaseResources functionality"""

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
    "../features/tmc_mccs/xtp-30608_release_resources_mccs.feature",
    "Release resources from MCCS Subarray using TMC",
)
def test_releaseresources_command():
    """BDD test scenario for verifying successful execution of
    the Release Resources command with TMC and MCCS devices for pairwise
    testing."""


@given("the Telescope is in ON state")
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


@given(parsers.parse("TMC subarray {subarray_id} in the IDLE obsState"))
def subarray_in_idle_obsstate(
    central_node_low,
    event_recorder,
    subarray_id,
    subarray_node_low,
    command_input_factory,
):
    """Checks if SubarrayNode's obsState attribute value is IDLE"""
    central_node_low.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )

    event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@when("I release the assigned resources for subarray using TMC")
def invoke_releaseresources(
    central_node_low, command_input_factory, event_recorder
):
    """Invokes ReleaseResources command on TMC"""
    release_input = prepare_json_args_for_centralnode_commands(
        "release_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.invoke_release_resources(release_input)
    event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


@then("the MCCS subarray must be in EMPTY obsState")
def mccs_subarray_empty(subarray_node_low, event_recorder):
    """Checks if Csp Subarray's obsState attribute value is EMPTY"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.EMPTY,
    )


@then("TMC subarray obsState transitions to EMPTY")
def tmc_subarray_empty(subarray_node_low, event_recorder):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.EMPTY
    )
