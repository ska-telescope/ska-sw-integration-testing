

Scenario: Starting up low telescope
    Given low telescope
    When I turn telescope to ON state
    Then the central node goes to state ON

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