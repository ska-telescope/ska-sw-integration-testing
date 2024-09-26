# This BDD test performs TMC-CSP pairwise testing to verify Standby command flow.
@XTP-29583 @XTP-29251 @tmc_csp
Scenario: Standby the Telescope with real TMC and CSP devices
    Given a Telescope consisting of TMC, CSP, simulated DISH and simulated SDP devices
    And telescope is in ON state
    When I standby the telescope
    Then the csp controller must go to standby state
    And the csp subarray must go to off state
    And telescope state is STANDBY
    