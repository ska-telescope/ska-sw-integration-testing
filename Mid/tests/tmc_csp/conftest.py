"""Pytest BDD step implementations specific to tmc integration
tests."""

import json
import logging

from pytest_bdd import given, parsers, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from tango import DevState

from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    update_scan_id,
)
from tests.resources.test_harness.utils.common_utils import (
    check_scan_successful_csp,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@given("the telescope is in ON state")
def given_a_tmc(central_node_mid, event_recorder, subarray_node):
    """A method to define TMC and CSP and subscribe ."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["csp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("csp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices["csp_subarray"], "State"
    )
    event_recorder.subscribe_event(central_node_mid.csp_master, "State")
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    central_node_mid.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@when(parsers.parse("I assign resources to TMC SubarrayNode {subarray_id}"))
def telescope_is_in_idle_state(
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node,
):
    """A method to move subarray into the IDLE ObsState."""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid_multiple_scantype", command_input_factory
    )

    assign_str = json.loads(assign_input_json)
    _, unique_id = central_node_mid.store_resources(json.dumps(assign_str))

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
        "I reassign with new resources to TMC SubarrayNode {subarray_id}"
    )
)
def reassign_resources(
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node,
):
    """A method to move subarray into the IDLE ObsState"""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid_multiple_scantype_new_resources",
        command_input_factory,
    )

    assign_str = json.loads(assign_input_json)

    _, unique_id = central_node_mid.store_resources(json.dumps(assign_str))

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
        lookahead=10,
    )


@when(parsers.parse("end the configuration on TMC SubarrayNode {subarray_id}"))
def execute_end_command(
    subarray_node,
    command_input_factory,
    central_node_mid,
    event_recorder,
    subarray_id,
    scan_types,
):
    """ "A method to invoke end command"""

    central_node_mid.set_subarray_id(subarray_id)
    _, unique_id = subarray_node.end_observation()

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
        lookahead=20,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.IDLE, lookahead=20
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=10,
    )


@when(parsers.parse("release the resources on TMC SubarrayNode {subarray_id}"))
def execute_release_resources_command(
    command_input_factory,
    central_node_mid,
    event_recorder,
    subarray_id,
):
    """ "A method to invoke Release Resources command"""

    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    _, unique_id = central_node_mid.invoke_release_resources(
        release_input_json
    )

    check_subarray_instance(
        central_node_mid.subarray_devices.get("csp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=5,
    )


@then(
    parsers.parse(
        "TMC SubarrayNode {subarray_id} transitions to EMPTY ObsState"
    )
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


@when(
    parsers.parse(
        "reperform scan with same configuration and new scan id {new_scan_id}"
    )
)
def reexecute_scan_command(
    command_input_factory, event_recorder, subarray_node, new_scan_id
):
    """A method to invoke scan command with new scan_id"""

    scan_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )

    scan_json = update_scan_id(scan_json, new_scan_id)
    _, unique_id = subarray_node.execute_transition("Scan", argin=scan_json)

    check_scan_successful_csp(
        subarray_node, event_recorder, new_scan_id, unique_id
    )
