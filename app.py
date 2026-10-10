from __future__ import annotations

import os

import re
import textwrap

from datetime import date

from io import BytesIO

from pathlib import Path

import streamlit as st

from dotenv import load_dotenv

from pypdf import PdfReader

from research_agent import build_graph, DEFAULT_PACK

# =========================================================

# CONFIG

# =========================================================

ROOT = Path(__file__).resolve().parent

load_dotenv(ROOT / ".env")

st.set_page_config(

    page_title="S.I.A. | Super Investigation Agent",

    page_icon="◈",

    layout="wide",

    initial_sidebar_state="collapsed",

)

MAX_FILES = 20

MAX_TOTAL_BYTES = 20 * 1024 * 1024

DEMO_MODE = "Assignment Demo"

UPLOAD_MODE = "My Documents"

if "sia_ticker" not in st.session_state:

    st.session_state.sia_ticker = "SRVCABLE"

if "sia_previous_mode" not in st.session_state:

    st.session_state.sia_previous_mode = DEMO_MODE

# =========================================================

# THEME  (dark only)

# =========================================================

# Layered backgrounds, darkest to lightest:
#   bg      -> page canvas
#   input   -> inputs and option boxes (inset, darker than the card)
#   panel   -> cards, expanders, dialogs
#   group   -> raised group box (source selector)
#   header  -> top brand bar
#   soft    -> selected / hover / accent tint

C = {

    "bg": "repeating-radial-gradient(black, transparent 100px)",

    "panel": "repeating-linear-gradient(black, transparent 100px)",

    "input": "#0A1118",

    "group": "repeating-linear-gradient(black, transparent 100px)",

    "header": "repeating-radial-gradient(black, transparent 100px)",

    "header_border": "#24465B",

    "border": "#30194F",

    "text": "#EDF3F8",

    "muted": "#9EADBC",

    "accent": "#75DDBB",

    "button": "#176B57",

    "soft": "#18352D",

    "link": "#75DDBB",

}

