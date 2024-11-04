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
    "EndScan to the low telescope subarray using TMC",
)
def test_telescope_endscan():
    """
    Test case to verify scan functionality
    """


# @given("telescope is in ON state") -> conftest


@given("subarray is in SCANNING obsState")
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
    """Checks if Subarray's obsState attribute value is SCANNING"""
    set_subarray_to_ready(
        subarray_node_low, command_input_factory, event_tracer
    )

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
    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.SCANNING,
    )


@when("I end the scan")
def invoke_endscan(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Invokes EndSCan command before scan duration"""
    _, pytest.unique_id = subarray_node_low.remove_scan_data()

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


@then("the TMC, CSP, SDP and MCCS subarrays transition to READY obsState")
def subsystem_subarrays_in_scanning(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Checks if Subarray's obsState attribute value is READY"""

    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.READY,
    )
