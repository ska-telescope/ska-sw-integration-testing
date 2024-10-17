"""Test TMC-CSP succesive configure functionality"""

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
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory


@pytest.mark.skip(reason="issue at CSP for succesive configure (CIP-2967)")
@pytest.mark.tmc_csp
@scenario(
    "../../mid/features/tmc_csp/xtp_40073_succesive_configure.feature",
    "TMC-CSP succesive configure functionality",
)
def test_tmc_csp_succesive_configure_functionality():
    """
    Test case to verify TMC-CSP succesive configure functionality
    """


@given("a TMC and CSP")
def given_a_tmc(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    subarray_node: SubarrayNodeWrapper,
):
    """A method to define TMC and CSP and subscribe ."""
    assert central_node_mid.central_node.ping() > 0
    assert subarray_node.subarray_devices["csp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("csp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")


@given(parsers.parse("a subarray {subarray_id} in the IDLE obsState"))
def telescope_is_in_idle_state(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
    subarray_node: SubarrayNodeWrapper,
):
    """A method to move subarray into the IDLE ObsState."""

    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
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
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid_multiple_scantype", command_input_factory
    )

    _, unique_id = central_node_mid.store_resources(assign_input_json)

    check_subarray_instance(
        subarray_node.subarray_devices.get("csp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
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
    parsers.parse(
        "I invoke First Configure command on TMC subarray {subarray_id} "
        + "with {input_json1}"
    )
)
def execute_first_configure_command(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    input_json1: dict,
    event_recorder: EventRecorder,
    subarray_id: str,
):
    """ "A method to invoke first configure command"""

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        input_json1, command_input_factory
    )
    _, pytest.unique_id = subarray_node.execute_transition(
        "Configure", argin=configure_json
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.CONFIGURING,
    )


@then(parsers.parse("CSP subarray {subarray_id} must be in READY ObsState"))
def check_csp_subarray_is_in_ready_obsstate(
    subarray_node: SubarrayNodeWrapper,
    event_recorder: EventRecorder,
    subarray_id: str,
) -> None:
    """Method to check CSP Subarray is in READY obsstate"""
    check_subarray_instance(
        subarray_node.subarray_devices.get("csp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.READY,
    )


@then(parsers.parse("TMC subarray {subarray_id} must be in READY obsState"))
def check_subarray_is_in_ready_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    subarray_id: str,
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """Method to check TMC Subarray is in READY obsstate"""

    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
        lookahead=5,
    )


@when(
    parsers.parse(
        "I invoke Second Configure command on TMC subarray {subarray_id} "
        + "with {input_json2}"
    )
)
def execute_second_configure_command(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    input_json2: dict,
    event_recorder: EventRecorder,
    subarray_id: str,
):
    """ "A method to invoke second configure command"""

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        input_json2, command_input_factory
    )
    _, pytest.unique_id = subarray_node.execute_transition(
        "Configure", argin=configure_json
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.CONFIGURING,
    )
