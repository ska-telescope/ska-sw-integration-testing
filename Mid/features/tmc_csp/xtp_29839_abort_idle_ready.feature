# This BDD test performs TMC-CSP pairwise testing to verify Abort command flow in obsStates IDLE and READY.
@XTP-29839 @XTP-29583 @Team_SAHYADRI
Scenario: TMC executes an Abort on CSP subarray
	Given the telescope is in ON state
	And the TMC subarray <subarray_id> and CSP subarray <subarray_id> are in ObsState <obsstate>
	When I issued the Abort command to the TMC subarray
	Then the CSP subarray transitions to ObsState ABORTED
	And the TMC subarray transitions to ObsState ABORTED
	Examples:
	| subarray_id | obsstate |
	| 1           | IDLE     |
	| 1           | READY    |
	