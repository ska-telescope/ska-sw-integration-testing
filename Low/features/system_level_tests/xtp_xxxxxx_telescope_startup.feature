Scenario: Starting up low telescope
    Given a low telescope
    When I turn telescope to ON state
    Then the SDP, CSP and MCCS goes to ON state
    And the telescope goes to state ON

Scenario: Switch off the low telescope
    Given low telescope
    Given a Telescope consisting of SDP, CSP and MCCS that is ON
    When I switch off the telescope
    Then the SDP,CSP and MCCS must be off 

Scenario: Standby the low telescope
    Given low telescope
    Given a Telescope consisting of SDP, CSP and MCCS that is ON
    When I invoke stadby command on the telescope
    Then the telescope goes Standby state 