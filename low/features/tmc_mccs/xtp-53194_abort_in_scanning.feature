@XTP-53194 @XTP-30488 @Team_HIMALAYA @tmc_mccs
Scenario: Abort scanning MCCS using TMC
    Given TMC and MCCS subarray are busy scanning
    When I command it to Abort
    Then the MCCS subarray should go into an aborted obsstate
    And the TMC subarray node obsState is transitioned to ABORTED