st.markdown(

    f"""

    <style>

    :root {{

        color-scheme: dark;

        --bg: {C["bg"]};

        --panel: {C["panel"]};

        --input: {C["input"]};

        --group: {C["group"]};

        --header: {C["header"]};

        --header-border: {C["header_border"]};

        --border: {C["border"]};

        --text: {C["text"]};

        --muted: {C["muted"]};

        --accent: {C["accent"]};

        --button: {C["button"]};

        --soft: {C["soft"]};

        --link: {C["link"]};

    }}

    html, body, .stApp,

    [data-testid="stAppViewContainer"],

    [data-testid="stMain"],

    [data-testid="stMainBlockContainer"] {{

        background: var(--bg) !important;

        color: var(--text) !important;

    }}

    [data-testid="stHeader"],

    [data-testid="stToolbar"] {{

        background: var(--bg) !important;

    }}

    .block-container {{
        width: min(100% - 3rem, 1180px) !important;
        max-width: 1180px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
    }}

    h1, h2, h3, h4, p, li, label,

    [data-testid="stMarkdownContainer"] {{

        color: var(--text);

    }}

    h1, h2, h3 {{

        letter-spacing: -0.025em;

    }}

    [data-testid="stCaptionContainer"],

    .sia-subtitle, .sia-muted {{

        color: var(--muted) !important;

    }}

    hr {{

        border-color: var(--border) !important;

    }}

    .sia-brand {{

        display: flex;

        align-items: center;

        gap: 13px;

        min-height: 48px;

    }}

    .sia-mark {{

        width: 44px;

        height: 44px;

        display: flex;

        align-items: center;

        justify-content: center;

        border-radius: 12px;

        background: var(--soft);

        border: 1px solid var(--border);

        color: var(--accent);

        font-size: 27px;

        font-weight: 700;

        flex-shrink: 0;

    }}

    .sia-name {{
        font-size: 23px;
        line-height: 1.35;
        font-weight: 750;
        color: var(--text);
        overflow-wrap: anywhere;
    }}

    .sia-subtitle {{

        font-size: 12px;

        margin-top: 4px;
        

    }}

    .sia-label {{

        color: var(--muted);

        font-size: 12px;

        font-weight: 650;

        text-transform: uppercase;

        letter-spacing: .06em;

        margin-bottom: 7px;

    }}

    .sia-card {{

        background: var(--panel);

        border: 1px solid var(--border);

        border-radius: 13px;

        padding: 16px 18px;

    }}

    .sia-footer {{

        text-align: center;

        color: var(--muted);

        font-size: 12px;

    }}

    /* Inputs */

    [data-testid="stTextInput"] input,

    [data-testid="stDateInput"] input {{

        background: var(--input) !important;

        color: var(--text) !important;

        -webkit-text-fill-color: var(--text) !important;

        border: 1px solid var(--border) !important;

        border-radius: 9px !important;

        min-height: 42px;

        box-shadow: none !important;

    }}

    [data-testid="stTextInput"] input:focus,

    [data-testid="stDateInput"] input:focus {{

        border-color: var(--accent) !important;

        box-shadow: 0 0 0 1px var(--accent) !important;

    }}

    [data-testid="stDateInput"] button {{

        color: var(--accent) !important;

        background: var(--panel) !important;

    }}

    [data-baseweb="calendar"],

    [data-baseweb="popover"] > div {{

        background: var(--panel) !important;

        color: var(--text) !important;

    }}

    /* Radio controls */

    /* Centered source selector with two separate option boxes */

    [data-testid="stRadio"] {{
        width: 100% !important;
        text-align: center !important;
        margin: 0 auto 1.25rem !important;
    }}

    [data-testid="stRadio"] > label {{
        display: block !important;
        width: 100% !important;
        text-align: center !important;
        margin: 0 auto 12px !important;
    }}

    [data-testid="stRadio"] > div {{
        display: flex !important;
        justify-content: center !important;
        align-items: stretch !important;
        gap: 14px !important;
        width: 100% !important;
        margin: 0 auto !important;
    }}

    [data-testid="stRadio"] > div > label {{
        box-sizing: border-box !important;
        flex: 0 1 240px !important;
        width: 240px !important;
        min-width: 0 !important;
        min-height: 54px !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: var(--text) !important;
        background: var(--panel) !important;
        border: 1px solid var(--border) !important;
        border-radius: 11px !important;
        padding: 12px 18px !important;
        transition: border-color .15s ease, background .15s ease;
    }}

    [data-testid="stRadio"] > div > label:has(input:checked) {{
        background: var(--soft) !important;
        border-color: var(--accent) !important;
    }}

    [data-testid="stRadio"] > div > label:hover {{
        border-color: var(--accent) !important;
        background: var(--soft) !important;
    }}

    [data-testid="stRadio"] > div > label p {{
        color: var(--text) !important;
        margin: 0 !important;
    }}

    @media (max-width: 560px) {{
        .block-container {{
            width: calc(100% - 1rem) !important;
            padding: 1rem .5rem 2rem;
        }}
        [data-testid="stRadio"] > div {{
            flex-direction: column !important;
            align-items: center !important;
        }}
        [data-testid="stRadio"] > div > label {{
            flex: 0 1 auto !important;
            width: min(100%, 320px) !important;
            min-width: 0 !important;
        }}
    }}

    .stButton > button,

    .stDownloadButton > button {{

        border-radius: 9px !important;

        min-height: 40px;

        font-weight: 600;

        transition: border-color .15s ease, background .15s ease;

    }}

    .stButton > button[kind="primary"],
    .stButton > button[kind="primary"]:hover,
    .stButton > button[kind="primary"]:focus,
    .stButton > button[kind="primary"]:active,
    [data-testid="stBaseButton-primary"],
    [data-testid="stBaseButton-primary"]:hover,
    [data-testid="stBaseButton-primary"]:focus,
    [data-testid="stBaseButton-primary"]:active {{
        background: var(--button) !important;
        background-color: var(--button) !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid var(--button) !important;
        min-height: 46px;
        box-shadow: none !important;
        filter: none !important;
    }}

    .stButton > button[kind="primary"]:hover,
    [data-testid="stBaseButton-primary"]:hover {{
        border-color: var(--accent) !important;
        background: var(--button) !important;
        background-color: var(--button) !important;
    }}

    .stButton > button[kind="primary"]:disabled,
    [data-testid="stBaseButton-primary"]:disabled {{
        background: var(--button) !important;
        color: #FFFFFF !important;
        opacity: .58 !important;
    }}

    .stButton > button[kind="secondary"],

    .stDownloadButton > button {{

        background: var(--panel) !important;

        color: var(--accent) !important;

        border: 1px solid var(--border) !important;

    }}

    .stButton > button[kind="secondary"]:hover,

    .stDownloadButton > button:hover {{

        border-color: var(--accent) !important;

    }}

    .stButton > button:disabled {{

        opacity: .45;

    }}

    /* Upload */

    [data-testid="stFileUploader"] {{

        background: var(--panel) !important;

        border: 1px dashed var(--border) !important;

        border-radius: 12px !important;

        padding: 10px !important;

    }}

    [data-testid="stFileUploader"] section,

    [data-testid="stFileUploader"] section div {{

        background: transparent !important;

        color: var(--text) !important;

    }}

    [data-testid="stFileUploader"] button {{

        background: var(--soft) !important;

        color: var(--text) !important;

        border: 1px solid var(--border) !important;

        border-radius: 8px !important;

    }}

    /* Status and expanders */

    [data-testid="stStatusWidget"],
    [data-testid="stStatusWidget"] *,
    [data-testid="stSpinner"],
    [data-testid="stSpinner"] *,

    [data-testid="stStatusWidget"] details,

    [data-testid="stStatusWidget"] summary,

    [data-testid="stExpander"],

    [data-testid="stExpander"] details,

    [data-testid="stExpander"] summary {{

        background: var(--panel) !important;

        color: var(--text) !important;

        border-color: var(--border) !important;

        border-radius: 10px !important;

    }}

    /* Source filenames */

    [data-testid="stMarkdownContainer"] code {{

        background: var(--soft) !important;

        color: var(--accent) !important;

        border: 1px solid var(--border);

        border-radius: 5px;

        padding: 2px 5px;

        overflow-wrap: anywhere;

        white-space: normal;

    }}

    [data-testid="stMarkdownContainer"] pre {{

        background: var(--panel) !important;

        border: 1px solid var(--border);

        border-radius: 9px;

        overflow-x: auto;

    }}

    [data-testid="stMarkdownContainer"] pre code {{

        background: transparent !important;

        border: none;

        color: var(--text) !important;

        white-space: pre;

    }}

    [data-testid="stMarkdownContainer"] a {{

        color: var(--link) !important;

    }}

    [data-testid="stDialog"] [role="dialog"] {{

        background: var(--panel) !important;

        color: var(--text) !important;

    }}

    [data-baseweb="modal"] > div:first-child {{

        background: rgba(0, 0, 0, .55) !important;

    }}

    @media (max-width: 700px) {{

        .block-container {{

            padding: 1rem .8rem 2rem;

        }}

        .sia-name {{

            font-size: 19px;

        }}

        .sia-mark {{

            width: 38px;

            height: 38px;

            font-size: 23px;

        }}

    }}


    /* Final layout normalization: one shared content grid and control scale */
    .block-container {{
        width: min(100% - 3rem, 1180px) !important;
        max-width: 1180px !important;
        margin-inline: auto !important;
    }}

    [data-testid="stHorizontalBlock"] {{
        align-items: stretch;
    }}

    [data-testid="stTextInput"],
    [data-testid="stDateInput"] {{
        width: 100% !important;
    }}

    [data-testid="stTextInput"] input,
    [data-testid="stDateInput"] input {{
        box-sizing: border-box !important;
        height: 46px !important;
        min-height: 46px !important;
        width: 100% !important;
    }}

    [data-testid="stRadio"] {{
        width: 100% !important;
        margin-inline: auto !important;
    }}

    [data-testid="stRadio"] > div {{
        display: flex !important;
        justify-content: center !important;
        align-items: stretch !important;
        gap: 14px !important;
        width: 100% !important;
    }}

    [data-testid="stRadio"] > div > label {{
        box-sizing: border-box !important;
        flex: 0 1 240px !important;
        width: 240px !important;
        min-width: 0 !important;
        min-height: 54px !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 12px 18px !important;
        border-radius: 11px !important;
        background: var(--panel) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }}

    [data-testid="stRadio"] > div > label:has(input:checked) {{
        background: var(--soft) !important;
        border-color: var(--accent) !important;
    }}

    [data-testid="stRadio"] > div > label:hover {{
        background: var(--soft) !important;
        border-color: var(--accent) !important;
    }}

    .stButton > button,
    .stDownloadButton > button {{
        box-sizing: border-box !important;
        min-height: 44px !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
    }}

    .stButton > button[kind="primary"],
    .stButton > button[kind="primary"]:hover,
    .stButton > button[kind="primary"]:focus,
    .stButton > button[kind="primary"]:active,
    [data-testid="stBaseButton-primary"],
    [data-testid="stBaseButton-primary"]:hover,
    [data-testid="stBaseButton-primary"]:focus,
    [data-testid="stBaseButton-primary"]:active {{
        background: var(--button) !important;
        background-color: var(--button) !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border-color: var(--button) !important;
        box-shadow: none !important;
        filter: none !important;
    }}

    [data-testid="stStatusWidget"],
    [data-testid="stStatusWidget"] *,
    [data-testid="stSpinner"],
    [data-testid="stSpinner"] * {{
        background-color: var(--panel) !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
    }}

    [data-testid="stFileUploader"],
    [data-testid="stExpander"],
    [data-testid="stExpander"] details {{
        border-radius: 11px !important;
    }}

    @media (max-width: 560px) {{
        .block-container {{
            width: calc(100% - 1rem) !important;
            padding: 1rem .5rem 2rem !important;
        }}

        [data-testid="stRadio"] > div {{
            flex-direction: column !important;
            align-items: center !important;
        }}

        [data-testid="stRadio"] > div > label {{
            flex: 0 1 auto !important;
            width: min(100%, 320px) !important;
            min-width: 0 !important;
        }}
    }}

    
    /* Hide Streamlit's top chrome (Deploy, toolbar and menu) */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    #MainMenu,
    footer {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }}

    [data-testid="stAppViewContainer"] > .main {{
        padding-top: 0 !important;
    }}


    .sia-page-intro {{
        text-align: center;
        margin: 2.6rem auto 1.3rem;
    }}
    .sia-page-intro h1 {{
        font-size: clamp(25px, 3vw, 30px);
        margin: 0 0 12px;
        color: var(--text) !important;
        font-weight: 750;
    }}
    .sia-page-intro p {{
        margin: 0;
        color: var(--muted) !important;
        font-size: 14px;
        line-height: 1.6;
    }}

    /* Consistent centered source selector */
    [data-testid="stRadio"] {{
        width: 100% !important;
        max-width: 520px !important;
        margin: 0 auto 12px !important;
        padding: 16px !important;
        box-sizing: border-box !important;
        background: var(--group) !important;
        border: 1px solid var(--border) !important;
        border-radius: 13px !important;
        text-align: center !important;
    }}
    [data-testid="stRadio"] > label {{
        display: block !important;
        width: 100% !important;
        text-align: center !important;
        margin: 0 0 12px !important;
        font-weight: 700 !important;
    }}
    [data-testid="stRadio"] > div {{
        display: flex !important;
        justify-content: center !important;
        gap: 10px !important;
        width: 100% !important;
        margin: 0 auto !important;
    }}
    [data-testid="stRadio"] > div > label {{
        box-sizing: border-box !important;
        flex: 1 1 0 !important;
        min-width: 0 !important;
        min-height: 48px !important;
        margin: 0 !important;
        padding: 10px 12px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: var(--input) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
    }}
    [data-testid="stRadio"] > div > label:has(input:checked) {{
        background: var(--soft) !important;
        border-color: var(--accent) !important;
    }}
    [data-testid="stRadio"] > div > label:hover {{
        background: var(--soft) !important;
        border-color: var(--accent) !important;
    }}

    /* Same height and spacing for all form controls */
    [data-testid="stTextInput"] input,
    [data-testid="stDateInput"] input {{
        width: 100% !important;
        height: 46px !important;
        min-height: 46px !important;
        box-sizing: border-box !important;
    }}
    [data-testid="stFileUploader"] {{
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    .stButton > button[kind="primary"],
    .stButton > button[kind="primary"]:hover,
    .stButton > button[kind="primary"]:focus,
    .stButton > button[kind="primary"]:active,
    [data-testid="stBaseButton-primary"],
    [data-testid="stBaseButton-primary"]:hover,
    [data-testid="stBaseButton-primary"]:focus,
    [data-testid="stBaseButton-primary"]:active {{
        background: var(--button) !important;
        background-color: var(--button) !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid var(--button) !important;
        box-shadow: none !important;
        filter: none !important;
    }}

    /* Clearly visible centered research setup card */
    [data-testid="stVerticalBlockBorderWrapper"]:has(.sia-page-intro) {{
        box-sizing: border-box !important;
        background: var(--panel) !important;
        border: 1.5px solid #405367 !important;
        outline: 1px solid rgba(117, 221, 187, 0.10) !important;
        outline-offset: -4px !important;
        border-radius: 18px !important;
        padding: 24px 22px !important;
        box-shadow:
            0 0 0 1px rgba(64, 83, 103, 0.22),
            0 12px 32px rgba(0, 0, 0, 0.18) !important;
    }}

    [data-testid="stVerticalBlockBorderWrapper"]:has(.sia-page-intro) > div {{
        gap: 1rem !important;
    }}

    /* Keep other bordered elements independent from the main setup card */
    [data-testid="stVerticalBlockBorderWrapper"]:not(:has(.sia-page-intro)) {{
        border-color: var(--border) !important;
        border-radius: 12px !important;
    }}

    /* The report stays on the wide page canvas, not inside the setup card */
    .sia-report-wide {{
        width: 100%;
    }}

        /* Compact header with balanced, consistent spacing */
    div[data-testid="stHorizontalBlock"]:has(.sia-brand) {{
        box-sizing: border-box !important;
        min-height: 64px !important;
        padding: 1px 10px 14px !important;
        margin: 0 auto 1.25rem !important;
        gap: 10px !important;
        align-items: center !important;
        background: var(--header) !important;
        border: 1px solid var(--header-border) !important;
        border-radius: 13px !important;
    }}
    .sia-brand {{
        box-sizing: border-box !important;
        min-height: 100px !important;
        gap: 11px !important;
        padding: 0px !important;
        align-items: center !important;
    }}
    .sia-mark {{
        box-sizing: border-box !important;
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        border-radius: 11px !important;
    }}
    .sia-name {{
        margin: 0 !important;
        line-height: 1.2 !important;
        font-size: 21px !important;
    }}
    .sia-brand .sia-subtitle {{
        margin-top: 3px !important;
        line-height: 1.25 !important;
    }}
    /* Theme/help buttons share the same compact height */
    div[data-testid="stHorizontalBlock"]:has(.sia-brand) .stButton > button {{
        box-sizing: border-box !important;
        height: 42px !important;
        min-height: 42px !important;
        padding: 0 12px !important;
        margin: 0 !important;
        border-radius: 9px !important;
    }}

    /* Clearly defined setup card with consistent inner spacing */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        box-sizing: border-box !important;
        width: 100% !important;
        background: var(--panel) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 22px 24px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, .12) !important;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] > div {{
        gap: 14px !important;
    }}

    /* Wider source selector and equally sized options */
    [data-testid="stRadio"] {{
        max-width: 100% !important;
        width: 100vh !important;
        box-sizing: border-box !important;
        padding: 16px 18px !important;
        margin: 0 auto 8px !important;
        background: var(--group) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }}
    [data-testid="stRadio"] > div {{
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: stretch !important;
        gap: 12px !important;
    }}
    [data-testid="stRadio"] > div > label {{
        box-sizing: border-box !important;
        flex: 1 1 0 !important;
        width: 50% !important;
        min-height: 48px !important;
        padding: 10px 14px !important;
        margin: 0 !important;
        border-radius: 10px !important;
    }}


    /* Keep generated output aligned to the wide page canvas */
    [data-testid="stMainBlockContainer"] > div:has(> [data-testid="stMarkdownContainer"] .sia-report-meta) {{
        width: 100% !important;
        max-width: 100% !important;
    }}
    /* Header brand area */
    div[data-testid="stHorizontalBlock"]:has(.sia-brand) {{
        background: var(--header) !important;
        border-radius: 13px !important;
    }}
    .sia-mark {{
        background: var(--soft) !important;
        color: var(--accent) !important;
        border-color: var(--accent) !important;
    }}
    .sia-name {{
        color: #FFFFFF !important;
    }}
    .sia-brand .sia-subtitle {{
        color: #D0E0EA !important;
    }}

    @media (max-width: 560px) {{
        .block-container {{
            width: calc(100% - 1rem) !important;
            padding: 1rem .5rem 2rem;
        }}
        [data-testid="stRadio"] > div {{
            flex-direction: column !important;
        }}
        [data-testid="stRadio"] > div > label {{
            width: 100% !important;
        }}
        .sia-page-intro {{
            margin-top: 1.8rem;
        }}
    }}

</style>

    """,

    unsafe_allow_html=True,

)

