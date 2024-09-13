"""Test module for TMC-CSP AssignResources functionality"""

import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-29657_assign_resources_csp.feature",
    "Assign resources to CSP subarray using TMC",
)
def test_assignresources_command(central_node_low):
    """BDD test scenario for verifying successful execution of
    the AssignResources command with TMC and CSP devices for pairwise
    testing."""
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["csp_subarray"].ping() > 0


@given("the Telescope is in ON state")
def given_a_telescope_in_on_state(
    central_node_low, subarray_node_low, event_recorder
):
    """Checks if CentralNode's telescopeState attribute value is on."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_low.csp_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("TMC subarray {subarray_id} is in EMPTY ObsState"))
def subarray_in_empty_obsstate(
    central_node_low, subarray_node_low, event_recorder, subarray_id
):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    central_node_low.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert subarray_node_low.subarray_node.obsState == ObsState.EMPTY


@when("I assign resources to the subarray")
def invoke_assignresources(
    central_node_real_csp_low, command_input_factory, event_recorder
):
    """Invokes AssignResources command on TMC"""
    event_recorder.subscribe_event(
        central_node_real_csp_low.central_node, "longRunningCommandResult"
    )
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_real_csp_low.set_serial_number_of_cbf_processor()
    _, unique_id = central_node_real_csp_low.store_resources(input_json)
    event_recorder.has_change_event_occurred(
        central_node_real_csp_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@then("the CSP subarray must be in IDLE obsState")
def csp_subarray_idle(subarray_node_low, event_recorder):
    """Checks if Csp Subarray's obsState attribute value is IDLE"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("csp_subarray"), "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )


@then("the TMC subarray obsState is transitioned to IDLE")
def tmc_subarray_idle(subarray_node_low, event_recorder):
    """Checks if SubarrayNode's obsState attribute value is IDLE"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.IDLE
    )
