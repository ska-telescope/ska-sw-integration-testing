@XTP-64114 @XTP-28348 @XTP-64112 @TEAM_HIMALAYA
Scenario: Starting up low telescope
    Given a low telescope
    When I invoke the ON command on the telescope
    Then the SDP, CSP and MCCS go to ON state
    And the telescope go to ON state

@XTP-64122 @XTP-28348 @XTP-64112 @TEAM_HIMALAYA
Scenario: Switch off the low telescope
    Given a low telescope
    And a Telescope consisting of SDP, CSP and MCCS that is ON
    When I invoke the OFF command on the telescope
    Then the SDP and MCCS go to OFF state
    And the CSP remains in ON state

@XTP-64119 @XTP-28348 @XTP-64112 @TEAM_HIMALAYA
Scenario: Standby the low telescope
    Given a low telescope
    And a Telescope consisting of SDP, CSP and MCCS that is ON
    When I invoke the STANDBY command on the telescope
    Then the telescope go to STANDBY state