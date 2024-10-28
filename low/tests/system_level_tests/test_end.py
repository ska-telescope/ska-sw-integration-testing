"""Test module for TMC END functionality (XTP-66037)"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.system_level_tests.conftest import (
    check_subarray_obsstate,
    set_subarray_to_idle,
    set_subarray_to_ready,
)

TIMEOUT = 100
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])


@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_telescope_subarray_transitions.feature",
    "End Configuration to the low telescope subarray using TMC",
)
def test_telescope_end():
    """
    Test case to verify End functionality
    """


# @given("telescope is in ON state") -> conftest


@given(parsers.parse("subarray is in READY ObsState"))
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
