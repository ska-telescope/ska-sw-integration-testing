@XTP-53197 @XTP-30488 @Team_HIMALAYA @tmc_mccs
Scenario Outline: Abort resourced MCCS and TMC subarray
  Given TMC subarray in obsState <obsstate>
  When I command it to Abort
  Then the MCCS subarray should go into an aborted obsstate
  And the TMC subarray obsState is transitioned to ABORTED

Examples:
  | obsstate |
  | IDLE     |
  | READY    |