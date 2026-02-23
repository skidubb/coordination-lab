"""P4: Multi-Round Debate Protocol — Agent-agnostic orchestrator.

N rounds of structured debate → synthesis of evolved positions.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import anthropic

from protocols.scoping import filter_context_for_agent, tag_context
from protocols.tracing import make_client
from .prompts import (
    FINAL_PROMPT,
    OPENING_PROMPT,
    REBUTTAL_PROMPT,
    SYNTHESIS_PROMPT,
    format_prior_arguments,
)


@dataclass
class DebateArgument:
    name: str
    content: str
    round_number: int


@dataclass
class DebateRound:
    round_number: int
    round_type: str  # "opening", "rebuttal", "final"
    arguments: list[DebateArgument] = field(default_factory=list)


@dataclass
class DebateResult:
    question: str
    rounds: list[DebateRound] = field(default_factory=list)
    synthesis: str = ""


class DebateOrchestrator:
    """Runs the multi-round debate protocol with any set of agents."""

    def __init__(
        self,
        agents: list[dict],
        rounds: int = 3,
        thinking_model: str = "claude-opus-4-6",
        thinking_budget: int = 10_000,
        trace: bool = False,
    ):
        """
        Args:
            agents: List of {"name": str, "system_prompt": str} dicts.
            rounds: Number of debate rounds (minimum 2: opening + final).
            thinking_model: Model for all debate rounds and synthesis.
            thinking_budget: Token budget for extended thinking on Opus calls.
            trace: Enable JSONL execution tracing.
        """
        if not agents:
            raise ValueError("At least one agent is required")
        if rounds < 2:
            raise ValueError("At least 2 rounds required (opening + final)")
        self.agents = agents
        self.num_rounds = rounds
        self.thinking_model = thinking_model
        self.thinking_budget = thinking_budget
        self.client = make_client(protocol_id="p04_multi_round_debate", trace=trace)

    async def run(self, question: str) -> DebateResult:
        """Execute the full multi-round debate protocol."""
        result = DebateResult(question=question)

        for round_num in range(1, self.num_rounds + 1):
            if round_num == 1:
                round_type = "opening"
                print(f"Round {round_num}/{self.num_rounds}: Opening statements...")
            elif round_num == self.num_rounds:
                round_type = "final"
                print(f"Round {round_num}/{self.num_rounds}: Final statements...")
            else:
                round_type = "rebuttal"
                print(f"Round {round_num}/{self.num_rounds}: Rebuttals...")

            arguments = await self._run_round(
                question, round_num, round_type, result.rounds
            )
            result.rounds.append(
                DebateRound(
                    round_number=round_num,
                    round_type=round_type,
                    arguments=arguments,
                )
            )

        # Synthesis
        print("Synthesizing debate...")
        result.synthesis = await self._synthesize(question, result.rounds)

        return result

    async def _run_round(
        self,
        question: str,
        round_number: int,
        round_type: str,
        prior_rounds: list[DebateRound],
    ) -> list[DebateArgument]:
        """Run a single debate round with all agents in parallel."""

        async def query_agent(agent: dict) -> DebateArgument:
            if round_type == "opening":
                prompt = OPENING_PROMPT.format(question=question)
            elif round_type == "final":
                # Build scoped context blocks from prior arguments
                context_blocks = _build_context_blocks(prior_rounds)
                scoped_args = filter_context_for_agent(agent, context_blocks)
                prompt = FINAL_PROMPT.format(
                    question=question,
                    prior_arguments=scoped_args,
                )
            else:
                context_blocks = _build_context_blocks(prior_rounds)
                scoped_args = filter_context_for_agent(agent, context_blocks)
                prompt = REBUTTAL_PROMPT.format(
                    question=question,
                    round_number=round_number,
                    prior_arguments=scoped_args,
                )

            response = await self.client.messages.create(
                model=self.thinking_model,
                max_tokens=self.thinking_budget + 4096,
                thinking={"type": "enabled", "budget_tokens": self.thinking_budget},
                system=agent["system_prompt"],
                messages=[{"role": "user", "content": prompt}],
            )
            return DebateArgument(
                name=agent["name"],
                content=_extract_text(response),
                round_number=round_number,
            )

        return await asyncio.gather(
            *(query_agent(agent) for agent in self.agents)
        )

    async def _synthesize(
        self, question: str, rounds: list[DebateRound]
    ) -> str:
        """Synthesize the full debate transcript."""
        transcript = format_prior_arguments(rounds)
        response = await self.client.messages.create(
            model=self.thinking_model,
            max_tokens=self.thinking_budget + 4096,
            thinking={"type": "enabled", "budget_tokens": self.thinking_budget},
            system="You are a strategic synthesizer producing actionable conclusions from structured debates.",
            messages=[{
                "role": "user",
                "content": SYNTHESIS_PROMPT.format(
                    question=question, transcript=transcript
                ),
            }],
        )
        return _extract_text(response)


def _extract_text(response: anthropic.types.Message) -> str:
    """Extract text from a response that may contain thinking blocks."""
    parts = []
    for block in response.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "\n".join(parts)


def _build_context_blocks(rounds: list[DebateRound]) -> list[dict]:
    """Build scoped context blocks from debate rounds for agent filtering."""
    blocks = []
    for rnd in rounds:
        for arg in rnd.arguments:
            # Infer scope from agent name — defaults to "all" for unscoped agents
            scope = "all"
            name_lower = arg.name.lower()
            if "financial" in name_lower or "cfo" in name_lower:
                scope = "financial"
            elif "technology" in name_lower or "cto" in name_lower:
                scope = "technical"
            elif "marketing" in name_lower or "cmo" in name_lower:
                scope = "market"
            elif "operations" in name_lower or "coo" in name_lower:
                scope = "operational"
            elif "revenue" in name_lower or "cro" in name_lower:
                scope = "financial"
            blocks.append(tag_context(
                f"--- Round {rnd.round_number} ({rnd.round_type}) ---\n[{arg.name}]:\n{arg.content}",
                scope,
            ))
    return blocks
