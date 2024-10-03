# This BDD test performs TMC-CSP pairwise testing to verify Off command flow.
@XTP-29583 @XTP-29250 @tmc_csp
Scenario: Turn Off Telescope with real TMC and CSP devices
    Given a Telescope consisting of TMC, CSP, simulated DISH and simulated SDP devices
    And telescope is in ON state
    When I switch off telescope
    Then the CSP must go to OFF state
    And telescope state is OFF
    