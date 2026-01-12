from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PipelinePacket:
    value: Any = None
    active: bool = True
    meta: Mapping[str, Any] = field(default_factory=dict)

    @staticmethod
    def inactive(**meta: Any) -> PipelinePacket:
        return PipelinePacket(value=None, active=False, meta=meta)

    def with_meta(self, **updates: Any) -> PipelinePacket:
        merged = dict(self.meta)
        merged.update(updates)
        return PipelinePacket(value=self.value, active=self.active, meta=merged)
