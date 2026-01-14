#!/usr/bin/env python
"""Build all UI files from .ui to _ui.py."""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

UI_FILES = [
    # views
    ("tse_analytics/views/main_window.ui", "tse_analytics/views/main_window_ui.py"),
    ("tse_analytics/views/misc/raw_data_widget/raw_data_widget.ui", "tse_analytics/views/misc/raw_data_widget/raw_data_widget_ui.py"),
    ("tse_analytics/views/general/factors/factors_dialog.ui", "tse_analytics/views/general/factors/factors_dialog_ui.py"),
    ("tse_analytics/views/general/variables/add_variable_dialog.ui", "tse_analytics/views/general/variables/add_variable_dialog_ui.py"),
    ("tse_analytics/views/general/datasets/datasets_merge_dialog.ui", "tse_analytics/views/general/datasets/datasets_merge_dialog_ui.py"),
    ("tse_analytics/views/general/datasets/adjust_dataset_dialog.ui", "tse_analytics/views/general/datasets/adjust_dataset_dialog_ui.py"),
    ("tse_analytics/views/general/settings/binning_settings_widget.ui", "tse_analytics/views/general/settings/binning_settings_widget_ui.py"),
    ("tse_analytics/views/general/about/about_dialog.ui", "tse_analytics/views/general/about/about_dialog_ui.py"),
    ("tse_analytics/views/general/settings/settings_dialog.ui", "tse_analytics/views/general/settings/settings_dialog_ui.py"),
    # toolbox
    ("tse_analytics/toolbox/n_way_anova/n_way_anova_settings_widget.ui", "tse_analytics/toolbox/n_way_anova/n_way_anova_settings_widget_ui.py"),
    ("tse_analytics/toolbox/rm_anova/rm_anova_settings_widget.ui", "tse_analytics/toolbox/rm_anova/rm_anova_settings_widget_ui.py"),
    ("tse_analytics/toolbox/mixed_anova/mixed_anova_settings_widget.ui", "tse_analytics/toolbox/mixed_anova/mixed_anova_settings_widget_ui.py"),
    ("tse_analytics/toolbox/ancova/ancova_settings_widget.ui", "tse_analytics/toolbox/ancova/ancova_settings_widget_ui.py"),
    ("tse_analytics/toolbox/reports/report_widget.ui", "tse_analytics/toolbox/reports/report_widget_ui.py"),
    # phenomaster
    ("tse_analytics/modules/phenomaster/views/import_csv_dialog.ui", "tse_analytics/modules/phenomaster/views/import_csv_dialog_ui.py"),
    ("tse_analytics/modules/phenomaster/views/import_tse_dialog.ui", "tse_analytics/modules/phenomaster/views/import_tse_dialog_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/drinkfeed/views/drinkfeed_dialog.ui", "tse_analytics/modules/phenomaster/submodules/drinkfeed/views/drinkfeed_dialog_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/drinkfeed/views/settings/settings_widget.ui", "tse_analytics/modules/phenomaster/submodules/drinkfeed/views/settings/settings_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/calo/views/calo_dialog.ui", "tse_analytics/modules/phenomaster/submodules/calo/views/calo_dialog_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/calo/views/plot/plot_widget.ui", "tse_analytics/modules/phenomaster/submodules/calo/views/plot/plot_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/calo/views/settings/settings_widget.ui", "tse_analytics/modules/phenomaster/submodules/calo/views/settings/settings_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/calo/views/settings/gas_settings/gas_settings_widget.ui", "tse_analytics/modules/phenomaster/submodules/calo/views/settings/gas_settings/gas_settings_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/calo/views/test_fit/test_fit_widget.ui", "tse_analytics/modules/phenomaster/submodules/calo/views/test_fit/test_fit_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/calo/views/rer/rer_widget.ui", "tse_analytics/modules/phenomaster/submodules/calo/views/rer/rer_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/actimot/views/actimot_dialog.ui", "tse_analytics/modules/phenomaster/submodules/actimot/views/actimot_dialog_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/actimot/views/plot/plot_widget.ui", "tse_analytics/modules/phenomaster/submodules/actimot/views/plot/plot_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/actimot/views/settings/settings_widget.ui", "tse_analytics/modules/phenomaster/submodules/actimot/views/settings/settings_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/actimot/views/stream/stream_widget.ui", "tse_analytics/modules/phenomaster/submodules/actimot/views/stream/stream_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/actimot/views/heatmap/heatmap_widget.ui", "tse_analytics/modules/phenomaster/submodules/actimot/views/heatmap/heatmap_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/actimot/views/trajectory/trajectory_widget.ui", "tse_analytics/modules/phenomaster/submodules/actimot/views/trajectory/trajectory_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/actimot/views/frames/frames_widget.ui", "tse_analytics/modules/phenomaster/submodules/actimot/views/frames/frames_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/grouphousing/views/grouphousing_dialog.ui", "tse_analytics/modules/phenomaster/submodules/grouphousing/views/grouphousing_dialog_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/grouphousing/views/heatmap/heatmap_widget.ui", "tse_analytics/modules/phenomaster/submodules/grouphousing/views/heatmap/heatmap_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/grouphousing/views/raw_data/raw_data_widget.ui", "tse_analytics/modules/phenomaster/submodules/grouphousing/views/raw_data/raw_data_widget_ui.py"),
    ("tse_analytics/modules/phenomaster/submodules/grouphousing/views/preprocessed_data/preprocessed_data_widget.ui", "tse_analytics/modules/phenomaster/submodules/grouphousing/views/preprocessed_data/preprocessed_data_widget_ui.py"),
    # intellicage
    ("tse_analytics/modules/intellicage/toolbox/place_preference/place_preference_settings_widget.ui", "tse_analytics/modules/intellicage/toolbox/place_preference/place_preference_settings_widget_ui.py"),
    # intellimaze
    ("tse_analytics/modules/intellimaze/views/export_merged_csv/export_merged_csv_dialog.ui", "tse_analytics/modules/intellimaze/views/export_merged_csv/export_merged_csv_dialog_ui.py"),
]


def compile_ui(ui_input: str, py_output: str) -> tuple[str, int]:
    cmd = ["pyside6-uic", ui_input, "-o", py_output]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return ui_input, result.returncode


def main():
    print(f"Building {len(UI_FILES)} UI files...")
    failed = []

    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda args: compile_ui(*args), UI_FILES)
        for ui_file, returncode in results:
            if returncode != 0:
                failed.append(ui_file)
            else:
                print(f"  ✓ {ui_file}")

    if failed:
        print(f"\nFailed to compile {len(failed)} files:")
        for f in failed:
            print(f"  ✗ {f}")
        sys.exit(1)

    print("\nAll UI files built successfully.")


if __name__ == "__main__":
    main()
