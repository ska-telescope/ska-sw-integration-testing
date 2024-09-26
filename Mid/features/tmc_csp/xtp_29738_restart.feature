# This BDD test performs TMC-CSP pairwise testing to verify Restart command flow.
@XTP-29738 @XTP-29583 @Team_SAHYADRI @tmc_csp
Scenario: TMC executes a Restart on CSP subarray when subarray completes abort
	Given the telescope is in ON state
	And TMC and CSP subarray <subarray_id> is in ObsState ABORTED
	When I command it to Restart
	Then the CSP subarray <subarray_id> transitions to ObsState EMPTY
	And the TMC subarray <subarray_id> transitions to ObsState EMPTY
	Examples:
	| subarray_id |
	| 1           |
	