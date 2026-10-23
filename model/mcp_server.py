#!/usr/bin/env python3
"""C9orf72-Nature2Agent MCP server.

Exposes the study's computational tools over the Model Context Protocol, turning
the Michaelis et al. (2025) Nature paper into an interactive, executable agent
(the Paper2Agent output shape). Any MCP client (Claude Code, Claude Desktop, ...)
can connect and ask the agent to explain the design, query the data, reproduce
analyses and figures, interrogate epitopes and HLA, and run the discovery
analyses.

Run:  python model/mcp_server.py           # stdio transport
Connect from Claude Code via the repo's .mcp.json.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.server.mcpserver import MCPServer  # noqa: E402

from c9n2a import tools as T  # noqa: E402

INSTRUCTIONS = """\
Interactive computational representation of Michaelis et al. (2025), 'Autoimmune
response to C9orf72 protein in amyotrophic lateral sclerosis' (Nature,
10.1038/s41586-025-09588-6). Use the tools to explain the experimental design,
retrieve observations, reproduce statistical analyses and figures, interrogate
the 100-peptide screen and HLA data, and run reproduction/discovery analyses.
All results are computed from the study's own source data; cite the original
paper for any finding.
"""


def build_server() -> MCPServer:
    mcp = MCPServer("c9orf72-nature2agent", instructions=INSTRUCTIONS)
    for tool in T.TOOLS.values():
        mcp.add_tool(tool.fn, name=tool.name, description=tool.description)
    return mcp


mcp = build_server()


if __name__ == "__main__":
    mcp.run("stdio")
