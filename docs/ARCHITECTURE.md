# Architecture

Atlas is a research state machine with retrieval, evidence and verification — not a chatbot wrapper.

## Layers

```text
API / Streamlit UI
        ↓
Orchestrator (LangGraph compile + checkpoints)
        ↓
Agents (planner, researcher, document analyst, verifier, critic, synthesiser)
        ↓
Tools (least privilege) + RAG (hybrid retrieval)
        ↓
PostgreSQL / pgvector / Redis
```

## Workflow

See the README Mermaid diagram. The compiled graph lives in `src/atlas/graph/workflow.py`.

## Evidence model

`Claim` → `Citation` → `Evidence` → source URL or document ID.

If the chain cannot be closed, the claim is `unsupported`.

## Memory

Conversation state stays in the graph checkpoint. Long-term memory is explicit (`POST /memory`) and removable.
