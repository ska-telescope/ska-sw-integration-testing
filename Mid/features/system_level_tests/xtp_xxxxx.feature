@XTP- @XTP- @TEAM_SAHYADRI
Scenario: Starting up low telescope
    Given a low telescope
    When I invoke the ON command on the telescope
    Then the SDP, CSP and DISH goes to ON state
    And the telescope goes to ON state

@XTP- @XTP- @TEAM_SAHYADRI
Scenario: Switch off the low telescope
    Given a low telescope
    And an Telescope consisting of SDP, CSP and DISH that is ON
    When I switch off the telescope
    Then the SDP,CSP and DISH must be OFF 

@XTP- @XTP- @TEAM_SAHYADRI
Scenario: Standby the low telescope
    Given a low telescope
    And a telescope consisting of SDP, CSP and DISH that is ON
    When I invoke STANDBY command on the telescope
    Then the telescope goes to STANDBY state