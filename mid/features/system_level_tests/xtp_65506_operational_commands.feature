@XTP- @XTP- @TEAM_SAHYADRI
Scenario: ON to OFF - CMD on mid telescope
    Given a mid telescope
    When I start up the telescope
    Then SDP, CSP must go to ON state
    AND DishMaster <dish_ids> must transition to STANDBY-FP mode
    When I put the telescope to STANDBY
    Then the SDP, CSP  must go to STANDBY state
    When I switch off the telescope
    Then the SDP,CSP must go to OFF state
    And DishMaster <dish_ids> must transition to STANDBY-LP mode

    Examples:
        | dish_ids                           |
        | SKA001,SKA036,SKA063,SKA100        |

