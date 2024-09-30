@XTP-64114 @XTP-64112 @TEAM_HIMALAYA
Scenario: Starting up low telescope
    Given a low telescope
    When I invoke the ON command on the telescope
    Then the SDP, CSP and MCCS goes to ON state
    And the telescope goes to ON state

@XTP-64119 @XTP-64122 @TEAM_HIMALAYA
Scenario: Switch off the low telescope
    Given a low telescope
    And an Telescope consisting of SDP, CSP and MCCS that is ON
    When I switch off the telescope
    Then the SDP and MCCS must be OFF and CSP remains in ON state 

@XTP-64119 @XTP-64112 @TEAM_HIMALAYA
Scenario: Standby the low telescope
    Given a low telescope
    And an Telescope consisting of SDP, CSP and MCCS that is ON
    When I invoke STANDBY command on the telescope
    Then the telescope goes to STANDBY state