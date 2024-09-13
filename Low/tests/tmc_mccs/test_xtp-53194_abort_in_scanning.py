"""Test TMC-MCCS Abort functionality in Scanning obstate"""
import pytest
from pytest_bdd import given, scenario, then
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-53194_abort_in_scanning.feature",
    "Abort scanning MCCS using TMC",
)
def test_tmc_mccs_abort_in_scanning(central_node_low):
    """
    Test case to verify TMC-MCCS Abort functionality in SCANNING obsState
    """
    assert central_node_low.subarray_devices["mccs_subarray"].ping() > 0


@given("TMC and MCCS subarray are busy scanning")
def subarray_is_in_scanning_obsstate(
    central_node_low,
    event_recorder,
    command_input_factory,
    subarray_node_low,
):
    """ "A method to check if telescope in is SCANNING obsSstate."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    scan_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    event_recorder.subscribe_event(
        subarray_node_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    event_recorder.subscribe_event(
        subarray_node_low.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("mccs_subarray"), "obsState"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    subarray_node_low.force_change_of_obs_state(
        "SCANNING",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
        scan_input_json=scan_json,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.SCANNING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.SCANNING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.SCANNING,
        lookahead=20,
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


@then("the TMC subarray node obsState is transitioned to ABORTED")
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
