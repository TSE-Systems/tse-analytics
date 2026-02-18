from great_tables import GT, loc, style

style_descriptive_table = r"""
table {
    font-size: 10pt;
    border-collapse: collapse;
    border: 1px solid silver;
    margin-bottom: 20px;
}
caption {
    font-size: 12pt;
    font-weight: bold;
}
th {
    padding: 5px;
    background: #dfebea;
}
td {
    padding: 5px;
}
"""


DEFAULT_GREAT_TABLE_FONT = "Segoe UI"


def gt_theme_tse(gt: GT) -> GT:
    gt_themed = (
        gt
        .opt_table_font(font=DEFAULT_GREAT_TABLE_FONT)
        .tab_style(
            style=style.text(
                font=DEFAULT_GREAT_TABLE_FONT,
                weight="bold",
                size="16px",
            ),
            locations=loc.title(),
        )
        .tab_style(
            style=[
                style.borders(
                    sides="top",
                    color="black",
                    weight="2px",
                ),
                style.text(
                    font=DEFAULT_GREAT_TABLE_FONT,
                    v_align="bottom",
                    size="13px",
                    weight="bold",
                ),
            ],
            locations=[loc.column_labels(), loc.stubhead()],
        )
        .tab_options(
            column_labels_background_color="white",
            column_labels_border_bottom_color="black",
            column_labels_border_bottom_width="2px",
            column_labels_border_top_style="none",
            column_labels_font_weight="normal",
            data_row_padding="3px",
            heading_align="left",
            heading_background_color="#dfebea",
            heading_border_bottom_style="none",
            row_group_border_bottom_color="black",  # Altered wrt R package
            row_group_border_bottom_width="1px",
            row_group_border_top_color="black",
            row_group_border_top_style="none",
            source_notes_border_lr_style="none",
            source_notes_font_size="12px",
            stub_border_color="white",
            stub_border_width="0px",
            table_border_bottom_style="none",
            table_border_top_style="none",
            table_border_top_width="3px",
            table_font_size="13px",
            table_margin_left="4px",
        )
    )

    return gt_themed
