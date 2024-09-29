Feature: Default

	#This BDD test performs TMC-SDP pairwise testing to verify Scan command flow.
	@XTP-29456 @XTP-29227 @tmc_sdp
	Scenario: TMC executes a scan on SDP subarray 
		Given the subarray <subarray_id> obsState is READY
		When I issue scan command with scan Id <scan_id> on subarray <subarray_id>
		Then the subarray <subarray_id> obsState transitions to SCANNING
		And the sdp subarray <subarray_id> obsState transitions to READY after the scan duration elapsed
		And the TMC subarray <subarray_id> obsState transitions back to READY
		Examples:
		| subarray_id   | scan_id  |
		|  1            | 123      |