"""Test TMC-CSP Sucessive AssignResources functionality"""
import ast
import json
import logging

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

LOGGER = logging.getLogger(__name__)
assigned_resources = []


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_40072_succesive_assignresources.feature",
    "Validate succesive AssignResources command",
)
def test_tmc_csp_sucessive_assignresources_functionality():
    """
    Test case to verify sucessive AssignResources on TMC-CSP
    """


@given(parsers.parse("TMC subarray {subarray_id} is in EMPTY ObsState"))
def subarray_is_in_empty_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    subarray_id: str,
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """Checks whether subarray is in empty obsstae or not."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["csp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")

    central_node_mid.move_to_on()

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when(
    parsers.parse(
        "I invoke First AssignResources on TMC subarray {subarray_id} with "
        + "{receptors1} on TMC subarray {subarray_id}"
    )
)
def invoke_first_assign_resources(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    subarray_id: str,
    command_input_factory: JsonFactory,
    receptors1: list,
) -> None:
    """
    Invokes first AssignResources command on TMC and check assigned resources
    """

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    assign_input_json = json.loads(input_json)
    resources = ast.literal_eval(receptors1)
    assign_input_json["dish"]["receptor_ids"] = resources
    assigned_resources.extend(resources)
    LOGGER.info(f"assignresources: {assign_input_json}")
    pytest.command_result = central_node_mid.store_resources(
        json.dumps(assign_input_json)
    )
    LOGGER.info(f"Pytest result:{pytest.command_result}")


@then(parsers.parse("CSP subarray {subarray_id} must be in IDLE ObsState"))
def check_csp_subarray_is_in_idle_obsstate(
    subarray_node: SubarrayNodeWrapper,
    event_recorder: EventRecorder,
    subarray_id: str,
) -> None:
    """Method to check CSP Subarray is in IDLE obsstate"""
    check_subarray_instance(
        subarray_node.subarray_devices.get("csp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )


@then(parsers.parse("TMC subarray {subarray_id} must be in IDLE obsState"))
def check_subarray_is_in_idle_obsstate(
    event_recorder: EventRecorder,
    subarray_id: str,
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """Method to check TMC Subarray is in IDLE obsstate"""
    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@then(parsers.parse("Resources are assigned to TMC subarray {subarray_id}"))
def check_assigned_resources(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    subarray_id: str,
    subarray_node: SubarrayNodeWrapper,
):
    """
    Method to check Resultcode of AssignResources is Ok and
    check resouurces assigned to TMC subarray
    """
    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_node, "assignedResources"
    )
    LOGGER.info(f"assigned resources: {assigned_resources}")
    LOGGER.info(f"type assigned resources: {type(assigned_resources)}")
    LOGGER.info(f"tuple>> {tuple(assigned_resources)}")

    LOGGER.info(
        f"assignedResources:: {subarray_node.subarray_node.assignedResources}"
    )
    LOGGER.info(
        f"type:: {type(subarray_node.subarray_node.assignedResources)}"
    )

    assert subarray_node.subarray_node.assignedResources == tuple(
        assigned_resources
    )


@when(
    parsers.parse(
        "I invoke Second AssignResources on TMC subarray {subarray_id} with "
        + "{receptors1} on TMC subarray {subarray_id}"
    )
)
def invoke_second_assign_Resources(
    central_node_mid: CentralNodeWrapperMid,
    subarray_id: str,
    command_input_factory: JsonFactory,
    receptors1: list,
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """
    Invokes second AssignResources command on TMC and check assigned resources
    """

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    assign_input_json = json.loads(input_json)
    resources = ast.literal_eval(receptors1)
    assign_input_json["dish"]["receptor_ids"] = resources
    assigned_resources.extend(resources)

    LOGGER.info(f"assignresources: {assign_input_json}")
    pytest.command_result = central_node_mid.store_resources(
        json.dumps(assign_input_json)
    )
