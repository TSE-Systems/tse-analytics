from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass(frozen=True)
class PipelinePacket:
    value: Any = None
    report: str | None = None
    active: bool = True
    meta: Mapping[str, Any] = field(default_factory=dict)

    @staticmethod
    def inactive(**meta: Any) -> PipelinePacket:
        if "reason" in meta:
            logger.warning(str(meta["reason"]))
        return PipelinePacket(value=None, report=None, active=False, meta=meta)

    def with_meta(self, **updates: Any) -> PipelinePacket:
        merged = dict(self.meta)
        merged.update(updates)
        return PipelinePacket(value=self.value, report=self.report, active=self.active, meta=merged)
