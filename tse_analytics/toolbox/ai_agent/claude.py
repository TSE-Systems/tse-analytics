from __future__ import annotations

from typing import Any

import anthropic

MAX_TOKENS = 16000


def call_claude(
    api_key: str,
    model_name: str,
    system_blocks: list[dict[str, Any]],
    history: list[dict[str, Any]],
) -> anthropic.types.Message:
    """Worker entry point — runs in a thread, must not touch Qt."""
    client = anthropic.Anthropic(api_key=api_key)
    return client.messages.create(
        model=model_name,
        max_tokens=MAX_TOKENS,
        system=system_blocks,
        messages=history,
        thinking={"type": "adaptive"},
    )
