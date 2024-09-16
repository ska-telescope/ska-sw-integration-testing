"""Test module for TMC-CSP AssignResources functionality"""
import ast
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29259_assign.feature",
    "Assign resources to CSP subarray using TMC",
)
def test_assignresources_command():
    """BDD test scenario for verifying successful execution of
    the AssignResources command with TMC and CSP devices for pairwise
    testing."""


@given(parsers.parse("TMC subarray {subarray_id} is in EMPTY ObsState"))
def subarray_in_empty_obsstate(central_node_mid, event_recorder, subarray_id):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node, "obsState", ObsState.EMPTY
    )


@when(
    parsers.parse(
        "I assign resources with {receptors} to TMC subarray {subarray_id}"
    )
)
def invoke_assignresources(
    central_node_mid,
    subarray_id,
    receptors,
    command_input_factory,
):
    """Invokes AssignResources command on TMC"""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    assign_input = json.loads(assign_input_json)
    assign_input["subarray_id"] = int(subarray_id)
    pytest.command_result = central_node_mid.perform_action(
        "AssignResources", json.dumps(assign_input)
    )


@then(
    parsers.parse("CSP subarray {subarray_id} transitioned to ObsState IDLE")
)
def csp_subarray_idle(central_node_mid, event_recorder, subarray_id):
    """Checks if Csp Subarray's obsState attribute value is IDLE"""
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )


@then(
    parsers.parse("TMC subarray {subarray_id} transitioned to ObsState IDLE")
)
def tmc_subarray_idle(central_node_mid, event_recorder, subarray_id):
    """Checks if SubarrayNode's obsState attribute value is IDLE"""
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node, "obsState", ObsState.IDLE
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )


@then(
    parsers.parse(
        "correct resources {receptors} are assigned to"
        + " TMC subarray {subarray_id}"
    )
)
def resources_assigned_to_subarray(
    central_node_mid, event_recorder, receptors, subarray_id
):
    """Checks if correct ressources are assigned to Subarray"""
    central_node_mid.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(
        central_node_mid.subarray_node, "assignedResources"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "assignedResources",
        ast.literal_eval(receptors),  # casts string coded tuple to tuple
    )
