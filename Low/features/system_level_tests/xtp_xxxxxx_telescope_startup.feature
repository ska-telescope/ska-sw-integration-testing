Scenario: Starting up low telescope
    Given an low telescope
    When I turn telescope to ON state
    Then the SDP, CSP and MCCS goes to ON state
    And the telescope goes to state ON

Scenario: Switch off the low telescope
    Given an low telescope
    And an Telescope consisting of SDP, CSP and MCCS that is ON
    When I switch off the telescope
    Then the SDP,CSP and MCCS must be OFF 

Scenario: Standby the low telescope
    Given an low telescope
    And an Telescope consisting of SDP, CSP and MCCS that is ON
    When I invoke standby command on the telescope
    Then the telescope goes to Standby state 