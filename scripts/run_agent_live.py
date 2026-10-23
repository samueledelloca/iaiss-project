#!/usr/bin/env python3
"""Run one agent LIVE over the MCP tools, using the Anthropic API.

This demonstrates real language-model reasoning: the agent decides which tools to
call, reads their outputs and writes a conclusion. It requires ANTHROPIC_API_KEY
(create one at https://console.anthropic.com/). Without a key, the project's agents
run deterministically instead; see results/discovery/agent_reasoning_example.md for
the equivalent in-session reasoning.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python scripts/run_agent_live.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from c9n2a import agentkit, discovery, paths  # noqa: E402

QUESTION = ("Using the tools, determine whether the ALS versus HC IL-5 response bias is "
            "specific to C9orf72 or shared with the other neuroantigens (TDP-43, SOD1, EBV), "
            "and whether the C9orf72 increases survive multiple-testing correction. "
            "Call the tools you need, then give a short conclusion with the numbers.")


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set. This script needs an Anthropic API key to run "
              "the agent live.\nSet it and re-run:\n  export ANTHROPIC_API_KEY=sk-ant-...\n"
              "  python scripts/run_agent_live.py\n\nWithout a key the project's agents run "
              "deterministically; see results/discovery/agent_reasoning_example.md.")
        sys.exit(1)

    spec = discovery.AGENT_SPECS["immunology_agent"]
    agent = agentkit.Agent(spec, handler=lambda rec, ctx: {}, backend="anthropic")
    print(f"Running '{spec.name}' LIVE over {len(spec.tools)} tools (model via AnthropicBackend)...\n")
    result = agent.run(QUESTION)

    out = paths.RESULTS / "discovery"
    out.mkdir(parents=True, exist_ok=True)
    (out / "live_run.json").write_text(json.dumps(result.as_dict(), indent=2, default=str))
    print("TOOL CALLS MADE BY THE AGENT:")
    for c in result.tool_calls:
        print(f"  - {c['tool']}({', '.join(f'{k}={v}' for k, v in c['args'].items())})")
    print("\nAGENT CONCLUSION:\n")
    print(result.output.get("text", result.output))
    print(f"\n(backend={result.backend}; full transcript in {out / 'live_run.json'})")


if __name__ == "__main__":
    main()
