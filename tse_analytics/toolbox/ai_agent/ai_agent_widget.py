"""AI Agent toolbox widget.

Lets the user ask natural-language questions about the current
:class:`Datatable`. Claude generates pandas code, the widget executes it
in-process and renders the result inline alongside the conversation transcript.
"""

from __future__ import annotations

import html
import os
import re
import traceback
from dataclasses import dataclass
from typing import Any

import anthropic
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger
from matplotlib.figure import Figure
from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon, QTextCursor
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QToolBar,
    QWidget,
)

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils.formatting import get_great_table, get_html_image_from_figure
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.toolbox.ai_agent.prompt_builder import build_system_prompt
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase

CLAUDE_MODELS = [
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
]
DEFAULT_MODEL = "claude-opus-4-7"
MAX_RESULT_ROWS = 200
MAX_TOKENS = 16000

_CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


@dataclass
class AIAgentWidgetSettings:
    """Persisted per-widget settings (kept minimal — conversation is per-session)."""

    model: str = DEFAULT_MODEL


def _extract_code(text: str) -> str:
    """Return the first fenced python block's body, or the whole text if none."""
    match = _CODE_BLOCK_RE.search(text)
    return (match.group(1) if match else text).strip()


def _run_code(code: str, df: pd.DataFrame) -> Any:
    """Execute ``code`` with ``df``/``pd``/``np``/``plt`` in scope.

    Returns the value assigned to ``result``. If ``result`` stays ``None`` we
    evaluate the last line of the block as a fallback expression (so one-liners
    without explicit ``result = ...`` still show something).
    """
    namespace: dict[str, Any] = {
        "df": df,
        "pd": pd,
        "np": np,
        "plt": plt,
        "result": None,
    }
    exec(compile(code, "<ai_agent>", "exec"), namespace)
    if namespace["result"] is not None:
        return namespace["result"]
    lines = code.strip().splitlines()
    if not lines:
        return None
    last = lines[-1].strip()
    try:
        return eval(last, namespace)
    except SyntaxError:
        return None


def _call_claude(
    api_key: str,
    model: str,
    system_blocks: list[dict[str, Any]],
    history: list[dict[str, Any]],
) -> anthropic.types.Message:
    """Worker entry point — runs in a thread, must not touch Qt."""
    client = anthropic.Anthropic(api_key=api_key)
    return client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        system=system_blocks,
        messages=history,
        thinking={"type": "adaptive"},
    )


