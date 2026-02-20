"""CLI entry point for P3: Parallel Synthesis Protocol.

Usage:
    python -m protocols.p03_parallel_synthesis.run \
        --question "Should we expand into Europe?" \
        --agents ceo cfo cto

    python -m protocols.p03_parallel_synthesis.run \
        --question "..." \
        --agent-config agents.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .orchestrator import SynthesisOrchestrator

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
    agent_names: list[str] | None, agent_config_path: str | None
) -> list[dict]:
    """Build agent list from CLI args."""
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


def print_result(result):
    """Pretty-print the synthesis result."""
    print("\n" + "=" * 70)
    print("PARALLEL SYNTHESIS RESULTS")
    print("=" * 70)

    print(f"\nQuestion: {result.question}\n")

    for p in result.perspectives:
        print("-" * 40)
        print(f"  {p.name}")
        print("-" * 40)
        print(f"{p.response}\n")

    print("=" * 70)
    print("SYNTHESIS")
    print("=" * 70)
    print(f"\n{result.synthesis}")


def main():
    parser = argparse.ArgumentParser(description="P3: Parallel Synthesis Protocol")
    parser.add_argument("--question", "-q", required=True, help="The question to analyze")
    parser.add_argument("--agents", "-a", nargs="+", help="Built-in agent roles (e.g., ceo cfo cto)")
    parser.add_argument("--agent-config", help="Path to JSON file with custom agent definitions")
    parser.add_argument("--thinking-model", default="claude-opus-4-6", help="Model for agent reasoning")
    parser.add_argument("--orchestration-model", default="claude-haiku-4-5-20251001", help="Model for mechanical steps")
    parser.add_argument("--thinking-budget", type=int, default=10000, help="Token budget for extended thinking (default: 10000)")
    args = parser.parse_args()

    agents = build_agents(args.agents, args.agent_config)
    orchestrator = SynthesisOrchestrator(
        agents=agents,
        thinking_model=args.thinking_model,
        thinking_budget=args.thinking_budget,
    )

    print(f"Running Parallel Synthesis with {len(agents)} agents: {', '.join(a['name'] for a in agents)}")
    result = asyncio.run(orchestrator.run(args.question))
    print_result(result)


if __name__ == "__main__":
    main()
