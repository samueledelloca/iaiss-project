"""Minimal agent framework for the C9orf72 scientific ecosystem.

An :class:`Agent` is a declarative :class:`AgentSpec` (name, layer, role, allowed
tools, system prompt) plus a *reasoning backend* and the shared tool registry.
Every run is logged to ``experiments/`` with the full prompt, the tool calls and
the output, satisfying the reproducibility requirement to record prompts, agent
configurations and all AI-assisted steps.

Two backends are provided:

* :class:`CachedBackend` (default) - deterministic. The agent's reasoning is
  computed from explicit tool calls and rules in :mod:`c9n2a.discovery`, and the
  run is recorded. This is what runs when no API key is present.
* :class:`AnthropicBackend` - live. If ``ANTHROPIC_API_KEY`` is set, an agent can
  additionally run a Claude tool-use loop over the same tools. The repo therefore
  *can* run live, while the committed results come from the deterministic path.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from . import logging_utils, paths, tools


@dataclass
class AgentSpec:
    name: str
    layer: int
    role: str
    system_prompt: str
    tools: list[str] = field(default_factory=list)
    kind: str = "scientific"   # scientific | paper | discovery | pi

    def tool_schema(self) -> list[dict]:
        return [{"name": n, "description": tools.TOOLS[n].description}
                for n in self.tools if n in tools.TOOLS]


@dataclass
class AgentResult:
    agent: str
    task: str
    output: dict
    tool_calls: list[dict] = field(default_factory=list)
    backend: str = "cached"
    run_id: str = ""
    duration_s: float = 0.0

    def as_dict(self) -> dict:
        return asdict(self)


class CachedBackend:
    """Deterministic backend: the handler computes the output from tools."""

    name = "cached"

    def run(self, spec: AgentSpec, task: str, handler: Callable, context: dict,
            recorder: "ToolRecorder") -> dict:
        return handler(recorder, context)


class AnthropicBackend:
    """Live backend using Claude with a tool-use loop over the shared tools."""

    name = "anthropic"

    def __init__(self, model: str = "claude-opus-4-8", temperature: float = 0.0):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = model
        self.temperature = temperature

    def run(self, spec: AgentSpec, task: str, handler: Callable, context: dict,
            recorder: "ToolRecorder") -> dict:
        schema = [{"name": n, "description": tools.TOOLS[n].description,
                   "input_schema": {"type": "object", "additionalProperties": True}}
                  for n in spec.tools]
        messages = [{"role": "user", "content": task + "\n\nContext:\n"
                     + json.dumps(context, default=str)[:4000]}]
        for _ in range(8):
            resp = self.client.messages.create(
                model=self.model, max_tokens=2048, temperature=self.temperature,
                system=spec.system_prompt, tools=schema, messages=messages)
            messages.append({"role": "assistant", "content": resp.content})
            tool_uses = [b for b in resp.content if getattr(b, "type", "") == "tool_use"]
            if not tool_uses:
                text = "".join(getattr(b, "text", "") for b in resp.content)
                return {"text": text}
            results = []
            for tu in tool_uses:
                out = recorder.call(tu.name, **tu.input)
                results.append({"type": "tool_result", "tool_use_id": tu.id,
                                "content": json.dumps(out, default=str)[:6000]})
            messages.append({"role": "user", "content": results})
        return {"text": "max tool iterations reached"}


class ToolRecorder:
    """Wraps the tool registry so every call made during a run is logged."""

    def __init__(self, allowed: list[str]):
        self.allowed = set(allowed)
        self.calls: list[dict] = []

    def call(self, tool_name: str, **kwargs) -> dict:
        if self.allowed and tool_name not in self.allowed:
            raise PermissionError(f"agent not permitted to use tool '{tool_name}'")
        out = tools.call(tool_name, **kwargs)
        self.calls.append({"tool": tool_name, "args": kwargs})
        return out


def _backend(name: str):
    if name == "anthropic" and os.environ.get("ANTHROPIC_API_KEY"):
        return AnthropicBackend()
    return CachedBackend()


class Agent:
    def __init__(self, spec: AgentSpec, handler: Callable, backend: str = "cached"):
        self.spec = spec
        self.handler = handler
        self.backend = _backend(backend)

    def run(self, task: str, context: dict | None = None,
            log_dir: Path | None = None) -> AgentResult:
        context = context or {}
        run_id = f"{self.spec.name}-{uuid.uuid4().hex[:8]}"
        log_dir = Path(log_dir or (paths.EXPERIMENTS / "agent_runs"))
        logger = logging_utils.get_logger(f"agent.{self.spec.name}",
                                          jsonl_path=log_dir / f"{run_id}.jsonl")
        recorder = ToolRecorder(self.spec.tools)
        t0 = time.time()
        logger.info(f"[{self.spec.name}] task: {task}",
                    extra={"event": "agent_start", "agent": self.spec.name})
        output = self.backend.run(self.spec, task, self.handler, context, recorder)
        dt = time.time() - t0
        result = AgentResult(agent=self.spec.name, task=task, output=output,
                             tool_calls=recorder.calls, backend=self.backend.name,
                             run_id=run_id, duration_s=round(dt, 3))
        record = {"spec": asdict(self.spec), "prompt": self.spec.system_prompt,
                  **result.as_dict()}
        (log_dir / f"{run_id}.json").parent.mkdir(parents=True, exist_ok=True)
        (log_dir / f"{run_id}.json").write_text(json.dumps(record, indent=2, default=str))
        logger.info(f"[{self.spec.name}] done ({len(recorder.calls)} tool calls, {dt:.2f}s)",
                    extra={"event": "agent_done", "agent": self.spec.name})
        return result


def prompt_hash(spec: AgentSpec, task: str, context: dict) -> str:
    payload = json.dumps({"name": spec.name, "prompt": spec.system_prompt,
                          "task": task, "context": context}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
