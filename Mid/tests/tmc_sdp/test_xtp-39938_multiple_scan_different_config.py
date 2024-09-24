"""Test TMC-SDP multiple scans with different resources and configurations
 functionality"""

import logging

import pytest
from pytest_bdd import scenario
from ska_ser_logging import configure_logging

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.skip(reason="This test case is not in the scope of this story")
@pytest.mark.tmc_sdp
@scenario(
    "../../features/tmc_sdp/xtp-39938_multiple_scan_different_config.feature",
    "TMC Mid executes multiple scans with different resources "
    "and configurations",
)
def test_tmc_sdp_long_sequences():
    """
    Test case to verify TMC-SDP functionality  multiple scans with different
    resources and configurations functionality
    """
