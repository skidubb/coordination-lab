"""Shared agent registry and builder for all coordination protocols."""

from __future__ import annotations

import json
import sys


BUILTIN_AGENTS = {
    "ceo": {
        "name": "CEO",
        "system_prompt": "You are a CEO focused on strategy, vision, competitive positioning, and stakeholder management.",
    },
    "cfo": {
        "name": "CFO",
        "system_prompt": "You are a CFO focused on financial risk, cash flow, unit economics, margins, and capital allocation.",
    },
    "cto": {
        "name": "CTO",
        "system_prompt": "You are a CTO focused on technical architecture, scalability, security, tech debt, and engineering execution.",
    },
    "cmo": {
        "name": "CMO",
        "system_prompt": "You are a CMO focused on market positioning, brand risk, customer acquisition, messaging, and competitive dynamics.",
    },
    "coo": {
        "name": "COO",
        "system_prompt": "You are a COO focused on operations, process execution, resource allocation, scaling, and cross-functional coordination.",
    },
    "cpo": {
        "name": "CPO",
        "system_prompt": "You are a CPO focused on product-market fit, user needs, roadmap priorities, and competitive differentiation.",
    },
    "cro": {
        "name": "CRO",
        "system_prompt": "You are a CRO focused on revenue strategy, pipeline health, sales execution, and go-to-market alignment.",
    },
}


def build_agents(
    agent_names: list[str] | None = None,
    agent_config_path: str | None = None,
) -> list[dict]:
    """Build agent list from CLI args.

    Supports both a list of built-in agent keys and a path to a JSON config file.
    """
    if agent_config_path:
        with open(agent_config_path) as f:
            return json.load(f)

    names = agent_names or ["ceo", "cfo", "cto", "cmo"]
    agents = []
    for name in names:
        key = name.lower()
        if key not in BUILTIN_AGENTS:
            print(f"Unknown agent: {name}. Available: {', '.join(BUILTIN_AGENTS)}")
            sys.exit(1)
        agents.append(BUILTIN_AGENTS[key])
    return agents