@toolbox_plugin(
    category="AI",
    label="AI Agent",
    icon=":/icons/icons8-analyze-16.png",
    order=0,
)
class AIAgentWidget(ToolboxWidgetBase):
    """Natural-language pandas agent for a :class:`Datatable`."""

    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            AIAgentWidgetSettings,
            title="AI Agent",
            parent=parent,
        )

        # Repurpose the built-in "Update" action as "Send".
        self.update_action.setText("Send")
        self.update_action.setIcon(QIcon(":/icons/icons8-play-16.png"))

        # Per-session state.
        self._history: list[dict[str, Any]] = []
        self._transcript_html: str = ""
        self._alive: bool = True
        self.destroyed.connect(lambda: self._on_widget_destroyed())

        # Prompt input sits below the report view.
        self.prompt_edit = QLineEdit(self)
        self.prompt_edit.setPlaceholderText("Ask Claude about this datatable — e.g. 'How many animals are there?'")
        self.prompt_edit.returnPressed.connect(self._update)
        self._layout.addWidget(self.prompt_edit)

        if not self._resolve_api_key():
            self._append_system_notice(
                "No Anthropic API key configured. Set one in Settings → AI Agent or "
                "via the <code>ANTHROPIC_API_KEY</code> environment variable."
            )

    # ------------------------------------------------------------------
    # ToolboxWidgetBase hooks
    # ------------------------------------------------------------------

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        toolbar.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox(toolbar)
        self.model_combo.addItems(CLAUDE_MODELS)
        default_model = str(QSettings().value("DefaultClaudeModel", DEFAULT_MODEL))
        initial = self._settings.model if self._settings.model in CLAUDE_MODELS else default_model
        if initial not in CLAUDE_MODELS:
            initial = DEFAULT_MODEL
        self.model_combo.setCurrentText(initial)
        toolbar.addWidget(self.model_combo)

        toolbar.addSeparator()
        clear_action = toolbar.addAction(QIcon(":/icons/icons8-erase-16.png"), "Clear")
        clear_action.triggered.connect(self._clear_conversation)

        toolbar.addSeparator()
        status = "OK" if self._resolve_api_key() else "Missing"
        self.api_key_label = QLabel(f"API key: {status}")
        toolbar.addWidget(self.api_key_label)

    def _get_settings_value(self) -> AIAgentWidgetSettings:
        model = self.model_combo.currentText() if hasattr(self, "model_combo") else DEFAULT_MODEL
        return AIAgentWidgetSettings(model=model)

    def _update(self) -> None:
        """Send the current prompt to Claude."""
        prompt = self.prompt_edit.text().strip()
        if not prompt:
            return

        api_key = self._resolve_api_key()
        if not api_key:
            make_toast(
                self,
                self.title,
                "No Anthropic API key configured.",
                duration=3000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        self._append_user_turn(prompt)
        self._history.append({"role": "user", "content": prompt})

        self.update_action.setEnabled(False)
        self.prompt_edit.setEnabled(False)

        system_blocks = build_system_prompt(self.datatable)
        worker = Worker(
            _call_claude,
            api_key,
            self.model_combo.currentText(),
            system_blocks,
            list(self._history),
        )
        worker.signals.result.connect(self._on_llm_result)
        worker.signals.error.connect(self._on_llm_error)
        worker.signals.finished.connect(self._on_llm_finished)
        TaskManager.start_task(worker)

    # ------------------------------------------------------------------
    # Worker callbacks
    # ------------------------------------------------------------------

    def _on_llm_result(self, response: anthropic.types.Message) -> None:
        if not self._alive:
            return

        self._history.append({"role": "assistant", "content": response.content})

        try:
            usage = response.usage
            logger.debug(
                "AI agent usage: input={}, output={}, cache_read={}, cache_created={}",
                getattr(usage, "input_tokens", None),
                getattr(usage, "output_tokens", None),
                getattr(usage, "cache_read_input_tokens", None),
                getattr(usage, "cache_creation_input_tokens", None),
            )
        except Exception:
            pass

        text_parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
        assistant_text = "\n\n".join(text_parts).strip()
        self._append_assistant_turn(assistant_text)

        code = _extract_code(assistant_text)
        if not code:
            return

        self._append_code_block(code)
        try:
            result = _run_code(code, self.datatable.df)
        except Exception:
            self._append_error(traceback.format_exc())
            return

        self._append_result(result)

    def _on_llm_error(self, exc_tuple: tuple) -> None:
        if not self._alive:
            return
        exc_type, value, tb_str = exc_tuple
        exc_name = getattr(exc_type, "__name__", str(exc_type))
        if exc_name == "AuthenticationError":
            message = "Anthropic authentication failed. Check your API key in Settings → AI Agent."
        elif exc_name == "APIConnectionError":
            message = "Could not reach the Anthropic API. Check your internet connection."
        else:
            message = f"{exc_name}: {value}\n\n{tb_str}"
        self._append_error(message)
        # Pop the user turn so a retry doesn't send it twice.
        if self._history and self._history[-1].get("role") == "user":
            self._history.pop()

    def _on_llm_finished(self) -> None:
        if not self._alive:
            return
        self.update_action.setEnabled(True)
        self.prompt_edit.setEnabled(True)
        self.prompt_edit.clear()
        self.prompt_edit.setFocus()

    # ------------------------------------------------------------------
    # Transcript rendering
    # ------------------------------------------------------------------

    def _append_user_turn(self, text: str) -> None:
        self._transcript_html += f'<div style="margin:8px 0;"><b>You:</b> {html.escape(text)}</div>'
        self._flush_transcript()

    def _append_assistant_turn(self, text: str) -> None:
        # Strip the fenced code block from the displayed narration — we render it separately below.
        narration = _CODE_BLOCK_RE.sub("", text).strip()
        safe = html.escape(narration).replace("\n", "<br>")
        self._transcript_html += f'<div style="margin:8px 0;"><b>Claude:</b> {safe}</div>'
        self._flush_transcript()

    def _append_code_block(self, code: str) -> None:
        self._transcript_html += (
            '<pre style="background:#f4f4f4;border:1px solid #ddd;padding:8px;'
            'white-space:pre-wrap;">' + html.escape(code) + "</pre>"
        )
        self._flush_transcript()

    def _append_result(self, result: Any) -> None:
        if result is None:
            self._transcript_html += '<div style="color:#666;margin:4px 0;"><i>(No result assigned)</i></div>'
        elif isinstance(result, Figure):
            self._transcript_html += get_html_image_from_figure(result)
            plt.close(result)
        elif isinstance(result, pd.DataFrame):
            self._transcript_html += self._dataframe_to_html(result)
        elif isinstance(result, pd.Series):
            self._transcript_html += self._dataframe_to_html(result.to_frame())
        else:
            self._transcript_html += f'<pre style="background:#f4f4f4;padding:8px;">{html.escape(str(result))}</pre>'
        self._flush_transcript()

    def _append_error(self, message: str) -> None:
        self._transcript_html += (
            '<div style="color:#b00;margin:8px 0;"><b>Error:</b><pre style="white-space:pre-wrap;">'
            + html.escape(message)
            + "</pre></div>"
        )
        self._flush_transcript()

    def _append_system_notice(self, html_snippet: str) -> None:
        self._transcript_html += f'<div style="color:#666;margin:8px 0;"><i>{html_snippet}</i></div>'
        self._flush_transcript()

    def _dataframe_to_html(self, df: pd.DataFrame) -> str:
        total_rows = len(df)
        truncated = df.head(MAX_RESULT_ROWS) if total_rows > MAX_RESULT_ROWS else df
        title = (
            "Result"
            if total_rows <= MAX_RESULT_ROWS
            else f"Result (showing first {MAX_RESULT_ROWS} of {total_rows:,} rows)"
        )
        try:
            return get_great_table(truncated, title).as_raw_html(inline_css=True)
        except Exception:
            return truncated.to_html()

    def _flush_transcript(self) -> None:
        self.report_view.set_content(self._transcript_html)
        # Move the cursor to the end so the latest turn is visible after setHtml.
        self.report_view.moveCursor(QTextCursor.MoveOperation.End)
        self.report_view.ensureCursorVisible()

    # ------------------------------------------------------------------
    # Misc helpers
    # ------------------------------------------------------------------

    def _clear_conversation(self) -> None:
        self._history.clear()
        self._transcript_html = ""
        self.report_view.clear()

    def _resolve_api_key(self) -> str | None:
        key = str(QSettings().value("AnthropicApiKey", "")).strip() or None
        return key or os.environ.get("ANTHROPIC_API_KEY") or None

    def _on_widget_destroyed(self) -> None:
        self._alive = False
