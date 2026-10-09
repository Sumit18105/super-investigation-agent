from __future__ import annotations
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from research_agent import build_graph, DEFAULT_PACK

ROOT = Path(__file__).resolve().parent
load_dotenv()

st.set_page_config(page_title="AI Equity Research Agent", page_icon="📊", layout="wide")
st.title("AI Equity Research Agent")
st.caption("LangGraph + Gemini · Source-grounded research brief · No live web research")

with st.sidebar:
    st.subheader("Research settings")
    ticker = st.text_input("NSE ticker", value="SRVCABLE").strip().upper()
    if ticker and ticker != "SRVCABLE":
        st.error(
            "This demo contains research documents only for SRVCABLE. "
            "Please use SRVCABLE to avoid generating a misleading report."
        )
    as_of = st.date_input("Research cutoff date", value=__import__("datetime").date(2026, 9, 23))
    st.caption("This demo uses the bundled research documents. It does not fetch live prices or news.")
    st.divider()
    st.markdown("**Evidence rules**")
    st.markdown("- Cite claims with source IDs\n- Flag conflicting figures\n- Separate facts from management claims\n- Treat promotional sources cautiously")

api_key = os.getenv("GOOGLE_API_KEY", "")
try:
    if not api_key and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass

if not api_key:
    st.warning("The app owner must add GOOGLE_API_KEY in the deployment secrets. Visitors do not need their own key.")
else:
    os.environ["GOOGLE_API_KEY"] = api_key

if st.button(
    "Generate research brief",
    type="primary",
    disabled=not bool(ticker) or ticker != "SRVCABLE" or not bool(api_key),
):
    with st.spinner("Reading sources, building an evidence ledger, drafting, and checking citations..."):
        try:
            result = build_graph().invoke({
                "ticker": ticker,
                "as_of": as_of.isoformat(),
                "pack_dir": str(DEFAULT_PACK),
                "output_path": None,
            })
            brief = result.get("brief", "The workflow returned no brief.")
            st.success("Brief generated.")
            st.markdown(brief)
            st.download_button(
                "Download Markdown brief",
                data=brief,
                file_name=f"{ticker.lower()}_research_brief.md",
                mime="text/markdown",
            )
            with st.expander("Show validation details"):
                st.write(result.get("validation", "No validation details returned."))
        except Exception as exc:
            st.error("The model request failed. Check the deployment secret, Gemini API access, and quota.")
            st.code(f"{type(exc).__name__}: {exc}")

st.divider()
st.caption("Educational research workflow only. Not investment advice. Source documents may contain errors or conflicting claims.")
