# This BDD test performs Assign and Release command flow on Mid integration

Given a mid telescope
    When I <command> the subarray
    Then SDP, CSP must go to <state> ObsState
    And the Mid subarray must be in <final_obs_state> ObsState

Examples:
    | command          | state       | final_obs_state |
    | assign resources  | RESOURCING  | IDLE            |
    | release resources | EMPTY       | EMPTY           |