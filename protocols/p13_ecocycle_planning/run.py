#!/usr/bin/env python3
"""CLI entry point for P13: Ecocycle Planning."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .orchestrator import EcocyclePlanningOrchestrator, EcocycleResult

BUILTIN_AGENTS = {
    "ceo": {"name": "CEO", "system_prompt": "You are a CEO focused on strategy, vision, competitive positioning, and stakeholder management."},
    "cfo": {"name": "CFO", "system_prompt": "You are a CFO focused on financial risk, cash flow, unit economics, margins, and capital allocation."},
    "cto": {"name": "CTO", "system_prompt": "You are a CTO focused on technical architecture, scalability, security, tech debt, and engineering execution."},
    "cmo": {"name": "CMO", "system_prompt": "You are a CMO focused on market positioning, brand risk, customer acquisition, messaging, and competitive dynamics."},
    "coo": {"name": "COO", "system_prompt": "You are a COO focused on operations, process execution, resource allocation, scaling, and cross-functional coordination."},
    "cpo": {"name": "CPO", "system_prompt": "You are a CPO focused on product-market fit, user needs, roadmap priorities, and competitive differentiation."},
    "cro": {"name": "CRO", "system_prompt": "You are a CRO focused on revenue strategy, pipeline health, sales execution, and go-to-market alignment."},
}


def build_agents(keys: list[str]) -> list[dict[str, str]]:
    """Resolve agent keys to agent dicts."""
    agents = []
    for key in keys:
        key = key.lower()
        if key not in BUILTIN_AGENTS:
            print(f"Unknown agent: {key}. Available: {', '.join(BUILTIN_AGENTS)}")
            sys.exit(1)
        agents.append(BUILTIN_AGENTS[key])
    return agents


def print_result(result: EcocycleResult) -> None:
    """Pretty-print the Ecocycle Planning result."""
    sep = "=" * 72

    print(f"\n{sep}")
    print("P13: ECOCYCLE PLANNING RESULT")
    print(sep)
    print(f"\nQuestion: {result.question}")
    print(f"Initiatives: {len(result.initiatives)}\n")

    # Phase 1 — Agent Assessments
    print(f"{'-' * 40}")
    print("PHASE 1: AGENT ASSESSMENTS")
    print(f"{'-' * 40}")
    for initiative in result.initiatives:
        print(f"\n  [{initiative}]")
        relevant = [a for a in result.agent_assessments if a.initiative.lower().strip() == initiative.lower().strip()]
        for a in relevant:
            print(f"    {a.agent_name}: {a.stage.upper()} — {a.reasoning}")

    # Phase 2 — Consensus
    print(f"\n{'-' * 40}")
    print("PHASE 2: CONSENSUS STAGES")
    print(f"{'-' * 40}")
    for initiative in result.initiatives:
        stage = result.consensus_stages.get(initiative, "unknown")
        contested_marker = " [CONTESTED]" if initiative in result.contested else ""
        print(f"  {initiative} -> {stage.upper()}{contested_marker}")

    # Phase 3 — Action Plans
    print(f"\n{'-' * 40}")
    print("PHASE 3: ACTION PLANS")
    print(f"{'-' * 40}")
    for initiative in result.initiatives:
        stage = result.consensus_stages.get(initiative, "unknown")
        actions = result.action_plans.get(initiative, [])
        print(f"\n  [{initiative}] ({stage.upper()})")
        for i, action in enumerate(actions, 1):
            print(f"    {i}. {action}")

    # Portfolio Summary
    print(f"\n{'-' * 40}")
    print("PORTFOLIO SUMMARY")
    print(f"{'-' * 40}")
    print(f"  {result.portfolio_summary}")

    # Timings
    print(f"\n{'-' * 40}")
    print("TIMINGS")
    print(f"{'-' * 40}")
    total = 0.0
    for phase, elapsed in result.timings.items():
        print(f"  {phase}: {elapsed:.1f}s")
        total += elapsed
    print(f"  total: {total:.1f}s")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="P13: Ecocycle Planning — Lifecycle stage mapping for initiative portfolios",
    )
    parser.add_argument(
        "--question", "-q",
        required=True,
        help="Strategic context or question framing the portfolio assessment.",
    )
    parser.add_argument(
        "--initiatives", "-i",
        nargs="+",
        required=True,
        help="List of initiatives/projects to assess (e.g., -i 'Project Alpha' 'Legacy CRM' 'AI Chatbot').",
    )
    parser.add_argument(
        "--agents", "-a",
        nargs="+",
        default=["ceo", "cfo", "cto", "cmo"],
        help=f"Agent keys to use. Available: {', '.join(BUILTIN_AGENTS)}",
    )
    parser.add_argument(
        "--thinking-model",
        default=None,
        help="Override the thinking model (default: claude-opus-4-6).",
    )
    parser.add_argument(
        "--orchestration-model",
        default=None,
        help="Override the orchestration model (default: claude-haiku-4-5-20251001).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted text.",
    )

    args = parser.parse_args()
    agents = build_agents(args.agents)

    orchestrator = EcocyclePlanningOrchestrator(
        agents=agents,
        thinking_model=args.thinking_model,
        orchestration_model=args.orchestration_model,
    )

    result = asyncio.run(orchestrator.run(args.question, args.initiatives))

    if args.json:
        output = {
            "question": result.question,
            "initiatives": result.initiatives,
            "agent_assessments": [
                {"agent": a.agent_name, "initiative": a.initiative,
                 "stage": a.stage, "reasoning": a.reasoning}
                for a in result.agent_assessments
            ],
            "consensus_stages": result.consensus_stages,
            "contested": result.contested,
            "action_plans": result.action_plans,
            "portfolio_summary": result.portfolio_summary,
            "timings": result.timings,
        }
        print(json.dumps(output, indent=2))
    else:
        print_result(result)


if __name__ == "__main__":
    main()
