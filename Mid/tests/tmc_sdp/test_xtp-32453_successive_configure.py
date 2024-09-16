"""Test TMC-SDP Reconfigure functionality"""

import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.utils.common_utils import (
    wait_added_for_skb372,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-32453_successive_configure_with_real_sdp.feature",
    "TMC validates reconfigure functionality with real sdp devices",
)
def test_tmc_sdp_reconfigure_resources():
    """
    Test case to verify TMC-SDP reconfigure functionality
    """


@given("a TMC and SDP")
def given_a_tmc(central_node_mid, event_recorder, subarray_node):
    """A method to define TMC and SDP and subscribe ."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("sdp_subarray"), "obsState"
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("csp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")


@given(parsers.parse("a subarray {subarray_id} in the IDLE obsState"))
def telescope_is_in_idle_state(
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node,
):
    """A method to move subarray into the IDLE ObsState."""
    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid_multiple_scantype", command_input_factory
    )

    assign_str = json.loads(assign_input_json)
    # Here we are adding this to get an event of ObsState CONFIGURING from SDP
    # Subarray
    assign_str["sdp"]["processing_blocks"][0]["parameters"][
        "time-to-ready"
    ] = 2

    _, unique_id = central_node_mid.store_resources(json.dumps(assign_str))

    check_subarray_instance(
        subarray_node.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )


@when(parsers.parse("the command configure is issued with {input_json1}"))
def execute_initial_configure_command(
    subarray_node, command_input_factory, input_json1, event_recorder
):
    """ "A method to invoke configure command"""

    configure_json = prepare_json_args_for_commands(
        input_json1, command_input_factory
    )

    wait_added_for_skb372()
    subarray_node.execute_transition("Configure", argin=configure_json)


@when("the subarray transitions to obsState READY")
def check_subarray_in_ready(subarray_node, event_recorder):
    """A method to check SDP subarray obsstate"""

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )


@when(
    parsers.parse(
        "the next successive configure command is issued with {input_json2}"
    )
)
def execute_next_configure_command(
    subarray_node, command_input_factory, input_json2
):
    """ "A method to invoke configure command"""

    configure_json = prepare_json_args_for_commands(
        input_json2, command_input_factory
    )
    wait_added_for_skb372()
    subarray_node.execute_transition("Configure", argin=configure_json)

    # TODO :: Issue is raised with SDP team , awating for
    #  confirmation to raise it as bug
    # assert event_recorder.has_change_event_occurred(
    #     subarray_node.subarray_devices["sdp_subarray"],
    #     "obsState",
    #     ObsState.CONFIGURING,
    # )


@then(
    parsers.parse(
        "the subarray {subarray_id} reconfigures changing its "
        "obsState to READY"
    )
)
def check_subarray_in_ready_in_reconfigure(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstate"""

    # TODO :: Issue is raised with SDP team ,
    #  awating for confirmation to raise it as bug
    # check_subarray_instance(
    #     central_node_mid.subarray_devices.get("sdp_subarray"), subarray_id
    # )
    #
    # assert event_recorder.has_change_event_occurred(
    #     subarray_node.subarray_devices["sdp_subarray"],
    #     "obsState",
    #     ObsState.READY,
    # )

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
