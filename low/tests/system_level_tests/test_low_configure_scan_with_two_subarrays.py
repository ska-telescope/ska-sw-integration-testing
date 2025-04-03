"""Test module for TMC Configure functionality (XTP-66007)"""
import json
import logging

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.helpers import update_scan_id
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

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


# @pytest.mark.skip(reason="To be tested")
@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/"
    + "xtp_64112_telescope_two_subarrays_testing.feature",
    "Execute Scans on two Low telescope subarrays using TMC",
)
def test_configure_command_with_two_subarrays():
    """
    Test case to verify Configure and Scan functionality with two subarrays
    """


# @given("telescope is in ON state") -> conftest


@given("I assign station 1 to subarray 1 and station 2 to subarray 2")
def subarrays_in_idle_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_node_2_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    # Assign resources to subarray 1
    set_subarray_to_idle(
        central_node_low,
        subarray_node_low,
        command_input_factory,
        event_tracer,
        "1",
    )

    # Assign resources to Subarray 2
    set_subarray_to_idle(
        central_node_low,
        subarray_node_2_low,
        command_input_factory,
        event_tracer,
        "2",
    )


@given("I configure the two subarrays for scan")
def subarrays_in_ready_obsstate(
    subarray_node_low, subarray_node_2_low, event_tracer, command_input_factory
):
    configure_input_json_1 = prepare_json_args_for_commands(
        "configure_low_real_subarray1", command_input_factory
    )
    configure_input_json_2 = prepare_json_args_for_commands(
        "configure_low_real_subarray2", command_input_factory
    )
    _, pytest.unique_id_sa_1 = subarray_node_low.store_configuration_data(
        configure_input_json_1, "1"
    )

    _, pytest.unique_id_sa_2 = subarray_node_2_low.store_configuration_data(
        configure_input_json_2, "2"
    )

    LOGGER.info(
        "LRCR Subarray1: %s",
        subarray_node_low.subarray_node.read_attribute(
            "longRunningCommandResult"
        ).value,
    )
    LOGGER.info("Unique id 1: %s", pytest.unique_id_sa_1[0])
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
        (pytest.unique_id_sa_1[0], COMMAND_COMPLETED),
    )

    LOGGER.info(
        "LRCR Subarray2: %s",
        subarray_node_2_low.subarray_node.read_attribute(
            "longRunningCommandResult"
        ).value,
    )
    LOGGER.info(
        "Unique id 2:  %s ,%s",
        pytest.unique_id_sa_2[0],
        subarray_node_2_low.subarray_node.dev_name(),
    )
    # Verify longRunningCommandResult for the TMC Subarray Node 2
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in READY obsState'"
        "TMC Subarray Node device"
        f"({subarray_node_2_low.subarray_node.dev_name()}) "
        "is expected to have longRunningCommandResult as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(200).has_change_event_occurred(
        subarray_node_2_low.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id_sa_2[0], COMMAND_COMPLETED),
    )

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
    event_tracer.clear_events()


@when("I invoke scan command on two subarrays")
def invoke_scan_on_two_subarrays(
    subarray_node_low, subarray_node_2_low, event_tracer, command_input_factory
):
    scan_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    scan_id_for_subarray1 = 1
    scan_input_json = update_scan_id(scan_json, scan_id_for_subarray1)
    _, pytest.unique_id_subarray1 = subarray_node_low.store_scan_data(
        scan_input_json
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER SCAN COMMAND: "
        "Scan ID on SDP devices"
        "are expected to be as per JSON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "scanID",
        int(scan_id_for_subarray1),
    )

    scan_id_for_subarray2 = 2
    scan_input_json = update_scan_id(scan_json, scan_id_for_subarray2)
    _, pytest.unique_id_subarray2 = subarray_node_2_low.store_scan_data(
        scan_input_json
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER SCAN COMMAND: "
        "Scan ID on SDP devices"
        "are expected to be as per JSON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_2_low.subarray_devices["sdp_subarray"],
        "scanID",
        int(scan_id_for_subarray2),
    )


@then("the TMC, CSP, SDP and MCCS subarrays transition to SCANNING obsState")
def subsystem_subarrays_in_scanning(
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_node_2_low,
    event_tracer: TangoEventTracer,
):
    """Check if all subarrays are in CONFIGURING obsState."""
    # Check if the TMC, CSP, SDP, and MCCS subarrays are in the expected
    # observation state by verifying the observed state changes for each
    # subarray device.
    check_subarray_obsstate(
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
        event_tracer,
        obs_state=ObsState.SCANNING,
    )

    check_subarray_obsstate(
        subarray_node_2_low.subarray_devices,
        subarray_node_2_low.subarray_node,
        event_tracer,
        obs_state=ObsState.SCANNING,
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
        (pytest.unique_id_subarray1[0], COMMAND_COMPLETED),
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in SCANNING obsState'"
        "TMC Subarray Node device"
        f"({subarray_node_2_low.subarray_node.dev_name()}) "
        "is expected to have longRunningCommandResult as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_2_low.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id_subarray2[0], COMMAND_COMPLETED),
    )


@then("after the scan duration they transition back to READY obsState")
def subsystem_subarrays_in_ready(
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
