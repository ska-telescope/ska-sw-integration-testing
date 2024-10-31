"""Test module for TMC Configure functionality (XTP-66007)"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_commands,
)
from tests.system_level_tests.conftest import (
    check_subarray_obsstate,
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
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    _, pytest.unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
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
