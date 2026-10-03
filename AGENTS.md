# RetailMind — AI implementation instructions

Updated: 2026-10-03

## 1. Current user direction

Build the complete RetailMind V1 first. The user will review the working project and learn its implementation afterward. The user will find and supply the frontend design. Ask the user for necessary inputs when a real dependency requires them; continue independent work meanwhile.

This direction supersedes the teaching-paced instructions in `RetailMind_Codex_Plan.md`, including the requirement to implement only one learning session, stop for exercises, or require learner understanding before advancing. The original plan remains the product and evaluation specification. Its 12-week schedule is a learning roadmap, not a mandatory execution duration for AI.

Communicate with the user in Vietnamese. Write source code, identifiers, docstrings, README and product UI in English. Post-project learning guides may be Vietnamese with English technical terms.

## 2. First actions in the actual workspace

1. Read the entire `RetailMind_Codex_Plan.md` and all applicable repository instructions.
2. Inspect existing source, progress, uncommitted changes, Git root, branch and remotes. Preserve existing work and reuse suitable implementations. Do not initialize a nested repository.
3. Check the actual OS, Python, package manager and available resources. Do not infer the user's hardware from this document or conversation history.
4. Identify completed work from executable evidence. Create an implementation checklist in `docs/progress.md`.
5. Set up a project-specific environment. Install only needed dependencies; verify compatibility and record reproducible versions. Consult current official documentation for installed APIs.
6. Proceed through the phases below until V1 is implemented and verified, or a concrete blocker prevents further dependent work. Do not pause merely because a teaching session or phase has ended.

This file does not claim that any repository, dependency installation, trained model or GitHub action already exists.

## 3. Product and evaluation invariants

- Predict a ranked list of up to 10 products a customer may purchase in the next 30 days. Repeat purchases are allowed. A ranking score is not a purchase probability.
- Use UCI Online Retail II as specified in the original plan. Check the actual workbook and all sheets; record source, license, file hash, schema and row counts.
- Preserve source timestamps with their unspecified timezone; do not silently assign UTC.
- Historical inputs satisfy `timestamp < cutoff`. Outcomes satisfy `cutoff <= timestamp < cutoff + 30 days`.
- All models, features, mappings, product descriptions, RFM thresholds, popularity, candidate sets and explanation evidence must respect the snapshot cutoff.
- Build separate validation and test bundles. Historical replay uses the bundle built from that cutoff's history, never a later model.
- Select hyperparameters and routing on validation, freeze them, then evaluate test. Do not tune on test results. If a protocol bug requires a rerun, document what happened and the corrected run.
- Compare Popularity, ItemCF and ALS on the same candidate set, cohorts, labels and repeat policy. ALS is not required to win.
- The main ranking cohort is historical customers with at least one valid future purchase. Report customers with empty labels separately rather than assigning them zero recall.
- Main Recall includes all distinct valid future products, including products unknown at cutoff. Report eligible-label recall and label availability separately.
- Use full candidate ranking and macro averaging as specified in the plan. Avoid sampled negatives in V1.
- Keep recommendation services separate from future labels. Outcomes are exposed only through the separate evaluation/replay path.
- Keep raw source immutable. Track row lineage and cleaning counts. Missing CustomerID may support analytics, never a fabricated shared customer.
- Do not use future cancellations to revise past snapshots. Keep cancellation/adjustment handling explicit and auditable.
- Explain recommendations from actual historical evidence. Report the true serving model and fallback reason.
- Unknown customer IDs and explicit new-customer mode are distinct cases.
- Do not add churn prediction, payments, inventory management, chatbot, demand forecasting or unrelated V2 features without user direction.
- Never invent metrics, revenue gains, benchmark results, test passes, public URLs or GitHub completion claims.

## 4. Frontend design handoff

The final visual design is supplied by the user. Build the data pipeline, evaluation and API while waiting. A minimal inspection interface is acceptable for functional verification; label it provisional in progress and do not treat it as the approved frontend.

When the frontend phase needs the design, request a bundled handoff containing:

