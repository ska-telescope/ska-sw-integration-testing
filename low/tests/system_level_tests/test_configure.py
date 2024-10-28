"""Test module for TMC Configure functionality (XTP-66007)"""
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
    execute_command,
    set_subarray_to_idle,
)

TIMEOUT = 100
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])


@pytest.mark.system_level_tests2
@scenario(
    "system_level_tests/" + "xtp_64112_telescope_subarray_transitions.feature",
    "Configure the Low telescope subarray using TMC",
)
def test_configure_command():
    """
    Test case to verify Configure functionality
    """


# @given("telescope is in ON state") -> conftest


@given(parsers.parse("subarray is in IDLE ObsState"))
def subarray_in_idle_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    set_subarray_to_idle(
        central_node_low,
        subarray_node_low,
        command_input_factory,
        event_tracer,
    )


@when("I configure it for a scan")
def invoke_configure(subarray_node_low, event_tracer, command_input_factory):
    execute_command(
        subarray_node_low,
        event_tracer,
        command_name="Configure",
        command_input_factory=command_input_factory,
        expected_obs_state=ObsState.CONFIGURING,
    )


@then(
    "the TMC, CSP, SDP, and MCCS subarrays transition to CONFIGURING obsState"
)
def subsystem_subarrays_in_configuring(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Check if all subarrays are in CONFIGURING obsState."""
    # Check if the TMC, CSP, SDP, and MCCS subarrays are in the expected
    # observation state by verifying the observed state changes for each
    # subarray device. This function can be used to validate any obsState.
    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.CONFIGURING,
    )


@then("the TMC, CSP, SDP, and MCCS subarrays transition to READY obsState")
def tmc_subarray_ready(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Checks if SubarrayNode's obsState attribute value is READY"""
    # Check if the TMC, CSP, SDP, and MCCS subarrays are in the expected
    # observation state by verifying the observed state changes for each
    # subarray device. This function can be used to validate any obsState.
    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.READY,
    )
