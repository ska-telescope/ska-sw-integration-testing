"""Test module for TMC-DISH End functionality"""

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
    "../features/tmc_dish/xtp-29417_end.feature",
    "TMC executes End command on DISH.LMC",
)
def test_tmc_dish_end():
    """
    Test case to verify TMC-DISH End functionality
    """


@given(parsers.parse("TMC subarray {subarray_id} is in READY ObsState"))
def check_subarray_obsstate(
    subarray_node,
    command_input_factory,
    event_tracer: TangoEventTracer,
    central_node_mid,
    subarray_id,
):
    """Method to check subarray is in READY obstate

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        event_recorder: Fixture for EventRecorder class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_id (str): Subarray ID
    """
    event_tracer.subscribe_event(subarray_node.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    central_node_mid.set_subarray_id(subarray_id)
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

    event_tracer.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )

    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    _, pytest.unique_id = subarray_node.execute_transition(
        "Configure", configure_input_json
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
            "'the dish must be in the OPERATE dishMode'"
            "dish device"
            f"({central_node_mid.dish_master_dict[dish_id].dev_name()}) "
            "is expected to be in OPERATE dishMode",
        ).within_timeout(160).has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
        )

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'the DishLeafNode must be in the OPERATE dishMode'"
            "dish device"
            f"({central_node_mid.dish_leaf_node_dict[dish_id].dev_name()}) "
            "is expected to be in OPERATE dishMode",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
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
    parsers.parse("I issue the End command to the TMC subarray {subarray_id}")
)
def invoke_end(central_node_mid, subarray_node, subarray_id):
    """A method to invoke End command

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_node: Fixture for a Subarray Node wrapper class
        subarray_id (str): Subarray ID
        event_recorder: Fixture for EventRecorder class
    """
    central_node_mid.set_subarray_id(subarray_id)
    _, pytest.unique_id = subarray_node.execute_transition("End")


@then(
    parsers.parse("the DishMaster {dish_ids} transitions pointingState READY")
)
def check_dish_mode_and_pointing_state(
    central_node_mid, event_tracer: TangoEventTracer, dish_ids
):
    """
    Method to check dishMode and pointingState of DISH

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        dish_ids (str): Comma-separated IDs of DISH components.
        command_input_factory: fixture for creating input required
        for command
    """
    for dish_id in dish_ids.split(","):
        log_events(
            {
                central_node_mid.dish_master_dict.get(dish_id): [
                    "pointingState"
                ],
            }
        )

    for dish_id in dish_ids.split(","):
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "THEN" STEP: '
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
            'FAILED ASSUMPTION IN "THEN" STEP: '
            "'the DishLeafNode must be in the READY PointingState'"
            "dish leaf node device"
            f"({central_node_mid.dish_leaf_node_dict[dish_id].dev_name()}) "
            "is expected to be in READY PointingState",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.READY,
        )


@then(
    parsers.parse(
        "TMC subarray {subarray_id} obsState transitions to IDLE obsState"
    )
)
def check_subarray_obsState_idle(
    central_node_mid,
    subarray_node,
    event_tracer: TangoEventTracer,
    subarray_id,
):
    """Method to check subarray is in IDLE obstate

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        subarray_id (str): Subarray ID
    """
    central_node_mid.set_subarray_id(subarray_id)

    log_events(
        {
            subarray_node.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
        }
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
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
