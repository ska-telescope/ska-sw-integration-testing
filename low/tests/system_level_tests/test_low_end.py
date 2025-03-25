"""Test module for TMC END functionality (XTP-66037)"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.system_level_tests.utils import (
    check_subarray_obsstate,
    set_subarray_to_idle,
    set_subarray_to_ready,
)

TIMEOUT = 100
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])


@pytest.mark.skip(reason="Disabled temporarily")
@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_telescope_subarray_transitions.feature",
    "End Configuration to the Low telescope subarray using TMC",
)
def test_telescope_end():
    """
    Test case to verify End functionality
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
        "1",
    )
    # Then set it to READY state
    set_subarray_to_ready(
        subarray_node_low, command_input_factory, event_tracer
    )


@when("I end the configuration")
def invoke_end(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Invokes End command"""
    _, pytest.unique_id = subarray_node_low.end_observation()

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


@then("the TMC, CSP, SDP and MCCS subarrays transition to IDLE obsState")
def subsystem_subarrays_in_idle(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Check if all subarrays are in IDLE obsState."""
    # Check if the TMC, CSP, SDP, and MCCS subarrays are in the expected
    # observation state by verifying the observed state changes for each
    # subarray device. This function can be used to validate any obsState.
    check_subarray_obsstate(
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
        event_tracer,
        obs_state=ObsState.IDLE,
    )
