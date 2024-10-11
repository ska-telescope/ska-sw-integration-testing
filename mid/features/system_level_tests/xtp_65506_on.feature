@XTP- @XTP-65506 @TEAM_SAHYADRI
Scenario: Starting up mid telescope
    Given a mid telescope
    When I invoke the ON command on the telescope
    Then the SDP and CSP to ON state
    And DishMaster must transition to STANDBY-FP mode



