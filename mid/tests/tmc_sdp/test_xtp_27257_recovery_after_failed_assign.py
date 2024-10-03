"""Test TMC-SDP Recovery after failed Assign functionality"""
import time

import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from tango import DevState
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.skip(reason="Duplicate scenario")
@pytest.mark.tmc_sdp
@scenario(
    "../../mid/features/tmc_sdp/xtp_27257_recovery_after_failed_assign.feature",
    "Fix bug SKB-185 in TMC",
)
def test_tmc_sdp_recovery_after_failed_assign_resources():
    """
    Test case to verify TMC-SDP Recovery after failed Assign functionality
    """


@given("an TMC")
def telescope_with_resources_assigned(
    central_node_mid, event_recorder, command_input_factory
):
    """A telescope with resouces assigned, and released from it."""
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    central_node_mid.set_subarray_id(1)
    central_node_mid.move_to_on()

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
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

    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )

    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )
    _, unique_id = central_node_mid.invoke_release_resources(
        release_input_json
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )


@given("the resources are re-assigned to tmc with duplicate eb-id")
def reallocation_of_resources_with_same_eb_id(
    central_node_mid, command_input_factory
):
    """Allocating the same resources to TMC."""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    central_node_mid.perform_action("AssignResources", assign_input_json)


@given("the sdp subarray throws an error and remains in obsState EMPTY")
def sdp_subarray_in_empty_obs_state(central_node_mid, event_recorder):
    """The SDP subarray remains in EMPTY ObsState"""
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices.get("sdp_subarray"), "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )


@given("the resources are assigned to csp subarray")
def resources_assigned_to_csp(central_node_mid, event_recorder):
    """CSP Subarray in IDLE state"""
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices.get("csp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(
        central_node_mid.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.IDLE,
    )


@given("the subarray node is stuck in obsState RESOURCING")
def subarray_node_stuck_in_resourcing(central_node_mid, event_recorder):
    """Subarray Node stuck in RESOURCING state"""
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )


@when("I release the resources from the csp subarray")
def releasing_csp_subarray_resources(central_node_mid):
    """Invoking ReleaseResources on CSPSLN"""
    central_node_mid.csp_subarray_leaf_node.ReleaseAllResources()


@then("the csp subarray changes its obsState to EMPTY")
def csp_subarray_in_empty_obs_state(central_node_mid, event_recorder):
    """CSP Subarray in EMPTY state"""
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )


@then("the subarray node changes its obsState back to EMPTY")
def subarray_node_in_empty_obs_state(central_node_mid, event_recorder):
    """Subarray Node in EMPTY state"""
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