# =========================================================

# HELPERS

# =========================================================

def extract_document(uploaded_file) -> str:

    """Extract text from Markdown, TXT, or text-based PDF."""

    filename = uploaded_file.name

    suffix = Path(filename).suffix.lower()

    raw_bytes = uploaded_file.getvalue()

    if suffix in {".md", ".txt"}:

        text = raw_bytes.decode("utf-8-sig", errors="replace")

    elif suffix == ".pdf":

        reader = PdfReader(BytesIO(raw_bytes))

        if reader.is_encrypted:

            try:

                if not reader.decrypt(""):

                    raise ValueError("The PDF requires a password.")

            except Exception as exc:

                raise ValueError(

                    f"Cannot read encrypted PDF: {filename}"

                ) from exc

        text = "\n\n".join(

            page.extract_text() or ""

            for page in reader.pages

        )

    else:

        raise ValueError(f"Unsupported file type: {filename}")

    text = text.strip()

    if not text:

        raise ValueError(

            f"No readable text found in {filename}. "

            "Scanned PDFs need OCR before uploading."

        )

    return text

def load_api_key() -> str:

    """Read the API key from .env or Streamlit secrets."""

    key = os.getenv("GOOGLE_API_KEY", "").strip()

    if not key:

        try:

            key = str(st.secrets.get("GOOGLE_API_KEY", "")).strip()

        except Exception:

            key = ""

    if key:

        os.environ["GOOGLE_API_KEY"] = key

    return key

