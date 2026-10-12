from __future__ import annotations

import csv
import hashlib
import io
import re
import zipfile
from collections import Counter
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pymupdf
import streamlit as st
from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError
from wordcloud import WordCloud
import docx

from modules.pdf_utils import docx_to_pdf_bytes as libreoffice_docx_to_pdf_bytes

# -----------------------------------------------------------------------------
# Page configuration and theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ashutosh Studio | Engineering Toolkit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp, [data-testid="stAppViewContainer"] {
        background: #0b1020; color: #f3f6fc;
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    [data-testid="stHeader"], header[data-testid="stHeader"] { background: #0b1020 !important; }
    .block-container, [data-testid="stMainBlockContainer"] {
        padding-top: 2.5rem !important; padding-bottom: 2rem !important;
        overflow: visible !important;
    }
    [data-testid="stSidebar"] { background: #10182a !important; border-right: 1px solid #293750; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label { color: #e6edf8 !important; }
    h1, h2, h3, h4, p, li, label { color: #f3f6fc; }
    .hero-title {
        font-size: clamp(1.8rem, 3vw, 2.5rem); font-weight: 850;
        letter-spacing: -.035em; line-height: 1.25;
        background: linear-gradient(110deg,#60a5fa 0%,#a78bfa 58%,#f0abfc 100%);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent; margin: 0 0 .45rem 0;
        padding-top: .15rem;
    }
    .hero-subtitle { color: #c1cbda !important; line-height: 1.65; margin-bottom: 1.4rem; }
    .workflow-card {
        background: #111a2d; border: 1px solid #34435e; border-radius: 14px;
        padding: 1.2rem 1.25rem; margin: .35rem 0 1rem 0; min-height: 150px;
    }
    .workflow-card p { color: #d0d9e7 !important; line-height: 1.6; }
    .muted { color: #bac5d6 !important; }
    .empty-state {
        background: #121c30; border: 1px dashed #50617d; border-radius: 12px;
        padding: 1.15rem 1.25rem; color: #d2dceb; margin: .75rem 0 1rem 0;
    }
    .status-pill {
        display: inline-block; border: 1px solid #1e7759; color: #6ee7b7 !important;
        background: #0c2c27; border-radius: 100px; padding: .24rem .65rem;
        font-size: .75rem; font-weight: 700;
    }
    .file-summary {
        background: #131e32; border: 1px solid #3a4b68; border-radius: 10px;
        padding: .75rem 1rem; margin: .5rem 0 1rem 0; color: #e6edf8;
        overflow-wrap: anywhere;
    }
    .file-summary span { color: #bfcbdd; }
    .stTabs [data-baseweb="tab-list"] { gap: .35rem; border-bottom: 1px solid #34435e; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] {
        min-height: 2.6rem; background: #141f33 !important;
        border: 1px solid #34435e !important; border-radius: 9px 9px 0 0;
        padding: .5rem .8rem;
    }
    .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] div {
        color: #dce5f2 !important; font-weight: 650 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #243550 !important; border-color: #6ba7f5 !important;
        border-bottom: 3px solid #fb7185 !important;
    }
    [data-testid="stFileUploader"] section {
        background: #151e30 !important; border: 1px dashed #546783 !important; border-radius: 12px;
    }
    [data-testid="stFileUploader"] section *, [data-testid="stFileUploader"] button {
        color: #e3eaf5 !important;
    }
    [data-testid="stFileUploader"] button { background: #25334b !important; border: 1px solid #526582 !important; }
    input, textarea, [data-baseweb="select"] > div { color: #f5f7fb !important; }
    [data-baseweb="select"] > div { background: #18233a !important; border-color: #50617d !important; }
    .stButton > button, .stDownloadButton > button {
        border-radius: 9px; min-height: 2.45rem; font-weight: 700;
    }
    .stButton > button:hover, .stDownloadButton > button:hover { border-color: #93c5fd !important; }
    .stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {
        background: #2563eb !important; border: 1px solid #60a5fa !important; color: white !important;
    }
    section[data-testid="stSidebar"] .stButton > button,
    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
        background: #172033 !important; color: #f9fafb !important; border: 1px solid #334155 !important;
    }
    section[data-testid="stSidebar"] .stButton > button p,
    section[data-testid="stSidebar"] .stButton > button span,
    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] p,
    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] span { color: #f9fafb !important; }
    section[data-testid="stSidebar"] .stButton > button:hover { background: #25334b !important; border-color: #60a5fa !important; }
    [data-testid="stMetric"] { background: #121c30; border: 1px solid #34435e; border-radius: 12px; padding: .8rem 1rem; }
    [data-testid="stMetricLabel"] { color: #c0ccdc !important; }
    [data-testid="stMetricValue"] { color: #f7faff !important; }
    hr { border-color: #34435e !important; }
    @media (max-width: 700px) {
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; padding-top: 2rem !important; }
        .workflow-card { min-height: auto; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Shared helpers
# -----------------------------------------------------------------------------
def format_size(n_bytes: int) -> str:
    size = float(n_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{int(size)} B" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def file_signature(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def show_file_summary(name: str, data: bytes, details: str = "") -> None:
    tail = f"<span> • {details}</span>" if details else ""
    st.markdown(
        f"<div class='file-summary'><strong>📎 {name}</strong><br>"
        f"<span>{format_size(len(data))}</span>{tail}</div>",
        unsafe_allow_html=True,
    )


def empty_state(title: str, instructions: str) -> None:
    st.markdown(
        f"<div class='empty-state'><strong>📂 {title}</strong><br>{instructions}</div>",
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, emoji: str) -> None:
    st.markdown(f"<div class='hero-title'>{emoji} {title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def tool_intro(title: str, description: str) -> None:
    st.markdown(f"### {title}")
    st.markdown(f"<p class='muted'>{description}</p>", unsafe_allow_html=True)


def save_result(key: str, source_sig: str, data: bytes | str, filename: str, mime: str, kind: str = "") -> None:
    st.session_state[f"result_{key}"] = {
        "sig": source_sig, "data": data, "filename": filename, "mime": mime, "kind": kind
    }


def show_result(key: str, source_sig: str) -> None:
    result = st.session_state.get(f"result_{key}")
    if not result or result["sig"] != source_sig:
        return
    if result["kind"] == "image":
        st.image(result["data"], caption="Preview of processed output", use_container_width=True)
    elif result["kind"] == "text":
        st.text_area("Output preview", str(result["data"]), height=220, key=f"preview_{key}")
    st.download_button(
        "⬇️ Download result", data=result["data"], file_name=result["filename"],
        mime=result["mime"], key=f"download_{key}", use_container_width=True,
    )


def pdf_text_pages(data: bytes) -> list[str]:
    with pymupdf.open(stream=data, filetype="pdf") as pdf:
        return [page.get_text("text").strip() for page in pdf]


def pdf_to_markdown(data: bytes) -> str:
    pages = pdf_text_pages(data)
    return "\n\n---\n\n".join(
        f"## Page {i}\n\n{text or '_No extractable text on this page._'}"
        for i, text in enumerate(pages, start=1)
    )


def pdf_to_docx_bytes(data: bytes) -> bytes:
    document = docx.Document()
    pages = pdf_text_pages(data)
    for i, text in enumerate(pages, start=1):
        if i > 1:
            document.add_page_break()
        document.add_heading(f"Page {i}", level=2)
        document.add_paragraph(text or "[No extractable text on this page]")
    output = io.BytesIO()
    document.save(output)
    return output.getvalue()


def compress_pdf_bytes(data: bytes) -> bytes:
    with pymupdf.open(stream=data, filetype="pdf") as pdf:
        output = io.BytesIO()
        pdf.save(output, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
        return output.getvalue()


def merge_pdf_bytes(files: list[tuple[str, bytes]]) -> bytes:
    merged = pymupdf.open()
    try:
        for _name, data in files:
            with pymupdf.open(stream=data, filetype="pdf") as source:
                merged.insert_pdf(source)
        output = io.BytesIO()
        merged.save(output, garbage=4, deflate=True)
        return output.getvalue()
    finally:
        merged.close()


def images_to_pdf_bytes(images: list[tuple[str, bytes]]) -> bytes:
    converted: list[Image.Image] = []
    try:
        for _name, raw in images:
            with Image.open(io.BytesIO(raw)) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                converted.append(image.copy())
        if not converted:
            raise ValueError("Upload at least one supported image.")
        output = io.BytesIO()
        converted[0].save(output, format="PDF", save_all=True, append_images=converted[1:])
        return output.getvalue()
    finally:
        for image in converted:
            image.close()


def get_image(raw: bytes) -> Image.Image:
    image = Image.open(io.BytesIO(raw))
    image.load()
    return ImageOps.exif_transpose(image)


def output_name(name: str, suffix: str) -> str:
    stem = re.sub(r"\.[^.]+$", "", name)
    return f"{stem}{suffix}"

# -----------------------------------------------------------------------------
# Sidebar navigation
# -----------------------------------------------------------------------------
PAGES = ["🏠 Platform Overview", "📄 Document Intelligence", "🖼️ Media Studio"]
if "active_page" not in st.session_state:
    st.session_state.active_page = PAGES[0]

st.sidebar.markdown("# ⚡ ASHUTOSH STUDIO")
st.sidebar.markdown(
    "<p style='color:#bac8dc !important;font-size:.86rem;line-height:1.6;'>"
    "Engineering & Computational Toolkit<br><strong>Ashutosh Borah</strong></p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Workspace Directory")
for index, page_name in enumerate(PAGES):
    if st.sidebar.button(
        page_name, key=f"nav_{index}", use_container_width=True,
        type="primary" if st.session_state.active_page == page_name else "secondary",
    ):
        st.session_state.active_page = page_name
        st.rerun()
st.sidebar.markdown("---")
st.sidebar.markdown("<span class='status-pill'>● SYSTEM ONLINE</span>", unsafe_allow_html=True)
st.sidebar.caption("Local file processing · No account required")

# -----------------------------------------------------------------------------
# Platform overview
# -----------------------------------------------------------------------------
if st.session_state.active_page == PAGES[0]:
    page_header(
        "Welcome to Ashutosh Studio",
        "A practical workspace for document conversion, PDF operations, document analysis, and image optimization.",
        "⚡",
    )
    a, b, c = st.columns(3)
    a.metric("Workspace modules", "2")
    b.metric("Document & media tools", "15+")
    c.metric("Interface", "Responsive")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            """<div class='workflow-card'><h3 style='color:#8bbdff;margin-top:0'>📄 Document Intelligence</h3>
            <p>Convert PDFs and Word files, merge or compress PDFs, create PDFs from images, analyse document text, and inspect embedded PDF images.</p>
            <p><strong>Best for:</strong> document cleanup, conversion, and investigation.</p></div>""",
            unsafe_allow_html=True,
        )
        if st.button("Open Document Intelligence →", type="primary", use_container_width=True):
            st.session_state.active_page = PAGES[1]
            st.rerun()
    with right:
        st.markdown(
            """<div class='workflow-card'><h3 style='color:#6ee7b7;margin-top:0'>🖼️ Media Studio</h3>
            <p>Resize, crop, rotate, compress, convert, or watermark images. Review dimensions and colour histograms.</p>
            <p><strong>Best for:</strong> preparing and optimizing image assets.</p></div>""",
            unsafe_allow_html=True,
        )
        if st.button("Open Media Studio →", type="primary", use_container_width=True):
            st.session_state.active_page = PAGES[2]
            st.rerun()
    st.markdown("### How to use the studio")
    x, y, z = st.columns(3)
    x.markdown("**1 · Upload**\n\nChoose a supported file and review its name and size.")
    y.markdown("**2 · Process**\n\nChoose a tool and adjust any settings.")
    z.markdown("**3 · Review & download**\n\nCheck the output preview, then download the result.")
    st.info("Files are processed by the app while you use it. Avoid uploading confidential documents to a public deployment unless you are comfortable with its hosting and data-handling setup.")

# -----------------------------------------------------------------------------
# Document Intelligence
# -----------------------------------------------------------------------------
elif st.session_state.active_page == PAGES[1]:
    page_header("Document Intelligence Hub", "Convert, combine, compress, and inspect common document formats.", "📄")
    tabs = st.tabs([
        "PDF → Markdown", "PDF → Word", "Word → PDF", "Merge PDFs", "Images → PDF",
        "Compress PDF", "Document Analyzer", "PDF Asset Inspector",
    ])

    with tabs[0]:
        tool_intro("Convert PDF to Markdown", "Extract selectable PDF text by page and download a Markdown file. Scanned pages require OCR, which is not included.")
        uploaded = st.file_uploader("Upload a PDF", type=["pdf"], key="pdf_md_upload")
        if uploaded:
            data = uploaded.getvalue(); sig = file_signature(data)
            show_file_summary(uploaded.name, data, "PDF document")
            if st.button("Convert to Markdown", type="primary", key="run_pdf_md"):
                try:
                    save_result("pdf_md", sig, pdf_to_markdown(data), output_name(uploaded.name, ".md"), "text/markdown", "text")
                except Exception as exc:
                    st.error(f"Could not read this PDF: {exc}")
            show_result("pdf_md", sig)
        else:
            empty_state("Ready to convert", "Upload a PDF with selectable text to create a Markdown version.")

    with tabs[1]:
        tool_intro("Convert PDF to Word", "Create an editable DOCX from selectable PDF text. This extracts text; the original layout and images are not reproduced exactly.")
        uploaded = st.file_uploader("Upload a PDF", type=["pdf"], key="pdf_docx_upload")
        if uploaded:
            data = uploaded.getvalue(); sig = file_signature(data)
            show_file_summary(uploaded.name, data, "PDF document")
            if st.button("Convert to Word", type="primary", key="run_pdf_docx"):
                try:
                    save_result("pdf_docx", sig, pdf_to_docx_bytes(data), output_name(uploaded.name, ".docx"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                except Exception as exc:
                    st.error(f"Could not convert this PDF: {exc}")
            show_result("pdf_docx", sig)
        else:
            empty_state("Ready to convert", "Upload a PDF to create an editable Word document.")

    with tabs[2]:
        tool_intro("Convert Word to PDF", "Uses LibreOffice to retain Word layout, tables, headers, footers, and embedded images much better than rebuilding the document from text.")
        uploaded = st.file_uploader("Upload a Word document", type=["docx"], key="docx_pdf_upload")
        if uploaded:
            data = uploaded.getvalue(); sig = file_signature(data)
            show_file_summary(uploaded.name, data, "DOCX document")
            if st.button("Convert to PDF", type="primary", key="run_docx_pdf"):
                try:
                    converted = libreoffice_docx_to_pdf_bytes(data)
                    save_result("docx_pdf", sig, converted, output_name(uploaded.name, ".pdf"), "application/pdf")
                except Exception as exc:
                    st.error(f"Could not convert this DOCX. Check that LibreOffice is installed and the file is valid. Details: {exc}")
            show_result("docx_pdf", sig)
        else:
            empty_state("Ready to convert", "Upload a DOCX file. The converter requires the system packages in packages.txt to finish installing.")

    with tabs[3]:
        tool_intro("Merge PDF files", "Combine PDFs in the order shown below. Rearrange your upload selection before processing if the order matters.")
        uploads = st.file_uploader("Select two or more PDFs", type=["pdf"], accept_multiple_files=True, key="merge_pdfs_upload")
        if uploads:
            items = [(item.name, item.getvalue()) for item in uploads]
            sig = file_signature(b"".join(name.encode() + b"\0" + raw for name, raw in items))
            st.write(f"Selected files: **{len(items)}**")
            for i, (name, raw) in enumerate(items, start=1):
                st.write(f"{i}. {name} — {format_size(len(raw))}")
            if st.button("Merge PDFs", type="primary", key="run_merge_pdfs"):
                try:
                    merged = merge_pdf_bytes(items)
                    save_result("merge_pdfs", sig, merged, "merged.pdf", "application/pdf")
                except Exception as exc:
                    st.error(f"Could not merge these PDFs: {exc}")
            show_result("merge_pdfs", sig)
        else:
            empty_state("Ready to merge", "Upload multiple PDF files to combine them into one document.")

    with tabs[4]:
        tool_intro("Convert images to PDF", "Combine multiple images into a single PDF, one image per page.")
        uploads = st.file_uploader("Select images", type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"], accept_multiple_files=True, key="images_pdf_upload")
        if uploads:
            items = [(item.name, item.getvalue()) for item in uploads]
            sig = file_signature(b"".join(name.encode() + b"\0" + raw for name, raw in items))
            st.write(f"Selected images: **{len(items)}**")
            for name, raw in items:
                st.caption(f"{name} · {format_size(len(raw))}")
            if st.button("Create PDF", type="primary", key="run_images_pdf"):
                try:
                    result = images_to_pdf_bytes(items)
                    save_result("images_pdf", sig, result, "images.pdf", "application/pdf")
                except (UnidentifiedImageError, OSError, ValueError) as exc:
                    st.error(f"Could not build the PDF: {exc}")
            show_result("images_pdf", sig)
        else:
            empty_state("Ready to compile", "Upload images to compile them into one PDF.")

    with tabs[5]:
        tool_intro("Compress PDF", "Rewrites PDF streams and removes unused objects where possible. This may reduce the file size, but already-optimized or image-heavy PDFs may not shrink much.")
        uploaded = st.file_uploader("Upload a PDF", type=["pdf"], key="compress_pdf_upload")
        if uploaded:
            data = uploaded.getvalue(); sig = file_signature(data)
            show_file_summary(uploaded.name, data, "PDF document")
            if st.button("Compress PDF", type="primary", key="run_compress_pdf"):
                try:
                    compressed = compress_pdf_bytes(data)
                    save_result("compress_pdf", sig, compressed, output_name(uploaded.name, "_compressed.pdf"), "application/pdf")
                    delta = len(compressed) - len(data)
                    if delta < 0:
                        st.success(f"Reduced file size by {format_size(-delta)} ({-delta / max(len(data), 1) * 100:.1f}%).")
                    else:
                        st.info("The PDF was rewritten, but the file did not get smaller. Some PDFs are already optimized.")
                except Exception as exc:
                    st.error(f"Could not compress this PDF: {exc}")
            show_result("compress_pdf", sig)
        else:
            empty_state("Ready to compress", "Upload a PDF to optimize its internal structure.")

    with tabs[6]:
        tool_intro("Document Analyzer", "Understand a PDF using ranked terms, page statistics, custom keyword counts, a searchable frequency table, and downloadable data. This analyzes selectable text only.")
        uploaded = st.file_uploader("Upload a text-based PDF", type=["pdf"], key="analyzer_pdf_upload")
        if uploaded:
            data = uploaded.getvalue(); sig = file_signature(data)
            show_file_summary(uploaded.name, data, "PDF document")
            try:
                pages = pdf_text_pages(data)
                full_text = "\n".join(pages)
                words = re.findall(r"\b[A-Za-z][A-Za-z'-]{2,}\b", full_text.lower())
                stop_default = "about, after, again, also, among, because, been, before, being, between, both, could, does, doing, down, each, from, further, have, having, into, itself, just, more, most, over, same, should, some, such, than, that, their, them, then, there, these, they, this, those, through, under, until, very, what, when, where, which, while, with, would, your, page, figure, table, using, used, based, results, study"
                stop_input = st.text_input("Additional stop words (comma-separated)", value=stop_default, key="analyzer_stop_words")
                stop_words = {item.strip().lower() for item in stop_input.split(",") if item.strip()}
                filtered_words = [word for word in words if word not in stop_words and not word.isdigit()]
                counts = Counter(filtered_words)
                top_n = st.slider("Number of terms to display", 10, 50, 20, key="analyzer_top_n")
                query = st.text_input("Check keyword or phrase (optional)", key="analyzer_keyword_query").strip().lower()
                word_total = len(re.findall(r"\b\w+\b", full_text))
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Pages", len(pages))
                m2.metric("Words", f"{word_total:,}")
                m3.metric("Unique terms", f"{len(set(filtered_words)):,}")
                m4.metric("Characters", f"{len(full_text):,}")
                if query:
                    per_page = [page.lower().count(query) for page in pages]
                    st.write(f"**Occurrences of ‘{query}’:** {sum(per_page)}")
                    st.dataframe([{"Page": i, "Occurrences": count} for i, count in enumerate(per_page, 1)], use_container_width=True, hide_index=True)
                if counts:
                    top_items = counts.most_common(top_n)
                    frequency_rows = [{"Term": term, "Frequency": count} for term, count in top_items]
                    st.markdown("#### Most frequent meaningful terms")
                    st.dataframe(frequency_rows, use_container_width=True, hide_index=True)
                    fig, ax = plt.subplots(figsize=(9, max(4, top_n * 0.28)))
                    display_items = list(reversed(top_items))
                    ax.barh([item[0] for item in display_items], [item[1] for item in display_items])
                    ax.set_xlabel("Occurrences")
                    ax.set_title(f"Top {len(top_items)} terms by frequency")
                    ax.grid(axis="x", alpha=0.2)
                    fig.tight_layout()
                    st.pyplot(fig, clear_figure=True)
                    csv_buffer = io.StringIO()
                    writer = csv.DictWriter(csv_buffer, fieldnames=["Term", "Frequency"])
                    writer.writeheader(); writer.writerows([{"Term": term, "Frequency": n} for term, n in counts.most_common()])
                    st.download_button("Download all term frequencies (CSV)", csv_buffer.getvalue().encode("utf-8-sig"), output_name(uploaded.name, "_term_frequencies.csv"), "text/csv", key="download_term_csv")
                    if st.checkbox("Also generate a word cloud", key="analyzer_wordcloud_toggle"):
                        cloud = WordCloud(width=1200, height=600, background_color="#0b1020", colormap="viridis", stopwords=stop_words, collocations=False).generate_from_frequencies(dict(counts))
                        cloud_out = io.BytesIO(); cloud.to_image().save(cloud_out, format="PNG")
                        st.image(cloud_out.getvalue(), caption="Word cloud (larger words appear more frequently)", use_container_width=True)
                        st.download_button("Download word cloud (PNG)", cloud_out.getvalue(), output_name(uploaded.name, "_wordcloud.png"), "image/png", key="download_wordcloud_png")
                else:
                    st.warning("No analyzable text was found after stop-word filtering. This may be a scanned PDF or a document with very little text.")
                with st.expander("Page-by-page text statistics"):
                    stats = []
                    for i, page in enumerate(pages, 1):
                        stats.append({"Page": i, "Words": len(re.findall(r"\b\w+\b", page)), "Characters": len(page), "Extracted text": page[:240].replace("\n", " ")})
                    st.dataframe(stats, use_container_width=True, hide_index=True)
            except Exception as exc:
                st.error(f"Could not analyze this PDF: {exc}")
        else:
            empty_state("Ready to analyze", "Upload a PDF to see term frequencies, keywords, and page-level statistics.")

    with tabs[7]:
        tool_intro("PDF Asset Inspector", "Inspect embedded raster images with page number, dimensions, format, and size. Select assets to download individually or in a ZIP. Vector graphics may not appear as standalone embedded images.")
        uploaded = st.file_uploader("Upload a PDF", type=["pdf"], key="asset_pdf_upload")
        if uploaded:
            data = uploaded.getvalue()
            show_file_summary(uploaded.name, data, "PDF document")
            try:
                assets: list[dict[str, Any]] = []
                with pymupdf.open(stream=data, filetype="pdf") as pdf:
                    for page_number, page in enumerate(pdf, start=1):
                        for image_info in page.get_images(full=True):
                            xref = image_info[0]
                            try:
                                extracted = pdf.extract_image(xref)
                                image_data = extracted.get("image", b"")
                                if not image_data:
                                    continue
                                asset = {
                                    "label": f"Page {page_number} · xref {xref} · {extracted.get('width', '?')}×{extracted.get('height', '?')}",
                                    "page": page_number,
                                    "xref": xref,
                                    "width": extracted.get("width", 0),
                                    "height": extracted.get("height", 0),
                                    "format": extracted.get("ext", "bin").upper(),
                                    "bytes": len(image_data),
                                    "data": image_data,
                                }
                                assets.append(asset)
                            except Exception:
                                continue
                if not assets:
                    st.info("No embedded raster images were found. The PDF may contain vector drawings or page-rendered content rather than standalone raster images.")
                else:
                    st.success(f"Found {len(assets)} embedded image occurrence(s). Repeated references may appear more than once when used on different pages.")
                    rows = [{"Asset": item["label"], "Page": item["page"], "Width (px)": item["width"], "Height (px)": item["height"], "Format": item["format"], "File size": format_size(item["bytes"])} for item in assets]
                    st.dataframe(rows, use_container_width=True, hide_index=True)
                    chosen = st.multiselect("Choose assets to export", options=[item["label"] for item in assets], default=[item["label"] for item in assets], key="chosen_pdf_assets")
                    selected = [item for item in assets if item["label"] in chosen]
                    if selected:
                        preview_cols = st.columns(min(3, len(selected)))
                        for idx, item in enumerate(selected[:6]):
                            with preview_cols[idx % len(preview_cols)]:
                                st.caption(item["label"])
                                try:
                                    st.image(item["data"], use_container_width=True)
                                except Exception:
                                    st.caption("Preview unavailable for this image format.")
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                            for i, item in enumerate(selected, 1):
                                ext = item["format"].lower().replace("jpeg", "jpg")
                                zip_file.writestr(f"page_{item['page']}_image_{i}_xref_{item['xref']}.{ext}", item["data"])
                        st.download_button("Download selected assets (ZIP)", zip_buffer.getvalue(), output_name(uploaded.name, "_assets.zip"), "application/zip", key="download_assets_zip")
                        for i, item in enumerate(selected, 1):
                            ext = item["format"].lower().replace("jpeg", "jpg")
                            st.download_button(f"Download image {i} · Page {item['page']}", item["data"], f"page_{item['page']}_image_{i}.{ext}", "application/octet-stream", key=f"download_asset_{i}_{item['xref']}")
            except Exception as exc:
                st.error(f"Could not inspect this PDF: {exc}")
        else:
            empty_state("Ready to inspect", "Upload a PDF to review and export its embedded raster images.")

# -----------------------------------------------------------------------------
# Media Studio
# -----------------------------------------------------------------------------
elif st.session_state.active_page == PAGES[2]:
    page_header("Media Studio", "Resize, crop, rotate, compress, convert, and watermark images with clear previews.", "🖼️")
    tabs = st.tabs(["Resize", "JPEG Compress", "Grayscale", "Crop", "Rotate & Flip", "Convert Format", "Watermark", "Image Analysis"])

    with tabs[0]:
        tool_intro("Resize image", "Set a new width and height. Use the aspect-ratio option to avoid stretching the image.")
        uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"], key="resize_upload")
        if uploaded:
            raw = uploaded.getvalue(); sig = file_signature(raw)
            try:
                image = get_image(raw)
                show_file_summary(uploaded.name, raw, f"{image.width} × {image.height} px")
                st.image(image, caption="Original image", use_container_width=True)
                preserve = st.checkbox("Preserve aspect ratio", value=True, key="resize_preserve")
                width = st.number_input("Output width (px)", min_value=1, max_value=12000, value=int(image.width), step=1, key="resize_width")
                height = st.number_input("Output height (px)", min_value=1, max_value=12000, value=int(image.height), step=1, key="resize_height")
                if st.button("Resize image", type="primary", key="run_resize"):
                    new_size = (int(width), int(height))
                    if preserve:
                        copy = image.copy(); copy.thumbnail(new_size, Image.Resampling.LANCZOS); result_image = copy
                    else:
                        result_image = image.resize(new_size, Image.Resampling.LANCZOS)
                    fmt = "PNG" if result_image.mode in ("RGBA", "LA") else "JPEG"
                    if fmt == "JPEG": result_image = result_image.convert("RGB")
                    out = io.BytesIO(); result_image.save(out, format=fmt, quality=92)
                    save_result("resize", sig, out.getvalue(), output_name(uploaded.name, f"_resized.{fmt.lower()}"), f"image/{fmt.lower()}", "image")
                show_result("resize", sig)
            except Exception as exc:
                st.error(f"Could not process this image: {exc}")

    with tabs[1]:
        tool_intro("Compress to JPEG", "JPEG is lossy and does not support transparency. Transparent pixels are placed on a white background.")
        uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"], key="jpeg_upload")
        if uploaded:
            raw = uploaded.getvalue(); sig = file_signature(raw)
            try:
                image = get_image(raw).convert("RGB")
                show_file_summary(uploaded.name, raw, f"{image.width} × {image.height} px")
                quality = st.slider("JPEG quality", 20, 95, 78, key="jpeg_quality")
                if st.button("Compress image", type="primary", key="run_jpeg"):
                    out = io.BytesIO(); image.save(out, format="JPEG", quality=quality, optimize=True, progressive=True)
                    result = out.getvalue()
                    save_result("jpeg", sig, result, output_name(uploaded.name, "_compressed.jpg"), "image/jpeg", "image")
                    st.caption(f"Original: {format_size(len(raw))} · Output: {format_size(len(result))}")
                show_result("jpeg", sig)
            except Exception as exc:
                st.error(f"Could not compress this image: {exc}")

    with tabs[2]:
        tool_intro("Convert to grayscale", "Create a grayscale image from colour input.")
        uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"], key="gray_upload")
        if uploaded:
            raw = uploaded.getvalue(); sig = file_signature(raw)
            try:
                image = get_image(raw)
                if st.button("Convert to grayscale", type="primary", key="run_gray"):
                    result_image = ImageOps.grayscale(image)
                    out = io.BytesIO(); result_image.save(out, format="PNG")
                    save_result("gray", sig, out.getvalue(), output_name(uploaded.name, "_grayscale.png"), "image/png", "image")
                show_result("gray", sig)
            except Exception as exc:
                st.error(f"Could not convert this image: {exc}")

    with tabs[3]:
        tool_intro("Crop image", "Crop by choosing the left, top, right, and bottom margins as percentages of the original dimensions.")
        uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"], key="crop_upload")
        if uploaded:
            raw = uploaded.getvalue(); sig = file_signature(raw)
            try:
                image = get_image(raw)
                a, b, c, d = st.columns(4)
                left = a.slider("Left %", 0, 90, 0, key="crop_left")
                top = b.slider("Top %", 0, 90, 0, key="crop_top")
                right = c.slider("Right %", 0, 90, 0, key="crop_right")
                bottom = d.slider("Bottom %", 0, 90, 0, key="crop_bottom")
                if st.button("Crop image", type="primary", key="run_crop"):
                    x1 = int(image.width * left / 100); y1 = int(image.height * top / 100)
                    x2 = int(image.width * (100 - right) / 100); y2 = int(image.height * (100 - bottom) / 100)
                    if x2 <= x1 or y2 <= y1:
                        st.error("The crop margins remove the entire image. Reduce the margins and try again.")
                    else:
                        result_image = image.crop((x1, y1, x2, y2))
                        out = io.BytesIO(); fmt = "PNG" if "A" in result_image.getbands() else "JPEG"
                        if fmt == "JPEG": result_image = result_image.convert("RGB")
                        result_image.save(out, format=fmt, quality=92)
                        save_result("crop", sig, out.getvalue(), output_name(uploaded.name, f"_cropped.{fmt.lower()}"), f"image/{fmt.lower()}", "image")
                show_result("crop", sig)
            except Exception as exc:
                st.error(f"Could not crop this image: {exc}")

    with tabs[4]:
        tool_intro("Rotate and flip", "Rotate by 90-degree increments or flip the image horizontally or vertically.")
        uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"], key="rotate_upload")
        if uploaded:
            raw = uploaded.getvalue(); sig = file_signature(raw)
            try:
                image = get_image(raw)
                rotation = st.selectbox("Rotation", [0, 90, 180, 270], format_func=lambda x: f"{x}°", key="rotation_degrees")
                flip = st.selectbox("Flip", ["None", "Horizontal", "Vertical"], key="rotation_flip")
                if st.button("Apply transform", type="primary", key="run_rotate"):
                    result_image = image.rotate(-rotation, expand=True)
                    if flip == "Horizontal": result_image = ImageOps.mirror(result_image)
                    elif flip == "Vertical": result_image = ImageOps.flip(result_image)
                    fmt = "PNG" if "A" in result_image.getbands() else "JPEG"
                    if fmt == "JPEG": result_image = result_image.convert("RGB")
                    out = io.BytesIO(); result_image.save(out, format=fmt, quality=92)
                    save_result("rotate", sig, out.getvalue(), output_name(uploaded.name, f"_transformed.{fmt.lower()}"), f"image/{fmt.lower()}", "image")
                show_result("rotate", sig)
            except Exception as exc:
                st.error(f"Could not transform this image: {exc}")

    with tabs[5]:
        tool_intro("Convert image format", "Convert to PNG, JPEG, or WEBP. Transparency is retained for PNG and WEBP; JPEG uses a white background.")
        uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"], key="format_upload")
        if uploaded:
            raw = uploaded.getvalue(); sig = file_signature(raw)
            try:
                image = get_image(raw)
                target = st.selectbox("Target format", ["PNG", "JPEG", "WEBP"], key="target_image_format")
                quality = st.slider("Quality (JPEG/WEBP)", 30, 100, 88, key="target_image_quality")
                if st.button("Convert format", type="primary", key="run_format"):
                    if target == "JPEG":
                        background = Image.new("RGB", image.size, "white")
                        if "A" in image.getbands(): background.paste(image, mask=image.getchannel("A"))
                        else: background.paste(image.convert("RGB"))
                        result_image = background
                    else:
                        result_image = image.copy()
                        if target == "PNG" and result_image.mode not in ("RGB", "RGBA", "L", "LA", "P"): result_image = result_image.convert("RGBA")
                    out = io.BytesIO(); save_args = {"format": target}
                    if target in ("JPEG", "WEBP"): save_args["quality"] = quality
                    result_image.save(out, **save_args)
                    ext = target.lower().replace("jpeg", "jpg")
                    save_result("format", sig, out.getvalue(), output_name(uploaded.name, f"_converted.{ext}"), f"image/{'jpeg' if target == 'JPEG' else ext}", "image")
                show_result("format", sig)
            except Exception as exc:
                st.error(f"Could not convert this image: {exc}")

    with tabs[6]:
        tool_intro("Add a text watermark", "Place a readable text watermark on an image. Keep a copy of your original file.")
        uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"], key="watermark_upload")
        if uploaded:
            raw = uploaded.getvalue(); sig = file_signature(raw)
            try:
                image = get_image(raw).convert("RGBA")
                watermark = st.text_input("Watermark text", value="Ashutosh Studio", key="watermark_text")
                opacity = st.slider("Opacity", 20, 255, 150, key="watermark_opacity")
                position = st.selectbox("Position", ["Bottom right", "Bottom left", "Top right", "Top left", "Center"], key="watermark_position")
                if st.button("Apply watermark", type="primary", key="run_watermark"):
                    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
                    font_size = max(14, image.width // 32)
                    try:
                        from PIL import ImageFont
                        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                    except Exception:
                        font = ImageDraw.load_default()
                    bbox = draw.textbbox((0, 0), watermark, font=font, stroke_width=1)
                    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    margin = max(10, image.width // 40)
                    positions = {
                        "Bottom right": (image.width - tw - margin, image.height - th - margin),
                        "Bottom left": (margin, image.height - th - margin),
                        "Top right": (image.width - tw - margin, margin),
                        "Top left": (margin, margin),
                        "Center": ((image.width - tw) // 2, (image.height - th) // 2),
                    }
                    xy = positions[position]
                    draw.text(xy, watermark, font=font, fill=(255, 255, 255, opacity), stroke_width=2, stroke_fill=(0, 0, 0, min(220, opacity)))
                    result_image = Image.alpha_composite(image, overlay)
                    out = io.BytesIO(); result_image.save(out, format="PNG")
                    save_result("watermark", sig, out.getvalue(), output_name(uploaded.name, "_watermarked.png"), "image/png", "image")
                show_result("watermark", sig)
            except Exception as exc:
                st.error(f"Could not add watermark: {exc}")

    with tabs[7]:
        tool_intro("Image analysis", "Review image dimensions and file size, then inspect a separate histogram for each RGB channel.")
        uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"], key="analysis_upload")
        if uploaded:
            raw = uploaded.getvalue()
            try:
                image = get_image(raw).convert("RGB")
                x, y, z = st.columns(3)
                x.metric("Width", f"{image.width:,} px")
                y.metric("Height", f"{image.height:,} px")
                z.metric("File size", format_size(len(raw)))
                st.image(image, caption=uploaded.name, use_container_width=True)
                array = np.asarray(image)
                fig, ax = plt.subplots(figsize=(9, 4))
                for channel, label in enumerate(["Red", "Green", "Blue"]):
                    counts, bins = np.histogram(array[:, :, channel], bins=256, range=(0, 256))
                    ax.plot(bins[:-1], counts, label=label)
                ax.set_title("RGB intensity distribution")
                ax.set_xlabel("Pixel intensity (0–255)"); ax.set_ylabel("Pixel count")
                ax.legend(); ax.grid(alpha=.2); fig.tight_layout()
                st.pyplot(fig, clear_figure=True)
            except Exception as exc:
                st.error(f"Could not analyze this image: {exc}")

st.markdown("---")
st.caption("Ashutosh Studio · Engineering & Computational Toolkit")
