import json
import logging

import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.helpers import update_scan_id
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_commands,
)
from tests.system_level_tests.utils import check_subarray_obsstate

TIMEOUT = 100
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/"
    + "xtp_64112_telescope_two_subarrays_testing.feature",
    "Execute Abort on two Low telescope subarrays using TMC",
)
def test_abort_command_with_two_subarrays():
    """
    Test case to verify Configure and Scan functionality with two subarrays
    """


# @given("telescope is in ON state") -> conftest


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


@when("I Abort subarray1")
def invoke_abort_subarray1(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Invokes ABORT command"""
    _, pytest.unique_id_sa_1 = subarray_node_low.abort_subarray()
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "Central Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.STARTED,"Command Started"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id_sa_1[0], COMMAND_COMPLETED),
    )
    check_subarray_obsstate(
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
        event_tracer,
        obs_state=ObsState.ABORTED,
    )


@then("subarray1 goes to obstate= empty")
def chek_obsste_for_subarray1(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    check_subarray_obsstate(
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
        event_tracer,
        obs_state=ObsState.EMPTY,
    )


@then(
    "subarray2 continues to be in Obstate=ready with the originally assigned "
    "resources and configuration"
)
def chek_obsste_for_subarray2(
    subarray_node_2_low, event_tracer: TangoEventTracer
):
    check_subarray_obsstate(
        subarray_node_2_low.subarray_devices,
        subarray_node_2_low.subarray_node,
        event_tracer,
        obs_state=ObsState.READY,
    )
    event_tracer.clear_events()
