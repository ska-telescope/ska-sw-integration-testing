# This BDD test performs TMC-SDP pairwise testing to verify healthState unhappy path.
@XTP-39507 @XTP-29381 @Team_SAHYADRI @tmc_sdp_unhappy
Scenario: SDP Subarray report the error when one of the SDP's component is unavailable
    Given a Telescope consisting of TMC,SDP,simulated CSP and simulated Dish 
    And the telescope is in ON state
    And the subarray is in EMPTY obsState
    When one of the SDP's component subsystem is made unavailable
    And I assign resources to the subarray <subarray_id>
    Then SDP subarray report the unavailability of SDP Component
    And TMC should report the error to client
    And the TMC SubarrayNode <subarray_id> stuck in RESOURCING
    Examples: 
        | subarray_id |
        | 1           | 