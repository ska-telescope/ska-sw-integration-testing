"""Test TMC Mid executes multiple scan with same configuration successfully"""

import logging

import pytest
from pytest_bdd import scenario
from ska_ser_logging import configure_logging

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.skip(reason="This test case is not in the scope of this story")
@pytest.mark.tmc_sdp
@scenario(
    "../../features/tmc_sdp/xtp-39931_multiple_scan_same_configuration."
    "feature",
    "TMC Mid executes multiple scan with same configuration successfully",
)
def test_tmc_sdp_successive_scan_sequences():
    """
    Test case to verify TMC-SDP  functionality TMC Mid executes multiple scan
    with same configuration successfully
    """
