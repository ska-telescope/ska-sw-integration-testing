"""Init Module of tests folder
"""
from assertpy import add_extension

from tests.resources.test_harness.utils.assertions import (
    has_desired_result_code_message_in_lrcr_event,
)

add_extension(has_desired_result_code_message_in_lrcr_event)
