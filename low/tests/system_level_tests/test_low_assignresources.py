"""Test module for TMC StartUp functionality (XTP-64114)"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)

TIMEOUT = 100
COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])


@pytest.mark.system_level_tests1
@scenario(
    "system_level_tests/" + "xtp_xxxxx_telescope_assign_release.feature",
    "Assign resources to low subarray",
)
def test_telescope_assignresources():
    """
    Test case to verify StartUp functionality
    """


@given("telescope is in ON state")
def move_telescope_to_on(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """A method to turn on the telescope."""
    central_node_low.move_to_on()

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("subarray {subarray_id} is in EMPTY ObsState"))
def subarray_in_empty_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_recorder: TangoEventTracer,
    subarray_id: int,
):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    central_node_low.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert subarray_node_low.subarray_node.obsState == ObsState.EMPTY


@when("I assign resources to the subarray")
def invoke_assignresources(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory,
    event_tracer: TangoEventTracer,
):
    """Invokes AssignResources command on TMC"""
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.set_serial_number_of_cbf_processor()
    _, pytest.unique_id = central_node_low.store_resources(input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(60).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )


@then("the CSP, SDP and MCCS subarrays must be in IDLE obsState")
def subsystem_subarrays_in_idle(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Checks if Csp Subarray's obsState attribute value is IDLE"""
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")

    csp = subarray_node_low.subarray_devices["csp_subarray"]
    sdp = subarray_node_low.subarray_devices["sdp_subarray"]
    mccs = subarray_node_low.subarray_devices["mccs_subarray"]

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "SDP Subarray device"
        f"({sdp.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.IDLE,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "CSP Subarray device"
        f"({csp.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "MCCS Subarray device"
        f"({mccs.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.IDLE,
    )


@then("the subarray obsState is transitioned to IDLE")
def tmc_subarray_idle(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Checks if SubarrayNode's obsState attribute value is IDLE"""

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "TMC Subarray device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
