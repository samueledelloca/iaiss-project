"""Structured logging: a rich console handler plus an optional JSONL file sink.

Every pipeline stage and agent run should obtain a logger via :func:`get_logger`
so that human-readable console output and a machine-readable JSONL event log are
produced together.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from rich.logging import RichHandler


class JsonlHandler(logging.Handler):
    """Write one JSON object per log record to a .jsonl file."""

    def __init__(self, path: Path):
        super().__init__()
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, record: logging.LogRecord) -> None:
        obj = {
            "ts": record.created,
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in ("event", "stage", "agent", "extra"):
            if hasattr(record, key):
                obj[key] = getattr(record, key)
        with open(self.path, "a") as fh:
            fh.write(json.dumps(obj, default=str) + "\n")


def get_logger(name: str = "c9n2a", jsonl_path: Path | None = None,
               level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger (idempotent for a given name)."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    has_console = any(isinstance(h, RichHandler) for h in logger.handlers)
    if not has_console:
        logger.addHandler(RichHandler(rich_tracebacks=True, show_path=False))
    if jsonl_path is not None and not any(
        isinstance(h, JsonlHandler) and h.path == Path(jsonl_path)
        for h in logger.handlers
    ):
        logger.addHandler(JsonlHandler(Path(jsonl_path)))
    return logger
