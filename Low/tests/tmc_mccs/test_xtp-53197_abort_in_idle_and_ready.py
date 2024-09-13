"""Test TMC-MCCS Abort functionality in IDLE-READY obstate"""
import pytest
from pytest_bdd import given, parsers, scenario, then
from ska_control_model import ObsState, ResultCode
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-53197_abort_idle_ready.feature",
    "Abort resourced MCCS and TMC subarray",
)
def test_tmc_mccs_abort_in_given_obsstate(central_node_low):
    """
    Test case to verify TMC-MCCS Abort functionality in IDLE and READY obsState
    """
    assert central_node_low.subarray_devices["mccs_subarray"].ping() > 0


@given(parsers.parse("TMC subarray in obsState {obsstate}"))
def subarray_is_in_given_obsstate(
    central_node_low,
    event_recorder,
    command_input_factory,
    obsstate,
    subarray_node_low,
):
    """A method to check if telescope in is given obsSstate."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)

    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("mccs_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(ResultCode.OK.value)),
    )

    if obsstate == "READY":

        input_json = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        _, unique_id = subarray_node_low.execute_transition(
            "Configure", input_json
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_devices["mccs_subarray"],
            "obsState",
            ObsState.READY,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.READY,
        )
        event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (unique_id[0], str(ResultCode.OK.value)),
        )


# @when -> ../conftest.py


@then("the MCCS subarray should go into an aborted obsstate")
def mccs_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Method to check MCCS subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
        ObsState.ABORTING,
        lookahead=20,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
        ObsState.ABORTED,
        lookahead=20,
    )


@then("the TMC subarray obsState is transitioned to ABORTED")
def tmc_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Method to check if TMC subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
        lookahead=20,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
        lookahead=20,
    )
