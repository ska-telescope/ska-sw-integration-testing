"""Test TMC-SDP ReleaseResources functionality"""
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_sdp
@scenario(
    "../../mid/features/tmc_sdp/xtp-29294_release_resources.feature",
    "Release resources from SDP Subarray using TMC",
)
def test_tmc_sdp_release_resources():
    """
    Test case to verify TMC-SDP ReleaseResources functionality
    """


@given("a TMC and SDP")
def given_a_tmc(central_node_mid):
    """A method to define TMC and SDP."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0


@given(parsers.parse("a subarray {subarray_id} in the IDLE obsState"))
def telescope_is_in_idle_state(
    central_node_mid, event_recorder, command_input_factory, subarray_id
):
    """ "A method to move subarray into the IDLE ObsState."""
    central_node_mid.move_to_on()
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    # Need to add a wait explicitly as the CentralNode does not receive
    # the longRunningCommandResult event on TelescopeOn command completion
    time.sleep(2)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    _, unique_id = central_node_mid.store_resources(assign_input_json)
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=5,
    )


@when(
    parsers.parse("I release all resources assigned to subarray {subarray_id}")
)
def release_resources_to_subarray(
    central_node_mid, command_input_factory, subarray_id
):
    """Method to release resources from subarray."""
    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    central_node_mid.invoke_release_resources(release_input_json)


@then(
    parsers.parse("the SDP subarray {subarray_id} must be in EMPTY obsState")
)
def check_sdp_is_in_empty_obsstate(
    central_node_mid, event_recorder, subarray_id
):
    """Method to check SDP is in EMPTY obsstate"""
    check_subarray_instance(
        central_node_mid.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )


@then(
    parsers.parse("TMC subarray {subarray_id} obsState transitions to EMPTY")
)
def check_tmc_is_in_empty_obsstate(
    central_node_mid, event_recorder, subarray_id
):
    """Method to check TMC is in EMPTY obsstate."""
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
