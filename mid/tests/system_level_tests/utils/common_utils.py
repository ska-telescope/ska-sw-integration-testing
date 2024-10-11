from ska_control_model import ResultCode
from tests.system_level_tests.conftest import SubarrayTestContextData


def _get_long_run_command_id(context_fixt: SubarrayTestContextData) -> str:
    return context_fixt.when_action_result[1][0]


def _get_expected_long_run_command_result(context_fixt) -> tuple[str, str]:
    return (
        _get_long_run_command_id(context_fixt),
        f'[{ResultCode.OK.value}, "Command Completed"]',
    )
