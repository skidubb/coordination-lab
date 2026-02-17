"""CLI entry point for P22: Sequential Pipeline Protocol.

Usage:
    python -m protocols.p22_sequential_pipeline.run --question "..." --agents ceo cfo cto cmo
"""

import argparse
import asyncio
import sys
import time

from .orchestrator import SequentialPipelineOrchestrator, SequentialPipelineResult

BUILTIN_AGENTS = {
    "ceo": {"name": "CEO", "system_prompt": "You are a CEO focused on strategy, vision, competitive positioning, and stakeholder management."},
    "cfo": {"name": "CFO", "system_prompt": "You are a CFO focused on financial risk, cash flow, unit economics, margins, and capital allocation."},
    "cto": {"name": "CTO", "system_prompt": "You are a CTO focused on technical architecture, scalability, security, tech debt, and engineering execution."},
    "cmo": {"name": "CMO", "system_prompt": "You are a CMO focused on market positioning, brand risk, customer acquisition, messaging, and competitive dynamics."},
    "coo": {"name": "COO", "system_prompt": "You are a COO focused on operations, process execution, resource allocation, scaling, and cross-functional coordination."},
    "cpo": {"name": "CPO", "system_prompt": "You are a CPO focused on product-market fit, user needs, roadmap priorities, and competitive differentiation."},
    "cro": {"name": "CRO", "system_prompt": "You are a CRO focused on revenue strategy, pipeline health, sales execution, and go-to-market alignment."},
}


def build_agents(agent_keys: list[str]) -> list[dict]:
    """Build ordered agent list from CLI keys."""
    agents = []
    for key in agent_keys:
        key_lower = key.lower()
        if key_lower not in BUILTIN_AGENTS:
            print(f"Error: Unknown agent '{key}'. Available: {', '.join(BUILTIN_AGENTS.keys())}")
            sys.exit(1)
        agents.append(BUILTIN_AGENTS[key_lower])
    return agents


def print_result(result: SequentialPipelineResult, elapsed: float) -> None:
    """Print the pipeline result to stdout."""
    print("\n" + "=" * 80)
    print("P22: SEQUENTIAL PIPELINE — RESULTS")
    print("=" * 80)

    print(f"\nQuestion: {result.question}")
    print(f"Stages: {len(result.stages)}")
    print(f"Quality Gate: {'PASSED' if result.quality_passed else 'FAILED'}")
    print(f"Time: {elapsed:.1f}s")

    print("\n" + "-" * 80)
    print("PROCESSING LINEAGE")
    print("-" * 80)
    for stage in result.stages:
        print(f"\n--- Stage {stage.stage_number}: {stage.agent_name} ---")
        print(stage.content[:500] + ("..." if len(stage.content) > 500 else ""))

    print("\n" + "-" * 80)
    print("FINAL SYNTHESIZED OUTPUT")
    print("-" * 80)
    print(f"\n{result.final_output}")
    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="P22: Sequential Pipeline — agents process in sequence, each building on prior output."
    )
    parser.add_argument(
        "--question", "-q", required=True, help="The strategic question to analyze."
    )
    parser.add_argument(
        "--agents", "-a", nargs="+", default=["ceo", "cfo", "cto"],
        help="Ordered list of agents (order matters). Default: ceo cfo cto. "
             f"Available: {', '.join(BUILTIN_AGENTS.keys())}",
    )
    parser.add_argument(
        "--thinking-tokens", "-t", type=int, default=10000,
        help="Max thinking tokens per stage (default: 10000).",
    )
    args = parser.parse_args()

    agents = build_agents(args.agents)

    print(f"P22: Sequential Pipeline")
    print(f"Question: {args.question}")
    print(f"Pipeline: {' -> '.join(a['name'] for a in agents)}")
    print()

    orchestrator = SequentialPipelineOrchestrator(
        max_thinking_tokens=args.thinking_tokens,
    )

    start = time.time()
    result = asyncio.run(orchestrator.run(args.question, agents))
    elapsed = time.time() - start

    print_result(result, elapsed)


if __name__ == "__main__":
    main()
