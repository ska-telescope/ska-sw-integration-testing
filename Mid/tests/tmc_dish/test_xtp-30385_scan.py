"""Test module for TMC-DISH Scan functionality
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events

from Mid.tests.resources.test_harness.central_node_mid import (
    CentralNodeWrapperMid,
)
from Mid.tests.resources.test_harness.constant import COMMAND_COMPLETED
from Mid.tests.resources.test_harness.helpers import (
    check_long_running_command_status,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from Mid.tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from Mid.tests.resources.test_harness.utils.common_utils import JsonFactory
from Mid.tests.resources.test_support.enum import DishMode, PointingState


@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-30385_scan.feature",
    "TMC executes Scan command on DISH",
)
def test_tmc_dish_scan():
    """
    Test case to verify TMC-DISH Scan functionality
    """


@given(parsers.parse("TMC subarray {subarray_id} is in READY obsState"))
def check_subarray_obsState_ready(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    central_node_mid: CentralNodeWrapperMid,
    subarray_id: str,
):
    """
    Method to check subarray is in READY obsState

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        event_recorder: Fixture for EventRecorder class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_id (str): Subarray ID
        dish_ids (str): Comma-separated IDs of DISH components.
    """

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    central_node_mid.set_subarray_id(subarray_id)
    _, pytest.unique_id = central_node_mid.store_resources(assign_input_json)

    event_tracer.subscribe_event(subarray_node.subarray_node, "obsState")
    event_tracer.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
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
        "TMC Central Node device"
        f"({central_node_mid.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(60).has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )
    configure_json = json.loads(configure_input_json)
    configure_json["tmc"]["scan_duration"] = 10.0
    _, pytest.unique_id = subarray_node.execute_transition(
        "Configure", json.dumps(configure_json)
    )


@given(
    parsers.parse(
        "Dish {dish_ids} is in dishMode OPERATE with pointingState TRACK"
    )
)
def check_dish_mode_and_pointing_state(
    central_node_mid: CentralNodeWrapperMid,
    event_tracer: TangoEventTracer,
    dish_ids: str,
    subarray_node: SubarrayNodeWrapper,
):
    """
    Method to check dishMode and pointingState

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        dish_ids (str): Comma-separated IDs of DISH components.
        subarray_node: Fixture for a Subarray Node wrapper class
    """
    for dish_id in dish_ids.split(","):
        log_events(
            {
                central_node_mid.dish_master_dict.get(dish_id): ["dishMode"],
                central_node_mid.dish_master_dict.get(dish_id): [
                    "pointingState"
                ],
            }
        )

    for dish_id in dish_ids.split(","):
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
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
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
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
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


@when(
    parsers.parse("I issue the Scan command to the TMC subarray {subarray_id}")
)
def invoke_scan(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    subarray_id: str,
):
    """
    A method to invoke Scan command

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        subarray_id (str): Subarray ID
    """
    scan_input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    central_node_mid.set_subarray_id(subarray_id)
    _, pytest.unique_id = subarray_node.execute_transition(
        "Scan", scan_input_json
    )


@then(parsers.parse("{scan_id} assigned to Dish {dish_ids}"))
def check_scan_id(
    central_node_mid: CentralNodeWrapperMid,
    event_tracer: TangoEventTracer,
    dish_ids: str,
    scan_id: str,
):
    """
    Method to check scan_id value of DISH

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        dish_ids (str): Comma-separated IDs of DISH components.
        scan_id (str): scanID for DISH components
    """
    for dish_id in dish_ids.split(","):
        event_tracer.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "scanID"
        )

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "THEN" STEP: '
            "'the dish must be in the assigned scan_id'"
            "dish device"
            f"({central_node_mid.dish_master_dict[dish_id].dev_name()}) "
            "is expected to be in assigned scan_id",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "scanID",
            scan_id,
        )


@then(
    parsers.parse(
        "the Dish {dish_ids} remains in dishMode"
        + " OPERATE and pointingState TRACK"
    )
)
def check_dish_mode_and_pointing_state_after_scan(
    central_node_mid: CentralNodeWrapperMid,
    dish_ids: str,
):
    """
    Method to check dishMode and pointingState of DISH

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        dish_ids (str): Comma-separated IDs of DISH components.
    """
    for dish_id in dish_ids.split(","):
        assert (
            central_node_mid.dish_master_dict[dish_id].dishMode
            == DishMode.OPERATE
        )
        assert (
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode
            == DishMode.OPERATE
        )
        assert (
            central_node_mid.dish_master_dict[dish_id].pointingState
            == PointingState.TRACK
        )
        assert (
            central_node_mid.dish_leaf_node_dict[dish_id].pointingState
            == PointingState.TRACK
        )
        assert check_long_running_command_status(
            central_node_mid.dish_master_dict[dish_id],
            "longRunningCommandStatus",
            "_Scan",
            "COMPLETED",
        )


@then("TMC SubarrayNode transitions to obsState SCANNING")
def tmc_subarray_scanning(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    event_tracer: TangoEventTracer,
    subarray_id: str,
):
    """
    Checks if SubarrayNode's obsState attribute value is SCANNING

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        subarray_id (str): Subarray ID
    """
    central_node_mid.set_subarray_id(int(subarray_id))
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the SCANNING obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in SCANNING obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )


@then(
    "TMC SubarrayNode transitions to obsState READY"
    + " once the scan duration is elapsed"
)
def check_subarray_obsstate_ready(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    event_tracer: TangoEventTracer,
    subarray_id: str,
):
    """
    Checks if SubarrayNode's obsState attribute value is READY

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        subarray_id (str): Subarray ID
    """
    central_node_mid.set_subarray_id(int(subarray_id))

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
