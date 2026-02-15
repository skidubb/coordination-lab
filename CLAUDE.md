# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Coordination Lab** — Cardinal Element's multi-agent research program. The goal is to empirically validate 30 coordination protocols across 8+ problem types with varying tool-access conditions, then build an **adaptive router** that selects the optimal protocol for any incoming strategic question.

This is a **research and documentation project**, not a traditional codebase. There are no build commands, tests, or linters.

## Key Documents

- `The Coordination Lab *.md` — The master research spec: problem type taxonomy (8 types, 12 total), 30 coordination protocols, 20-week execution roadmap, evaluation rubrics, and benchmark questions
- `Deep Research - multiagent teams.txt` — Literature review citing academic papers (2024–2026) that validate the protocol designs. Key papers: Reasoning Router, AgentiQL, TAO, AgentCDM, TRIZ Agents, HypoAgents, MDAgents
- `protocol-diagrams/` — Mermaid diagram reference for all 30 protocols (see below)

## Protocol Diagrams Structure

```
protocol-diagrams/
├── 00-overview.md              # Index, legend, category map + P0 meta-protocols
├── 01-baselines.md             # P1-P5
├── 02-liberating-structures.md # P6-P15
├── 03-intelligence-analysis.md # P16-P18
├── 04-game-theory.md           # P19-P21
├── 05-org-theory.md            # P22-P23
├── 06-systems-thinking.md      # P24-P25
└── 07-design-thinking.md       # P26-P27
```

Each protocol has a **summary flow** (compact `graph LR`) and **detailed mechanics** (expanded `graph TB` with agent counts, inputs/outputs, decision criteria, and aggregation methods).

## Diagram Conventions

When creating or editing Mermaid diagrams, follow these conventions:
- `([Text]):::agent` — Agent/role nodes (rounded)
- `[Text]:::stage` — Processing stages (rectangles)
- `{Text}:::decision` — Decision gates (diamonds)
- Arrow labels describe data flowing between stages
- Category-specific agent colors:
  - Meta-Protocols: `#607D8B` | Baselines: `#4A90D9` | Liberating Structures: `#9B59B6`
  - Intelligence Analysis: `#E74C3C` | Game Theory: `#F39C12` | Org Theory: `#1ABC9C`
  - Systems Thinking: `#2ECC71` | Design Thinking: `#E91E63`

## Protocol Taxonomy

- **P0a-P0c: Meta-Protocols** — Router layer (Reasoning Router, Skip Gate, Tiered Escalation)
- **P1-P5: Baselines** — Single agent, parallel synthesis, debate, constraint negotiation
- **P6-P15: Liberating Structures** — TRIZ, Wicked Questions, Min Specs, Troika, HSR, DAD, 25/10, Ecocycle, 1-2-4-All, What/So What/Now What
- **P16-P18: Intelligence Analysis** — ACH, Red/Blue/White Team, Delphi Method
- **P19-P21: Game Theory** — Vickrey Auction, Borda Count, Interests-Based Negotiation
- **P22-P23: Org Theory** — Sequential Pipeline, Cynefin Probe-Sense-Respond
- **P24-P25: Systems Thinking** — Causal Loop Mapping, System Archetype Detection
- **P26-P27: Design Thinking** — Crazy Eights, Affinity Mapping

## Important Context

- The adaptive router uses **Cynefin framework** as its meta-logic (Clear/Complicated/Complex/Chaotic → different protocol families)
- Problem types map to protocol families: Diagnostic → ACH, Exploration → 1-2-4-All, Adversarial → Red/Blue/White, Prioritization → Borda Count, etc.
- The research program spans 20 weeks in 4 phases, testing protocols against benchmark questions with controlled variables
- "C-Suite" refers to Cardinal Element's multi-agent advisory product with role-specific agents (CEO, CFO, CTO, CMO, COO, CPO)
