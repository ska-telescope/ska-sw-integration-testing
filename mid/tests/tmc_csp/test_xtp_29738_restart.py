"""Test TMC-CSP Restart functionality"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_csp
@scenario(
    "../../features/tmc_csp/xtp_29738_restart.feature",
    "TMC executes a Restart on CSP subarray when subarray completes abort",
)
def test_tmc_csp_restart(central_node_mid):
    """
    Test case to verify TMC-CSP Restart functionality
    """


@given(
    parsers.parse("TMC and CSP subarray {subarray_id} is in ObsState ABORTED")
)
def subarray_is_in_aborted_obsstate(
    central_node_mid,
    subarray_node,
    event_recorder,
    command_input_factory,
    subarray_id,
):
    """Method to move subarray in ABORTED Obsstate."""
    central_node_mid.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    central_node_mid.store_resources(assign_input_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    subarray_node.abort_subarray()
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@when("I command it to Restart")
def invoke_restart(subarray_node, subarray_id):
    """
    This method is to invoke Restart command on TMC subarray
    """
    subarray_node.set_subarray_id(subarray_id)
    subarray_node.restart_subarray()


@then(
    parsers.parse(
        "the CSP subarray {subarray_id} transitions to ObsState EMPTY"
    )
)
def csp_subarray_is_in_empty_obsstate(
    subarray_node, event_recorder, subarray_id
):
    """
    This method checks if the CSP subarray is in EMPTY obstate
    """
    subarray_node.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState EMPTY"
    )
)
def tmc_subarray_is_in_empty_obsstate(
    subarray_node, event_recorder, subarray_id
):
    """
    This method checks if TMC subarray is in EMPTY obsstate
    """
    subarray_node.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
