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
from tests.system_level_tests.utils import (
    check_subarray_obsstate,
    set_subarray_to_idle,
)

TIMEOUT = 100
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])


@pytest.mark.skip(reason = "To be tested")
@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_telescope_subarray_transitions.feature",
    "Configure two Low telescope subarrays using TMC",
)
def test_configure_command_with_two_subarrays():
    """
    Test case to verify Configure functionality with two subarrays
    """


# @given("telescope is in ON state") -> conftest


@given(parsers.parse("I assign station 1 to subarray 1"))
def subarray1_in_idle_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    # subscribe_to_obsstate_events(event_tracer,
    # subarray_node_low.subarray_devices, subarray_node_low.subarray_node)
    set_subarray_to_idle(
        central_node_low,
        subarray_node_low,
        command_input_factory,
        event_tracer,
        "1",
    )


@given(parsers.parse("I assign station 2 to subarray 2"))
def subarray2_in_idle_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    # subscribe_to_obsstate_events(event_tracer,
    # subarray_node_low.subarray_devices, subarray_node_low.subarray_node)
    set_subarray_to_idle(
        central_node_low,
        subarray_node_low,
        command_input_factory,
        event_tracer,
        "2",
    )


@when("I configure the two subarrays for scan")
def invoke_configure(
    subarray_node_low, subarray_node_2_low, event_tracer, command_input_factory
):
    configure_input_json = prepare_json_args_for_commands(
        "configure_low_real", command_input_factory
    )
    _, pytest.unique_id = subarray_node_low.store_configuration_data(
        configure_input_json, "1"
    )

    _, pytest.unique_id = subarray_node_2_low.store_configuration_data(
        configure_input_json, "2"
    )

    # Verify longRunningCommandResult for the TMC Subarray Node 1
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

    # Verify longRunningCommandResult for the TMC Subarray Node 2
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in READY obsState'"
        "TMC Subarray Node device"
        f"({subarray_node_2_low.subarray_node.dev_name()}) "
        "is expected to have longRunningCommandResult as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_2_low.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )


@then(
    "the TMC, CSP, SDP, and MCCS subarray instances 1 and 2 transition to "
    + "CONFIGURING obsState"
)
def subsystem_subarrays_in_configuring(
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_node_2_low,
    event_tracer: TangoEventTracer,
):
    """Check if all subarrays are in CONFIGURING obsState."""
    # Check if the TMC, CSP, SDP, and MCCS subarrays are in the expected
    # observation state by verifying the observed state changes for each
    # subarray device. This function can be used to validate any obsState.
    check_subarray_obsstate(
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
        event_tracer,
        obs_state=ObsState.CONFIGURING,
    )
    check_subarray_obsstate(
        subarray_node_2_low.subarray_devices,
        subarray_node_2_low.subarray_node,
        event_tracer,
        obs_state=ObsState.CONFIGURING,
    )


@then(
    "the TMC, CSP, SDP, and MCCS subarrays instances 1 and 2 transition "
    + "to READY obsState"
)
def tmc_subarray_ready(
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_node_2_low,
    event_tracer: TangoEventTracer,
):
    """Checks if SubarrayNode's obsState attribute value is READY"""
    # Check if the TMC, CSP, SDP, and MCCS subarrays are in the expected
    # observation state by verifying the observed state changes for each
    # subarray device. This function can be used to validate any obsState.
    check_subarray_obsstate(
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
        event_tracer,
        obs_state=ObsState.READY,
    )
    check_subarray_obsstate(
        subarray_node_2_low.subarray_devices,
        subarray_node_2_low.subarray_node,
        event_tracer,
        obs_state=ObsState.READY,
    )
