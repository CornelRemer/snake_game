CONTAINER_PORT = $(or $(BLOG_CONTAINER_PORT),$(BLOG_CONTAINER_PORT),8000)
POSTGRES_CONTAINER_IP = 192.168.0.101


help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

start:     ## start game
	poetry run python main.py

test:     ## run all tests
	poetry run pytest tests

integration-test:     ## run all tests marked as 'integration'
	poetry run pytest -m integration tests

static-check: \
	black \
	isort \
	mypy \
	pylint

black:     ## static analysis for black
	poetry run black .

isort:    ## static analysis for isort
	poetry run isort .

mypy:    ## static analysis for mypy
	poetry run mypy --config-file config/mypy/mypy.ini .

pylint:    ## static analysis for pylint
	poetry run pylint --rcfile config/pylint/pylint.ini main.py snake tests
