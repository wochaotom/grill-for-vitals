# Anti-Overexpansion Query Protocol

Use this when vault research is needed. The goal is to get useful vault evidence without turning graph or retrieval expansion into false authority.

## Contents

- Core Rule
- Academic Note Corpora
- Business Note Corpora
- Overflow Handling
- Evidence Labels
- Recommended Query Shapes
- Hard Prohibitions
- Report Language

## Core Rule

Treat maps as maps and notes as evidence.

```text
navigation hint -> retrieval receipt -> direct note reads -> cited claim
```

No graph output, manifest summary, cluster label, or search result is proof by itself.

## Academic Note Corpora

Use the strictest corpus policy available:

- Do not use graph output as evidence.
- Do not use graph output as a connection map unless the user explicitly allows graph navigation.
- Do not use graph output for file selection unless the user changes that policy in the current turn.
- Use deterministic retrieval when the local corpus tooling supports it.
- Read every `read_in_full` note for non-overflow results.

If the user explicitly changes this policy in the current Grill run, graph navigation may be used only as a map to find candidate notes, rare terms, or communities. It still cannot answer the question, prove coverage, rank truth, or replace deterministic retrieval plus direct note reads.

Good pattern:

```text
run deterministic retrieval over the selected corpus with:
query: "SCMP Firecracker gVisor"
terms: "SCMP,Firecracker,gVisor"
max-read: bounded to the local policy
```

Clean receipt shape:

```text
query: SCMP Firecracker gVisor
corpus_total_notes: <count>
candidates_total: <count>
read_in_full: <count>
overflow: false
manifest_sha256: <hash>
```

Use rare anchors such as `SCMP`, `Firecracker`, `gVisor`, `ablation`, `verifiers`, and specific paper IDs instead of broad phrases like "agent risk tool design".

## Business Note Corpora

Some business-note corpora may allow graph navigation for broad orientation:

- Consult graph maps only when the user's current policy allows it.
- Treat graph maps as navigation only.
- Verify every substantive claim against durable notes read directly in this run.
- Use deterministic retrieval for reproducible receipts.

Correct flow:

```text
graph map -> likely communities/notes/terms
deterministic retrieval -> receipt
direct durable note reads -> evidence
```

Clean receipt examples:

```text
query: mnemonic
corpus_total_notes: <count>
candidates_total: <count>
read_in_full: <count>
overflow: false
manifest_sha256: <hash>
```

```text
query: AFK
corpus_total_notes: <count>
candidates_total: <count>
read_in_full: <count>
overflow: false
manifest_sha256: <hash>
```

## What Causes Overflow

The retrieval engine tokenizes the raw query too. Narrow `--terms` are not enough if the raw query contains broad words.

Avoid raw queries like:

```text
Business support for high-risk agent skill design permission gates credential data tool authority
```

Prefer:

```text
AFK
mnemonic
SCMP Firecracker gVisor
```

## Handling Overflow

If `overflow=true`:

1. Do not claim exhaustive vault support.
2. Treat the result as navigation only unless the required full-candidate reading process is completed.
3. Split the topic into narrower rare-anchor queries.
4. Read the top durable notes directly when they are clearly relevant.
5. Label direct reads as direct evidence and overflowed receipts as navigation.

## Direct Reads

When direct-reading notes after a map or overflowed receipt, say so plainly:

```text
Evidence basis: direct reads of durable notes X, Y, Z.
Coverage caveat: broad retrieval overflowed, so the receipt is navigation only.
```

This prevents coverage laundering.
