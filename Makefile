#SHELL:=/usr/bin/env bash -O extglob -O globstar -o pipefail
# if there is trailing spaces remove by running: perl -pi -e 's/^  */\t/' Makefile

###############   Application Parameters   ###############

VENV_NAME = venv
VENV_PIP_PATH = $(VENV_NAME)/bin/pip3
VENV_PYTHON_PATH = $(VENV_NAME)/bin/python3

APPS = bbg_ingest email_ingest teams_ingest voice_ingest zoom_ingest shared

WORKING_APP:=teams_ingest# <<< Set working tenant at will!

######################   HELP  #######################

help:
	@echo  'Commands targets:'
	@echo  '  make help                   show this message '
	@echo
	@echo  '  make create-venv            creates the virtualenv for the given WORKING_APP '
	@echo  '  make install-venv           install requirements.txt on the virtualenv at WORKING_APP '
	@echo  '  make destroy-venv           removes the virtualenv for the given WORKING_APP '
	@echo

	@echo  '  make precommit              applies pre-commit hooks to structure code standards '
	@echo  '  make lint                   applies black linter with args line=110 & not-replacing quotes '
	@echo  '  make imports                aaplies isort to organize the imports of project'
	@echo
	@echo  '  make tests                  runs the pytest suite at working app '
	@echo  '  make update-pip             Updates the Python library pip packages versions '


######################   Target / Commands   #######################


.SILENT: create-venv
create-venv:
	cd $(WORKING_APP); \
	echo ' ...Creating Virtual Env on $(WORKING_APP)... '; \
	python3 -m venv $(VENV_NAME);

.SILENT: install-venv
install-venv:
	cd $(WORKING_APP); \
	$(VENV_PIP_PATH) install -r requirements.txt; \
	$(VENV_PIP_PATH) install -r ../requirements_dev.txt; \
	$(VENV_PIP_PATH) install -r ../shared/requirements.txt; \

.PHONY: destroy-venv
destroy-venv:
	pip cache purge; \
	cd $(WORKING_APP); \
	rm -r -f $(VENV_NAME)

.PHONY: precommit lint imports tests update-pip

precommit:
	git ls-files -- '$(WORKING_APP)/*' | xargs pre-commit run --files

lint:
	black --line-length=110 --skip-string-normalization $(WORKING_APP)/.

imports:
	isort --profile black --skip $(VENV_NAME) node_modules $(WORKING_APP)/.

tests:
	pytest -n auto $(WORKING_APP)

update-pip:
	cd $(WORKING_APP); \
	$(VENV_PYTHON_PATH) -m pip install --upgrade pip3; \
	$(VENV_PIP_PATH) list --outdated | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip3 install -U

sls-plugins:
	sls plugin install -n serverless-stage-manager --stage dev
	sls plugin install -n serverless-pseudo-parameters --stage dev
	sls plugin install -n serverless-python-requirements --stage dev
	sls plugin install --name serverless-step-functions --stage=dev