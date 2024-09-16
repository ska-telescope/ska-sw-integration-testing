"""Test module for TMC-DISH successive Scan functionality"""

import json
import logging
import time

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.enum import DishMode, PointingState


@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-42757_successive_scan.feature",
    "Testing of successive Scan functionality for tmc-dish interface",
)
def test_tmc_dish_successive_scan_with_different_scan_duration():
    """
    Test case to verify TMC-DISH successive Scab functionality
    with different receiver band and scan duration.
    """


@given("TMC subarray is in IDLE obsState")
def check_subarray_obsState_idle(
    subarray_node,
    central_node_mid,
    event_tracer: TangoEventTracer,
    command_input_factory,
):
    """
    Method to check subarray is in IDLE obsState

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        command_input_factory: fixture for creating input required
        for command
    """
    log_events(
        {
            subarray_node.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
        }
    )
    event_tracer.subscribe_event(subarray_node.subarray_node, "obsState")

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    _, pytest.unique_id = central_node_mid.store_resources(assign_input_json)

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_tracer.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Central Node device"
        f"({central_node_mid.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(60).has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )


@given(
    parsers.parse(
        "the command Configure is issued to the TMC"
        + " subarray with {receiver_band1} and {scan_duration1} sec"
    )
)
def invoke_configure(
    subarray_node, command_input_factory, receiver_band1, scan_duration1
):
    """
    A method to invoke Configure command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        receiver_band1(str) : receiver band for configure command
        scan_duration1 (str): scan duration required
    """

    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input = json.loads(configure_input_json)
    configure_input["dish"]["receiver_band"] = receiver_band1
    configure_input["tmc"]["scan_duration"] = float(scan_duration1)
    _, pytest.unique_id = subarray_node.execute_transition(
        "Configure", json.dumps(configure_input)
    )


@then("the TMC subarray transitions to obsState READY")
@given("the TMC subarray transitions to obsState READY")
def check_dish_mode_and_pointing_state(
    subarray_node, event_tracer: TangoEventTracer, central_node_mid
):
    """
    Method to check dishMode and pointingState of DISH and
    SubarrayNode obsState.

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        subarray_id (str): Subarray ID
        event_recorder: Fixture for EventRecorder class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
    """
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        log_events(
            {
                central_node_mid.dish_master_dict.get(dish_id): ["dishMode"],
                central_node_mid.dish_master_dict.get(dish_id): [
                    "pointingState"
                ],
            }
        )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_tracer.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        event_tracer.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )
        event_tracer.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_tracer.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "pointingState"
        )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the dish must be in the OPERATE dishMode'"
            "dish device"
            f"({central_node_mid.dish_master_dict[dish_id].dev_name()}) "
            "is expected to be in OPERATE dishMode",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
        )

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the DishLeafNode must be in the OPERATE dishMode'"
            "dish device"
            f"({central_node_mid.dish_leaf_node_dict[dish_id].dev_name()}) "
            "is expected to be in OPERATE dishMode",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
        )

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the dish must be in the TRACK pointingState'"
            "dish device"
            f"({central_node_mid.dish_master_dict[dish_id].dev_name()}) "
            "is expected to be in TRACK pointingState",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
        )

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the DishLeafNode must be in the TRACK pointingState'"
            "dish device"
            f"({central_node_mid.dish_leaf_node_dict[dish_id].dev_name()}) "
            "is expected to be in TRACK pointingState",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
        )

    event_tracer.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    csp = subarray_node.subarray_devices.get("csp_subarray")
    sdp = subarray_node.subarray_devices.get("sdp_subarray")

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "SDP Subarray device"
        f"({sdp.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "CSP Subarray device"
        f"({csp.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray is in READY obsState'"
        "TMC Subarray Node device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )


@then("with command Scan TMC subarray transitions to obsState SCANNING")
@given("with command Scan TMC subarray transitions to obsState SCANNING")
def invoke_scan(
    subarray_node, command_input_factory, event_tracer: TangoEventTracer
):
    """
    A method to invoke Scan command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        event_recorder: Fixture for EventRecorder class
    """
    event_tracer.clear_events()
    scan_input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    subarray_node.execute_transition("Scan", scan_input_json)

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN/THEN" STEP: '
        "'the subarray must be in the SCANNING obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in SCANNING obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )


@given(
    parsers.parse(
        "the TMC subarray transitions to obsState READY when scan"
        + " duration {scan_duration1} is over"
    )
)
def check_automatic_endscan_with_scan_duration1(
    subarray_node, event_tracer: TangoEventTracer, scan_duration1
):
    """
    A method to check if EndScan is successful.

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        scan_duration1 (str): scan duration required
    """
    time.sleep(int(scan_duration1))
    logging.info("Scan 1 duration is: %s", scan_duration1)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the READY obsState' "
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in READY obstate with scan duration1",
    ).within_timeout(100).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
    logging.info(
        "SubarrayNode obsstate is: %s", subarray_node.subarray_node.obsState
    )


@then(
    parsers.parse(
        "the TMC subarray transitions to obsState READY when scan"
        + " duration {scan_duration2} is over"
    )
)
def check_automatic_endscan_with_scan_duration2(
    subarray_node, event_tracer: TangoEventTracer, scan_duration2
):
    """
    A method to check if EndScan is successful.

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        scan_duration2 (str): scan duration required
    """
    time.sleep(int(scan_duration2))
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the READY obsState' "
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in READY obstate scan duration2",
    ).within_timeout(100).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )


@given("with command End TMC subarray transitions to obsState IDLE")
def invoke_end_command(
    subarray_node, event_tracer: TangoEventTracer, central_node_mid
):
    """
    This method invokes End command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
    """
    _, pytest.unique_id = subarray_node.execute_transition("End")

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the dish must be in the READY PointingState'"
            "dish device"
            f"({central_node_mid.dish_master_dict[dish_id].dev_name()}) "
            "is expected to be in READY PointingState",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.READY,
        )

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the DishLeafNode must be in the READY PointingState'"
            "dish leaf node device"
            f"({central_node_mid.dish_leaf_node_dict[dish_id].dev_name()}) "
            "is expected to be in READY PointingState",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.READY,
        )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Subarray Node device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(100).has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )


@when(
    parsers.parse(
        "the next configure command is issued to the TMC"
        + " subarray with {receiver_band2} and {scan_duration2} sec"
    )
)
def invoke_next_configure(
    subarray_node, command_input_factory, receiver_band2, scan_duration2
):
    """
    A method to invoke Configure command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        receiver_band2 (str) : receiver band for configure command
        scan_duration2 (str) : scan duration required

    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input = json.loads(configure_input_json)
    configure_input["dish"]["receiver_band"] = receiver_band2
    configure_input["tmc"]["scan_duration"] = float(scan_duration2)
    configure_input["csp"]["common"]["frequency_band"] = receiver_band2

    _, pytest.unique_id = subarray_node.execute_transition(
        "Configure", json.dumps(configure_input)
    )
