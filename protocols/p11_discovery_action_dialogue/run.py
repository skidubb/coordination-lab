#!/usr/bin/env python3
"""CLI entry point for P11: Discovery & Action Dialogue (DAD)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .orchestrator import DADOrchestrator, DADResult

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


def print_result(result: DADResult) -> None:
    """Pretty-print the DAD result."""
    sep = "=" * 72

    print(f"\n{sep}")
    print("P11: DISCOVERY & ACTION DIALOGUE")
    print(sep)
    print(f"\nQuestion: {result.question}\n")

    # Phase 1 — Scouted Deviants
    print(f"{'-' * 40}")
    print("PHASE 1: SCOUTED POSITIVE DEVIANTS")
    print("-" * 40)
    for d in result.scouted_deviants:
        agent = d.get("source_agent", "?")
        print(f"\n  [{agent}] {d.get('deviant', '?')}")
        print(f"    Behavior: {d.get('behavior', '?')}")
        print(f"    Why: {d.get('why_it_works', '?')}")

    # Phase 2 — Filtered Behaviors
    print(f"\n{'-' * 40}")
    print(f"PHASE 2: FILTERED BEHAVIORS ({len(result.filtered_behaviors)} passed / {len(result.scouted_deviants)} scouted)")
    print("-" * 40)
    for b in result.filtered_behaviors:
        print(f"\n  {b.get('deviant', '?')}: {b.get('behavior', '?')}")
        print(f"    Uncommon: {b.get('uncommon', '?')} — {b.get('uncommon_reasoning', '')}")
        print(f"    Accessible: {b.get('accessible', '?')} — {b.get('accessible_reasoning', '')}")
        print(f"    Evidence: {b.get('evidence', '?')} — {b.get('evidence_reasoning', '')}")

    # Phase 3 — Extracted Practices
    print(f"\n{'-' * 40}")
    print("PHASE 3: EXTRACTED PRACTICES")
    print("-" * 40)
    for i, p in enumerate(result.extracted_practices, 1):
        print(f"\n  {i}. {p.get('practice', '?')}")
        print(f"     {p.get('description', '')}")
        print(f"     Derived from: {', '.join(p.get('derived_from', []))}")
        print(f"     Mechanism: {p.get('mechanism', '')}")

    # Phase 4 — Adapted Recommendations
    print(f"\n{'-' * 40}")
    print("PHASE 4: ADAPTED RECOMMENDATIONS")
    print("-" * 40)
    print(f"\n{result.adapted_recommendations}")

    # Timings
    print(f"\n{'-' * 40}")
    print("TIMINGS")
    print("-" * 40)
    total = 0.0
    for phase, elapsed in result.timings.items():
        print(f"  {phase}: {elapsed:.1f}s")
        total += elapsed
    print(f"  total: {total:.1f}s")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="P11: Discovery & Action Dialogue (DAD) — Positive deviant identification",
    )
    parser.add_argument(
        "--question", "-q",
        required=True,
        help="The strategic question to analyze.",
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
        "--thinking-budget",
        type=int,
        default=10_000,
        help="Extended thinking budget in tokens (default: 10000).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted text.",
    )

    args = parser.parse_args()
    agents = build_agents(args.agents)

    orchestrator = DADOrchestrator(
        agents=agents,
        thinking_model=args.thinking_model,
        orchestration_model=args.orchestration_model,
        thinking_budget=args.thinking_budget,
    )

    result = asyncio.run(orchestrator.run(args.question))

    if args.json:
        output = {
            "question": result.question,
            "scouted_deviants": result.scouted_deviants,
            "filtered_behaviors": result.filtered_behaviors,
            "extracted_practices": result.extracted_practices,
            "adapted_recommendations": result.adapted_recommendations,
            "timings": result.timings,
        }
        print(json.dumps(output, indent=2))
    else:
        print_result(result)


if __name__ == "__main__":
    main()
