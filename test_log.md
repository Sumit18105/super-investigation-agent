# Test Log — SRVCABLE Research Agent

## Run 1 — Baseline evidence-first prompt

**Command:** `python research_agent.py SRVCABLE --as-of 2026-09-23 --output output/run1.md`

**Design:** Initial evidence-first workflow with source IDs, brief generation, and automated citation review.

**Actual result:** Generated the five required sections: Snapshot, Bull case, Bear case, Open questions, and Sources. Automated citation review returned PASS.

**Observed limitation:** The report flagged the conflicting Q1 revenue figures, but the prompt could more explicitly specify source priority and conflict-handling rules.

**Change for Run 2:** Added stricter rules for conflicting figures, official-source prioritization, management guidance, promotional sources, and similarly named entities.

## Run 2 — Stricter conflict handling

**Command:** `python research_agent.py SRVCABLE --as-of 2026-09-23 --output output/run2.md`

**Prompt/design change:** Strengthened conflict-handling and evidence-quality instructions in `system_prompt.md`.

**Actual result:** The brief explicitly compared official revenue of ₹1,248 crore with the secondary-news figure of ₹1,428 crore. It attributed growth guidance to management and distinguished Sarvottam Cable Network from Sarvottam Cables Ltd. Automated citation review returned PASS.

**Observed limitation:** The GST section did not fully preserve the company's stated appeal position and expectation of no material impact.

**Change for Run 3:** Strengthened citation/source-ID rules, entity matching, preservation of official-disclosure context, and required-section checks.

## Run 3 — Citation and entity validation

**Command:** `python research_agent.py SRVCABLE --as-of 2026-09-23 --output output/run3.md`

**Prompt/design change:** Added explicit instructions to use valid source IDs, connect citations to claims, distinguish source types, avoid entity confusion, and preserve material legal-disclosure context.

**Actual result:** The generated brief included all five required sections, flagged the revenue discrepancy, described the GST demand and intended appeal, and distinguished current promoter pledging from historical reports. Automated citation review returned PASS.

**Observed limitation:** The output included a historical stock closing price that was not necessary for the core research brief. Automated review PASS does not independently guarantee the factual accuracy of every claim. A manual review also identified a formatting typo in the basis-point figure.

**Final improvement identified:** Remove unnecessary historical price detail or label it explicitly as historical, correct the typo, and continue reviewing whether each citation supports the exact claim it accompanies.