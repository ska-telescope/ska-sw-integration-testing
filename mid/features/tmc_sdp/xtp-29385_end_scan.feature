# This BDD test performs TMC-SDP pairwise testing to verify EndScan command flow.
@XTP-29385 @XTP-29381 @Team_SAHYADRI @tmc_sdp
Scenario: TMC executes a EndScan command on SDP subarray
	Given the telescope is in ON state
	And TMC subarray <subarray_id> is in Scanning ObsState
	When I issue the Endscan command to the TMC subarray <subarray_id>
	Then the SDP subarray transitions to ObsState READY
	And the TMC subarray <subarray_id> transitions to ObsState READY
	Examples:
	| subarray_id |
	| 1 |
	