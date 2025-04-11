import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import update_eb_pb_ids
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.system_level_tests.utils import (
    check_subarray_obsstate,
    set_subarray_to_idle,
    set_subarray_to_ready,
    subscribe_to_obsstate_events,
)

TIMEOUT = 100


@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_abort.feature",
    "Validates Abort Command",
)
def test_abort_command():
    """
    BDD test scenario for verifying successful execution of
    the Abort command in a TMC.

    """


#  @given("telescope is in ON state") -> conftest


def ensure_subarray_in_obsstate(
    target_state,
    central_node_low,
    subarray_node_low,
    command_input_factory,
    event_tracer,
):
    """Ensures subarray is in the required state before transitioning"""
    subscribe_to_obsstate_events(
        event_tracer,
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
    )

    if target_state in ["IDLE", "READY", "SCANNING", "CONFIGURING"]:
        set_subarray_to_idle(
            central_node_low,
            subarray_node_low,
            command_input_factory,
            event_tracer,
            "1",
        )

    if target_state in ["READY", "SCANNING"]:
        set_subarray_to_ready(
            subarray_node_low, command_input_factory, event_tracer
        )


@given(parsers.parse("subarray is in {obs_state} ObsState"))
def subarray_in_obsstate(
    obs_state,
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    ensure_subarray_in_obsstate(
        obs_state,
        central_node_low,
        subarray_node_low,
        command_input_factory,
        event_tracer,
    )

    if obs_state == "SCANNING":
        scan_json = prepare_json_args_for_commands(
            "scan_low", command_input_factory
        )
        _, pytest.unique_id = subarray_node_low.store_scan_data(scan_json)

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the subarray is in SCANNING obsState'"
            f"TMC Subarray Node ({subarray_node_low.subarray_node.dev_name()})"
            "is expected to have longRunningCommandResult as"
            '(unique_id,(ResultCode.OK,"Command Completed"))'
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (pytest.unique_id[0], COMMAND_COMPLETED),
        )

        check_subarray_obsstate(
            subarray_node_low.subarray_devices,
            subarray_node_low.subarray_node,
            event_tracer,
            obs_state=ObsState.SCANNING,
        )

    elif obs_state == "RESOURCING":
        input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low_real", command_input_factory
        )
        assign_input_json = update_eb_pb_ids(input_json)
        central_node_low.set_serial_number_of_cbf_processor()
        _, pytest.unique_id = central_node_low.store_resources(
            assign_input_json, "1"
        )

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the subarray is in RESOURCING obsState'"
            f"TMC Central Node ({central_node_low.central_node.dev_name()}) "
            "is expected to have longRunningCommand as"
            '(unique_id,(ResultCode.OK,"Command Completed"))'
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (pytest.unique_id[0], COMMAND_COMPLETED),
        )

        check_subarray_obsstate(
            subarray_node_low.subarray_devices,
            subarray_node_low.subarray_node,
            event_tracer,
            obs_state=ObsState.RESOURCING,
        )

    elif obs_state == "CONFIGURING":
        configure_input_json = prepare_json_args_for_commands(
            "configure_low_real_subarray1", command_input_factory
        )
        _, pytest.unique_id = subarray_node_low.store_configuration_data(
            configure_input_json, "1"
        )

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the subarray is in CONFIGURING obsState'"
            f"TMC Subarray Node ({subarray_node_low.subarray_node.dev_name()})"
            "is expected to have longRunningCommandResult as"
            '(unique_id,(ResultCode.OK,"Command Completed"))'
        ).within_timeout(200).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (pytest.unique_id[0], COMMAND_COMPLETED),
        )

        check_subarray_obsstate(
            subarray_node_low.subarray_devices,
            subarray_node_low.subarray_node,
            event_tracer,
            obs_state=ObsState.CONFIGURING,
        )
        event_tracer.clear_events()


@when("I Abort it")
def invoke_abort(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Invokes ABORT command"""
    _, unique_id = subarray_node_low.abort_subarray("1")
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "Central Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.STARTED,"Command Started"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.STARTED), "Command Started")),
        ),
    )


@then("the TMC, CSP, SDP and MCCS subarrays transitions to ABORTED obsState")
def subsystem_subarrays_in_aborted(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Check if all subarrays are in ABORTED obsState."""
    # Check if the TMC, CSP, SDP, and MCCS subarrays are in the expected
    # observation state by verifying the observed state changes for each
    # subarray device.
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN STEP: '
        f'"the Subarray transitions to ABORTED obsState"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        f"is expected to be in ABORTING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )
    check_subarray_obsstate(
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
        event_tracer,
        obs_state=ObsState.ABORTED,
    )
