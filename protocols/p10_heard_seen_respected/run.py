#!/usr/bin/env python3
"""CLI entry-point for P10: Heard-Seen-Respected protocol."""

from __future__ import annotations

import argparse
import asyncio
import sys
import textwrap

from .orchestrator import AgentSpec, HSROrchestrator, HSRResult

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


def print_result(result: HSRResult) -> None:
    """Pretty-print the full HSR result."""
    sep = "=" * 72

    print(f"\n{sep}")
    print("P10: HEARD-SEEN-RESPECTED RESULT")
    print(sep)
    print(f"\nQuestion: {result.question}\n")

    # Phase 1 — Narratives
    print(f"{sep}\nPHASE 1 — STAKEHOLDER NARRATIVES\n{sep}")
    for name, text in result.narratives.items():
        print(f"\n--- {name} ---")
        print(textwrap.fill(text, width=88))

    # Phase 2 — Reflections
    print(f"\n{sep}\nPHASE 2 — REFLECTIONS\n{sep}")
    for r in result.reflections:
        print(f"\n--- {r['reflector']} reflecting on {r['reflected_on']} ---")
        print(textwrap.fill(r["reflection"], width=88))

    # Phase 3 — Bridge Synthesis
    print(f"\n{sep}\nPHASE 3 — BRIDGE SYNTHESIS\n{sep}")

    print(f"\n--- Common Ground ---")
    print(result.common_ground)

    print(f"\n--- Key Differences ---")
    print(result.key_differences)

    print(f"\n--- Translation Guide ---")
    print(result.translation_guide)

    # Stats
    print(f"\n{sep}\nSTATS\n{sep}")
    for phase, elapsed in result.timings.items():
        print(f"  {phase}: {elapsed}s")
    for model, count in result.model_calls.items():
        print(f"  {model}: {count} calls")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="P10: Heard-Seen-Respected — Empathy & perspective translation protocol",
    )
    parser.add_argument("--question", "-q", required=True, help="Strategic challenge to explore")
    parser.add_argument(
        "--agents", "-a",
        nargs="+",
        default=["ceo", "cfo", "cto", "cmo"],
        help="Agent keys to include (default: ceo cfo cto cmo)",
    )
    parser.add_argument("--thinking-budget", type=int, default=10_000, help="Extended thinking budget")
    args = parser.parse_args()

    agents = build_agents(args.agents)
    orchestrator = HSROrchestrator(agents=agents, thinking_budget=args.thinking_budget)
    result = asyncio.run(orchestrator.run(args.question))
    print_result(result)


if __name__ == "__main__":
    main()
