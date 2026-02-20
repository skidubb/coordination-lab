"""CLI entry point for P5: Constraint Negotiation Protocol.

Usage:
    python -m protocols.p05_constraint_negotiation.run \
        --question "Should we expand into Europe?" \
        --agents ceo cfo cto --rounds 3

    python -m protocols.p05_constraint_negotiation.run \
        --question "..." \
        --agent-config agents.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .orchestrator import NegotiationOrchestrator

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
    """Pretty-print the negotiation result."""
    print("\n" + "=" * 70)
    print("CONSTRAINT NEGOTIATION RESULTS")
    print("=" * 70)

    print(f"\nQuestion: {result.question}\n")

    for rnd in result.rounds:
        print("-" * 40)
        print(f"  Round {rnd.round_number} — {rnd.round_type.upper()}")
        print("-" * 40)
        for arg in rnd.arguments:
            print(f"\n  [{arg.name}]:")
            print(f"  {arg.content}\n")

    print("-" * 40)
    print("CONSTRAINT TABLE")
    print("-" * 40)
    print(result.constraints.format_for_prompt())

    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)
    print(f"\n{result.synthesis}")


def main():
    parser = argparse.ArgumentParser(description="P5: Constraint Negotiation Protocol")
    parser.add_argument("--question", "-q", required=True, help="The question to negotiate")
    parser.add_argument("--agents", "-a", nargs="+", help="Built-in agent roles (e.g., ceo cfo cto)")
    parser.add_argument("--agent-config", help="Path to JSON file with custom agent definitions")
    parser.add_argument("--rounds", "-r", type=int, default=3, help="Number of negotiation rounds (default: 3)")
    parser.add_argument("--thinking-model", default="claude-opus-4-6", help="Model for agent reasoning")
    parser.add_argument("--orchestration-model", default="claude-haiku-4-5-20251001", help="Model for constraint extraction")
    args = parser.parse_args()

    agents = build_agents(args.agents, args.agent_config)
    orchestrator = NegotiationOrchestrator(
        agents=agents,
        rounds=args.rounds,
        thinking_model=args.thinking_model,
        orchestration_model=args.orchestration_model,
    )

    print(f"Running {args.rounds}-round negotiation with {len(agents)} agents: {', '.join(a['name'] for a in agents)}")
    result = asyncio.run(orchestrator.run(args.question))
    print_result(result)


if __name__ == "__main__":
    main()
