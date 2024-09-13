Feature:  TMC Low executes long running sequences with real sdp devices

	@XTP-39894 @XTP-29227 @Team_HIMALAYA
	Scenario: TMC Low executes configure-scan sequence of commands successfully
		Given the Telescope is in ON state
		When I assign resources to TMC SubarrayNode <subarray_id>
		And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
		And end the configuration on TMC SubarrayNode <subarray_id>
		And release the resources on TMC SubarrayNode <subarray_id>
		Then TMC SubarrayNode transitions to EMPTY ObsState
		
		Examples:
		    |subarray_id   |scan_types                                   |scan_ids     |
		    |1             |["science_A"]                                |["1"]        |
		    |1             |["science_A", "target:a"]                    |["1","2"]    |
		    |1             |["science_A", "science_A"]                   |["1","2"]    |
		    |1             |["science_A", "science_A"]                   |["1","1"]    |
		    |1             |["science_A", "target:a", "callibration_B"]  |["1","2","3"]|



	@XTP-39896 @XTP-29227 @Team_HIMALAYA
	Scenario: TMC Low executes multiple scans with same configuration successfully
		Given the Telescope is in ON state
		When I assign resources to TMC SubarrayNode <subarray_id>
		And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
		And reperform scan with same configuration <scan_types> and new scan id
		And end the configuration on TMC SubarrayNode <subarray_id>
		And release the resources on TMC SubarrayNode <subarray_id>
		Then TMC SubarrayNode transitions to EMPTY ObsState
		
		Examples:
		    |subarray_id  |scan_ids |scan_types     |
		    |1            |["1"]    |["science_A"]  |


	@XTP-39897 @XTP-29227 @Team_HIMALAYA
	Scenario: TMC Low executes multiple scans with different resources and configurations
		Given the Telescope is in ON state
		When I assign resources to TMC SubarrayNode <subarray_id>
		And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
		And end the configuration on TMC SubarrayNode <subarray_id>
		And release the resources on TMC SubarrayNode <subarray_id>
		And I reassign with new resources to TMC SubarrayNode <subarray_id>
		And configure and scan TMC SubarrayNode <subarray_id> for <new_scan_types> and <new_scan_ids>
		And end the configuration on TMC SubarrayNode <subarray_id>
		And release the resources on TMC SubarrayNode <subarray_id>
		Then TMC SubarrayNode transitions to EMPTY ObsState
		
		Examples:
			|subarray_id  |scan_ids  |scan_types      |new_scan_ids   |new_scan_types |
			|1            |["1"]     |["science_A"]   |["2"]          |["target:a"]   |