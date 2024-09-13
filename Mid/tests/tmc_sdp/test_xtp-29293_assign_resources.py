"""Test TMC-SDP AssignResources functionality"""
import ast

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from Mid.tests.resources.test_harness.constant import COMMAND_COMPLETED
from Mid.tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29293_assign_resources.feature",
    "Assign resources to SDP subarray using TMC",
)
def test_tmc_sdp_assign_resources(central_node_mid):
    """
    Test case to verify TMC-SDP AssignResources functionality
    """
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0


@given("the Telescope is in ON state")
def telescope_is_in_on_state(central_node_mid, event_recorder):
    """ "A method to move telescope into the ON state."""
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_mid.sdp_master, "State")
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices["sdp_subarray"], "State"
    )

    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.sdp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices["sdp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("the subarray {subarray_id} obsState is EMPTY"))
def subarray_is_in_empty_obsstate(
    event_recorder, central_node_mid, subarray_id
):
    """Method to check subarray is in EMPTY obstate"""
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when(
    parsers.parse(
        "I assign resources with the {receptors} to the subarray {subarray_id}"
    )
)
def assign_resources_to_subarray(
    central_node_mid, command_input_factory, subarray_id, stored_unique_id
):
    """Method to assign resources to subarray."""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    _, unique_id = central_node_mid.store_resources(assign_input_json)
    stored_unique_id.append(unique_id[0])


@then(parsers.parse("the sdp subarray {subarray_id} obsState is IDLE"))
def check_sdp_is_in_idle_obsstate(
    central_node_mid, event_recorder, subarray_id
):
    """Method to check SDP is in IDLE obsstate"""
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices.get("sdp_subarray"), "obsState"
    )
    check_subarray_instance(
        central_node_mid.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} obsState is transitioned to IDLE"
    )
)
def check_tmc_is_in_idle_obsstate(
    central_node_mid, event_recorder, subarray_id, stored_unique_id
):
    """Method to check TMC is in IDLE obsstate."""
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (stored_unique_id[0], COMMAND_COMPLETED),
        lookahead=5,
    )


@then(
    parsers.parse(
        "the correct resources {receptors} are assigned to sdp subarray "
        + "and TMC subarray"
    )
)
def check_assign_resources_to_tmc(central_node_mid, event_recorder, receptors):
    """Methos checks whether proper resources are assigned or not."""
    event_recorder.subscribe_event(
        central_node_mid.subarray_node, "assignedResources"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "assignedResources",
        ast.literal_eval(receptors),  # casts string coded tuple to tuple
    )
