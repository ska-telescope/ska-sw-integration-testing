"""TMC Subarray handles the exception duplicate eb-id raised
by SDP subarray"""
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from tango import DevState
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    check_for_device_command_event,
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant import (
    tmc_sdp_subarray_leaf_node,
    tmc_subarraynode1,
)


@pytest.mark.skip(reason="This test case is not in the scope of this story")
@pytest.mark.tmc_sdp
@scenario(
    "../../mid/features/tmc_sdp/xtp-32451_sdp_exception.feature",
    "TMC Subarray handles the exception duplicate"
    " eb-id raised by SDP subarray",
)
def test_duplicate_ebid_exception_propagation(
    central_node_mid, subarray_node, event_recorder, simulator_factory
):
    """
    Test to verify TMC failure handling when duplicate EB ID is sent to
    SDP,command raises exception on SDP Subarray.
    After first AssignResources completes
    on SDP and CSP Subarrays, and it transitions to obsState IDLE.
    Whereas after next AssignResources SDP Subarray is  in obsState
    IDLE.Test makes sure that exception sent by SDP gets caught by TMC
    and gets propagated to central node and is available in long-running
    attribute of central node. As a handling Abort + Restart command sequence
    is executed on
    the Subarray to take it to the initial obsState Empty.
    Glossary:
    - "central_node_mid": fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    - "event_recorder": fixture for a MockTangoEventCallbackGroup
    for validating the subscribing and receiving events.
    - "simulator_factory": fixture for creating simulator devices for
    mid-Telescope respectively.
    """


@given(
    parsers.parse(
        "The TMC and SDP subarray {subarray_id} in the IDLE "
        "obsState using {input_json1}"
    )
)
def given_assign_resources_executed_on_tmc_subarray(
    central_node_mid,
    event_recorder,
    input_json1,
    command_input_factory,
    subarray_id,
    subarray_node,
):
    """
    AssignResources is executed with input_json1 successfully
    on SubarrayNode 1.
    """

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("csp_subarray"), "obsState"
    )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )

    central_node_mid.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    # Need to add a wait explicitly as the CentralNode does not receive
    # the longRunningCommandResult event on TelescopeOn command completion
    time.sleep(2)

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )

    assign_input_json = prepare_json_args_for_centralnode_commands(
        input_json1, command_input_factory
    )

    _, unique_id = central_node_mid.perform_action(
        "AssignResources", assign_input_json
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.IDLE, lookahead=15
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )


@when(
    parsers.parse(
        "TMC executes second AssignResources command with duplicate"
        " eb-id from {input_json1}"
    )
)
def reassign_resources_to_subarray(
    central_node_mid,
    event_recorder,
    input_json1,
    command_input_factory,
    shared_context,
):
    """
    TMC executes second AssignResources command with duplicate eb-id
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        input_json1, command_input_factory
    )
    pytest.result, pytest.unique_id = central_node_mid.perform_action(
        "AssignResources", assign_input_json
    )
    assert pytest.unique_id[0].endswith("AssignResources")
    assert pytest.result[0] == ResultCode.QUEUED


@then(
    parsers.parse(
        "SDP subarray {subarray_id} throws an exception and "
        "remain in IDLE obsState"
    )
)
def sdp_subarray_remains_in_idle(event_recorder, subarray_id, subarray_node):
    """
    Check if SDP remains in IDLE status
    """
    event_recorder.subscribe_event(
        subarray_node.sdp_subarray_leaf_node, "longRunningCommandResult"
    )
    check_subarray_instance(
        subarray_node.subarray_devices.get("sdp_subarray"), subarray_id
    )
    exception_message = (
        "Execution block eb-mvp01-20210623-00000 already exists"
    )
    assert check_for_device_command_event(
        subarray_node.sdp_subarray_leaf_node,
        "longRunningCommandResult",
        exception_message,
        event_recorder,
        "AssignResources",
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )


@then(
    parsers.parse("TMC subarray {subarray_id} remains in RESOURCING obsState")
)
def tmc_subarray_remains_in_resourcing(
    subarray_id, subarray_node, event_recorder
):
    """
    Check if TMC Subarray remains in RESOURCING status
    """
    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )


@then("exception is propagated to central node")
def check_exception_propagation_to_central_node(
    central_node_mid,
    event_recorder,
    shared_context,
):
    """
    Check exception propagation
    """
    exception_message = (
        f"Exception occurred on device: {tmc_subarraynode1}: "
        + "Exception occurred on the following devices: "
        + f"{tmc_sdp_subarray_leaf_node}: "
        + "Execution block eb-mvp01-20210623-00000 already exists\n"
    )

    event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(pytest.unique_id[0], exception_message),
    )


@when(parsers.parse("I issue the Abort command on TMC Subarray {subarray_id}"))
def send_command_abort(subarray_node, subarray_id):
    """
    Issue Abort command
    """
    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    subarray_node.subarray_node.Abort()


@then(
    parsers.parse(
        "the CSP, SDP and TMC Subarray {subarray_id} transitions to "
        + "obsState ABORTED"
    )
)
def subarray_transitions_to_aborted(
    subarray_node, event_recorder, subarray_id
):
    """
    Check if TMC subarray , CSP Subarray and real SDP Subarray
    move to abort.
    """

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@then(
    parsers.parse("I issue the Restart command on TMC Subarray {subarray_id}")
)
def send_command_restart(subarray_id, subarray_node):
    """
    Issue restart command.
    """
    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    subarray_node.restart_subarray()


@then(
    parsers.parse(
        "the CSP, SDP and TMC Subarray {subarray_id} transitions to "
        + "obsState EMPTY"
    )
)
def subarray_transitions_to_empty(subarray_node, subarray_id, event_recorder):
    """
    Check if CSP, SDP and TMC subarray  transitions to obsState EMPTY
    """

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )
    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@then(
    parsers.parse(
        "AssignResources command is executed and TMC and"
        " SDP subarray {subarray_id} transitions to IDLE"
    )
)
def assign_resources_executed_on_subarray(
    subarray_node,
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
):
    """
    Check assignResources command is executed successfully
    """

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )

    subarray_node.store_resources(assign_input_json)

    check_subarray_instance(
        subarray_node.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )

    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )

    _, unique_id = central_node_mid.invoke_release_resources(
        release_input_json
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )
