#!/usr/bin/env python3
"""CLI entry point for P19: Vickrey Auction — Second-Price Sealed-Bid Option Selection."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .orchestrator import VickreyOrchestrator, VickreyResult

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


def print_result(result: VickreyResult) -> None:
    """Pretty-print the Vickrey Auction result."""
    print("\n" + "=" * 70)
    print("P19: VICKREY AUCTION — SECOND-PRICE SEALED-BID SELECTION")
    print("=" * 70)
    print(f"\nQuestion: {result.question}")
    print(f"Options: {', '.join(result.options)}\n")

    # Sealed Bids
    print("-" * 40)
    print("SEALED BIDS (revealed)")
    print("-" * 40)
    for b in sorted(result.bids, key=lambda x: x.confidence, reverse=True):
        marker = " << WINNER" if b.agent == result.winner else ""
        print(f"  {b.agent}: \"{b.selected_option}\" "
              f"(confidence: {b.confidence}/100){marker}")
        print(f"      {b.reasoning}")

    # Auction Result
    print(f"\n{'-' * 40}")
    print("AUCTION RESULT")
    print("-" * 40)
    print(f"  Winner:               {result.winner}")
    print(f"  Winning Option:       {result.winning_option}")
    print(f"  Original Confidence:  {result.original_confidence}/100")
    print(f"  Second-Price (paid):  {result.second_price_confidence}/100")
    print(f"  Consensus Score:      {result.consensus_score:.2f}")

    # Bid Distribution
    print(f"\n{'-' * 40}")
    print("BID DISTRIBUTION")
    print("-" * 40)
    for opt, confs in result.bid_distribution.items():
        avg = sum(confs) / len(confs)
        print(f"  \"{opt}\": {len(confs)} bid(s), "
              f"confidences: {confs}, avg: {avg:.0f}")

    # Calibrated Justification
    print(f"\n{'-' * 40}")
    print("CALIBRATED JUSTIFICATION")
    print("-" * 40)
    print(f"  {result.calibrated_justification}")

    # Synthesis
    print(f"\n{'-' * 40}")
    print("SYNTHESIS")
    print("-" * 40)
    syn = result.synthesis
    if syn.get("summary"):
        print(f"\n  Summary: {syn['summary']}")
    if syn.get("consensus_analysis"):
        print(f"  Consensus: {syn['consensus_analysis']}")
    if syn.get("distribution_insights"):
        print(f"  Distribution: {syn['distribution_insights']}")
    if syn.get("dissenting_perspectives"):
        print("  Dissenting Perspectives:")
        for d in syn["dissenting_perspectives"]:
            print(f"    - {d}")

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
        description="P19: Vickrey Auction — Second-Price Sealed-Bid Option Selection",
    )
    parser.add_argument(
        "--question", "-q",
        required=True,
        help="The strategic question to evaluate options for.",
    )
    parser.add_argument(
        "--options", "-o",
        nargs="+",
        required=True,
        help="The options to evaluate (space-separated, quote multi-word options).",
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

    orchestrator = VickreyOrchestrator(
        agents=agents,
        thinking_model=args.thinking_model,
        orchestration_model=args.orchestration_model,
    )

    result = asyncio.run(orchestrator.run(args.question, args.options))

    if args.json:
        output = {
            "question": result.question,
            "options": result.options,
            "bids": [
                {"agent": b.agent, "selected_option": b.selected_option,
                 "confidence": b.confidence, "reasoning": b.reasoning}
                for b in result.bids
            ],
            "winner": result.winner,
            "winning_option": result.winning_option,
            "original_confidence": result.original_confidence,
            "second_price_confidence": result.second_price_confidence,
            "calibrated_justification": result.calibrated_justification,
            "bid_distribution": result.bid_distribution,
            "consensus_score": result.consensus_score,
            "synthesis": result.synthesis,
            "timings": result.timings,
        }
        print(json.dumps(output, indent=2))
    else:
        print_result(result)


if __name__ == "__main__":
    main()