def load_assignment_pack() -> Path:

    """Check that the bundled assignment pack exists."""

    pack_path = Path(DEFAULT_PACK)

    if not pack_path.is_absolute():

        pack_path = ROOT / pack_path

    if not pack_path.is_dir():

        raise FileNotFoundError(

            f"Research pack directory not found: {pack_path}"

        )

    if not any(pack_path.glob("*.md")):

        raise FileNotFoundError(

            f"No Markdown documents found in {pack_path}"

        )

    return pack_path

def highlight_source_filenames(markdown: str) -> str:

    """Highlight source filenames without altering fenced code."""

    pattern = re.compile(

        r"(?<![\`/\w])([\w .()\\-]+\\.(?:md|txt|pdf))(?![\`/\w])",

        re.IGNORECASE,

    )

    output = []

    in_fence = False

    for line in markdown.splitlines():

        stripped = line.strip()

        if stripped.startswith(("```", "~~~")):

            in_fence = not in_fence

            output.append(line)

        elif in_fence:

            output.append(line)

        else:

            output.append(pattern.sub(r"`\1`", line))

    return "\n".join(output)

# =========================================================

# HELP

# =========================================================

@st.dialog("S.I.A. Help", width="medium")

def show_help():

    st.markdown(

        """

        ### Getting started

        1. Choose \\Assignment Demo\\ or \\My Documents\\.

        2. Enter the company ticker and cutoff date.

        3. Upload documents if you selected My Documents.

        4. Select \\Generate research brief\\.

        5. Review the report, citations and validation details.

        6. Download the report as Markdown.

        ### Document requirements

        - Supported formats: \`.md\`, \`.txt\`, \`.pdf\`

        - Maximum 20 files and 20 MB combined

        - Scanned PDFs require OCR

        - Upload documents for one company at a time

        ### Evidence policy

        S.I.A. uses the supplied documents only. It does not fetch live prices,

        news or web research. Check the cited evidence and any flagged conflicts.

        \\Educational research only — not investment advice.\\

        """

    )

