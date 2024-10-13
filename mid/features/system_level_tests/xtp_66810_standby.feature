@XTP-66801 @XTP-66810 @TEAM_SAHYADRI
Scenario: Standby the mid telescope
    Given a mid telescope
    And a Telescope consisting of SDP, CSP and DISH that is ON
    When I invoke the STANDBY command on the telescope
    Then the telescope go to STANDBY state
