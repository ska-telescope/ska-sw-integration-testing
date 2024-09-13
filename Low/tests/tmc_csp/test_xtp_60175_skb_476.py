"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system with CSP resolution of SKB-476.
"""


import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_with_csp_low import (
    CentralNodeCspWrapperLow,
)
from tests.resources.test_harness.subarray_node_with_csp_low import (
    SubarrayNodeCspWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.constant_low import TIMEOUT


@scenario(
    "../features/tmc_csp/xtp_60175_verify_skb_476.feature",
    "verify SKB-476",
)
def test_verify_skb_476():
    """BDD test scenario for verifying SKB-476"""


@given("the Telescope is in ON state")
def given_a_tmc(
    central_node_real_csp_low: CentralNodeCspWrapperLow,
    event_tracer: TangoEventTracer,
):
    """
    This method invokes On command from central node and verifies
    the state of telescope after the invocation.
    Args:
        central_node_real_csp_low (CentralNodeCspWrapperLow): Object of
        Central node wrapper
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
    """
    central_node_real_csp_low.csp_master.adminMode = 0
    central_node_real_csp_low.csp_subarray1.adminMode = 0
    event_tracer.subscribe_event(central_node_real_csp_low.pst, "State")

    event_tracer.subscribe_event(central_node_real_csp_low.pst, "adminMode")
    event_tracer.subscribe_event(
        central_node_real_csp_low.csp_master, "adminMode"
    )
    event_tracer.subscribe_event(
        central_node_real_csp_low.csp_subarray1, "adminMode"
    )
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED ADMIN MODE: "
        "CSP Master device"
        f"({central_node_real_csp_low.csp_master.dev_name()}) "
        "is expected to be in Admin Mode ONLINE",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_real_csp_low.csp_master,
        "adminMode",
        0,
    )

    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED ADMIN MODE: "
        "CSP Master device"
        f"({central_node_real_csp_low.csp_master.dev_name()}) "
        "is expected to be in Admin Mode ONLINE",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_real_csp_low.csp_master,
        "adminMode",
        0,
    )

    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED ADMIN MODE: "
        "CSP Subarray device"
        f"({central_node_real_csp_low.csp_subarray1.dev_name()}) "
        "is expected to be in Admin Mode ONLINE",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_real_csp_low.csp_subarray1,
        "adminMode",
        0,
    )

    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED ADMIN MODE: "
        "PST device"
        f"({central_node_real_csp_low.pst.dev_name()}) "
        "is expected to be in Admin Mode ONLINE",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_real_csp_low.pst,
        "adminMode",
        0,
    )

    event_tracer.subscribe_event(
        central_node_real_csp_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_real_csp_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_real_csp_low.subarray_node, "obsState"
    )
    log_events(
        {
            central_node_real_csp_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            central_node_real_csp_low.subarray_node: ["obsState"],
        }
    )
    central_node_real_csp_low.move_to_on()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the telescope is is ON state'"
        "Central Node device"
        f"({central_node_real_csp_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_real_csp_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device"
        f"({central_node_real_csp_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the telescope is is ON state'"
        "PST device"
        f"({central_node_real_csp_low.pst.dev_name()}) "
        "is expected to be in State ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_real_csp_low.pst,
        "State",
        DevState.ON,
    )


@given("subarray node is in observation state IDLE")
def central_node_assign_resources(
    central_node_real_csp_low: CentralNodeCspWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """
    This method invokes AssignResources command on central node.

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        command_input_factory (JsonFactory): Object of json factory
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
    """
    central_node_real_csp_low.set_serial_number_of_cbf_processor()
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    result, pytest.unique_id = central_node_real_csp_low.perform_action(
        "AssignResources", assign_input_json
    )
    assert pytest.unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED

    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "Subarray Node device"
        f"({central_node_real_csp_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when(
    parsers.parse(
        "I invoke configure command without {key} " + "in csp configure json"
    )
)
def check_configure_json_and_invoke_command(
    command_input_factory: JsonFactory,
    subarray_node_real_csp_low: SubarrayNodeCspWrapperLow,
    key: str,
):
    """Method to verify the input json and invocation of conigure command
    on subarray node.

    Args:
        command_input_factory (JsonFactory): Object of json factory
        subarray_node_low (SubarrayNodeWrapperLow): Object of subarray
        node wrapper
        key (str): key that should be present in configure json
    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_low_without_timing_beams", command_input_factory
    )
    assert key not in json.loads(configure_input_json)["csp"]["lowcbf"].keys()
    subarray_node_real_csp_low.store_configuration_data(configure_input_json)


@then("csp subbaray node transitions to observation state READY")
def check_csp_obs_state_ready(
    event_tracer: TangoEventTracer,
    subarray_node_real_csp_low: SubarrayNodeCspWrapperLow,
):
    """Method to check observation state of subarray node
    after configure command.

    Args:
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
        subarray_node_low (SubarrayNodeWrapperLow): Object of subarray
        node wrapper
    """
    event_tracer.subscribe_event(
        subarray_node_real_csp_low.csp_subarray1, "obsState"
    )
    log_events(
        {
            subarray_node_real_csp_low.csp_subarray1: ["obsState"],
        }
    )
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "CSP Subarray Node device"
        f"({subarray_node_real_csp_low.csp_subarray1.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_real_csp_low.csp_subarray1,
        "obsState",
        ObsState.READY,
    )


@then("subarray node transitions to observation state READY")
def check_obs_state_ready(
    event_tracer: TangoEventTracer,
    subarray_node_real_csp_low: SubarrayNodeCspWrapperLow,
):
    """Method to check observation state of subarray node
    after configure command.

    Args:
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
        subarray_node_low (SubarrayNodeWrapperLow): Object of subarray
        node wrapper
    """
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "Subarray Node device"
        f"({subarray_node_real_csp_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