- A Figma link, screenshots, template or reference pages.
- Which reference applies to each of the six planned pages, if available.
- Required colors, typography, logo and assets, if the reference does not establish them.
- Preferred frontend framework, if the user has a preference.
- Any specifically required responsive behavior or interactions.

Do not require every asset to exist before proceeding. Infer ordinary details from a clear reference and record the decisions. Ask for clarification only if ambiguity materially changes the result.

Streamlit is the original default. Inspect the design before committing to the final UI framework. If the supplied layout requires substantially more customization, explain the tradeoff and resolve the framework choice with the user. Keep domain logic in Python services and a stable API so UI choice does not require reimplementing recommendation logic.

The six pages remain Overview, Customers, Historical Replay, Products, Model Evaluation and Data Quality. Preserve snapshot context, KPI definitions, units, evidence, fallback states, loading/empty/error states and CSV metadata. Build and verify the agreed layouts on desktop and mobile. Verify snapshot switching and caching behavior through actual interaction.

Do not describe the full project as complete while the final design, frontend integration or relevant verification is pending. Report backend readiness and overall V1 readiness separately.

## 5. Execution phases

### A. Foundation and repository

Set up the package, configuration, README, ignore rules and progress/decision logs. Inspect and connect the actual GitHub repository. Establish reproducible setup and small fixtures. Avoid installing the entire future stack unnecessarily.

### B. Data ingestion and quality

Implement workbook inspection, source manifest, raw row lineage, raw Parquet generation and analytics/recommendation eligibility. Preserve raw values where needed. Build row-count reconciliation and data-quality reporting. Verify cancellations, missing IDs, invalid price/quantity, duplicate handling and idempotency on meaningful fixtures before the full source run.

### C. SQL and snapshots

Implement DuckDB queries, documented KPIs, invoice-level aggregation, RFM, customer/product snapshots, interactions and candidate sets. Add cutoff boundary and future-invariance checks. Determine actual schema and exclusions from inspected evidence; avoid undocumented product-code heuristics.

### D. Baseline and evaluator

Implement 30-day labels, cohort accounting, ranking metrics and Popularity. Verify metrics by hand on tiny examples and run the same evaluator on real validation data. Add the provisional V0 inspection interface if useful. Record real baseline results and unresolved limits.

### E. ItemCF and ALS

Implement sparse interactions, ItemCF without diagonal self-similarity, ALS with checked axis conventions and confidence scaling applied once. Preserve repeat purchases. Use a limited, logged validation search and reproducible seeds. Implement evidence and fallback. Select the serving model from validation, not model complexity.

### F. Frozen evaluation and reporting

Analyze cohorts and failure cases, freeze settings, build the test bundle and run final test evaluation. Preserve both replay bundles. Produce evaluation reports and a model card with measured results, cohort sizes, metadata and limitations. A model that does not outperform Popularity is a valid documented outcome.

### G. API and frontend integration contract

Implement FastAPI schemas, read-only model loading, endpoints, validation, error codes, request IDs, logs and CSV export. Do not train within requests. Keep future labels outside recommendation service loading. Test ordinary and failure paths, then hand a working API contract to the frontend implementation.

### H. User-designed frontend

Implement the supplied design and six functional pages. Integrate the real API, snapshot selector, recommendations, evidence, historical outcomes and evaluation artifacts. Do not use invented production data to make screens appear complete. Clearly label any synthetic fixture used for local development.

### I. Packaging and delivery

Complete meaningful tests and GitHub CI, build Docker packaging, verify setup from a clean environment and measure documented performance on the actual machine. Prepare screenshots, README, architecture, data dictionary, learning guides and a demo script. Create release checkpoints only after verification.

Local run instructions and a working local demo are required. Public hosting remains optional until a destination and costs are resolved. Paid services, credentials and hosting decisions must not be guessed. Produce a reviewable implementation before requesting a deployment decision if one is needed.

## 6. GitHub workflow

GitHub is mandatory throughout the project. Inspect the existing repository and configured account/remote before requesting an account or repository destination.

