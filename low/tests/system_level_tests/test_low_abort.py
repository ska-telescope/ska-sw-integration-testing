import json

import pytest
from assertpy import assert_that
from pytest_bdd import parsers, scenario, then, when
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


@pytest.mark.test1
@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_abort.feature",
    "IDLE to ABORT - CMD Abort",
)
def test_idle_to_abort():
    """
    Test IDLE to ABORT transitions
    """


@pytest.mark.test1
@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_abort.feature",
    "READY to ABORT - CMD Abort",
)
def test_ready_to_abort():
    """
    Test READY to ABORT transitions
    """


@pytest.mark.test1
@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_abort.feature",
    "SCANNING to ABORT - CMD Abort",
)
def test_scanning_to_abort():
    """
    Test SCANNING to ABORT transitions
    """


@pytest.mark.test1
@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_abort.feature",
    "RESOURCING to ABORT -CMD Abort",
)
def test_resourcing_to_abort():
    """
    Test RESOURCING to ABORT transitions
    """


@pytest.mark.test1
@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/" + "xtp_64112_abort.feature",
    "CONFIGURING to ABORT -CMD Abort",
)
def test_configuring_to_abort():
    """
    Test CONFIGURING to ABORT transitions
    """


#  @given("telescope is in ON state") -> conftest


@then(parsers.parse("subarrays is in IDLE ObsState"))
def subarray_in_idle_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    subscribe_to_obsstate_events(event_tracer, subarray_node_low)
    set_subarray_to_idle(
        central_node_low,
        subarray_node_low,
        command_input_factory,
        event_tracer,
    )


@then(parsers.parse("subarrays is in READY ObsState"))
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
    subscribe_to_obsstate_events(event_tracer, subarray_node_low)
    set_subarray_to_ready(
        subarray_node_low,
        command_input_factory,
        event_tracer,
    )


@then(parsers.parse("subarrays is in SCANNING ObsState"))
def subarray_in_scanning_obsstate(
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


@then(parsers.parse("subarrays is in RESOURCING ObsState"))
def subarray_in_resourcing_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    """Invokes AssignResources command on TMC"""
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low_real", command_input_factory
    )
    assign_input_json = update_eb_pb_ids(input_json)
    central_node_low.set_serial_number_of_cbf_processor()
    _, pytest.unique_id = central_node_low.store_resources(assign_input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
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
        obs_state=ObsState.RESOURCING,
    )


@then("subarrays is in CONFIGURING obsState")
def invoke_configure(
    central_node_low, subarray_node_low, event_tracer, command_input_factory
):
    # First ensure the subarray is in IDLE state
    set_subarray_to_idle(
        central_node_low,
        subarray_node_low,
        command_input_factory,
        event_tracer,
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low_real", command_input_factory
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
    check_subarray_obsstate(
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.CONFIGURING,
    )


@when("I Abort it")
def invoke_abort(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Invokes ABORT command"""
    _, unique_id = subarray_node_low.abort_subarray()
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
    # subarray device. This function can be used to validate any obsState.
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
        subarray_node_low,
        event_tracer,
        obs_state=ObsState.ABORTED,
    )
