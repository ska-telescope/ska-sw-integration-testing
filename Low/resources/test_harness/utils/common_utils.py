"""This module implement common utils
"""
import json
from os.path import dirname, join
from typing import List

from ska_control_model import ObsState

from tests.resources.test_harness.utils.wait_helpers import Waiter
from tests.resources.test_support.common_utils.result_code import ResultCode

TIMEOUT = 200


def check_scan_successful(
    subarray_node, event_recorder, scan_id, unique_id
) -> None:
    """
    1)SDP , TMC subarray  go to scanning
    2)scan_id attribute from SDP subarray reflects exact scan_id
    sent by TMC .This makes sure we are checking some more attributes
    from SDP .In future this can be extended to include other attribute
    verification as well.
    3)After scan duration is completed , end scan will be triggered
    taking system to READY state. Related Obs-state checks are  added.
    """

    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate(
        "SCANNING", [subarray_node.subarray_node]
    )
    the_waiter.wait(TIMEOUT)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.SCANNING,
        lookahead=10,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "scanID",
        int(scan_id),
        lookahead=10,
    )

    the_waiter.set_wait_for_specific_obsstate(
        "READY", [subarray_node.subarray_node]
    )
    the_waiter.wait(TIMEOUT)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
        lookahead=10,
    )

    the_waiter.set_wait_for_specific_obsstate(
        "READY", [subarray_node.subarray_node]
    )
    the_waiter.wait(TIMEOUT)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=10
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
        lookahead=15,
    )


def check_configure_successful(
    subarray_node, event_recorder, unique_id, scan_type, processed_scan_type
) -> None:
    """
    Adds check to verify if configure command is successful
    """
    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate(
        "READY", [subarray_node.subarray_devices["sdp_subarray"]]
    )
    the_waiter.wait(TIMEOUT)

    the_waiter.set_wait_for_specific_obsstate(
        "READY", [subarray_node.subarray_node]
    )
    the_waiter.wait(TIMEOUT)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=10
    )

    if scan_type != processed_scan_type:
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_devices["sdp_subarray"],
            "scanType",
            scan_type,
            lookahead=10,
        )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
        lookahead=10,
    )


def get_subarray_input_json(slug):
    """
    Args:
        slug (str): base name of file
    Return:
        Read and return content of file
    """
    assign_json_file_path = join(
        dirname(__file__),
        "..",
        "..",
        "..",
        "data",
        "subarray",
        f"{slug}.json",
    )
    with open(assign_json_file_path, "r", encoding="UTF-8") as f:
        assign_json = f.read()
    return assign_json


def get_centralnode_input_json(slug):
    """
    Args:
        slug (str): base name of file
    Return:
        Read and return content of file
    """
    assign_json_file_path = join(
        dirname(__file__),
        "..",
        "..",
        "..",
        "data",
        "centralnode",
        f"{slug}.json",
    )
    with open(assign_json_file_path, "r", encoding="UTF-8") as f:
        assign_json = f.read()
    return assign_json


def update_receptors_in_assign_json(
    assign_input_json: str, receptor_list: List[str]
) -> str:
    """
    Update the list of receptors in the given JSON string.

    Args:
        assign_input_json (str): Input JSON string containing SDP resources.
        receptor_list (List[str]): List of receptors to replace existing one.

    Returns:
        str: Updated JSON string with the list of receptors modified.

    """
    # Parse the input JSON string
    assign_input_json = json.loads(assign_input_json)

    # Update the list of receptors
    assign_input_json["sdp"]["resources"]["receptors"] = receptor_list

    # Convert the modified JSON back to a string
    assign_input_json = json.dumps(assign_input_json)

    return assign_input_json


class JsonFactory(object):
    """Implement methods required for getting json"""

    def create_subarray_configuration(self, json_type):
        """Read and return configuration json file from
            tests/data/subarray folder
        Args:
            json_type (str): Base name of file which is stored in data folder
        Return:
            config_json (str): Return configure json based json type provided
        """
        return get_subarray_input_json(json_type)

    def create_assign_resources_configuration(self, json_type):
        """Read and return configuration json file from
            tests/data/subarray folder
        Args:
            json_type (str): Base name of file which is stored in data folder
        Return:
            config_json (str): Return configure json based json type provided
        """
        return get_subarray_input_json(json_type)

    def create_centralnode_configuration(self, json_type):
        """Read and return configuration json file from
            tests/data/centralnode folder
        Args:
            json_type (str): Base name of file which is stored in data folder
        Return:
            config_json (str): Return configure json based json type provided
        """
        return get_centralnode_input_json(json_type)
