@XTP- @XTP- @TEAM_SAHYADRI
Scenario: ON to STANDBY - CMD on mid telescope
    Given a mid telescope
    When I start up the telescope
    Then SDP, CSP must go to ON state
    And DishMaster <dish_ids> must transition to STANDBY-FP mode
    When I put the telescope to STANDBY
    Then the SDP, CSP  must go to STANDBY state
    And the SDP,CSP must go to OFF state
    And DishMaster <dish_ids> must transition to STANDBY-LP mode

    Examples:
        | dish_ids                                   |
        | dish_001,dish_036,dish_063,dish_100        |
