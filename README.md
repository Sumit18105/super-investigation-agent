
# Super Investing — AI Equity Research Agent

A source-grounded equity research workflow built with LangGraph, Gemini, and Streamlit. It produces concise research briefs from supplied company documents, with inline source citations, conflict detection, risk analysis, and automated review.

## Features

- **Assignment demo:** Research Sarvottam Cables Ltd (SRVCABLE) using the supplied research pack.
- **Custom document upload:** Upload documents for another company and generate a separate research brief.
- **Supported document formats:** Markdown (`.md`), text (`.txt`), and PDF (`.pdf`), subject to successful text extraction.
- **Evidence-first analysis:** Extracts evidence before drafting the final brief.
- **Citation and risk review:** Checks required sections, source citations, conflicting claims, and company relevance.
- **Conditional revision:** A failed review can trigger a revision before the final output.
- **No live web research:** The agent uses documents supplied for the current run; it does not automatically fetch live prices, news, or exchange filings.

## Why LangGraph?

LangGraph makes the research workflow explicit:

Document loading → Evidence extraction → Drafting → Validation → Conditional revision → Final brief.

The conditional edge routes a draft through revision when review fails, subject to the workflow's configured retry limit. This makes the process more explainable than a single large prompt, but does not guarantee factual correctness.

## Requirements

- Python 3.10 or newer, subject to dependency compatibility.
- A Google Gemini API key with access to the configured model.
- Dependencies listed in `requirements.txt`.

API quotas, model availability, and billing or usage limits depend on the provider and account.

## Setup

Create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a local `.env` file using `.env.example` as a reference. Set your Gemini API key:

```env
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Use the model name supported by your current code and Google AI account. The value above is an example; model availability can change. Never commit `.env` or expose API keys in source code, logs, screenshots, or recordings.

## Run the Streamlit application

From the project root:

```bash
python -m streamlit run app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501` or another port if that one is occupied.

### Mode 1: Assignment demo — SRVCABLE

1. Select **Assignment demo (SRVCABLE)**.
2. Use the supplied documents in `research_pack/`.
3. Set the assignment cutoff date to 23 September 2026 (`2026-09-23`).
4. Generate the research brief.

The assignment requires the fictional SRVCABLE case to be analyzed using its supplied documents. Do not search online for the fictional company.

### Mode 2: Upload my own documents

1. Select **Upload my own documents**.
2. Upload documents belonging to one company.
3. Enter the appropriate company ticker or identifier.
4. Set the research cutoff date.
5. Generate and inspect the brief.

For reliable company isolation, do not mix documents from unrelated companies in one run. Check that every cited source ID maps to a document uploaded for that run.

The upload feature enables document-based research on other companies. It does not provide automatic web search or guarantee that uploaded information is complete or accurate.

## Research Brief Format

The generated brief uses these five sections:

1. **Snapshot** — Company identity, reported results, and operating context.
2. **Bull case** — Evidence-supported growth drivers and positive developments.
3. **Bear case** — Material risks and adverse evidence.
4. **Open questions** — Unresolved discrepancies and missing information.
5. **Sources** — Source IDs, document names, and available source metadata.

Material factual claims should include inline citations such as `[S1]`. Historical results, management guidance, analyst opinions, and promotional claims must be distinguished. Conflicting figures should be reported rather than silently reconciled.

## Tests

Run the automated test suite:

```bash
python -m pytest -v
```

The existing test suite checks source loading, HTML-comment removal, brief structure, citation handling, and graph validation or retry behavior, as covered by the tests in the repository.

Passing unit tests does not prove that every model-generated claim is correct. Test the application separately with the Gemini API enabled.

### Recommended manual test cases

- Generate the required SRVCABLE assignment brief.
- Upload the three NORTHSTAR test documents and inspect the resulting citations.
- Upload the three BLUEPEAK test documents and check whether the ₹310 crore versus ₹301 crore revenue discrepancy is flagged.
- Confirm that evidence from one company does not appear in another company's brief.
- Check how the app handles unreadable PDFs, missing text, invalid API credentials, and model/API errors.

Record actual outputs, failures, and dates in `test_log.md`. Do not describe a test as passed unless it was actually run.

## Design Choices

- Source IDs such as `[S1]` are assigned by the document-loading workflow.
- HTML comments are removed before model context is built to reduce one prompt-injection path.
- The workflow separates evidence extraction from final brief drafting.
- A reviewer checks structure, citations, conflicting evidence, entity relevance, and risk attribution.
- A failed review can trigger a revision according to the configured graph logic.
- Automated review status is shown to the user for transparency.

## Known Limitations

- LLM-based review is not a formal proof; citations and claims still require manual inspection.
- Removing HTML comments is not a complete prompt-injection defense. All source documents remain untrusted input.
- There is no automatic live web, market-price, or NSE data retrieval.
- Results depend on the quality and completeness of the supplied documents and the selected Gemini model.
- PDF support depends on extractable text; scanned image-only PDFs may require OCR, which is not guaranteed by the current workflow.
- A successful structural review does not establish that the underlying financial information is true.
- This application is an educational research workflow, not personalized investment advice.

## Streamlit Deployment

1. Push the project to GitHub without committing `.env` or API keys.
2. Configure the deployment to use `app.py`.
3. Add `GOOGLE_API_KEY` privately through the deployment platform's secrets settings.
4. Configure `GEMINI_MODEL` if required by the application.
5. Deploy and test the public URL in a private/incognito browser window.
6. Verify both assignment demo mode and custom document upload mode after deployment.

The evaluator should not need to supply their own API key if the deployment owner has configured the key correctly. Provider quotas and model availability can change.

## Suggested 2–3 Minute Demo

1. **Introduction (20 seconds):** Explain the problem and show the project structure.
2. **Architecture (35–45 seconds):** Show the LangGraph workflow and explain evidence extraction, validation, and conditional revision.
3. **Assignment demo (35–45 seconds):** Generate or display the SRVCABLE brief and highlight a source conflict or risk.
4. **Custom upload (30–40 seconds):** Show a NORTHSTAR or BLUEPEAK document-upload run and explain source attribution or conflict detection.
5. **Testing and limitations (20–30 seconds):** Show actual test results and mention that automated review does not guarantee factual accuracy.

## Important Notes

- `sample_output_not_model_generated.md`, if present, is an illustrative reference, not proof of an actual model run.
- Do not claim that sources were independently verified unless that verification was actually performed.
- Record real model outputs and test failures honestly.
