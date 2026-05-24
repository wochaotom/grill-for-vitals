# Report Template

Use this shape for checkpoint or final reports.

## Contents

- Vitals Report
- Scope Checked
- Scope Gate
- Summary
- Catastrophe Table
- Hard Stops
- Amber/Green/Unknowns
- Questions For User
- Evidence Inspected
- Source Basis
- Inferences
- Code-Hygiene Handoffs
- Next Verification
- Non-Claims

## Vitals Report

### Scope Checked

- Workspace:
- Project files inspected:
- Docs/configs inspected:
- Vault or web sources used:
- Activated standards/source IDs:
- Not inspected:

### Scope Gate

```text
Candidate vital:
Catastrophic failure mode:
Evidence gate:
Scope decision: <Grill / code-hygiene handoff / ordinary review>
```

### Summary

State the actual evidence. If the repo is empty, say so. If a vital is unknown, say unknown.

### Catastrophe Table

| Vital | Status | Evidence | Failure Mode | Required Next Step |
|---|---|---|---|---|
| Secrets/control plane | Unknown | No secret inventory found | Key leak or deploy/admin compromise | Inventory credentials and run secret scan |
| Auth/tenant isolation | Unknown | No auth code inspected | Cross-tenant access | Add/prove server-side authorization |

### Hard Stops

List `Red` items that should block launch, automation, or live operation.

```text
Red: <vital>
Evidence: <file/config/test/log or missing evidence>
Why it blocks: <catastrophic path>
Required fix/proof: <specific evidence gate>
```

### Amber Items

List sensitive areas where evidence is incomplete but no immediate hard stop is proven.

### Green Items

List only controls proven by inspected evidence.

### Unknowns

List unresolved questions. Unknowns should be concrete and answerable.

### Questions For User

Ask one question at a time in conversation. If writing a report, include the backlog:

```text
Question:
Recommended answer:
Evidence needed:
Why this matters:
```

### Evidence Inspected

Use exact paths, commands, receipts, and source links.

### Source Basis

List only sources activated by a vital.

```text
Source ID:
URL:
Checked date:
Used for:
Limitations: <draft/concept/provisional/vendor/not a compliance audit/etc.>
```

### Inferences

Separate inferred architecture or risks from direct evidence.

### Code-Hygiene Handoffs

List non-vital findings only as handoffs. Do not let them become the Grill report.

```text
Handoff:
Why not grilled:
Suggested owner:
```

### Next Verification

List commands, tests, code reads, or external checks that would move Red/Amber/Unknown toward Green.

### Non-Claims

Include when relevant:

- This is not a compliance certification.
- This is not legal, medical, or financial advice.
- No claim of safety/readiness is made for areas marked Unknown.
