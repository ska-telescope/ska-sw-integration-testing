"""Test module to verify SKB-413"""
import ast
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_telmodel.schema import validate as telmodel_validate
from tests.conftest import MID_DELAY_JSON, MID_DELAYMODEL_VERSION
from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import (
    JsonFactory,
    wait_added_for_skb372,
)


@pytest.mark.skip(reason="This test case is not in the scope of this story")
@pytest.mark.tmc_csp
@scenario(
    "../../features/tmc_csp/xtp_58590_verify_skb_413.feature",
    "Verify SKB-413 with TMC as entrypoint",
)
def test_verify_skb_413() -> None:
    """
    Test case to verify SKB-413: TMC Delay Model code
    pointing to correct assigned dishes
    """


@given(
    parsers.parse(
        "TMC SubarrayNode is in ObsState IDLE "
        + "with assigned receptors {receptors}"
    )
)
def move_subarray_node_to_idle_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    receptors: str,
) -> None:
    """Move TMC Subarray to IDLE obsstate."""
    assign_input_str = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assign_input_json = json.loads(assign_input_str)
    # Converting string to list
    receptors_ids_list = ast.literal_eval(receptors)
    assign_input_json["dish"]["receptor_ids"] = receptors_ids_list
    pytest.command_result = central_node_mid.store_resources(
        json.dumps(assign_input_json)
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
        lookahead=20,
    )
    wait_added_for_skb372()


@when("I issue the Configure command to the TMC SubarrayNode")
def invoke_configure_command(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder,
) -> None:
    """Invoke Configure command."""
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    pytest.command_result = subarray_node.execute_transition(
        "Configure", argin=configure_input_json
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )


@then(
    parsers.parse(
        "CspSubarrayLeafNode delay model points to "
        + "correct assigned receptors {receptors}"
    )
)
def check_delay_model(
    subarray_node: SubarrayNodeWrapper, receptors: str
) -> None:
    """Ensures the delayModel is pointing to assiged receptors"""
    generated_delay_model = (
        subarray_node.csp_subarray_leaf_node.read_attribute("delayModel").value
    )
    generated_delay_model_json = json.loads(generated_delay_model)
    assert generated_delay_model_json != json.dumps(MID_DELAY_JSON)
    telmodel_validate(
        version=MID_DELAYMODEL_VERSION,
        config=generated_delay_model_json,
        strictness=2,
    )
    receptors_ids_list = ast.literal_eval(receptors)
    for receptor_delay in generated_delay_model_json["receptor_delays"]:
        assert receptor_delay["receptor"] in receptors_ids_list


@then("the TMC subarray transitions to ObsState READY")
def check_tmc_subarray_in_ready_obsstate(
    subarray_node: SubarrayNodeWrapper, event_recorder: EventRecorder
) -> None:
    """Ensure TMC Subarray is moved to READY obsstate"""

    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=20,
    )
