"""
Test TMC-SDP Assign Resources functionality.
"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode

from tests.resources.test_harness.helpers import update_eb_pb_ids
from tests.resources.test_harness.utils.common_utils import (
    update_receptors_in_assign_json,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29292_assign_resources_to_sdp_subarray.feature",
    """Assign resources to SDP subarray using TMC""",
)
def test_tmc_sdp_assign_resources(central_node_low):
    """
    Test case to verify TMC-SDP Assignresources() functionality
    """
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0
    assert central_node_low.are_sdp_components_online()


# @given -> ../conftest.py


@given(parsers.parse("the subarray {subarray_id} obsState is EMPTY"))
def subarray_is_in_empty_obsstate(
    event_recorder, central_node_low, subarray_id
):
    """Verify that the specified subarray is in the EMPTY observation state.

    Args:
        event_recorder (EventRecorder): An instance of the EventRecorder class
          for recording events.
        central_node_low (CentralNodeLow): An instance of the CentralNodeLow
          class representing the central node.
        subarray_id (int): The identifier of the subarray to be checked.

    Raises:
        AssertionError: If the specified subarray fails to transition to the
        EMPTY observation state or if the expected event is not recorded.
    """
    central_node_low.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert central_node_low.subarray_node.obsState == ObsState.EMPTY


@when(
    parsers.parse(
        "I assign resources with the {receptors} to the subarray {subarray_id}"
    )
)
def assign_resources_to_subarray(
    central_node_low, command_input_factory, event_recorder, receptors
):
    """Method to assign resources to subarray."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )

    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    receptors = receptors.replace('"', "").split(", ")
    input_json = update_receptors_in_assign_json(input_json, receptors)
    input_json = update_eb_pb_ids(input_json)
    _, unique_id = central_node_low.store_resources(input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


@then(parsers.parse("the SDP subarray {subarray_id} must be in IDLE obsState"))
def check_sdp_is_in_idle_obsstate(central_node_low, event_recorder):
    """Method to check SDP is in IDLE obsstate"""
    event_recorder.subscribe_event(
        central_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} obsState is transitioned to IDLE"
    )
)
def check_tmc_is_in_idle_obsstate(central_node_low, event_recorder):
    """Method to check TMC is is in IDLE obsstate."""
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@then(
    parsers.parse(
        "the correct resources {receptors} are assigned to the SDP subarray "
        + "and the TMC subarray"
    )
)
def check_assign_resources_to_tmc(central_node_low, receptors):
    """Method to check whether resources are assigned"""
    receptor = json.loads(
        central_node_low.subarray_devices["sdp_subarray"].Resources
    )["receptors"]
    receptors = receptors.replace('"', "").split(", ")
    assert receptor == receptors
