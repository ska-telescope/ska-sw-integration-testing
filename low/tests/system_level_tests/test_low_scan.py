"""Test module for Scan functionality (XTP-69762)"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    update_scan_duration,
    update_scan_id,
)
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_commands,
)
from tests.system_level_tests.utils import (
    check_subarray_obsstate,
    set_subarray_to_idle,
)

TIMEOUT = 100


@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_telescope_subarray_transitions.feature",
    "Execute Scan on the Low telescope",
)
def test_telescope_scan():
    """
    Test case to verify scan functionality
    """


# @given("telescope is in ON state") -> conftest


@given(
    parsers.parse(
        "subarray is in READY ObsState with {scan_duration} scan_duration set"
    )
)
@given("subarray is in READY ObsState")
def subarray_in_ready_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
    scan_duration: int,
):
    """Checks if Subarray's obsState attribute value is READY"""
    # First ensure the subarray is in IDLE state
    set_subarray_to_idle(
        central_node_low,
        subarray_node_low,
        command_input_factory,
        event_tracer,
        "1",
    )
    # Then set it to READY state

    configure_input_json = prepare_json_args_for_commands(
        "configure_low_real_subarray1", command_input_factory
    )

    configure_json = update_scan_duration(configure_input_json, scan_duration)

    _, pytest.unique_id = subarray_node_low.store_configuration_data(
        configure_json, "1"
    )

    # Verify longRunningCommandResult for the TMC Subarray Node
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in READY obsState'"
        "TMC Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to have longRunningCommandResult as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )


@when(parsers.parse("I invoke scan command with scan id {scan_id}"))
def invoke_scan(
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
    scan_id: int,
):
    """Invoke the Scan command on TMC.

    Args:
        subarray_node_low (SubarrayNodeWrapperLow): Fixture for TMC
          SubarrayNode.
        event_tracer (EventTracer): Fixture for recording events.
        command_input_factory (JsonFactory): Factory for creating JSON input
    Raises:
        AssertionError: Scan Command is not Successful.
    """

    scan_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    scan_input_json = update_scan_id(scan_json, scan_id)
    _, pytest.unique_id = subarray_node_low.store_scan_data(scan_input_json)
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER SCAN COMMAND: "
        "Scan ID on SDP devices"
        "are expected to be as per JSON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "scanID",
        int(scan_id),
    )
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


@then("the TMC, CSP, SDP and MCCS subarrays transition to SCANNING obsState")
def subsystem_subarrays_in_scanning(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Checks if Subarray's obsState attribute value is SCANNING"""

    check_subarray_obsstate(
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
        event_tracer,
        obs_state=ObsState.SCANNING,
    )


@then("after the scan duration they transition back to READY obsState")
def subsystem_subarrays_in_ready(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Checks if Subarray's obsState attribute value is READY"""

    check_subarray_obsstate(
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
        event_tracer,
        obs_state=ObsState.READY,
    )
