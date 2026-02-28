# Why CortexLog Is Useful

## Simple version first

CortexLog is like a project memory notebook that both humans and AI agents can read and update.

In simple words, this tool is doing this:

- saving what we are trying to do
- saving what decisions we made
- saving what we claim is true
- saving proof for those claims
- checking if our claims conflict with each other
- preparing a clean handoff for the next person or agent

So instead of losing context between chats, sessions, or team members, the project keeps a durable memory timeline.

## What problem it solves

When people or AI agents work on code over time, they often forget:

- why a decision was made
- what is still pending
- whether a statement is still true
- where proof for a claim exists

This causes repeated mistakes, confusion in handoffs, and slow debugging.

CortexLog solves this by creating an append-only record of work events and a verification layer (TruthGraph).

## What is happening in this repo

This repo contains a CLI tool (`cortexlog.py`) and core logic (`tools/cortexlog.py`) that:

1. Records work events into `.cortexlog.jsonl`
2. Lets you search and summarize those events
3. Tracks open tasks from checkpoints and resolves
4. Captures causal claims (`trace`) with evidence and dependencies
5. Verifies consistency (`verify`) before handoff or release
6. Generates handoff packets (`handoff`) for the next human/agent

## Core commands in plain language

- `checkpoint`: "Here is the goal, decision, and what to do next."
- `trace`: "Here is a claim, and here is the proof/status."
- `verify`: "Check if our claims are consistent and complete enough."
- `resolve`: "This task is done now."
- `handoff`: "Create a summary for whoever works next."
- `search/list/stats`: "Help me find and review what happened."

## Why this is useful for humans

- You can return after a week and still understand the project state quickly.
- Team members can review decision history without guessing.
- Incident and release timelines are clearer.
- Handoffs are easier and less error-prone.
- You reduce "tribal knowledge" locked in one person’s head.

## Why this is useful for AI agents

AI agents often lose context when:

- session windows reset
- token limits cut older messages
- handoff happens between different agents

CortexLog provides durable memory outside the chat history.

This means an agent can recover state from the project itself, not from fragile conversation context.

## Why TruthGraph matters

TruthGraph is the part that turns notes into safer reasoning.

It checks for:

- Contradictions: same claim marked both confirmed and failed
- Dangling dependencies: claim depends on unknown trace IDs
- Unresolved failed claims: latest state is still failed
- Missing evidence warnings: claim confirmed without proof

This is useful because it prevents bad handoffs like:

- "tests pass" when later evidence says they failed
- "issue fixed" with no supporting trace

## Real-world example

Without CortexLog:

- Agent A says migration is safe
- Agent B later sees CI failure
- Agent C gets mixed messages and deploys anyway

With CortexLog + TruthGraph:

- Agent A records a confirmed claim with evidence
- Agent B records a failed claim for the same statement
- `verify` fails and blocks a confident handoff
- Team resolves contradiction before deploy

## Why append-only JSONL

- Easy to inspect with normal tools (`cat`, `tail`, `rg`)
- Easy to merge and audit
- No external service required
- Good fit for local-first workflows

## Limits to know

- It depends on disciplined updates (garbage in, garbage out)
- Evidence quality is user/agent dependent
- It is not a full graph database (by design, it is lightweight)

## When to use it

Use CortexLog if you:

- do iterative coding over multiple sessions
- collaborate across humans and AI agents
- need reliable handoffs and decision traceability
- want a cheap local guardrail before PR/release

## One-sentence takeaway

CortexLog is a lightweight memory + truth-check layer for coding workflows, so humans and AI agents can work faster with fewer context mistakes.
