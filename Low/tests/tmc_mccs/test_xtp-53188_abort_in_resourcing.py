"""Module for TMC-MCCS Abort command tests"""
import time

import pytest
from pytest_bdd import given, scenario, then
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-53188_abort_in_resourcing.feature",
    "Abort assigning using TMC",
)
def test_abort_in_resourcing(central_node_low):
    """BDD test scenario for verifying successful execution of
    the Abort command in Resourcing state with TMC and MCCS devices for
    pairwise testing."""
    assert central_node_low.subarray_devices["mccs_subarray"].ping() > 0


@given("TMC and MCCS subarray are busy assigning resources")
def subarray_busy_assigning(
    central_node_low, event_recorder, command_input_factory, subarray_node_low
):
    """Subarray busy Assigning"""
    # Turning the devices ON
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    # Invoking AssignResources command
    central_node_low.perform_action("AssignResources", input_json)
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")

    event_recorder.subscribe_event(
        central_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
    )
    event_recorder.subscribe_event(
        subarray_node_low.mccs_subarray_leaf_node, "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.RESOURCING,
    )
    # The sleep is added to allow Subarray Node time to update the device
    # obsStates before invoking the Abort command. Without sleep, Subarray Node
    # at times finds all devices in EMPTY and does not invoke Abort on them.
    time.sleep(1)


# @when -> ../conftest.py


@then("the MCCS subarray should go into an ABORTED obsstate")
def mccs_subarray_in_aborted_obs_state(subarray_node_low, event_recorder):
    """MCCS Subarray in ABORTED obsState."""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.ABORTING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
        ObsState.ABORTING,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.ABORTED,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
        lookahead=10,
    )


@then("the TMC subarray obsState is transitioned to ABORTED")
def subarray_in_aborted_obs_state(subarray_node_low, event_recorder):
    """Subarray Node in ABORTED obsState."""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
        ObsState.ABORTED,
        lookahead=10,
    )
