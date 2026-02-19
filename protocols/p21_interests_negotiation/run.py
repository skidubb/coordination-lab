#!/usr/bin/env python3
"""CLI entry point for P21: Interests-Based Negotiation."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .orchestrator import InterestsNegotiationOrchestrator, NegotiationResult

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


def print_result(result: NegotiationResult) -> None:
    """Pretty-print the negotiation result."""
    sep = "=" * 72

    print(f"\n{sep}")
    print("P21: INTERESTS-BASED NEGOTIATION")
    print(sep)
    print(f"\nScenario: {result.question}\n")

    # Phase 1 — Interests
    print(f"{sep}\nPHASE 1 — SURFACED INTERESTS\n{sep}")
    for agent_name, interests in result.interest_maps.items():
        print(f"\n--- {agent_name} ---")
        for i in interests:
            priority = i.get("priority", "?")
            itype = i.get("type", "?")
            print(f"  [{priority}/{itype}] {i.get('interest', '')}")

    # Phase 2 — Interest Map
    print(f"\n{sep}\nPHASE 2 — INTEREST MAP\n{sep}")
    cat = result.categorized_interests
    print("\nShared Interests:")
    for item in cat.get("shared", []):
        holders = ", ".join(item.get("holders", []))
        print(f"  - {item.get('interest', '')} ({holders})")
    print("\nCompatible Interests:")
    for item in cat.get("compatible", []):
        print(f"  - {item.get('interest', '')} ({item.get('holder', '')})")
    print("\nConflicting Interests:")
    for item in cat.get("conflicting", []):
        a = item.get("interest_a", {})
        b = item.get("interest_b", {})
        print(f"  - {a.get('holder', '')}: {a.get('interest', '')} vs {b.get('holder', '')}: {b.get('interest', '')}")
        print(f"    Tension: {item.get('tension', '')}")

    # Phase 3 — Options
    print(f"\n{sep}\nPHASE 3 — GENERATED OPTIONS\n{sep}")
    for i, opt in enumerate(result.generated_options):
        proposer = opt.get("proposed_by", "?")
        print(f"\n  Option {i} [{proposer}]: {opt.get('option', '')}")
        satisfies = opt.get("satisfies_interests", [])
        if satisfies:
            print(f"    Satisfies: {', '.join(satisfies)}")

    # Phase 4 — Scores
    print(f"\n{sep}\nPHASE 4 — OPTION SCORES\n{sep}")
    for s in result.option_scores:
        idx = s.get("option_index", "?")
        pareto = " [PARETO]" if s.get("pareto_optimal") else ""
        agent_scores = s.get("agent_scores", {})
        scores_str = ", ".join(
            f"{k}: {v.get('score', '?')}" for k, v in agent_scores.items()
        ) if isinstance(agent_scores, dict) else str(agent_scores)
        print(f"  Option {idx}{pareto}: {scores_str}")

    # Agreement
    print(f"\n{sep}\nFINAL AGREEMENT\n{sep}")
    agreement = result.selected_agreement.get("agreement", result.selected_agreement)
    print(f"\n{agreement.get('summary', '')}")
    terms = agreement.get("key_terms", [])
    if terms:
        print("\nKey Terms:")
        for t in terms:
            print(f"  - {t}")
    trade_offs = agreement.get("trade_offs", [])
    if trade_offs:
        print("\nTrade-offs:")
        for t in trade_offs:
            print(f"  - {t}")
    impl = agreement.get("implementation_notes", "")
    if impl:
        print(f"\nImplementation: {impl}")

    # Satisfaction
    print(f"\n{sep}\nINTEREST SATISFACTION\n{sep}")
    for agent, score in result.interest_satisfaction.items():
        print(f"  {agent}: {score:.2f}")

    # Timings
    print(f"\n{sep}\nTIMINGS\n{sep}")
    for phase, elapsed in result.timings.items():
        print(f"  {phase}: {elapsed}s")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="P21: Interests-Based Negotiation — mutual gains through interest mapping",
    )
    parser.add_argument("--question", "-q", required=True, help="Negotiation scenario to resolve")
    parser.add_argument(
        "--agents", "-a",
        nargs="+",
        default=["ceo", "cfo", "cto"],
        help="Agent keys to include (default: ceo cfo cto)",
    )
    parser.add_argument("--max-rounds", type=int, default=2, help="Max option-generation rounds (default: 2)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output raw JSON result")
    args = parser.parse_args()

    agents = build_agents(args.agents)
    orchestrator = InterestsNegotiationOrchestrator(
        agents=agents,
        max_rounds=args.max_rounds,
    )
    result = asyncio.run(orchestrator.run(args.question))

    if args.json_output:
        from dataclasses import asdict
        print(json.dumps(asdict(result), indent=2, default=str))
    else:
        print_result(result)


if __name__ == "__main__":
    main()
