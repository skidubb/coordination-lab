#!/usr/bin/env python3
"""CLI entry-point for P14: 1-2-4-All protocol."""

from __future__ import annotations

import argparse
import asyncio
import sys
import textwrap

from .orchestrator import AgentSpec, OneTwoFourAllOrchestrator, OneTwoFourAllResult

# ── Built-in C-Suite agents ────────────────────────────────────────
BUILTIN_AGENTS = {
    "ceo": {"name": "CEO", "system_prompt": "You are a CEO focused on strategy, vision, competitive positioning, and stakeholder management."},
    "cfo": {"name": "CFO", "system_prompt": "You are a CFO focused on financial risk, cash flow, unit economics, margins, and capital allocation."},
    "cto": {"name": "CTO", "system_prompt": "You are a CTO focused on technical architecture, scalability, security, tech debt, and engineering execution."},
    "cmo": {"name": "CMO", "system_prompt": "You are a CMO focused on market positioning, brand risk, customer acquisition, messaging, and competitive dynamics."},
    "coo": {"name": "COO", "system_prompt": "You are a COO focused on operations, process execution, resource allocation, scaling, and cross-functional coordination."},
    "cpo": {"name": "CPO", "system_prompt": "You are a CPO focused on product-market fit, user needs, roadmap priorities, and competitive differentiation."},
    "cro": {"name": "CRO", "system_prompt": "You are a CRO focused on revenue strategy, pipeline health, sales execution, and go-to-market alignment."},
}


def build_agents(keys: list[str]) -> list[AgentSpec]:
    """Resolve CLI agent keys to AgentSpec objects."""
    agents = []
    for key in keys:
        key_lower = key.lower()
        if key_lower not in BUILTIN_AGENTS:
            print(f"Unknown agent: {key}. Available: {', '.join(BUILTIN_AGENTS)}")
            sys.exit(1)
        cfg = BUILTIN_AGENTS[key_lower]
        agents.append(AgentSpec(name=cfg["name"], system_prompt=cfg["system_prompt"]))
    return agents


def print_result(result: OneTwoFourAllResult) -> None:
    """Pretty-print the full 1-2-4-All result."""
    sep = "=" * 72

    print(f"\n{sep}")
    print("P14: 1-2-4-ALL RESULT")
    print(sep)
    print(f"\nQuestion: {result.question}\n")

    # Stage 1 — Solo
    print(f"{sep}\nSTAGE 1 — SOLO IDEATION\n{sep}")
    for name, text in result.solo_outputs.items():
        print(f"\n--- {name} ---")
        print(textwrap.fill(text, width=88))

    # Stage 2 — Pairs
    print(f"\n{sep}\nSTAGE 2 — PAIR MERGES\n{sep}")
    for i, pair in enumerate(result.pair_outputs, 1):
        label = ", ".join(pair["names"])
        print(f"\n--- Pair {i} ({label}) ---")
        print(textwrap.fill(pair["text"], width=88))

    # Stage 3 — Quads
    print(f"\n{sep}\nSTAGE 3 — QUAD MERGES\n{sep}")
    for i, quad in enumerate(result.quad_outputs, 1):
        label = ", ".join(quad["names"])
        print(f"\n--- Quad {i} ({label}) ---")
        print(textwrap.fill(quad["text"], width=88))

    # Stage 4 — Final synthesis
    print(f"\n{sep}\nSTAGE 4 — FINAL SYNTHESIS\n{sep}")
    print(result.final_synthesis)

    # Stats
    print(f"\n{sep}\nSTATS\n{sep}")
    print(f"Elapsed: {result.elapsed_seconds}s")
    for model, count in result.model_calls.items():
        print(f"  {model}: {count} calls")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="P14: 1-2-4-All — Progressive merging protocol",
    )
    parser.add_argument("--question", "-q", required=True, help="Strategic question to explore")
    parser.add_argument(
        "--agents", "-a",
        nargs="+",
        default=["ceo", "cfo", "cto", "cmo"],
        help="Agent keys to include (default: ceo cfo cto cmo)",
    )
    parser.add_argument("--thinking-budget", type=int, default=10_000, help="Extended thinking budget")
    args = parser.parse_args()

    agents = build_agents(args.agents)
    orchestrator = OneTwoFourAllOrchestrator(agents=agents, thinking_budget=args.thinking_budget)
    result = asyncio.run(orchestrator.run(args.question))
    print_result(result)


if __name__ == "__main__":
    main()
