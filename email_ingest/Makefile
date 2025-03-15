.PHONY: style imports test coverage deploy-dev deploy-prod
APPS = EmaiIngestLambda helpers tests

install-local:
	virtualenv venv -p python3
	source venv/bin/activate
	pip install -r requirements.txt

git-to-master:
	git checkout master
	git merge development
	git push -u origin master
	git checkout development

serverless-key:
	export SERVERLESS_ACCESS_KEY=AKWRfJ6vDq5x7fcuT7coB7NqWq5C8Ev9QWNJeElA31qI8

style:
	flake8 --ignore=E501 $(APPS)

imports:
	isort -rc --atomic --skip venv .

test:
	pytest tests

coverage:
	pytest --cov=. tests

deploy-dev:
	sls deploy -s dev

deploy-prod:
	sls deploy -s prod