Use scoped Issues, branches, commits and PRs for meaningful changes. Review diffs and run relevant checks before merge. Solo self-review is allowed. Record local commit, push, PR, merge and CI status separately and only after verification. Do not require a user approval for routine authorized changes solely to reproduce the old teaching flow; follow actual environment approval requirements.

Keep source, SQL, configuration, dependency locks, small fixtures, docs and aggregate reports in Git. Ignore environments, secrets, raw/processed full data, request logs and large model artifacts. Do not commit credentials or embed tokens in remote URLs. Ask the user to authenticate through the supported local flow when needed, never to paste tokens into chat.

If GitHub is blocked, continue local implementation and record the exact missing step. Do not force push, discard user edits or rewrite history as a routine synchronization method.

## 7. Handling missing inputs and blockers

Resolve ordinary implementation choices autonomously. Ask only for information that is genuinely unavailable and affects a dependent task, such as:

- The actual project workspace when it is inaccessible.
- GitHub repository/account destination if not determined from the workspace.
- Authentication through the supported flow.
- Source file when an authorized download cannot be completed.
- The frontend design at its integration stage.
- A hosting destination or paid-service decision if public deployment is requested.

State what is needed, why, which task is blocked and what can proceed. Bundle related questions. Continue independent phases rather than repeatedly waiting on nonessential choices. Never guess identifiers, credentials or unseen designs.

Use progress states `planned`, `in_progress`, `done` and `blocked`. On a session interruption or context limit, persist a checkpoint and exact next actions. On resumption, inspect that checkpoint and continue rather than recreating completed work. Do not promise to keep working in the background after the active session ends.

## 8. Verification and completion

Run checks appropriate to each change. Required evidence includes:

- Source/sheet counts, file hash, row lineage and cleaning reconciliation.
- Idempotent ingestion and fixture cases for missing IDs, cancellations and invalid records.
- Cutoff boundaries and future-invariance of snapshots and recommendations.
- ID mapping round trips, sparse shapes, repeat policy, uniqueness and candidate eligibility.
- Hand-verified ranking metrics, cohort definitions and consistent model comparisons.
- Actual validation selection and frozen test results with configurations and metadata.
- API success/failure cases, explicit new-customer handling and missing-model behavior.
- End-to-end UI/API behavior with the supplied design and snapshot switching.
- A clean environment run using README commands.
- Real benchmark environment, warm/cold behavior and reported latency if measured.
- Verified GitHub source/CI/release status where access is available.

Report remaining blockers or failed acceptance criteria. Passing fixture tests is not evidence that full-data training, final evaluation or final frontend works. Synthetic results must never be presented as real-dataset results.

## 9. Learning materials prepared during implementation

The user studies after delivery. Document enough to reconstruct the reasoning without forcing the user through lessons while building:

- `docs/progress.md`: implemented scope, changed files, actual commands/results, blockers and GitHub state.
- `docs/decisions.md`: decisions, alternatives, reasons and evidence.
- `docs/architecture.md`: offline pipeline, serving path, artifacts and outcome separation.
- `docs/data_dictionary.md`: granularity, keys, schema and KPI definitions.
- `docs/learning_path.md`: prerequisite order and links to relevant modules in this repository.
- `docs/code_walkthrough.md`: trace one raw row through cleaning, snapshot construction, recommendation, evaluation and UI/API display.
- `docs/learning_log.md`: preserve learner-authored explanations; do not claim the user understands concepts they have not demonstrated. Mark suggested exercises as pending.

Explain important algorithms and invariants near the implementation or in focused docs. Prefer readable modules and explicit interfaces over notebook-dependent state or unnecessary abstractions. Post-project exercises should help the user explain, modify and debug the actual finished code.

## 10. Suggested kickoff message

```text
Read AGENTS.md and the full RetailMind_Codex_Plan.md, then inspect the actual workspace.
Build and verify complete RetailMind V1 under the AI implementation mode in AGENTS.md.
I will supply the frontend design and other truly necessary inputs when requested.
Continue independent work when an input blocks only one part. Preserve existing work,
record actual results and checkpoints, and prepare the documentation I will study afterward.
Start implementation now; do not stop at a plan or at the end of a teaching session.
```