# =========================================================

# HEADER

# =========================================================

left, _theme_spacer, help_col = st.columns(

    [7, 1.5, 1],

    vertical_alignment="center",

)

with left:

    st.markdown(
        textwrap.dedent("""
        <div class="sia-brand">
            <div class="sia-mark">◈</div>
            <div>
                <div class="sia-name">Super Investigation Agent</div>
                <div class="sia-subtitle">S.I.A. · Evidence-led equity research</div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

with help_col:

    if st.button(

        "?",

        key="sia_help",

        type="secondary",

        use_container_width=True,

    ):

        show_help()

st.markdown("")

# =========================================================
# CENTERED CONFIGURATION CARD
# =========================================================

form_left, form_center, form_right = st.columns([1, 2.8, 1], gap="small")
with form_center:
    with st.container(border=True):
        # =========================================================

        # RESEARCH SETTINGS

        # =========================================================

        st.markdown(
            textwrap.dedent("""
                <div class="sia-page-intro">
                    <h1>Generate Research Brief</h1>
                    <p>Configure your research source, company ticker and cutoff date.</p>
                </div>
            """),
            unsafe_allow_html=True,
        )

        mode = st.radio(

            "Research source",

            [DEMO_MODE, UPLOAD_MODE],

            horizontal=True,

            key="sia_mode",

        )

        previous_mode = st.session_state.sia_previous_mode

        if mode != previous_mode:

            current = str(st.session_state.sia_ticker).strip().upper()

            if previous_mode == DEMO_MODE and mode == UPLOAD_MODE:

                if current == "SRVCABLE":

                    st.session_state.sia_ticker = ""

            elif mode == DEMO_MODE and not current:

                st.session_state.sia_ticker = "SRVCABLE"

            st.session_state.sia_previous_mode = mode

        is_demo = mode == DEMO_MODE

        ticker_col, date_col = st.columns(2, gap="large")

        with ticker_col:

            st.markdown('<div class="sia-label">Company ticker</div>',

                        unsafe_allow_html=True)

            ticker = st.text_input(

                "Company ticker",

                key="sia_ticker",

                label_visibility="collapsed",

                placeholder="e.g. SRVCABLE",

            ).strip().upper()

        with date_col:

            st.markdown('<div class="sia-label">Research cutoff date</div>',

                        unsafe_allow_html=True)

            as_of = st.date_input(

                "Research cutoff date",

                value=date(2026, 9, 23),

                key="sia_as_of",

                label_visibility="collapsed",

            )

        # =========================================================

        # DOCUMENT INPUT

        # =========================================================

        uploaded_documents: list[dict[str, str]] = []

        files = []

        upload_valid = True

        if is_demo:
            st.caption("Using bundled SRVCABLE documents · No live web research")
        else:

            st.markdown('<div class="sia-label">Company documents</div>',

                        unsafe_allow_html=True)

            files = st.file_uploader(

                "Upload Markdown, TXT or text-based PDF files",

                type=["md", "txt", "pdf"],

                accept_multiple_files=True,

                key="sia_uploads",

            ) or []

            st.caption("Markdown · TXT · PDF  |  Maximum 20 files · 20 MB combined")

            total_bytes = sum(len(f.getvalue()) for f in files)

            if len(files) > MAX_FILES:

                st.error(f"Upload a maximum of {MAX_FILES} files.")

                upload_valid = False

            elif total_bytes > MAX_TOTAL_BYTES:

                st.error("The combined upload limit is 20 MB.")

                upload_valid = False

            else:

                seen_names = set()

                for uploaded_file in files:

                    name_key = uploaded_file.name.casefold()

                    if name_key in seen_names:

                        st.error(

                            f"Duplicate filename: {uploaded_file.name}. "

                            "Rename duplicate files before continuing."

                        )

                        upload_valid = False

                        continue

                    seen_names.add(name_key)

                    try:

                        uploaded_documents.append({

                            "filename": uploaded_file.name,

                            "content": extract_document(uploaded_file),

                        })

                    except Exception as exc:

                        st.error(f"Could not read {uploaded_file.name}: {exc}")

                        upload_valid = False

                if files and upload_valid and uploaded_documents:

                    st.caption(f"✓ {len(uploaded_documents)} document(s) ready")

        # =========================================================

        # GENERATION

        # =========================================================

        api_key = load_api_key()

        if not api_key:

            st.warning(

                "The app owner must configure GOOGLE_API_KEY in .env "

                "or deployment secrets. Visitors do not need their own key."

            )

        documents_ready = is_demo or (

            bool(files)

            and bool(uploaded_documents)

            and upload_valid

            and len(uploaded_documents) == len(files)

        )

        can_generate = bool(ticker) and bool(api_key) and documents_ready

        if is_demo and ticker != "SRVCABLE":

            st.error("The Assignment Demo supports SRVCABLE only.")

            can_generate = False

        if not is_demo and not upload_valid:

            can_generate = False

        st.markdown("")

        if st.button(

            "Generate research brief",

            type="primary",

            use_container_width=True,

            disabled=not can_generate,

            key="sia_generate",

        ):

            try:

                graph_input = {

                    "ticker": ticker,

                    "as_of": as_of.isoformat(),

                    "output_path": None,

                }

                if is_demo:

                    graph_input["pack_dir"] = str(load_assignment_pack())

                else:

                    graph_input["documents"] = uploaded_documents

                with st.status(

                    "Investigating documents…",

                    expanded=True,

                ) as status:

                    st.write("Running the evidence and citation workflow…")

                    result = build_graph().invoke(graph_input)

                    status.update(

                        label="Investigation completed",

                        state="complete",

                        expanded=False,

                    )

                brief = result.get("brief", "")

                if not isinstance(brief, str) or not brief.strip():

                    raise ValueError("The workflow returned an empty research brief.")

                st.session_state["sia_last_brief"] = brief.strip()

                st.session_state["sia_last_ticker"] = ticker

                st.session_state["sia_last_date"] = as_of.isoformat()

                st.session_state["sia_last_validation"] = result.get(

                    "validation", "No validation details returned."

                )

                st.session_state["sia_last_attempts"] = result.get("attempts")

            except Exception as exc:

                st.error(

                    "The research workflow failed. Check the API key, model "

                    "configuration, source documents and application logs."

                )

                with st.expander("Technical error details"):

                    st.exception(exc)

# =========================================================

# REPORT

# =========================================================

brief = st.session_state.get("sia_last_brief", "")

if brief:

    st.divider()

    report_col, download_col = st.columns(

        [5, 1.8],

        vertical_alignment="center",

    )

    with report_col:

        st.subheader("Research report")

        st.caption(

            f'{st.session_state.get("sia_last_ticker", "")} '

            f'· Cutoff {st.session_state.get("sia_last_date", "")}'

        )

    with download_col:

        st.download_button(

            "↓ Download Markdown",

            data=brief,

            file_name=(

                f'{st.session_state.get("sia_last_ticker", "company").lower()}'

                "_research_brief.md"

            ),

            mime="text/markdown",

            use_container_width=True,

            key="sia_download_report",

        )

    st.markdown(highlight_source_filenames(brief))

    with st.expander("Validation details"):

        validation = st.session_state.get(

            "sia_last_validation",

            "No validation details returned.",

        )

        if isinstance(validation, (dict, list)):

            st.json(validation)

        else:

            st.write(validation)

        attempts = st.session_state.get("sia_last_attempts")

        if attempts is not None:

            st.caption(f"Revision attempts reported: {attempts}")

# =========================================================

# FOOTER

# =========================================================

st.divider()

st.markdown(
    textwrap.dedent("""
    <div class="sia-footer">
        S.I.A. · Source-grounded analysis · Educational use only · Not investment advice
    </div>
    """),
    unsafe_allow_html=True,
)