# Super Investing — LangGraph Research Agent

A small multi-step research workflow that accepts a ticker and a folder of scraped Markdown documents, then produces a one-page source-grounded research brief.

## Why LangGraph?
LangGraph makes the orchestration explicit: document loading → evidence ledger → draft → citation/risk validation → conditional revision (up to one revision) → output. The conditional edge is intentional: a failed review routes the draft through revision; a passing review ends the loop. This is more explainable than a single large prompt, though it does not guarantee correctness.

## Requirements
- Python 3.10+
- An OpenAI API key with API access (API billing/limits are separate from a ChatGPT subscription)

## Setup
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY
```

## Run the required fictional test case
The eight supplied documents are in `research_pack/`. The assignment says the fictional company's cutoff date is 23 September 2026; do not search it online.
```bash
python research_agent.py SRVCABLE --as-of 2026-09-23 --output output/srvcable_brief.md
```
The final brief is printed and written to the output path. The model defaults to `gemini-2.5-flash-lite`; override with `GEMINI_MODEL` in `.env` if needed.

## Tests
Run `pytest` after installing the requirements. Unit tests check source loading, HTML-comment removal, and graph routing logic; they do not call the model API. Run the CLI three times with different prompt/design variants and record actual outputs and failures in `test_log.md` before claiming the assignment's three LLM runs are complete.

## Design choices
- Source IDs (`[S1]` etc.) are assigned deterministically from sorted filenames.
- HTML comments are removed before model context is built to reduce one prompt-injection path.
- The workflow asks the model to separate an evidence ledger from the final prose.
- A reviewer checks citations, source conflicts, entity confusion, dated claims, and promotional advice; failed reviews trigger one revision.
- The output retains the automated review status for transparency.

## Known limitations
- LLM review is not a formal proof; citations can still be wrong and must be manually checked.
- HTML comment removal is not a complete sanitizer; all source text remains untrusted.
- No live web/NSE data is used.
- The model's evidence extraction and draft quality depend on the selected model and API availability.
- The included `sample_output_not_model_generated.md` is an illustrative offline reference, not an actual model run.

## Suggested 2–3 minute demo
1. Show `research_pack/` and the CLI command (20 seconds).
2. Walk through `build_graph()` and explain the evidence-ledger node and conditional validation/revision loop (60 seconds).
3. Show the generated brief and how it flags the revenue conflict, the older pledge article versus newer shareholding filing, the GST demand, and the unrelated local cable-network penalty (45 seconds).
4. Show the test log and mention that model-generated runs must be recorded honestly; discuss citation-review limitations (20 seconds).


## Streamlit web app

The project includes `app.py` so an evaluator can use a browser instead of installing Python locally.

### Run locally

1. Create a Gemini API key in Google AI Studio.
2. Copy `.env.example` to `.env` and add your key as `GOOGLE_API_KEY`.
3. Install dependencies: `pip install -r requirements.txt`
4. Start the UI: `streamlit run app.py`

### Deploy for browser-only access

1. Push this project folder to a GitHub repository. Never commit `.env`.
2. Deploy the repository on Streamlit Community Cloud and choose `app.py`.
3. In the app's Advanced settings / Secrets, add:

   `GOOGLE_API_KEY = "your-key-here"`

4. Deploy and test the public app URL from a private/incognito browser window.

The evaluator does not need their own API key. The app owner supplies the key privately in deployment secrets. Gemini free-tier access and quotas may vary; monitor quota and do not promise unlimited usage.

The default model is `gemini-2.5-flash-lite`, selected as a lightweight option. You can change it using `GEMINI_MODEL` if the model name or availability changes.

## Important testing note

The bundled sample output is illustrative and is not a claim that the model has generated or validated it. Run the app and record actual test results before submitting the assignment.
