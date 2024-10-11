Scenario Outline: ON to OFF - CMD on mid telescope
    Given a mid telescope
    When I <command> the telescope
    Then SDP, CSP must go to <state> state
    And DishMaster must transition to <dish_mode> mode

    Examples:
        | command    | state | dish_mode   |
        | start up   | ON    | STANDBY-FP  |
        | switch off | OFF   | STANDBY-LP  |



