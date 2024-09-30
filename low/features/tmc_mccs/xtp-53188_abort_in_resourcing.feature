@XTP-53188 @XTP-30488 @Team_HIMALAYA @tmc_mccs
Scenario: Abort assigning using TMC
    Given TMC and MCCS subarray are busy assigning resources
    When I command it to Abort
    Then the MCCS subarray should go into an ABORTED obsstate
    And the TMC subarray obsState is transitioned to ABORTED