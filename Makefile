# Project makefile for a ska-tmc-integration project. You should normally only need to modify
# CAR_OCI_REGISTRY_USER and PROJECT below.
CAR_OCI_REGISTRY_HOST:=artefact.skao.int
PROJECT = ska-sw-integration-testing
TANGO_HOST ?= tango-databaseds:10000 ## TANGO_HOST connection to the Tango DSI
TANGO_HOST_NAME ?= tango-databaseds
TELESCOPE ?= SKA-mid
DISH_NAMESPACE_1 ?= dish-lmc-1
DISH_NAMESPACE_2 ?= dish-lmc-2
DISH_NAMESPACE_3 ?= dish-lmc-3
DISH_NAMESPACE_4 ?= dish-lmc-4
KUBE_NAMESPACE ?= ska-tmc-integration
KUBE_NAMESPACE_SDP ?= ska-tmc-integration-sdp
K8S_TIMEOUT ?= 800s
PYTHON_LINT_TARGET ?= tests/
DEPLOYMENT_TYPE = $(shell echo $(TELESCOPE) | cut -d '-' -f2)
MARK ?= $(shell echo $(TELESCOPE) | sed "s/-/_/g") ## What -m opt to pass to pytest
# run one test with FILE=acceptance/test_subarray_node.py::test_check_internal_model_according_to_the_tango_ecosystem_deployed
FILE ?= tests## A specific test file to pass to pytest
ADD_ARGS ?= ## Additional args to pass to pytest
FILE_NAME?= alarm_rules.txt


# ----------------------------------------------------------------------------
# Exit at failure flag
# 
# The following flag is used to determine whether the test run should exit at
# the first failure or continue running tests after a failure. By default, the
# test run will exit at the first failure. To continue running tests after a
# failure, set the flag to 'false'.

EXIT_AT_FAIL ?= true ## Flag for determining exit at failure. 
# Set 'true' to exit at first failure. Set 'false' to continue running 
# tests after failure. It defaults to 'true' if not set.
# Actually, any value other than 'false' will be treated as 'true'.

ifneq ($(EXIT_AT_FAIL), false)
ADD_ARGS += -x
endif

# ----------------------------------------------------------------------------

# KUBE_NAMESPACE defines the Kubernetes Namespace that will be deployed to
# using Helm.  If this does not already exist it will be created
ifneq ($(CI_JOB_ID),)
KUBE_NAMESPACE ?= ci-$(CI_PROJECT_NAME)-$(CI_COMMIT_SHORT_SHA)
endif
# HELM_RELEASE is the release that all Kubernetes resources will be labelled
# with
HELM_RELEASE ?= test

# UMBRELLA_CHART_PATH Path of the umbrella chart to work with
HELM_CHART=ska-tmc-testing-$(DEPLOYMENT_TYPE)
UMBRELLA_CHART_PATH ?= charts/$(HELM_CHART)/
K8S_CHARTS ?= ska-tmc-$(DEPLOYMENT_TYPE) ska-tmc-testing-$(DEPLOYMENT_TYPE)## list of charts
K8S_CHART ?= $(HELM_CHART)

DISH_TANGO_HOST ?= tango-databaseds
COUNT ?= 1 ## Number of times the tests should run
CLUSTER_DOMAIN ?= cluster.local
PORT ?= 10000
SUBARRAY_COUNT ?= 1
DISH_NAME_1 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_1).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA001
DISH_NAME_36 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_2).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA036
DISH_NAME_63 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_3).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA063
DISH_NAME_100 ?= tango://$(DISH_TANGO_HOST).$(DISH_NAMESPACE_4).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-dish/dish-manager/SKA100
CSP_MASTER ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-csp/control/0
CSP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-csp/subarray
SDP_MASTER ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-sdp/control/0
SDP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/mid-sdp/subarray

CI_REGISTRY ?= gitlab.com

# K8S_TEST_IMAGE_TO_TEST ?= artefact.skao.int/ska-tango-images-tango-itango:9.3.12## docker image that will be run for testing purpose
K8S_TEST_IMAGE_TO_TEST ?= harbor.skao.int/production/ska-tango-images-pytango-builder:9.4.2 

TARANTA_ENABLED ?= false

CI_PROJECT_DIR ?= .

