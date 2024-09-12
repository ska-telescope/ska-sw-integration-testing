"""Test module to test delay functionality."""
import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    calculate_epoch_difference,
    generate_ska_epoch_tai_value,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    wait_for_delay_updates_stop_on_delay_model,
    wait_till_delay_values_are_populated,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory

LOGGER = logging.getLogger(__name__)


@pytest.mark.tmc_csp
@scenario(
    "../features/test_harness/xtp_35778_test_delay_model.feature",
    "Verify generated delay epoch values are less than delay advance time",
)
def test_tmc_csp_delay_functionality() -> None:
    """
    Test case to verify delay generates properly.
    """


@given(parsers.parse("TMC subarray {subarray_id} in ObsState IDLE"))
def move_subarray_node_to_idle_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to IDLE ObsState."""
    central_node_mid.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    # Create json for AssignResources commands with requested subarray_id
    assign_input = json.loads(assign_input_json)
    assign_input["subarray_id"] = int(subarray_id)
    central_node_mid.store_resources(json.dumps(assign_input))

    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when("I configure the TMC subarray")
def invoke_configure_command(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
) -> None:
    """
    Invokes Configure command and checks whether subarray is in ObsState READY
    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.store_configuration_data(configure_input_json)
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    "CSP Subarray Leaf Node starts generating delay values with proper epoch"
)
def check_if_delay_values_are_generating(
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """Check if delay values are generating."""
    ska_epoch_tai = generate_ska_epoch_tai_value()
    LOGGER.info(f"ska_epoch_tai : {ska_epoch_tai}")
    delay_json, delay_generated_time = wait_till_delay_values_are_populated(
        subarray_node.csp_subarray_leaf_node
    )
    LOGGER.info(f"delay_json: {delay_json}")
    LOGGER.info(f"delay_generated_time: {delay_generated_time}")
    epoch_difference = calculate_epoch_difference(
        delay_generated_time, ska_epoch_tai, delay_json
    )
    LOGGER.info(f"epoch_difference: {epoch_difference}")
    assert epoch_difference < 30


@when("I end the observation")
def invoke_end_command(
    subarray_node: SubarrayNodeWrapper, event_recorder: EventRecorder
) -> None:
    """Invoke End command checks whether subarray is in ObsState IDLE"""
    subarray_node.end_observation()
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )


@then("CSP Subarray Leaf Node stops generating delay values")
def check_if_delay_values_are_stop_generating(
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """Check if delay values are stop generating."""
    wait_for_delay_updates_stop_on_delay_model(
        subarray_node.csp_subarray_leaf_node
    )


@when("I re-configure the TMC subarray")
def reconfigure_the_subarray(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
) -> None:
    """
    Invokes Configure command and checks whether subarray is in ObsState READY
    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.store_configuration_data(configure_input_json)
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )
