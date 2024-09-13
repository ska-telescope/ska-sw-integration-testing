Feature: Default

	
	@XTP-34886 @XTP-29227 @Team_HIMALAYA
	Scenario: TMC Subarray report the exception triggered by the SDP subarray when it encounters a duplicate eb-id/pb-id.
		Given a Telescope consisting of TMC, SDP, simulated CSP and simulated MCCS
		And The TMC and SDP subarray <subarray_id> in the IDLE obsState using <input_json1>
		When TMC executes another AssignResources command with a <duplicate_id> from <input_json1>
		And SDP subarray <subarray_id> throws an exception and remain in IDLE obsState
		And TMC subarray <subarray_id> remain in RESOURCING obsState
		Then exception is propagated to central node
		Examples:
            | subarray_id  | input_json1           | duplicate_id |
            | 1            | assign_resources_json | eb_id        |
            | 1            | assign_resources_json2 | pb_id        |