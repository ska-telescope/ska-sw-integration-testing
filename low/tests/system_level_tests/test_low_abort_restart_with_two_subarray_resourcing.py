import json
import logging

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_testing.integration import TangoEventTracer
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.helpers import update_eb_pb_ids
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.system_level_tests.utils import (
    check_subarray_obsstate,
    register_cbf_proc_devices,
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
    "Verify Abort-Restart workflow on Subarray 1 in obsState resourcing while "
    "the resources are assigned to subarray 2 successfully",
)
def test_abort_command_with_two_subarrays_in_obsstate_resourcing():
    """
    Test case to verify Abort-Restart workflow on one Subarray while the other
    Subarray continues observation
    """


# @given("telescope is in ON state") -> conftest


@given("2 subarrays are in obsState IDLE")
def subarrays_in_resourcing_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_node_2_low: SubarrayNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    subscribe_to_obsstate_events(
        event_tracer,
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
    )
    subscribe_to_obsstate_events(
        event_tracer,
        subarray_node_2_low.subarray_devices,
        subarray_node_2_low.subarray_node,
    )

    register_cbf_proc_devices()

    # Assign resources to subarray 1
    input_json_subarray1 = prepare_json_args_for_centralnode_commands(
        "assign_resources_low_real_subarray1_station1", command_input_factory
    )
    assign_input_json_subarray1 = update_eb_pb_ids(input_json_subarray1)
    central_node_low.central_node.AssignResources(assign_input_json_subarray1)
    LOGGER.info("Invoked AssignResources on CentralNode for Subarray1")

    # Assign resources to subarray 2
    input_json_subarray2 = prepare_json_args_for_centralnode_commands(
        "assign_resources_low_real_subarray2_station2", command_input_factory
    )
    assign_input_json_subarray2 = update_eb_pb_ids(input_json_subarray2)
    _, pytest.unique_id_sa_2 = central_node_low.central_node.AssignResources(
        assign_input_json_subarray2
    )
    LOGGER.info("Invoked AssignResources on CentralNode for Subarray2")

    # Confirm subarray 1 is in RESOURCING ObsState
    check_subarray_obsstate(
        subarray_node_low.subarray_devices,
        subarray_node_low.subarray_node,
        event_tracer,
        obs_state=ObsState.RESOURCING,
    )
    # Confirm subarray 2 is in RESOURCING ObsState
    check_subarray_obsstate(
        subarray_node_2_low.subarray_devices,
        subarray_node_2_low.subarray_node,
        event_tracer,
        obs_state=ObsState.RESOURCING,
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


@then("subarray 2 is assigned with the resources successfully")
def chek_obsste_for_subarray2(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_2_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    # Verify longRunningCommandResult for the TMC Central Node
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to have longRunningCommandResult as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (pytest.unique_id_sa_2[0], COMMAND_COMPLETED),
    )

    check_subarray_obsstate(
        subarray_node_2_low.subarray_devices,
        subarray_node_2_low.subarray_node,
        event_tracer,
        obs_state=ObsState.IDLE,
    )
