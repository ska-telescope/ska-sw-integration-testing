import json
import logging

import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
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
from tests.system_level_tests.utils import (
    check_subarray_obsstate,
    subscribe_to_obsstate_events,
)

TIMEOUT = 100
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.system_level_tests
@scenario(
    "system_level_tests/"
    + "xtp_64112_telescope_two_subarrays_testing_abort.feature",
    "Execute Abort on two Low telescope subarrays using TMC for IDLE",
)
def test_abort_command_with_two_subarrays():
    """
    Test case to verify Configure and Scan functionality with two subarrays
    """


@when("I Abort subarray1")
def invoke_abort_subarray1(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Invokes ABORT command"""
    subscribe_to_obsstate_events(
        event_tracer,
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
    )
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
    subarray_node_2_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):

    configure_input_json_2 = prepare_json_args_for_commands(
        "configure_low_real_subarray2", command_input_factory
    )
    _, pytest.unique_id_sa_2 = subarray_node_2_low.store_configuration_data(
        configure_input_json_2, "2"
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
        subarray_node_2_low.subarray_devices,
        subarray_node_2_low.subarray_node,
        event_tracer,
        obs_state=ObsState.READY,
    )
    event_tracer.clear_events()
