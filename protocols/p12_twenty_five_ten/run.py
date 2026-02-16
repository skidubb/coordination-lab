"""CLI entry point for P12: 25/10 Crowd Sourcing Protocol.

Usage:
    python -m protocols.p12_twenty_five_ten.run \
        --question "Rank these initiatives for a bootstrapped AI consultancy..." \
        --agents ceo cfo cto cmo coo cpo cro
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .orchestrator import TwentyFiveTenOrchestrator

BUILTIN_AGENTS = {
    "ceo": {"name": "CEO", "system_prompt": "You are a CEO focused on strategy, vision, competitive positioning, and stakeholder management."},
    "cfo": {"name": "CFO", "system_prompt": "You are a CFO focused on financial risk, cash flow, unit economics, margins, and capital allocation."},
    "cto": {"name": "CTO", "system_prompt": "You are a CTO focused on technical architecture, scalability, security, tech debt, and engineering execution."},
    "cmo": {"name": "CMO", "system_prompt": "You are a CMO focused on market positioning, brand risk, customer acquisition, messaging, and competitive dynamics."},
    "coo": {"name": "COO", "system_prompt": "You are a COO focused on operations, process execution, resource allocation, scaling, and cross-functional coordination."},
    "cpo": {"name": "CPO", "system_prompt": "You are a CPO focused on product-market fit, user needs, roadmap priorities, and competitive differentiation."},
    "cro": {"name": "CRO", "system_prompt": "You are a CRO focused on revenue strategy, pipeline health, sales execution, and go-to-market alignment."},
}


def build_agents(agent_names: list[str] | None, agent_config_path: str | None) -> list[dict]:
    if agent_config_path:
        with open(agent_config_path) as f:
            return json.load(f)
    names = agent_names or ["ceo", "cfo", "cto", "cmo", "coo", "cpo"]
    agents = []
    for name in names:
        key = name.lower()
        if key not in BUILTIN_AGENTS:
            print(f"Unknown agent: {name}. Available: {', '.join(BUILTIN_AGENTS)}")
            sys.exit(1)
        agents.append(BUILTIN_AGENTS[key])
    return agents


def print_result(result):
    print("\n" + "=" * 70)
    print("25/10 CROWD SOURCING RESULTS")
    print("=" * 70)

    print(f"\nChallenge: {result.challenge}")
    print(f"Ideas generated: {len(result.ideas)}")
    print(f"Scoring rounds: {result.scoring_rounds}")
    print(f"Total scores cast: {result.total_scores_cast}\n")

    print("-" * 40)
    print("RANKED IDEAS")
    print("-" * 40)
    for i, idea in enumerate(result.ideas):
        marker = " ★ TOP 25%" if idea.is_top_quartile else ""
        print(f"\n  #{i+1} [{idea.total_score:.0f} pts] {idea.title}{marker}")
        print(f"       Author: {idea.author}")
        print(f"       Avg: Overall={idea.avg_overall:.1f} Bold={idea.avg_boldness:.1f} Feasible={idea.avg_feasibility:.1f} Impact={idea.avg_impact:.1f}")
        print(f"       {idea.idea}")
        print(f"       Bold because: {idea.bold_because}")
        print(f"       Scores ({len(idea.scores)}):")
        for s in idea.scores:
            print(f"         {s['scorer']}: {s['overall']}/5 — \"{s['reaction']}\"")

    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)
    print(f"\n{result.synthesis}")


def main():
    parser = argparse.ArgumentParser(description="P12: 25/10 Crowd Sourcing")
    parser.add_argument("--question", "-q", required=True, help="The challenge to crowd-source ideas for")
    parser.add_argument("--agents", "-a", nargs="+", help="Built-in agent roles")
    parser.add_argument("--agent-config", help="Path to JSON with custom agents")
    parser.add_argument("--rounds", "-r", type=int, default=5, help="Number of scoring rounds")
    parser.add_argument("--thinking-model", default="claude-opus-4-6")
    parser.add_argument("--orchestration-model", default="claude-haiku-4-5-20251001")
    args = parser.parse_args()

    agents = build_agents(args.agents, args.agent_config)
    orchestrator = TwentyFiveTenOrchestrator(
        agents=agents,
        thinking_model=args.thinking_model,
        orchestration_model=args.orchestration_model,
        scoring_rounds=args.rounds,
    )

    print(f"Running 25/10 with {len(agents)} agents, {args.rounds} scoring rounds")
    result = asyncio.run(orchestrator.run(args.question))
    print_result(result)


if __name__ == "__main__":
    main()
