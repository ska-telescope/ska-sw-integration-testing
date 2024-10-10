"""Test module for TMC END functionality (XTP-66037)"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.helpers import generate_eb_pb_ids
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.system_level_tests.conftest import (
    check_subarray_obsstate,
    subscribe_to_obsstate_events,
)

TIMEOUT = 100
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])


@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_telescope_configure_end.feature",
    "End Configuration to the low telescope subarray using TMC",
)
def test_telescope_end():
    """
    Test case to verify End functionality
    """


# @given("telescope is in ON state") -> conftest


@given(parsers.parse("subarray {subarray_id} is in READY ObsState"))
def subarray_in_idle_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
    subarray_id: int,
):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    # Subscribe to the obsState change events for each subarray device
    # (SDP, CSP, MCCS, and TMC). This allows the event tracer to monitor
    # changes in observation states, enabling timely responses to state
    # transitions.
    subscribe_to_obsstate_events(event_tracer, subarray_node_low)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    input_json = json.loads(assign_input_json)
    generate_eb_pb_ids(input_json)
    central_node_low.set_serial_number_of_cbf_processor()
    _, pytest.unique_id = central_node_low.store_resources(
        json.dumps(input_json)
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )
    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.IDLE,
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    _, pytest.unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in READY obsState'"
        "TMC Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )
    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.READY,
    )


@when("I end the configuration")
def invoke_end(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    """Invokes End command"""
    subarray_node_low.execute_transition("End")


@then("the TMC, CSP, SDP and MCCS subarrays transition to IDLE obsState")
def subsystem_subarrays_in_configuring(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Check if all subarrays are in IDLE obsState."""
    # Check if the TMC, CSP, SDP, and MCCS subarrays are in the expected
    # observation state by verifying the observed state changes for each
    # subarray device. This function can be used to validate any obsState.
    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.IDLE,
    )