XAUTHORITY ?= $(HOME)/.Xauthority
THIS_HOST := $(shell ip a 2> /dev/null | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' | head -n1)
DISPLAY ?= $(THIS_HOST):0
JIVE ?= false# Enable jive
TARANTA ?= false
MINIKUBE ?= false ## Minikube or not
FAKE_DEVICES ?= false ## Install fake devices or not

ITANGO_DOCKER_IMAGE = $(CAR_OCI_REGISTRY_HOST)/ska-tango-images-tango-itango:9.3.10

# Test runner - run to completion job in K8s
# name of the pod running the k8s_tests
K8S_TEST_RUNNER = test-runner-$(HELM_RELEASE)

CI_PROJECT_PATH_SLUG ?= ska-sw-integration-testing
CI_ENVIRONMENT_SLUG ?= ska-sw-integration-testing
CSP_SIMULATION_ENABLED ?= true
SDP_SIMULATION_ENABLED ?= true
DISH_SIMULATION_ENABLED ?= true
SDP_PROCCONTROL_REPLICAS ?= 1

ifeq ($(MAKECMDGOALS),k8s-test)
ADD_ARGS +=  --true-context
MARK ?= $(shell echo $(TELESCOPE) | sed "s/-/_/g")
endif


PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK) $(ADDMARK)' $(ADD_ARGS) $(FILE) --count=$(COUNT)
CUSTOM_VALUES1 ?=
CUSTOM_VALUES2 ?=
ifeq ($(CSP_SIMULATION_ENABLED),false)
CUSTOM_VALUES1 =	--set tmc-mid.deviceServers.mocks.csp=$(CSP_SIMULATION_ENABLED)\
	--set ska-csp-lmc-mid.enabled=true
endif

ifeq ($(SDP_SIMULATION_ENABLED),false)
CUSTOM_VALUES2=	--set tmc-mid.deviceServers.mocks.sdp=$(SDP_SIMULATION_ENABLED)\
	--set global.sdp_master="$(SDP_MASTER)"\
	--set global.sdp_subarray_prefix="$(SDP_SUBARRAY_PREFIX)"\
	--set ska-sdp.proccontrol.replicas=$(SDP_PROCCONTROL_REPLICAS)\
	--set global.sdp.processingNamespace=$(KUBE_NAMESPACE_SDP)\
	--set ska-sdp.kafka.clusterDomain=$(CLUSTER_DOMAIN) \
	--set ska-sdp.kafka.zookeeper.clusterDomain=$(CLUSTER_DOMAIN) \
	--set ska-sdp.enabled=true\
	--set ska-sdp.lmc.loadBalancer=true\
	--set tmc-mid.subarray_count=1\
	--set ska-sdp.lmc.nsubarray=1
endif

K8S_CHART_PARAMS = --set global.minikube=$(MINIKUBE) \
	--set global.tango_host=$(TANGO_HOST) \
	--set ska-tango-base.display=$(DISPLAY) \
	--set ska-tango-base.xauthority=$(XAUTHORITY) \
	--set ska-tango-base.jive.enabled=$(JIVE) \
	--set global.exposeAllDS=false \
	--set global.cluster_domain=$(CLUSTER_DOMAIN) \
	--set global.operator=true \
	--set ska-taranta.enabled=$(TARANTA_ENABLED)\
	--set global.namespace_dish.dish_names[0]="$(DISH_NAME_1)"\
	--set global.namespace_dish.dish_names[1]="$(DISH_NAME_36)"\
	--set global.namespace_dish.dish_names[2]="$(DISH_NAME_63)"\
	--set global.namespace_dish.dish_names[3]="$(DISH_NAME_100)"\
	--set tmc-mid.deviceServers.mocks.dish=$(DISH_SIMULATION_ENABLED)\
	--set tmc-mid.subarray_count=$(SUBARRAY_COUNT)\
	$(CUSTOM_VALUES1)\
	$(CUSTOM_VALUES2)

PYTHON_VARS_BEFORE_PYTEST ?= PYTHONPATH=.:./src \
							 TANGO_HOST=$(TANGO_HOST) \
							 TELESCOPE=$(TELESCOPE) \
							 CLUSTER_DOMAIN=$(CLUSTER_DOMAIN) \
							 CSP_SIMULATION_ENABLED=$(CSP_SIMULATION_ENABLED) \
							 SDP_SIMULATION_ENABLED=$(SDP_SIMULATION_ENABLED) \
							 DISH_SIMULATION_ENABLED=$(DISH_SIMULATION_ENABLED) \
							 DISH_NAMESPACE_1=$(DISH_NAMESPACE_1) \
							 DISH_NAMESPACE_2=$(DISH_NAMESPACE_2) \
							 DISH_NAMESPACE_3=$(DISH_NAMESPACE_3) \
							 DISH_NAMESPACE_4=$(DISH_NAMESPACE_4) \
							 DISH_NAME_1=$(DISH_NAME_1) \
							 DISH_NAME_36=$(DISH_NAME_36) \
							 DISH_NAME_63=$(DISH_NAME_63) \
							 DISH_NAME_100=$(DISH_NAME_100) \
							 KUBE_NAMESPACE=$(KUBE_NAMESPACE) \
							 KUBE_NAMESPACE_SDP=$(KUBE_NAMESPACE_SDP)

K8S_TEST_TEST_COMMAND ?= $(PYTHON_VARS_BEFORE_PYTEST) $(PYTHON_RUNNER) \
						pytest \
						$(PYTHON_VARS_AFTER_PYTEST) ./tests \
						| tee pytest.stdout # k8s-test test command to run in container

