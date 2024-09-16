"""Test module for TMC-CSP Scan functionality"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory


@pytest.mark.tmc_csp
@scenario(
    "tmc_csp/xtp_29387_scan.feature",
    "TMC executes a Scan command on CSP subarray.",
)
def test_scan_command():
    """BDD test scenario for verifying successful execution of
    the Scan command with TMC and CSP devices for pairwise
    testing."""


@given(parsers.parse("TMC subarray {subarray_id} is in READY ObsState"))
def subarray_in_ready_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_node: SubarrayNodeWrapper,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to READY obsstate."""
    central_node_mid.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.force_change_of_obs_state(
        "READY",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=20,
    )


@when(
    parsers.parse("I issue the scan command to the TMC subarray {subarray_id}")
)
def invoke_scan(subarray_node, command_input_factory):
    """Invokes Scan command on TMC"""
    scan_input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    subarray_node.store_scan_data(scan_input_json)


@then(parsers.parse("the CSP subarray transitions to ObsState SCANNING"))
def csp_subarray_scanning(subarray_node, event_recorder):
    """Checks if Csp Subarray's obsState attribute value is SCANNING"""
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.SCANNING,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState SCANNING"
    )
)
def tmc_subarray_scanning(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """Checks if SubarrayNode's obsState attribute value is SCANNING"""
    central_node_mid.set_subarray_id(int(subarray_id))
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
        lookahead=15,
    )


@then(
    parsers.parse(
        "the CSP subarray ObsState transitions to READY after the"
        + " scan duration elapsed"
    )
)
def csp_subarray_ObsState(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """Checks if SubarrayNode's obsState attribute value is READY"""
    central_node_mid.set_subarray_id(int(subarray_id))
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} ObsState transitions back to READY"
    )
)
def tmc_subarray_ready(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    central_node_mid.set_subarray_id(int(subarray_id))
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY
    )
