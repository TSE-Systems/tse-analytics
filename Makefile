.PHONY: clean

SOURCE_DIR = tse_analytics

init:
	poetry install

freeze:
	pip freeze > requirements/requirements.frozen.txt

clean: ## remove all build, test, coverage and Python artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .pytest_cache/
	rm -fr .mypy_cache/
	rm -fr tse_analytics.egg-info/
	find $(SOURCE_DIR) -name '*_ui.py' -exec rm -f {} +
	find $(SOURCE_DIR) -name '*_rc.py' -exec rm -f {} +

flake8: ## check style with flake8
	flake8

pylint:
	pylint tse_analytics

ruff:
	ruff tse_analytics

pytest: ## run tests quickly with the default Python
	pytest

coverage: ## check code coverage
	pytest --cov=$(SOURCE_DIR) tests/

build_ui:
	pyside6-uic tse_analytics/views/main_window.ui -o tse_analytics/views/main_window_ui.py --from-imports
	pyside6-uic tse_analytics/views/factors_dialog.ui -o tse_analytics/views/factors_dialog_ui.py

build_resources:
	pyside6-rcc resources/resources.qrc -o tse_analytics/views/resources_rc.py

create_setup:
	pyinstaller setup/tse-analytics.spec
