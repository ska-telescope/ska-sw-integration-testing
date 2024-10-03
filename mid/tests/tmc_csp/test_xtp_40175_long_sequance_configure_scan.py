"""Test TMC-CSP Long Sequence of configure-scan functionality"""

import logging

import pytest
from pytest_bdd import parsers, scenario, when
from ska_ser_logging import configure_logging
from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_commands,
    update_scan_id,
    update_scan_type,
)
from tests.resources.test_harness.utils.common_utils import (
    check_configure_successful_csp,
    check_scan_successful_csp,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.skip(reason="This test case is not in the scope of this story")
@pytest.mark.tmc_csp
@scenario(
    "../../mid/features/tmc_csp/xtp_40175_long_sequence_configure_scan.feature",
    "TMC Mid executes configure-scan sequence of commands successfully",
)
def test_tmc_csp_long_sequences():
    """
    Test case to verify TMC-CSP functionality with long sequences of commands
    """


@when(
    parsers.parse(
        "configure and scan TMC SubarrayNode {subarray_id} "
        "for each {scan_types} and {scan_ids}"
    )
)
def execute_configure_scan_sequence(
    subarray_node,
    command_input_factory,
    scan_ids,
    event_recorder,
    subarray_id,
    scan_types,
):
    """A method to invoke configure and scan  command"""
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "scanID"
    )

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        "configure1_mid", command_input_factory
    )

    combined_dict = dict(zip(eval(scan_ids), eval(scan_types)))

    for scan_id, scan_type in combined_dict.items():
        configure_json = update_scan_type(configure_json, scan_type)
        _, unique_id = subarray_node.execute_transition(
            "Configure", argin=configure_json
        )

        check_configure_successful_csp(
            subarray_node, event_recorder, unique_id, scan_type
        )

        scan_json = prepare_json_args_for_commands(
            "scan_mid", command_input_factory
        )

        scan_json = update_scan_id(scan_json, scan_id)

        _, unique_id = subarray_node.store_scan_data(scan_json)

        check_scan_successful_csp(
            subarray_node, event_recorder, scan_id, unique_id
        )

        LOGGER.debug(
            f"Configure-scan sequence completed for {scan_id} "
            f"and scan_type {scan_type}"
        )
