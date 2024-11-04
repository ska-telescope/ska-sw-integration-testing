"""Test module for ReleaseResources functionality (XTP-65636)"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_commands,
)
from tests.system_level_tests.conftest import (
    check_subarray_obsstate,
    set_subarray_to_idle,
    set_subarray_to_ready,
)

TIMEOUT = 100


@pytest.mark.system_level_tests3
@scenario(
    "system_level_tests/" + "xtp_64112_telescope_subarray_transitions.feature",
    "Execute Scan on the Low telescope",
)
def test_telescope_scan():
    """
    Test case to verify scan functionality
    """


# @given("telescope is in ON state") -> conftest


@given("subarray is in READY ObsState")
def subarray_in_ready_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    # First ensure the subarray is in IDLE state
    set_subarray_to_idle(
        central_node_low,
        subarray_node_low,
        command_input_factory,
        event_tracer,
    )
    # Then set it to READY state
    set_subarray_to_ready(
        subarray_node_low, command_input_factory, event_tracer
    )


@when("I invoke scan command")
def invoke_scan(
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    """Invoke the Scan command on TMC.

    Args:
        subarray_node_low (SubarrayNodeWrapperLow): Fixture for TMC
          SubarrayNode.
        event_recorder (EventRecorder): Fixture for recording events.
        command_input_factory (JsonFactory): Factory for creating JSON input
    Raises:
        AssertionError: Scan Command is not Successful.
    """

    scan_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    _, pytest.unique_id = subarray_node_low.store_scan_data(scan_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in SCANNING obsState'"
        "TMC Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to have longRunningCommandResult as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )


@then("the TMC, CSP, SDP, and MCCS subarrays transition to SCANNING obsState")
def subsystem_subarrays_in_scanning(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Checks if Subarray's obsState attribute value is SCANNING"""

    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.SCANNING,
    )


@then("after the scan duration it transition back to READY obsState")
def subsystem_subarrays_in_ready(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Checks if Subarray's obsState attribute value is SCANNING"""

    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.READY,
    )
