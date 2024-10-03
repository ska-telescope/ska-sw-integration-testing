@XTP- @XTP- @TEAM_SAHYADRI
Scenario: ON to OFF - CMD on mid telescope
    Given a mid telescope
    When I invoke the ON command on the telescope
    Then the SDP, CSP and DISH <dish_ids> goes to STANDBY state
    Then the SDP, CSP and DISH <dish_ids> goes to ON state
    When I switch off the telescope
    Then the SDP,CSP and DISH must be OFF

    Examples:
        | dish_ids                           |
        | SKA001,SKA036,SKA063,SKA100        |

