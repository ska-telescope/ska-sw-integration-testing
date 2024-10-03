# This BDD test performs TMC-CSP pairwise testing to verify Abort command flow in obsState SCANNING.
@XTP-29842 @XTP-29583 @Team_SAHYADRI
Scenario: Abort scanning CSP using TMC
	Given the telescope is in ON state
	And the TMC subarray <subarray_id> and CSP subarray <subarray_id> are busy in SCANNING
	When I issued the Abort command to the TMC subarray
	Then the CSP subarray transitions to ObsState ABORTED
	And the TMC subarray transitions to ObsState ABORTED
	Examples:
	| subarray_id |
	| 1           |
	