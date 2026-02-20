"""P3: Parallel Synthesis Protocol — Agent-agnostic orchestrator.

All agents answer independently → synthesizer merges into unified recommendation.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import anthropic

from .prompts import SYNTHESIS_SYSTEM_PROMPT


@dataclass
class AgentPerspective:
    name: str
    response: str


@dataclass
class SynthesisResult:
    question: str
    perspectives: list[AgentPerspective] = field(default_factory=list)
    synthesis: str = ""


class SynthesisOrchestrator:
    """Runs the 2-stage Parallel Synthesis protocol with any set of agents."""

    def __init__(
        self,
        agents: list[dict],
        thinking_model: str = "claude-opus-4-6",
        orchestration_model: str = "claude-haiku-4-5-20251001",
    ):
        """
        Args:
            agents: List of {"name": str, "system_prompt": str} dicts.
            thinking_model: Model for agent reasoning and synthesis.
            orchestration_model: Not used in P3 (all stages are thinking tasks),
                                 kept for API consistency across protocols.
        """
        if not agents:
            raise ValueError("At least one agent is required")
        self.agents = agents
        self.thinking_model = thinking_model
        self.client = anthropic.AsyncAnthropic()

    async def run(self, question: str) -> SynthesisResult:
        """Execute the full Parallel Synthesis protocol."""
        result = SynthesisResult(question=question)

        # Stage 1: Parallel query — all agents answer independently
        print(f"Stage 1: Querying {len(self.agents)} agents in parallel...")
        responses = await self._parallel_query(question)
        result.perspectives = [
            AgentPerspective(name=agent["name"], response=resp)
            for agent, resp in zip(self.agents, responses)
        ]

        # Stage 2: Synthesis — merge all perspectives
        print("Stage 2: Synthesizing perspectives...")
        result.synthesis = await self._synthesize(question, result.perspectives)

        return result

    async def _parallel_query(self, question: str) -> list[str]:
        """Stage 1: All agents answer the question in parallel."""

        async def query_agent(agent: dict) -> str:
            response = await self.client.messages.create(
                model=self.thinking_model,
                max_tokens=4096,
                system=agent["system_prompt"],
                messages=[{"role": "user", "content": question}],
            )
            return response.content[0].text

        return await asyncio.gather(
            *(query_agent(agent) for agent in self.agents)
        )

    async def _synthesize(
        self, question: str, perspectives: list[AgentPerspective]
    ) -> str:
        """Stage 2: Synthesize all perspectives into a unified recommendation."""
        perspectives_text = "\n\n".join(
            f"=== {p.name} ===\n{p.response}" for p in perspectives
        )
        prompt = (
            f"ORIGINAL QUESTION:\n{question}\n\n"
            f"INDEPENDENT PERSPECTIVES:\n{perspectives_text}"
        )
        response = await self.client.messages.create(
            model=self.thinking_model,
            max_tokens=4096,
            system=SYNTHESIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
