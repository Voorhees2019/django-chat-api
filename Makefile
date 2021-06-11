.PHONY: setup \
	run \
	db \
	createsuperuser \
	black \
	flake8 \
	mypy \

venv/bin/activate: ## alias for virtual environment
	python -m venv venv

setup: venv/bin/activate ## project setup
	. venv/bin/activate; pip install pip wheel setuptools
	. venv/bin/activate; pip install -r requirements.txt

run: venv/bin/activate ## Run server
	. venv/bin/activate; python ./manage.py runserver

db: venv/bin/activate ## Run migrations
	. venv/bin/activate; python ./manage.py migrate

createsuperuser: venv/bin/activate ## Create superuser
	. venv/bin/activate; python ./manage.py createsuperuser

black: venv/bin/activate ## Format code with black
	. venv/bin/activate; black ./

flake8: venv/bin/activate ## Flake8 codestyle
	. venv/bin/activate; flake8 ./

mypy: venv/bin/activate ## Type checking
	. venv/bin/activate; mypy ./
