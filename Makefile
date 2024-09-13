# Project makefile for a ska-sw-integration-testing project. You should normally only need to modify
# CAR_OCI_REGISTRY_USER and PROJECT below.

# Low-specific variables
LOW_TANGO_HOST ?= tango-low-databaseds:10000
LOW_KUBE_NAMESPACE ?= ska-low-integration
LOW_CLUSTER_DOMAIN ?= cluster.local



# Test command for Low component
test-low:
	@echo "Running tests for Low component..."
	PYTHONPATH=$(CI_PROJECT_DIR) pytest $(PYTHON_VARS_AFTER_PYTEST) tests/low


# Test coverage for Low component
coverage-low:
	@echo "Running coverage analysis for Low component..."
	pytest --cov=src/low $(PYTHON_VARS_AFTER_PYTEST) tests/low


# CI-specific test commands for Low and Mid
ci-test-low:
	@echo "Running tests for Low component in CI environment..."
	CI=true PYTHONPATH=$(CI_PROJECT_DIR) pytest $(PYTHON_VARS_AFTER_PYTEST) tests/low
