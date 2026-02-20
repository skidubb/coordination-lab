"""P4: Multi-Round Debate Protocol — Agent-agnostic orchestrator.

N rounds of structured debate → synthesis of evolved positions.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import anthropic

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
        orchestration_model: str = "claude-haiku-4-5-20251001",
    ):
        """
        Args:
            agents: List of {"name": str, "system_prompt": str} dicts.
            rounds: Number of debate rounds (minimum 2: opening + final).
            thinking_model: Model for all debate rounds and synthesis.
            orchestration_model: Not used in P4, kept for API consistency.
        """
        if not agents:
            raise ValueError("At least one agent is required")
        if rounds < 2:
            raise ValueError("At least 2 rounds required (opening + final)")
        self.agents = agents
        self.num_rounds = rounds
        self.thinking_model = thinking_model
        self.client = anthropic.AsyncAnthropic()

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
                prompt = FINAL_PROMPT.format(
                    question=question,
                    prior_arguments=format_prior_arguments(prior_rounds),
                )
            else:
                prompt = REBUTTAL_PROMPT.format(
                    question=question,
                    round_number=round_number,
                    prior_arguments=format_prior_arguments(prior_rounds),
                )

            response = await self.client.messages.create(
                model=self.thinking_model,
                max_tokens=4096,
                system=agent["system_prompt"],
                messages=[{"role": "user", "content": prompt}],
            )
            return DebateArgument(
                name=agent["name"],
                content=response.content[0].text,
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
            max_tokens=4096,
            system="You are a strategic synthesizer producing actionable conclusions from structured debates.",
            messages=[{
                "role": "user",
                "content": SYNTHESIS_PROMPT.format(
                    question=question, transcript=transcript
                ),
            }],
        )
        return response.content[0].text
