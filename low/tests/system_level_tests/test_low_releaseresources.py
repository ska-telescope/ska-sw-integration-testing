"""Test module for ReleaseResources functionality (XTP-65636)"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import update_eb_pb_ids
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.system_level_tests.utils import (
    check_subarray_obsstate,
    subscribe_to_obsstate_events,
)

TIMEOUT = 100


@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_telescope_subarray_transitions.feature",
    "Release resources from Low subarray",
)
def test_telescope_release_resources():
    """
    Test case to verify releaseResources functionality
    """


# @given("telescope is in ON state") -> conftest


@given("subarray is in the IDLE obsState")
def invoke_assignresources(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    """Invokes AssignResources command on TMC"""
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_input_json = update_eb_pb_ids(input_json)
    subscribe_to_obsstate_events(event_tracer, subarray_node_low)
    central_node_low.set_serial_number_of_cbf_processor()
    _, pytest.unique_id = central_node_low.store_resources(assign_input_json)
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


@when("I release all resources assigned to it")
def invoke_release_resources(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    """Invokes ReleaseResources command on TMC"""
    release_input = prepare_json_args_for_centralnode_commands(
        "release_resources_low", command_input_factory
    )
    _, pytest.unique_id = central_node_low.invoke_release_resources(
        release_input
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'the subarray is in EMPTY obsState'"
        "TMC Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )


@then("the TMC, CSP, SDP, and MCCS subarrays transition to EMPTY obsState")
def subsystem_subarrays_in_empty(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Checks if Subarray's obsState attribute value is EMPTY"""

    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.EMPTY,
    )
