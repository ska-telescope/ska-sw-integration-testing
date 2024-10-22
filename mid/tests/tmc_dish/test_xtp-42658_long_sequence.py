"""Test module for long sequence functionality

This module tests the TMC-DISH long sequence functionality, ensuring that
a sequence of commands including configuration, scanning, and reconfiguration
are executed successfully and the system transitions
through the expected states.
"""

import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.enum import DishMode, PointingState


@pytest.mark.skip(reason="This test case is not in the scope of this story")
@pytest.mark.tmc_dish
@scenario(
    "../../mid/features/tmc_dish/xtp-42658_long_sequence.feature",
    "TMC executes long sequence of commands successfully",
)
def test_tmc_dish_long_sequence_functionality():
    """
    Test case to verify TMC-DISH long sequence functionality
    """


@given("TMC subarray is in IDLE obsState")
def check_subarray_obsState_idle(
    subarray_node,
    central_node_mid,
    event_tracer: TangoEventTracer,
    command_input_factory,
):
    """
    Method to check if the TMC subarray is in IDLE obsState.

    This function subscribes to the obsState event of the subarray node and
    assigns resources to the central node. It verifies that the subarray
    transitions to the IDLE obsState and that the longRunningCommandResult
    indicates a successful execution with ResultCode.OK.

    Args:
        subarray_node : A fixture for SubarrayNode tango device class
        central_node_mid : A fixture for CentralNode tango device class
        event_recorder: A fixture for EventRecorder class
        command_input_factory: A fixture for JsonFactory class
    """
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


@when(
    parsers.parse(
        "I configure the subarray {subarray_id} with {receiver_band_1}"
    )
)
def configure_subarray(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
    subarray_id: str,
    receiver_band_1: str,
):
    """
    A method to invoke first Configure command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        command_input_factory: fixture for creating input required
        for command
        subarray_id (str): Subarray ID
        receiver_band_1 (str): receiver band 1 for configure command
    """
    event_tracer.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input_json = json.loads(input_json)
    configure_input_json["dish"]["receiver_band"] = receiver_band_1
    configure_input_json["csp"]["common"]["frequency_band"] = "1"
    central_node_mid.set_subarray_id(subarray_id)
    _, pytest.unique_id = subarray_node.store_configuration_data(
        json.dumps(configure_input_json)
    )
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
            'FAILED ASSUMPTION IN "WHEN" STEP: '
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
            'FAILED ASSUMPTION IN "WHEN" STEP: '
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
            'FAILED ASSUMPTION IN "WHEN" STEP: '
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
            'FAILED ASSUMPTION IN "WHEN" STEP: '
            "'the DishLeafNode must be in the TRACK pointingState'"
            "dish device"
            f"({central_node_mid.dish_leaf_node_dict[dish_id].dev_name()}) "
            "is expected to be in TRACK pointingState",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
        )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
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
        'FAILED ASSUMPTION IN "WHEN" STEP: '
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


@when(parsers.parse("I issue End command to the subarray {subarray_id}"))
def end_configuration_on_subarray(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_tracer: TangoEventTracer,
    subarray_id: str,
):
    """
    A method to invoke end command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        subarray_id (str): Subarray ID
    """
    central_node_mid.set_subarray_id(subarray_id)
    _, pytest.unique_id = subarray_node.execute_transition("End")
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "WHEN" STEP: '
            "'the dish must be in the READY pointingState'"
            "dish device"
            f"({central_node_mid.dish_master_dict[dish_id].dev_name()}) "
            "is expected to be in READY pointingState",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.READY,
        )
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "WHEN" STEP: '
            "'the DishLeafNode must be in the READY pointingState'"
            "dish device"
            f"({central_node_mid.dish_leaf_node_dict[dish_id].dev_name()}) "
            "is expected to be in READY pointingState",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.READY,
        )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
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
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Central Node device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )


@when(
    parsers.parse(
        "I reconfigure subarray {subarray_id} with {receiver_band_2}"
    )
)
def reconfigure_subarray(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
    subarray_id: str,
    receiver_band_2: str,
):
    """
    A method to invoke second Configure command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        subarray_id (str): Subarray ID
        receiver_band_1 (str): receiver band 1 for configure command
    """
    input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input_json = json.loads(input_json)
    configure_input_json["dish"]["receiver_band"] = receiver_band_2
    configure_input_json["csp"]["common"]["frequency_band"] = "2"
    central_node_mid.set_subarray_id(subarray_id)
    _, pytest.unique_id = subarray_node.execute_transition(
        "Configure", json.dumps(configure_input_json)
    )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "WHEN" STEP: '
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
            'FAILED ASSUMPTION IN "WHEN" STEP: '
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
            'FAILED ASSUMPTION IN "WHEN" STEP: '
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
            'FAILED ASSUMPTION IN "WHEN" STEP: '
            "'the DishLeafNode must be in the TRACK pointingState'"
            "dish device"
            f"({central_node_mid.dish_leaf_node_dict[dish_id].dev_name()}) "
            "is expected to be in TRACK pointingState",
        ).within_timeout(60).has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
        )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
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
        'FAILED ASSUMPTION IN "WHEN" STEP: '
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


@when(parsers.parse("I issue scan command with {scan_id} on subarray"))
def invoke_scan(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    scan_id: str,
):
    """
    A method to invoke Scan command

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        event_recorder: Fixture for EventRecorder class
        scan_id (str): scan id for DISH components
    """
    scan_input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )

    _, pytest.unique_id = subarray_node.execute_transition(
        "Scan", scan_input_json
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_tracer.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "scanID"
        )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
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


@then("tmc subarraynode reports SCANNING obsState")
def check_tmc_subarray_scanning(
    subarray_node: SubarrayNodeWrapper,
    event_tracer: TangoEventTracer,
):
    """Checks if SubarrayNode's obsState attribute value is SCANNING

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
    """
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
