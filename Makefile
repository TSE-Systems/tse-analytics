.PHONY: clean

SOURCE_DIR = tse_analytics

init:
	pip install -r requirements/dev.txt

clean: ## remove all build, test, coverage and Python artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .pytest_cache/
	rm -fr tse_analytics.egg-info/
	find $(SOURCE_DIR) -name '*.ui.py' -exec rm -f {} +
	find $(SOURCE_DIR) -name '*_rc.py' -exec rm -f {} +

lint: ## check style with flake8
	flake8

test: ## run tests quickly with the default Python
	py.test

coverage: ## check code coverage
	pytest --cov=$(SOURCE_DIR) tests/

build_ui:
	pyside6-uic tse_analytics/views/main_window.ui -o tse_analytics/views/main_window_ui.py
	pyside6-uic tse_analytics/views/groups_dialog.ui -o tse_analytics/views/groups_dialog_ui.py

build_resources:
	pyside6-rcc resources/resources.qrc -o tse_analytics/resources_rc.py

build:
	python setup.py build_res

install: clean ## install the package to the active Python's site-packages
	python setup.py install

create_setup:
	pyinstaller setup/tse-analytics.spec