-include .make/base.mk
-include .make/k8s.mk
-include .make/helm.mk
-include .make/python.mk
-include .make/oci.mk
-include .make/xray.mk
-include PrivateRules.mak
-include resources/alarmhandler.mk

# to create SDP namespace
k8s-pre-install-chart:
ifeq ($(SDP_SIMULATION_ENABLED),false)
	@echo "k8s-pre-install-chart: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif

# to create SDP namespace
k8s-pre-install-chart-car:
ifeq ($(SDP_SIMULATION_ENABLED),false)
	@echo "k8s-pre-install-chart-car: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif

# to delete SDP namespace
k8s-post-uninstall-chart:
ifeq ($(SDP_SIMULATION_ENABLED),false)
	@echo "k8s-post-uninstall-chart: deleting the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-delete-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif

taranta-link:
	@echo "#            https://k8s.stfc.skao.int/$(KUBE_NAMESPACE)/taranta/dashboard"

alarm-handler-configurator-link:
	@echo "#            https://k8s.stfc.skao.int/$(KUBE_NAMESPACE)/alarm-handler/"


cred:
	make k8s-namespace
	curl -s https://gitlab.com/ska-telescope/templates-repository/-/raw/master/scripts/namespace_auth.sh | bash -s $(SERVICE_ACCOUNT) $(KUBE_NAMESPACE) || true


test-requirements:
	@poetry export --without-hashes --dev --format requirements.txt --output Mid/tests/requirements.txt

k8s-pre-test: test-requirements

# ----------------------------------------------------------------------------
# Trick to select a subset of the tests to run by their python name
# Very useful when debugging a single test
# 
# Example:
# make k8s-test MARK=tmc_csp PYTHON_TEST_NAME="abort"
# # Expected result: among all the tests with "tmc_csp" as a marker,
# #  			  only the ones with "abort" in their name will be run.

PYTHON_TEST_NAME ?= ## -k parameter for pytest

ifneq ($(PYTHON_TEST_NAME),)
	PYTHON_VARS_AFTER_PYTEST := $(PYTHON_VARS_AFTER_PYTEST) -k '$(PYTHON_TEST_NAME)'
endif

# ----------------------------------------------------------------------------
# test results files
# (The following variables are used to generate the various test results files
# i.e., cucumber.json, report.json, and report.html)
# 
# report.html is used to generate the BDD test report by the pytest-bdd-report
# plugin. The plugin generates a BDD test report in HTML format, that will
# then be published in the artifacts and that will be linked in the 
# Jira ticket of the test execution.

# target file names for the cucumber-related test results json files
CUCUMBER_JSON_RESULT_FILE ?= build/cucumber.json
REPORT_JSON_RESULT_FILE ?= build/report.json
XRAY_TEST_RESULT_FILE ?= build/cucumber.json

# configuration file for ska-ser-xray to publish the test results to Jira
XRAY_EXECUTION_CONFIG_FILE ?= tests/xray-config.json

# target file name for the BDD test report in HTML format
# Leave or set to empty to disable the HTML BDD test report generation
HTML_REPORT_TARGET_FILE ?= build/report.html

# ----------------------------------------------------------------------------
# Add all the flags needed to generate the test results files

# Add BDD report output 
PYTHON_VARS_AFTER_PYTEST := $(PYTHON_VARS_AFTER_PYTEST) \
	--cucumberjson="$(CUCUMBER_JSON_RESULT_FILE)" \
	--json-report \
	--json-report-file="$(REPORT_JSON_RESULT_FILE)"

# Add BDD HTML test report (if enabled)
ifneq ($(HTML_REPORT_TARGET_FILE),)
	PYTHON_VARS_AFTER_PYTEST := $(PYTHON_VARS_AFTER_PYTEST) \
		--bdd-report="$(HTML_REPORT_TARGET_FILE)"
endif

# ----------------------------------------------------------------------------
# Publish the BDD HTML test report to the just published
# Jira test execution issue

PUBLISH_HTML_REPORT_TO_JIRA_SCRIPT ?= helper_scripts/publish_test_report.py
## The Python script that will publish the BDD HTML test report to the Jira test execution issue
# (Set to empty to disable the publishing of the BDD HTML test report to the Jira test execution issue)

# after the test run and the Test Execution Jira ticket is created,
# if the HTML report is enabled and 
# the script to publish the HTML report to Jira is available,
# then publish a link to the HTML report to Jira
xray-post-publish:
	if [ -f "$(HTML_REPORT_TARGET_FILE)" ] && [ -f "$(PUBLISH_HTML_REPORT_TO_JIRA_SCRIPT)" ]; then \
		echo "Publishing the BDD HTML test report to the Jira test execution issue"; \
		python3 $(PUBLISH_HTML_REPORT_TO_JIRA_SCRIPT); \
	fi



