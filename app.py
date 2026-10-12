import hashlib
import io
import re
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pymupdf
import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError
from wordcloud import WordCloud
import docx


# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ashutosh Studio | Engineering Toolkit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# STYLING
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
        --as-bg: #0b1020;
        --as-panel: #111a2d;
        --as-panel-2: #18233a;
        --as-border: #34435e;
        --as-text: #f3f6fc;
        --as-muted: #bac5d6;
        --as-blue: #60a5fa;
        --as-red: #fb7185;
        --as-green: #34d399;
    }

    .stApp,
    [data-testid="stAppViewContainer"] {
        background: var(--as-bg);
        color: var(--as-text);
        font-family: Inter, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    /* HEADER AND TOP SPACING FIX */
    [data-testid="stHeader"],
    header[data-testid="stHeader"] {
        background: #0b1020 !important;
    }

    .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 3.5rem !important;
        padding-bottom: 2.5rem !important;
        overflow: visible !important;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: #10182a !important;
        border-right: 1px solid #293750;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #e6edf8;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        line-height: 1.5;
    }

    /* GENERAL TYPOGRAPHY */
    h1, h2, h3, h4, p, li, label,
    [data-testid="stCaptionContainer"] {
        color: var(--as-text);
    }

    .hero-title {
        font-size: clamp(1.8rem, 3vw, 2.45rem);
        font-weight: 850;
        letter-spacing: -0.035em;
        line-height: 1.25;
        background: linear-gradient(
            110deg,
            #60a5fa 0%,
            #a78bfa 58%,
            #f0abfc 100%
        );
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.4rem 0;
        padding-top: 0.15rem;
        overflow: visible;
    }

    .hero-subtitle {
        color: #c1cbda !important;
        font-size: 1rem;
        line-height: 1.65;
        margin-bottom: 1.5rem;
    }

    .section-kicker {
        color: #79b5ff !important;
        font-size: .9rem;
        font-weight: 750;
        letter-spacing: .02em;
    }

    /* CARDS */
    .workflow-card {
        background: var(--as-panel);
        border: 1px solid var(--as-border);
        border-radius: 14px;
        padding: 1.2rem 1.25rem;
        margin: .35rem 0 1rem 0;
        min-height: 150px;
    }

    .workflow-card p {
        color: #d0d9e7 !important;
        line-height: 1.6;
    }

    .muted {
        color: var(--as-muted) !important;
    }

    .empty-state {
        background: #121c30;
        border: 1px dashed #50617d;
        border-radius: 12px;
        padding: 1.15rem 1.25rem;
        color: #d2dceb;
        margin: .75rem 0 1rem 0;
    }

    .empty-state strong {
        color: #f7faff;
    }

    .status-pill {
        display: inline-block;
        border: 1px solid #1e7759;
        color: #6ee7b7 !important;
        background: #0c2c27;
        border-radius: 100px;
        padding: .24rem .65rem;
        font-size: .75rem;
        font-weight: 700;
    }

    .file-summary {
        background: #131e32;
        border: 1px solid #3a4b68;
        border-radius: 10px;
        padding: .75rem 1rem;
        margin: .5rem 0 1rem 0;
        color: #e6edf8;
        overflow-wrap: anywhere;
    }

    .file-summary span {
        color: #bfcbdd;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: .35rem;
        border-bottom: 1px solid #34435e;
        padding-bottom: .25rem;
        flex-wrap: wrap;
    }

    .stTabs [data-baseweb="tab"] {
        min-height: 2.65rem;
        background: #141f33 !important;
        border: 1px solid #34435e !important;
        border-radius: 9px 9px 0 0;
        padding: .55rem .85rem;
        transition: background .15s ease, border-color .15s ease;
    }

    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] div {
        color: #dce5f2 !important;
        font-weight: 650 !important;
        font-size: .88rem !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #22314b !important;
        border-color: #76aef5 !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #243550 !important;
        border-color: #6ba7f5 !important;
        border-bottom: 3px solid #fb7185 !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] p,
    .stTabs [data-baseweb="tab"][aria-selected="true"] div {
        color: #ffffff !important;
    }

    .stTabs [data-baseweb="tab"]:focus-visible {
        outline: 2px solid #93c5fd;
        outline-offset: 2px;
    }

    /* UPLOADERS */
    [data-testid="stFileUploader"] section {
        background: #151e30 !important;
        border: 1px dashed #546783 !important;
        border-radius: 12px;
    }

    [data-testid="stFileUploader"] section > div,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span {
        color: #e3eaf5 !important;
    }

    [data-testid="stFileUploader"] button {
        background: #25334b !important;
        color: #ffffff !important;
        border: 1px solid #526582 !important;
    }

    [data-testid="stFileUploader"] button:hover {
        border-color: #93c5fd !important;
    }

    /* INPUTS */
    input,
    textarea,
    [data-baseweb="select"] > div {
        color: #f5f7fb !important;
    }

    [data-baseweb="select"] > div {
        background: #18233a !important;
        border-color: #50617d !important;
    }

    [data-testid="stNumberInput"] button {
        color: #ffffff !important;
    }

    /* GENERAL BUTTONS */
    .stButton > button,
    .stDownloadButton > button {
        border-radius: 9px;
        min-height: 2.55rem;
        font-weight: 700;
        transition:
            transform .12s ease,
            border-color .12s ease,
            background .12s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: #93c5fd !important;
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"],
    [data-testid="stBaseButton-primary"] {
        background: #2563eb !important;
        border: 1px solid #60a5fa !important;
        color: #ffffff !important;
    }

    /* SIDEBAR NAVIGATION CONTRAST FIX */
    section[data-testid="stSidebar"] .stButton > button,
    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
        background: #172033 !important;
        color: #f9fafb !important;
        border: 1px solid #334155 !important;
    }

    section[data-testid="stSidebar"] .stButton > button p,
    section[data-testid="stSidebar"] .stButton > button span,
    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] p,
    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] span {
        color: #f9fafb !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover,
    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
        background: #25334b !important;
        border-color: #60a5fa !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="primary"],
    section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
        background: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #60a5fa !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] span,
    section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] p,
    section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] span {
        color: #ffffff !important;
    }

    /* METRICS AND ALERTS */
    [data-testid="stMetric"] {
        background: #121c30;
        border: 1px solid #34435e;
        border-radius: 12px;
        padding: .8rem 1rem;
    }

    [data-testid="stMetricLabel"] {
        color: #c0ccdc !important;
    }

    [data-testid="stMetricValue"] {
        color: #f7faff !important;
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    hr {
        border-color: #34435e !important;
    }

    /* MOBILE */
    @media (max-width: 700px) {
        .block-container,
        [data-testid="stMainBlockContainer"] {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 2.5rem !important;
        }

        .workflow-card {
            min-height: auto;
        }

        .stTabs [data-baseweb="tab"] {
            padding: .4rem .55rem;
        }

        .stTabs [data-baseweb="tab"] p {
            font-size: .78rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def format_size(n_bytes: int) -> str:
    size = float(n_bytes)

    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024

    return f"{size:.1f} GB"


def signature(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def multi_signature(items: list[tuple[str, bytes]]) -> str:
    payload = b"".join(
        name.encode("utf-8", errors="ignore") + b"\0" + data
        for name, data in items
    )
    return signature(payload)


def show_file_summary(
    name: str,
    data: bytes,
    details: Optional[str] = None,
) -> None:
    extra = f" <span>• {details}</span>" if details else ""

    st.markdown(
        f"<div class='file-summary'><strong>📎 {name}</strong><br>"
        f"<span>{format_size(len(data))}</span>{extra}</div>",
        unsafe_allow_html=True,
    )


def empty_state(title: str, instructions: str) -> None:
    st.markdown(
        f"<div class='empty-state'><strong>📂 {title}</strong><br>"
        f"{instructions}</div>",
        unsafe_allow_html=True,
    )


def output_key(key: str) -> str:
    return f"output_{key}"


def save_output(
    key: str,
    source_signature: str,
    data: Any,
    filename: str,
    mime: str,
    **meta: Any,
) -> None:
    st.session_state[output_key(key)] = {
        "source_signature": source_signature,
        "data": data,
        "filename": filename,
        "mime": mime,
        "meta": meta,
    }


def display_output(
    key: str,
    source_signature: str,
    preview: Optional[str] = None,
) -> None:
    result = st.session_state.get(output_key(key))

    if not result or result.get("source_signature") != source_signature:
        return

    if preview == "text":
        st.text_area(
            "Output preview",
            result["data"],
            height=240,
            key=f"preview_{key}",
        )

    elif preview == "image":
        try:
            st.image(
                result["data"],
                caption="Processed output",
                use_container_width=True,
            )
        except Exception:
            pass

    elif preview == "wordcloud":
        st.image(
            result["data"],
            caption="Word frequency cloud",
            use_container_width=True,
        )

    if result.get("meta", {}).get("message"):
        st.success(result["meta"]["message"])

    st.download_button(
        "⬇️ Download result",
        data=result["data"],
        file_name=result["filename"],
        mime=result["mime"],
        key=f"download_{key}",
        use_container_width=True,
    )


def read_pdf(data: bytes):
    return pymupdf.open(stream=data, filetype="pdf")


def docx_to_pdf_bytes(docx_data: bytes) -> bytes:
    """Convert DOCX paragraph and table text into a paginated PDF.

    This lightweight converter does not preserve full Word formatting,
    images, headers, footers, or complex table layout.
    """
    word_doc = docx.Document(io.BytesIO(docx_data))
    blocks: list[str] = []

    for paragraph in word_doc.paragraphs:
        if paragraph.text.strip():
            blocks.append(paragraph.text.strip())

    # Include basic table contents.
    for table in word_doc.tables:
        for row in table.rows:
            row_text = "  |  ".join(
                cell.text.strip().replace("\n", " ")
                for cell in row.cells
            )
            if row_text.strip(" |"):
                blocks.append(row_text)

    if not blocks:
        blocks = ["The document contains no extractable paragraph or table text."]

    pdf = pymupdf.open()

    page_width, page_height = 595, 842
    margin_x, margin_top, margin_bottom = 52, 54, 48
    font = pymupdf.Font("helv")
    font_size, line_height = 10.5, 15
    max_width = page_width - 2 * margin_x

    page = pdf.new_page(width=page_width, height=page_height)
    y = margin_top

    def new_page():
        nonlocal page, y
        page = pdf.new_page(width=page_width, height=page_height)
        y = margin_top
        page.insert_text(
            (margin_x, 32),
            "Converted from DOCX · Ashutosh Studio",
            fontsize=8,
            color=(0.35, 0.4, 0.48),
        )

    def wrap_paragraph(text: str) -> list[str]:
        words = text.split()

        if not words:
            return [""]

        lines = []
        current = ""

        for word in words:
            candidate = word if not current else f"{current} {word}"

            if font.text_length(candidate, fontsize=font_size) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)

                # Break exceptionally long words safely.
                fragment = ""

                for char in word:
                    if font.text_length(
                        fragment + char,
                        fontsize=font_size,
                    ) <= max_width:
                        fragment += char
                    else:
                        if fragment:
                            lines.append(fragment)
                        fragment = char

                current = fragment

        if current:
            lines.append(current)

        return lines

    page.insert_text(
        (margin_x, 32),
        "Converted from DOCX · Ashutosh Studio",
        fontsize=8,
        color=(0.35, 0.4, 0.48),
    )

    for block in blocks:
        for line in wrap_paragraph(block):
            if y + line_height > page_height - margin_bottom:
                new_page()

            page.insert_text(
                (margin_x, y),
                line,
                fontsize=font_size,
                fontname="helv",
                color=(0.08, 0.1, 0.15),
            )
            y += line_height

        y += 7

    out = io.BytesIO()
    pdf.save(out, garbage=4, deflate=True)
    pdf.close()

    return out.getvalue()


def compress_pdf_bytes(data: bytes) -> bytes:
    source = read_pdf(data)
    out = io.BytesIO()

    source.save(
        out,
        garbage=4,
        deflate=True,
        deflate_images=True,
        deflate_fonts=True,
    )

    source.close()
    return out.getvalue()


def pdf_to_markdown(data: bytes) -> str:
    with read_pdf(data) as pdf:
        sections = []

        for index, page in enumerate(pdf, start=1):
            page_text = page.get_text("text").strip()
            sections.append(
                f"## Page {index}\n\n"
                f"{page_text or '_No extractable text on this page._'}"
            )

    return "\n\n---\n\n".join(sections)


def pdf_to_docx_bytes(data: bytes) -> bytes:
    with read_pdf(data) as pdf:
        word_doc = docx.Document()

        for index, page in enumerate(pdf, start=1):
            if index > 1:
                word_doc.add_page_break()

            word_doc.add_heading(f"Page {index}", level=2)
            text = page.get_text("text").strip()
            word_doc.add_paragraph(
                text or "[No extractable text on this page]"
            )

    out = io.BytesIO()
    word_doc.save(out)
    return out.getvalue()


def get_pil_image(data: bytes) -> Image.Image:
    image = Image.open(io.BytesIO(data))
    image.load()
    return ImageOps.exif_transpose(image)


def set_page_header(
    title: str,
    subtitle: str,
    icon: str = "",
) -> None:
    st.markdown(
        f'<p class="hero-title">{icon} {title}</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="hero-subtitle">{subtitle}</p>',
        unsafe_allow_html=True,
    )


def tool_intro(title: str, description: str) -> None:
    st.markdown(f"### {title}")
    st.markdown(
        f"<p class='muted'>{description}</p>",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
PAGES = {
    "🏠 Platform Overview": "nav_overview",
    "📄 Document Intelligence": "nav_documents",
    "🖼️ Media Studio": "nav_media",
}

if "active_page" not in st.session_state:
    st.session_state.active_page = "🏠 Platform Overview"

st.sidebar.markdown("# ⚡ ASHUTOSH STUDIO")

st.sidebar.markdown(
    "<p style='color:#bac8dc !important;font-size:.86rem;line-height:1.6;'>"
    "Engineering & Computational Toolkit<br>"
    "<strong>Ashutosh Borah</strong></p>",
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Workspace Directory")

for page_label, button_key in PAGES.items():
    is_active = st.session_state.active_page == page_label

    if st.sidebar.button(
        page_label,
        key=button_key,
        use_container_width=True,
        type="primary" if is_active else "secondary",
    ):
        st.session_state.active_page = page_label
        st.rerun()

st.sidebar.markdown("---")

st.sidebar.markdown(
    "<span class='status-pill'>● SYSTEM ONLINE</span>",
    unsafe_allow_html=True,
)

st.sidebar.caption("Local file processing · No account required")

selected_page = st.session_state.active_page


# -----------------------------------------------------------------------------
# 0. PLATFORM OVERVIEW
# -----------------------------------------------------------------------------
if selected_page == "🏠 Platform Overview":
    set_page_header(
        "Welcome to Ashutosh Studio",
        "A practical workspace for document conversion, PDF operations, "
        "and image optimization.",
        "⚡",
    )

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Workspace modules", "2")
    metric2.metric("Available operations", "11")
    metric3.metric("Interface", "Responsive")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
            <div class="workflow-card">
                <h3 style="color:#8bbdff;margin-top:0">
                    📄 Document Intelligence
                </h3>
                <p>
                    Convert PDF text to Markdown or Word, convert DOCX text
                    to PDF, merge and compress PDFs, compile images into PDFs,
                    create word clouds, and extract embedded images.
                </p>
                <p><strong>Best for:</strong> document cleanup, conversion
                and batch utility tasks.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open Document Intelligence →",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.active_page = "📄 Document Intelligence"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div class="workflow-card">
                <h3 style="color:#6ee7b7;margin-top:0">
                    🖼️ Media Studio
                </h3>
                <p>
                    Resize image dimensions, convert images to grayscale,
                    and compress images to JPEG with a user-controlled
                    quality setting.
                </p>
                <p><strong>Best for:</strong> reducing image payload size
                and preparing assets.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open Media Studio →",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.active_page = "🖼️ Media Studio"
            st.rerun()

    st.markdown("### How to use the studio")

    step1, step2, step3 = st.columns(3)

    step1.markdown(
        "**1 · Upload**\n\n"
        "Choose a supported file. Its name and size will be shown "
        "before processing."
    )

    step2.markdown(
        "**2 · Process**\n\n"
        "Choose the operation and adjust available settings."
    )

    step3.markdown(
        "**3 · Review & download**\n\n"
        "Inspect the output preview or status, then download "
        "the generated file."
    )

    st.info(
        "Files are processed by the app while you use it. Avoid uploading "
        "confidential documents to a public deployment unless you are "
        "comfortable with its hosting and data-handling setup."
    )


# -----------------------------------------------------------------------------
# 1. DOCUMENT INTELLIGENCE
# -----------------------------------------------------------------------------
elif selected_page == "📄 Document Intelligence":
    set_page_header(
        "Document Intelligence Hub",
        "Convert, combine, compress, and inspect common document formats.",
        "📄",
    )

    tabs = st.tabs([
        "PDF → Markdown",
        "PDF → Word",
        "Word → PDF",
        "Merge PDFs",
        "Images → PDF",
        "Compress PDF",
        "Word Cloud",
        "Extract Assets",
    ])

    # -------------------------------------------------------------------------
    # PDF TO MARKDOWN
    # -------------------------------------------------------------------------
    with tabs[0]:
        tool_intro(
            "Convert PDF to Markdown",
            "Extract text one page at a time and download a clean .md file. "
            "Scanned pages require OCR, which is not included in this version.",
        )

        uploaded = st.file_uploader(
            "Upload a PDF",
            type=["pdf"],
            key="md_up",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = signature(data)

            show_file_summary(uploaded.name, data, "PDF document")

            if st.button(
                "Convert to Markdown",
                type="primary",
                key="run_md",
            ):
                try:
                    md = pdf_to_markdown(data)
                    filename = (
                        re.sub(r"\.pdf$", "", uploaded.name, flags=re.I)
                        + ".md"
                    )

                    save_output(
                        "md",
                        sig,
                        md,
                        filename,
                        "text/markdown",
                    )

                except Exception as exc:
                    st.error(
                        "Could not read this PDF. It may be damaged or "
                        f"password-protected. Details: {exc}"
                    )

            display_output("md", sig, preview="text")

        else:
            empty_state(
                "Ready for a PDF",
                "Upload a text-based PDF to extract its page text. "
                "The converted Markdown will appear here with a download link.",
            )

    # -------------------------------------------------------------------------
    # PDF TO WORD
    # -------------------------------------------------------------------------
    with tabs[1]:
        tool_intro(
            "Convert PDF to Word (.docx)",
            "Extract page text into an editable Word document. This focuses "
            "on text; the original PDF layout, columns, and embedded graphics "
            "may not be reproduced exactly.",
        )

        uploaded = st.file_uploader(
            "Upload a PDF",
            type=["pdf"],
            key="word_up",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = signature(data)

            show_file_summary(uploaded.name, data, "PDF document")

            if st.button(
                "Convert to Word",
                type="primary",
                key="run_pdf_docx",
            ):
                try:
                    converted = pdf_to_docx_bytes(data)
                    filename = (
                        re.sub(r"\.pdf$", "", uploaded.name, flags=re.I)
                        + ".docx"
                    )

                    save_output(
                        "pdf_docx",
                        sig,
                        converted,
                        filename,
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document",
                        message="Word document generated.",
                    )

                except Exception as exc:
                    st.error(f"Could not convert this PDF: {exc}")

            display_output("pdf_docx", sig)

        else:
            empty_state(
                "Ready to convert",
                "Upload a PDF. The output will be an editable DOCX with "
                "extracted text organized by page.",
            )

    # -------------------------------------------------------------------------
    # WORD TO PDF
    # -------------------------------------------------------------------------
    with tabs[2]:
        tool_intro(
            "Convert Word to PDF (.pdf)",
            "Generate a readable PDF from DOCX paragraph and table text. "
            "Complex Word styling, images, and headers/footers are not fully "
            "preserved by this lightweight converter.",
        )

        uploaded = st.file_uploader(
            "Upload a Word document",
            type=["docx"],
            key="docx_up",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = signature(data)

            show_file_summary(uploaded.name, data, "DOCX document")

            if st.button(
                "Convert to PDF",
                type="primary",
                key="run_docx_pdf",
            ):
                try:
                    converted = docx_to_pdf_bytes(data)
                    filename = (
                        re.sub(r"\.docx$", "", uploaded.name, flags=re.I)
                        + ".pdf"
                    )

                    save_output(
                        "docx_pdf",
                        sig,
                        converted,
                        filename,
                        "application/pdf",
                        message=(
                            "PDF generated. Check the output before relying "
                            "on its layout."
                        ),
                    )

                except Exception as exc:
                    st.error(
                        "Could not convert this DOCX. It may be invalid or "
                        f"corrupted. Details: {exc}"
                    )

            display_output("docx_pdf", sig)

        else:
            empty_state(
                "Ready to convert",
                "Upload a DOCX file. The generated PDF is paginated so long "
                "documents do not get clipped into a single page.",
            )

    # -------------------------------------------------------------------------
    # MERGE PDFS
    # -------------------------------------------------------------------------
    with tabs[3]:
        tool_intro(
            "Merge multiple PDFs",
            "Combine PDFs in the order shown below. The merge uses the "
            "upload order.",
        )

        uploads = st.file_uploader(
            "Upload two or more PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            key="merge_up",
        )

        if uploads:
            file_items = [
                (item.name, item.getvalue())
                for item in uploads
            ]
            sig = multi_signature(file_items)

            c1, c2 = st.columns(2)
            c1.metric("Files selected", len(file_items))
            c2.metric(
                "Combined input size",
                format_size(sum(len(data) for _, data in file_items)),
            )

            for index, (name, data) in enumerate(file_items, start=1):
                st.caption(f"{index}. {name} · {format_size(len(data))}")

            if len(file_items) < 2:
                st.warning("Select at least two PDFs to merge.")

            elif st.button(
                "Merge PDFs",
                type="primary",
                key="run_merge",
            ):
                try:
                    merged = pymupdf.open()

                    for _, data in file_items:
                        with read_pdf(data) as source_pdf:
                            merged.insert_pdf(source_pdf)

                    out = io.BytesIO()
                    merged.save(out, garbage=4, deflate=True)
                    merged.close()

                    save_output(
                        "merge",
                        sig,
                        out.getvalue(),
                        "merged.pdf",
                        "application/pdf",
                        message="PDFs merged in the selected order.",
                    )

                except Exception as exc:
                    st.error(
                        "Could not merge these PDFs. Check that each file "
                        "is valid and not password-protected. "
                        f"Details: {exc}"
                    )

            display_output("merge", sig)

        else:
            empty_state(
                "Build a combined PDF",
                "Upload two or more PDFs. The merge follows the displayed "
                "file order and produces one downloadable PDF.",
            )

    # -------------------------------------------------------------------------
    # IMAGES TO PDF
    # -------------------------------------------------------------------------
    with tabs[4]:
        tool_intro(
            "Compile images to PDF",
            "Turn selected PNG, JPEG, and WebP images into a multi-page PDF. "
            "Each image becomes one page.",
        )

        uploads = st.file_uploader(
            "Upload images",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key="img_pdf_up",
        )

        if uploads:
            file_items = [
                (item.name, item.getvalue())
                for item in uploads
            ]
            sig = multi_signature(file_items)

            st.metric("Images selected", len(file_items))

            for index, (name, data) in enumerate(file_items, start=1):
                try:
                    with get_pil_image(data) as image_obj:
                        st.caption(
                            f"{index}. {name} · {image_obj.width} × "
                            f"{image_obj.height} px"
                        )
                except Exception:
                    st.caption(f"{index}. {name} · unreadable image")

            if st.button(
                "Compile images to PDF",
                type="primary",
                key="run_img_pdf",
            ):
                try:
                    pages = []

                    for _, data in file_items:
                        with get_pil_image(data) as image_obj:
                            pages.append(image_obj.convert("RGB"))

                    if not pages:
                        st.warning("No valid images were found.")
                    else:
                        out = io.BytesIO()

                        pages[0].save(
                            out,
                            format="PDF",
                            save_all=True,
                            append_images=pages[1:],
                        )

                        save_output(
                            "img_pdf",
                            sig,
                            out.getvalue(),
                            "images_compiled.pdf",
                            "application/pdf",
                            message=(
                                f"Compiled {len(pages)} image(s) into one PDF."
                            ),
                        )

                except (UnidentifiedImageError, OSError, ValueError) as exc:
                    st.error(
                        f"At least one uploaded image could not be "
                        f"processed: {exc}"
                    )

            display_output("img_pdf", sig)

        else:
            empty_state(
                "Compile image pages",
                "Upload multiple images. They will be placed into a single "
                "PDF in the selected order.",
            )

    # -------------------------------------------------------------------------
    # COMPRESS PDF
    # -------------------------------------------------------------------------
    with tabs[5]:
        tool_intro(
            "Compress PDF footprint",
            "Rewrites PDF structures and compresses compatible streams. "
            "Already-optimized PDFs may not become smaller.",
        )

        uploaded = st.file_uploader(
            "Upload a PDF to compress",
            type=["pdf"],
            key="comp_up",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = signature(data)

            show_file_summary(uploaded.name, data, "Original PDF")

            if st.button(
                "Compress PDF",
                type="primary",
                key="run_compress_pdf",
            ):
                try:
                    compressed = compress_pdf_bytes(data)

                    old_size = len(data)
                    new_size = len(compressed)
                    delta = (
                        (old_size - new_size) / old_size * 100
                        if old_size
                        else 0
                    )

                    if delta > 0:
                        message = (
                            f"Reduced size by {delta:.1f}% "
                            f"({format_size(old_size - new_size)} saved)."
                        )
                    elif delta < 0:
                        message = (
                            f"The output is {abs(delta):.1f}% larger; "
                            "this PDF was not compressible with these settings."
                        )
                    else:
                        message = "The file size did not change."

                    save_output(
                        "compress_pdf",
                        sig,
                        compressed,
                        "compressed.pdf",
                        "application/pdf",
                        message=message,
                    )

                except Exception as exc:
                    st.error(f"Could not compress this PDF: {exc}")

            display_output("compress_pdf", sig)

        else:
            empty_state(
                "Reduce PDF overhead",
                "Upload a PDF to optimize its internal streams and compare "
                "the original and output sizes.",
            )

    # -------------------------------------------------------------------------
    # WORD CLOUD
    # -------------------------------------------------------------------------
    with tabs[6]:
        tool_intro(
            "Generate a word cloud",
            "Visualize frequently occurring words in extractable PDF text. "
            "Scanned documents require OCR before this tool can analyze them.",
        )

        uploaded = st.file_uploader(
            "Upload a PDF for text analysis",
            type=["pdf"],
            key="wc_up",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = signature(data)

            show_file_summary(uploaded.name, data)

            if st.button(
                "Generate word cloud",
                type="primary",
                key="run_wc",
            ):
                try:
                    with read_pdf(data) as pdf:
                        corpus = " ".join(
                            page.get_text("text") for page in pdf
                        ).strip()

                    if not corpus:
                        st.warning(
                            "No extractable text was found. The file may "
                            "contain scanned images rather than selectable text."
                        )
                    else:
                        cloud = WordCloud(
                            width=1200,
                            height=600,
                            background_color="#0b1020",
                            colormap="cool",
                            collocations=False,
                        ).generate(corpus)

                        fig, ax = plt.subplots(figsize=(10, 5), dpi=140)
                        fig.patch.set_facecolor("#0b1020")
                        ax.set_facecolor("#0b1020")
                        ax.imshow(cloud, interpolation="bilinear")
                        ax.axis("off")

                        png = io.BytesIO()

                        fig.savefig(
                            png,
                            format="png",
                            bbox_inches="tight",
                            facecolor=fig.get_facecolor(),
                            dpi=140,
                        )

                        plt.close(fig)

                        save_output(
                            "wordcloud",
                            sig,
                            png.getvalue(),
                            "word_cloud.png",
                            "image/png",
                            message=(
                                "Word cloud generated from extractable PDF text."
                            ),
                        )

                except Exception as exc:
                    st.error(f"Could not generate the word cloud: {exc}")

            display_output("wordcloud", sig, preview="wordcloud")

        else:
            empty_state(
                "Analyze a document's vocabulary",
                "Upload a text-based PDF to generate a word-frequency "
                "visualization and download it as a PNG.",
            )

    # -------------------------------------------------------------------------
    # EXTRACT EMBEDDED IMAGES
    # -------------------------------------------------------------------------
    with tabs[7]:
        tool_intro(
            "Extract embedded assets",
            "Find embedded raster images inside a PDF and download each "
            "asset separately. Page screenshots or backgrounds may not be "
            "stored as extractable image objects.",
        )

        uploaded = st.file_uploader(
            "Upload a PDF to inspect",
            type=["pdf"],
            key="ext_up",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = signature(data)

            show_file_summary(uploaded.name, data)

            asset_result_key = output_key("assets")

            if st.button(
                "Scan for embedded images",
                type="primary",
                key="run_assets",
            ):
                assets = []

                try:
                    with read_pdf(data) as pdf:
                        for page_index, page in enumerate(pdf, start=1):
                            for image_info in page.get_images(full=True):
                                try:
                                    extracted = pdf.extract_image(
                                        image_info[0]
                                    )

                                    assets.append({
                                        "page": page_index,
                                        "ext": extracted.get("ext", "bin"),
                                        "data": extracted["image"],
                                    })

                                except Exception:
                                    continue

                    st.session_state[asset_result_key] = {
                        "source_signature": sig,
                        "assets": assets,
                    }

                except Exception as exc:
                    st.error(f"Could not inspect this PDF: {exc}")

            cached = st.session_state.get(asset_result_key)

            if cached and cached.get("source_signature") == sig:
                assets = cached.get("assets", [])

                if not assets:
                    st.info(
                        "No extractable embedded raster images were found "
                        "in this PDF."
                    )
                else:
                    st.success(
                        f"Found {len(assets)} embedded image asset(s)."
                    )

                    cols = st.columns(3)

                    for index, asset in enumerate(assets, start=1):
                        with cols[(index - 1) % 3]:
                            st.image(
                                asset["data"],
                                caption=(
                                    f"Page {asset['page']} · Asset {index}"
                                ),
                                use_container_width=True,
                            )

                            st.download_button(
                                f"Download asset {index}",
                                data=asset["data"],
                                file_name=(
                                    f"page_{asset['page']}_asset_{index}."
                                    f"{asset['ext']}"
                                ),
                                mime="application/octet-stream",
                                key=f"download_asset_{sig[:10]}_{index}",
                                use_container_width=True,
                            )

        else:
            empty_state(
                "Inspect a PDF",
                "Upload a PDF and scan its pages for embedded images. "
                "Each detected asset gets its own preview and download control.",
            )


# -----------------------------------------------------------------------------
# 2. MEDIA STUDIO
# -----------------------------------------------------------------------------
elif selected_page == "🖼️ Media Studio":
    set_page_header(
        "Media Studio",
        "Resize images, reduce file size, and apply a grayscale conversion "
        "with clear output comparisons.",
        "🖼️",
    )

    tabs = st.tabs([
        "Resize Dimensions",
        "Quality Compression",
        "Grayscale Filter",
    ])

    # -------------------------------------------------------------------------
    # RESIZE IMAGE
    # -------------------------------------------------------------------------
    with tabs[0]:
        tool_intro(
            "Resize image dimensions",
            "Set output width and height. Enable aspect-ratio lock to avoid "
            "stretching the image unintentionally.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp"],
            key="resize_up",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = signature(data)

            try:
                image_obj = get_pil_image(data)

                show_file_summary(
                    uploaded.name,
                    data,
                    f"{image_obj.width} × {image_obj.height} px · "
                    f"{image_obj.format or 'Image'}",
                )

                left, right = st.columns([1, 1], gap="large")

                with left:
                    st.image(
                        image_obj,
                        caption="Original",
                        use_container_width=True,
                    )

                with right:
                    width_col, height_col = st.columns(2)

                    with width_col:
                        target_w = st.number_input(
                            "Target width (px)",
                            min_value=1,
                            max_value=20000,
                            value=int(image_obj.width),
                            step=1,
                            key="resize_w",
                        )

                    with height_col:
                        target_h = st.number_input(
                            "Target height (px)",
                            min_value=1,
                            max_value=20000,
                            value=int(image_obj.height),
                            step=1,
                            key="resize_h",
                        )

                    lock_ratio = st.checkbox(
                        "Keep original aspect ratio",
                        value=True,
                        key="resize_lock",
                    )

                    resample = st.selectbox(
                        "Resampling method",
                        [
                            "LANCZOS (best quality)",
                            "BICUBIC",
                            "BILINEAR",
                            "NEAREST",
                        ],
                        index=0,
                        key="resize_resample",
                    )

                    if st.button(
                        "Resize image",
                        type="primary",
                        key="run_resize",
                    ):
                        if lock_ratio:
                            ratio = image_obj.width / image_obj.height

                            # Fit the requested box without distorting the image.
                            if target_w / target_h > ratio:
                                final_h = int(target_h)
                                final_w = max(
                                    1,
                                    round(final_h * ratio),
                                )
                            else:
                                final_w = int(target_w)
                                final_h = max(
                                    1,
                                    round(final_w / ratio),
                                )
                        else:
                            final_w = int(target_w)
                            final_h = int(target_h)

                        resample_map = {
                            "LANCZOS (best quality)": Image.Resampling.LANCZOS,
                            "BICUBIC": Image.Resampling.BICUBIC,
                            "BILINEAR": Image.Resampling.BILINEAR,
                            "NEAREST": Image.Resampling.NEAREST,
                        }

                        resized = image_obj.resize(
                            (final_w, final_h),
                            resample_map[resample],
                        )

                        out = io.BytesIO()
                        resized.save(out, format="PNG", optimize=True)

                        save_output(
                            "resize",
                            sig,
                            out.getvalue(),
                            "resized_image.png",
                            "image/png",
                            message=(
                                f"Output dimensions: {final_w} × "
                                f"{final_h} px."
                            ),
                        )

                display_output("resize", sig, preview="image")

            except (
                UnidentifiedImageError,
                OSError,
                ValueError,
            ) as exc:
                st.error(f"Could not open this image: {exc}")

        else:
            empty_state(
                "Ready to resize",
                "Upload a PNG, JPEG, or WebP image. You'll see its original "
                "dimensions and can preview the resized result before downloading.",
            )

    # -------------------------------------------------------------------------
    # IMAGE COMPRESSION
    # -------------------------------------------------------------------------
    with tabs[1]:
        tool_intro(
            "Quality compression",
            "Encode the image as JPEG at a selected quality. JPEG is lossy "
            "and does not preserve transparency; the output is always a .jpg file.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp"],
            key="comp_img_up",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = signature(data)

            try:
                image_obj = get_pil_image(data)

                show_file_summary(
                    uploaded.name,
                    data,
                    f"{image_obj.width} × {image_obj.height} px",
                )

                quality = st.slider(
                    "JPEG quality",
                    min_value=10,
                    max_value=95,
                    value=80,
                    step=5,
                    key="jpeg_quality",
                )

                if st.button(
                    "Compress image",
                    type="primary",
                    key="run_img_compress",
                ):
                    out = io.BytesIO()

                    image_obj.convert("RGB").save(
                        out,
                        format="JPEG",
                        quality=quality,
                        optimize=True,
                        progressive=True,
                    )

                    compressed = out.getvalue()

                    reduction = (
                        (len(data) - len(compressed)) / len(data) * 100
                        if data
                        else 0
                    )

                    if reduction > 0:
                        message = (
                            f"Reduced file size by {reduction:.1f}% "
                            f"({format_size(len(data) - len(compressed))} saved)."
                        )
                    elif reduction < 0:
                        message = (
                            f"Output is {abs(reduction):.1f}% larger. "
                            "A JPEG conversion does not always reduce file size."
                        )
                    else:
                        message = "Output size is unchanged."

                    save_output(
                        "img_compress",
                        sig,
                        compressed,
                        "compressed_image.jpg",
                        "image/jpeg",
                        message=message,
                    )

                result = st.session_state.get(
                    output_key("img_compress")
                )

                if result and result.get("source_signature") == sig:
                    original_col, result_col = st.columns(2, gap="large")

                    with original_col:
                        st.image(
                            image_obj,
                            caption=f"Original · {format_size(len(data))}",
                            use_container_width=True,
                        )

                    with result_col:
                        st.image(
                            result["data"],
                            caption=(
                                "Compressed · "
                                f"{format_size(len(result['data']))}"
                            ),
                            use_container_width=True,
                        )

                    st.success(
                        result.get("meta", {}).get(
                            "message",
                            "Compression complete.",
                        )
                    )

                    st.download_button(
                        "⬇️ Download compressed JPG",
                        result["data"],
                        file_name=result["filename"],
                        mime=result["mime"],
                        key="download_img_compress",
                        use_container_width=True,
                    )

            except (
                UnidentifiedImageError,
                OSError,
                ValueError,
            ) as exc:
                st.error(f"Could not process this image: {exc}")

        else:
            empty_state(
                "Reduce image size",
                "Upload an image and adjust JPEG quality. The original and "
                "compressed previews will be shown side by side with a size comparison.",
            )

    # -------------------------------------------------------------------------
    # GRAYSCALE CONVERSION
    # -------------------------------------------------------------------------
    with tabs[2]:
        tool_intro(
            "Grayscale conversion",
            "Convert the image to a single-channel grayscale image and "
            "preview the result.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp"],
            key="gray_up",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = signature(data)

            try:
                image_obj = get_pil_image(data)

                show_file_summary(
                    uploaded.name,
                    data,
                    f"Mode: {image_obj.mode} · "
                    f"{image_obj.width} × {image_obj.height} px",
                )

                if st.button(
                    "Apply grayscale",
                    type="primary",
                    key="run_gray",
                ):
                    gray = ImageOps.grayscale(image_obj)
                    out = io.BytesIO()

                    gray.save(out, format="PNG", optimize=True)

                    save_output(
                        "grayscale",
                        sig,
                        out.getvalue(),
                        "grayscale_image.png",
                        "image/png",
                        message="Converted to grayscale.",
                    )

                result = st.session_state.get(
                    output_key("grayscale")
                )

                if result and result.get("source_signature") == sig:
                    before, after = st.columns(2, gap="large")

                    with before:
                        st.image(
                            image_obj,
                            caption="Original",
                            use_container_width=True,
                        )

                    with after:
                        st.image(
                            result["data"],
                            caption="Grayscale output",
                            use_container_width=True,
                        )

                    st.success(
                        result.get("meta", {}).get(
                            "message",
                            "Grayscale conversion complete.",
                        )
                    )

                    st.download_button(
                        "⬇️ Download grayscale PNG",
                        result["data"],
                        file_name=result["filename"],
                        mime=result["mime"],
                        key="download_grayscale",
                        use_container_width=True,
                    )

            except (
                UnidentifiedImageError,
                OSError,
                ValueError,
            ) as exc:
                st.error(f"Could not process this image: {exc}")

        else:
            empty_state(
                "Convert a color image",
                "Upload an image to preview the original and grayscale "
                "versions before downloading the PNG output.",
            )


# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")

st.markdown(
    "<p style='text-align:center;color:#91a0b7 !important;font-size:.8rem;'>"
    "Engineered with care by <strong>Ashutosh Borah</strong> · © 2026</p>",
    unsafe_allow_html=True,
)
