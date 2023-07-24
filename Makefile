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
	pyside6-uic tse_analytics/views/main_window.ui -o tse_analytics/views/main_window_ui.py
	pyside6-uic tse_analytics/views/factors_dialog.ui -o tse_analytics/views/factors_dialog_ui.py
	pyside6-uic tse_analytics/views/datasets_merge_dialog.ui -o tse_analytics/views/datasets_merge_dialog_ui.py
	pyside6-uic tse_analytics/views/selection/factors/factors_widget.ui -o tse_analytics/views/selection/factors/factors_widget_ui.py
	pyside6-uic tse_analytics/views/selection/animals/animals_widget.ui -o tse_analytics/views/selection/animals/animals_widget_ui.py
	pyside6-uic tse_analytics/views/selection/variables/variables_widget.ui -o tse_analytics/views/selection/variables/variables_widget_ui.py
	pyside6-uic tse_analytics/views/data/data_table_widget.ui -o tse_analytics/views/data/data_table_widget_ui.py
	pyside6-uic tse_analytics/views/data/data_plot_widget.ui -o tse_analytics/views/data/data_plot_widget_ui.py
	pyside6-uic tse_analytics/views/settings/time_intervals_settings_widget.ui -o tse_analytics/views/settings/time_intervals_settings_widget_ui.py
	pyside6-uic tse_analytics/views/settings/time_cycles_settings_widget.ui -o tse_analytics/views/settings/time_cycles_settings_widget_ui.py
	pyside6-uic tse_analytics/views/settings/time_phases_settings_widget.ui -o tse_analytics/views/settings/time_phases_settings_widget_ui.py
	pyside6-uic tse_analytics/views/settings/outliers_settings_widget.ui -o tse_analytics/views/settings/outliers_settings_widget_ui.py
	pyside6-uic tse_analytics/views/settings/binning_settings_widget.ui -o tse_analytics/views/settings/binning_settings_widget_ui.py
	pyside6-uic tse_analytics/views/analysis/histogram_widget.ui -o tse_analytics/views/analysis/histogram_widget_ui.py
	pyside6-uic tse_analytics/views/analysis/distribution_widget.ui -o tse_analytics/views/analysis/distribution_widget_ui.py
	pyside6-uic tse_analytics/views/analysis/normality_widget.ui -o tse_analytics/views/analysis/normality_widget_ui.py
	pyside6-uic tse_analytics/views/analysis/correlation_widget.ui -o tse_analytics/views/analysis/correlation_widget_ui.py
	pyside6-uic tse_analytics/views/analysis/anova_widget.ui -o tse_analytics/views/analysis/anova_widget_ui.py
	pyside6-uic tse_analytics/views/analysis/ancova_widget.ui -o tse_analytics/views/analysis/ancova_widget_ui.py
	pyside6-uic tse_analytics/views/analysis/glm_widget.ui -o tse_analytics/views/analysis/glm_widget_ui.py
	pyside6-uic tse_analytics/views/analysis/matrix_widget.ui -o tse_analytics/views/analysis/matrix_widget_ui.py
	pyside6-uic tse_analytics/views/analysis/pca_widget.ui -o tse_analytics/views/analysis/pca_widget_ui.py
	pyside6-uic tse_analytics/views/calo_details/calo_details_dialog.ui -o tse_analytics/views/calo_details/calo_details_dialog_ui.py
	pyside6-uic tse_analytics/views/calo_details/calo_details_plot_widget.ui -o tse_analytics/views/calo_details/calo_details_plot_widget_ui.py
	pyside6-uic tse_analytics/views/calo_details/calo_details_settings_widget.ui -o tse_analytics/views/calo_details/calo_details_settings_widget_ui.py
	pyside6-uic tse_analytics/views/calo_details/calo_details_gas_settings_widget.ui -o tse_analytics/views/calo_details/calo_details_gas_settings_widget_ui.py
	pyside6-uic tse_analytics/views/calo_details/calo_details_test_fit_widget.ui -o tse_analytics/views/calo_details/calo_details_test_fit_widget_ui.py
	pyside6-uic tse_analytics/views/calo_details/calo_details_rer_widget.ui -o tse_analytics/views/calo_details/calo_details_rer_widget_ui.py

build_resources:
	pyside6-rcc resources/resources.qrc -o tse_analytics/resources_rc.py

create_setup:
	pyinstaller setup/tse-analytics.spec
