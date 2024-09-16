"""
Test TMC-CSP AssignResources-ReleaseResources-AssignResources functionality
"""
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState
from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory


@pytest.mark.tmc_csp
@scenario(
    "../../features/tmc_csp/xtp_40072_succesive_assignresources.feature",
    "Validate second AssignResources command after "
    "first successful AssignResources and ReleaseResources are executed",
)
def test_tmc_csp_assign_release_assign_resources():
    """
    Test case to verify below sequence of events on TMC-CSP
     AssignResources,ReleaseResources,AssignResources
    """


@given(
    parsers.parse(
        "the TMC and CSP subarray {subarray_id} in the IDLE obsState"
    )
)
def telescope_is_in_idle_state(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
) -> None:
    """Method to move subarray into the IDLE ObsState."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["csp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")

    central_node_mid.move_to_on()
    time.sleep(2)

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    pytest.command_result = central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node, "obsState", ObsState.IDLE, lookahead=10
    )


@when(
    parsers.parse(
        "I release all resources assigned to TMC subarray {subarray_id}"
    )
)
def release_resources_of_subarray(
    central_node_mid: CentralNodeWrapperMid,
    command_input_factory: JsonFactory,
    subarray_id: str,
) -> None:
    """Method to release resources from subarray."""
    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    pytest.command_result = central_node_mid.invoke_release_resources(
        release_input_json
    )


@then(
    parsers.parse(
        "TMC and CSP subarray {subarray_id} must be in EMPTY obsState"
    )
)
def check_subarray_is_in_empty_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    subarray_id: str,
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """Method to check TMC Subarray abd CSP Subarray is in EMPTY obsstate"""
    check_subarray_instance(
        central_node_mid.subarray_devices.get("csp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )


@when(
    parsers.parse(
        "I invoked second AssignResources on TMC subarray {subarray_id}"
    )
)
def reassign_resources_on_subarray(
    central_node_mid: CentralNodeWrapperMid,
    subarray_id: str,
    command_input_factory: JsonFactory,
) -> None:
    """Execute second AssignResources command on TMC"""

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )

    pytest.command_result = central_node_mid.store_resources(assign_input_json)


@then(
    parsers.parse(
        "TMC and CSP subarray {subarray_id} transitions to IDLE obsState"
    )
)
def check_subarray_is_in_idle_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    subarray_id: str,
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """
    Check if TMC Subarray and CSP subarray has transitioned
    to ObsState IDLE
    """
    check_subarray_instance(
        subarray_node.subarray_devices.get("csp_subarray"), subarray_id
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )
