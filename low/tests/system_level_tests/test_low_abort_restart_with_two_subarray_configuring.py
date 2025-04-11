import json
import logging

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_testing.integration import TangoEventTracer
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
    + "xtp_64112_telescope_two_subarrays_testing_abort.feature",
    "Verify Abort-Restart workflow on Subarray 1 in obsState CONFIGURING "
    "while subarray 2 is configured successfully",
)
def test_abort_command_with_two_subarrays_in_obsstate_configuring():
    """
    Test case to verify Abort-Restart workflow on one Subarray while the other
    Subarray continues observation
    """


# @given("telescope is in ON state") -> conftest

# @given("2 subarrays are in obsState IDLE") -> conftest


@given("2 subarrays are in obsState CONFIGURING")
def subarrays_in_configuring_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_node_2_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):

    configure_input_json_1 = prepare_json_args_for_commands(
        "configure_low_real_subarray1", command_input_factory
    )
    configure_input_json_2 = prepare_json_args_for_commands(
        "configure_low_real_subarray2", command_input_factory
    )

    subarray_node_low.subarray_node.Configure(configure_input_json_1)
    LOGGER.info("Invoked Configure on SubarrayNode 1")

    _, pytest.unique_id_sa_2 = subarray_node_2_low.subarray_node.Configure(
        configure_input_json_2
    )
    LOGGER.info("Invoked Configure on SubarrayNode 2")

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


@when("I Abort subarray 1")
def invoke_abort_subarray1(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Invokes ABORT command"""
    _, pytest.unique_id_sa_1 = subarray_node_low.abort_subarray("1")


@then("subarray1 goes to obstate ABORTED")
def chek_obsste_for_subarray1(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
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


@then(
    "subarray 2 continues to be in Obstate=ready with the originally "
    "assigned resources and configuration"
)
def chek_obsste_for_subarray2(
    subarray_node_2_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
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
        subarray_node_2_low.subarray_devices,
        subarray_node_2_low.subarray_node,
        event_tracer,
        obs_state=ObsState.READY,
    )
