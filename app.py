from __future__ import annotations

import csv
import hashlib
import io
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pymupdf
import streamlit as st
import docx

from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError
from wordcloud import WordCloud

from modules.pdf_utils import (
    docx_to_pdf_bytes as libreoffice_docx_to_pdf_bytes,
)

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

try:
    import argostranslate.package as argos_package
    import argostranslate.translate as argos_translate
except ImportError:
    argos_package = None
    argos_translate = None

try:
    from indic_transliteration import sanscript
except ImportError:
    sanscript = None


# =============================================================================
# 1. PAGE CONFIGURATION AND DESIGN
# =============================================================================

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

    .stApp,
    [data-testid="stAppViewContainer"] {
        background: #0b1020;
        color: #f3f6fc;
        font-family: Inter, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    [data-testid="stHeader"],
    header[data-testid="stHeader"] {
        background: #0b1020 !important;
    }

    .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 2.5rem !important;
        padding-bottom: 2rem !important;
        overflow: visible !important;
    }

    [data-testid="stSidebar"] {
        background: #10182a !important;
        border-right: 1px solid #293750;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #e6edf8 !important;
    }

    .hero-title {
        font-size: clamp(1.8rem, 3vw, 2.5rem);
        font-weight: 850;
        letter-spacing: -.035em;
        line-height: 1.25;
        background: linear-gradient(
            110deg, #60a5fa 0%, #a78bfa 58%, #f0abfc 100%
        );
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 .45rem 0;
        padding-top: .15rem;
    }

    .hero-subtitle {
        color: #c1cbda !important;
        line-height: 1.65;
        margin-bottom: 1.4rem;
    }

    .workflow-card {
        background: #111a2d;
        border: 1px solid #34435e;
        border-radius: 14px;
        padding: 1.2rem;
        margin: .35rem 0 1rem;
        min-height: 145px;
    }

    .workflow-card p {
        color: #d0d9e7 !important;
        line-height: 1.6;
    }

    .muted {
        color: #bac5d6 !important;
    }

    .empty-state {
        background: #121c30;
        border: 1px dashed #50617d;
        border-radius: 12px;
        padding: 1.15rem;
        color: #d2dceb;
        margin: .75rem 0 1rem;
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
        margin: .5rem 0 1rem;
        color: #e6edf8;
        overflow-wrap: anywhere;
    }

    .file-summary span {
        color: #bfcbdd;
    }

    /* Make navigation tabs fit smaller screens where possible. */
    .stTabs [data-baseweb="tab-list"] {
        gap: .35rem;
        border-bottom: 1px solid #34435e;
        flex-wrap: wrap;
        white-space: normal;
    }

    .stTabs [data-baseweb="tab"] {
        min-height: 2.6rem;
        background: #141f33 !important;
        border: 1px solid #34435e !important;
        border-radius: 9px 9px 0 0;
        padding: .5rem .8rem;
    }

    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] div {
        color: #dce5f2 !important;
        font-weight: 650 !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #243550 !important;
        border-color: #6ba7f5 !important;
        border-bottom: 3px solid #fb7185 !important;
    }

    [data-testid="stFileUploader"] section {
        background: #151e30 !important;
        border: 1px dashed #546783 !important;
        border-radius: 12px;
    }

    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploader"] button {
        color: #e3eaf5 !important;
    }

    [data-testid="stFileUploader"] button {
        background: #25334b !important;
        border: 1px solid #526582 !important;
    }

    input,
    textarea,
    [data-baseweb="select"] > div {
        color: #f5f7fb !important;
    }

    [data-baseweb="select"] > div {
        background: #18233a !important;
        border-color: #50617d !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 9px;
        min-height: 2.45rem;
        font-weight: 700;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: #93c5fd !important;
    }

    .stButton > button[kind="primary"],
    [data-testid="stBaseButton-primary"] {
        background: #2563eb !important;
        border: 1px solid #60a5fa !important;
        color: white !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: #172033 !important;
        color: #f9fafb !important;
        border: 1px solid #334155 !important;
    }

    section[data-testid="stSidebar"] .stButton > button p,
    section[data-testid="stSidebar"] .stButton > button span {
        color: #f9fafb !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #25334b !important;
        border-color: #60a5fa !important;
    }

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

    hr {
        border-color: #34435e !important;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 2rem !important;
        }

        .workflow-card {
            min-height: auto;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# 2. SHARED HELPERS
# =============================================================================

def format_size(n_bytes: int) -> str:
    """Format a file size for display."""
    size = float(n_bytes)

    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return (
                f"{int(size)} B"
                if unit == "B"
                else f"{size:.1f} {unit}"
            )
        size /= 1024

    return f"{size:.1f} GB"


def file_signature(data: bytes) -> str:
    """Generate a stable identifier for uploaded content."""
    return hashlib.sha256(data).hexdigest()


def output_name(name: str, suffix: str) -> str:
    """Generate an output filename using the uploaded file's stem."""
    stem = re.sub(r"\.[^.]+$", "", name)
    return f"{stem}{suffix}"


def show_file_summary(
    name: str,
    data: bytes,
    details: str = "",
) -> None:
    """Display upload name, size, and optional details."""
    extra = f"<span> • {details}</span>" if details else ""

    st.markdown(
        f"<div class='file-summary'><strong>📎 {name}</strong><br>"
        f"<span>{format_size(len(data))}</span>{extra}</div>",
        unsafe_allow_html=True,
    )


def empty_state(title: str, instructions: str) -> None:
    """Display an empty-state message."""
    st.markdown(
        f"<div class='empty-state'><strong>📂 {title}</strong><br>"
        f"{instructions}</div>",
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, emoji: str) -> None:
    """Display a shared page heading."""
    st.markdown(
        f"<div class='hero-title'>{emoji} {title}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='hero-subtitle'>{subtitle}</div>",
        unsafe_allow_html=True,
    )


def tool_intro(title: str, description: str) -> None:
    """Display a tool heading and explanation."""
    st.markdown(f"### {title}")
    st.markdown(
        f"<p class='muted'>{description}</p>",
        unsafe_allow_html=True,
    )


def save_result(
    key: str,
    source_sig: str,
    data: bytes | str,
    filename: str,
    mime: str,
    kind: str = "",
) -> None:
    """Store the latest result for a specific tool."""
    st.session_state[f"result_{key}"] = {
        "sig": source_sig,
        "data": data,
        "filename": filename,
        "mime": mime,
        "kind": kind,
    }


def show_result(key: str, source_sig: str) -> None:
    """Show a saved preview and download button if the input still matches."""
    result = st.session_state.get(f"result_{key}")

    if not result or result["sig"] != source_sig:
        return

    if result["kind"] == "image":
        st.image(
            result["data"],
            caption="Processed output preview",
            use_container_width=True,
        )
    elif result["kind"] == "text":
        st.text_area(
            "Output preview",
            str(result["data"]),
            height=220,
            key=f"preview_{key}",
        )

    st.download_button(
        "⬇️ Download result",
        data=result["data"],
        file_name=result["filename"],
        mime=result["mime"],
        key=f"download_{key}",
        use_container_width=True,
    )


# =============================================================================
# 3. DOCUMENT HELPERS
# =============================================================================

def pdf_text_pages(data: bytes) -> list[str]:
    """Extract selectable text from each PDF page."""
    with pymupdf.open(stream=data, filetype="pdf") as pdf:
        return [page.get_text("text").strip() for page in pdf]


def pdf_to_markdown(data: bytes) -> str:
    """Convert selectable PDF text into page-separated Markdown."""
    pages = pdf_text_pages(data)

    return "\n\n---\n\n".join(
        f"## Page {index}\n\n"
        f"{text or '_No extractable text on this page._'}"
        for index, text in enumerate(pages, start=1)
    )


def pdf_to_docx_bytes(data: bytes) -> bytes:
    """Create an editable DOCX from extracted PDF text.

    This extracts text rather than reproducing the exact original page layout.
    """
    document = docx.Document()
    pages = pdf_text_pages(data)

    for index, text in enumerate(pages, start=1):
        if index > 1:
            document.add_page_break()

        document.add_heading(f"Page {index}", level=2)
        document.add_paragraph(
            text or "[No extractable text on this page]"
        )

    output = io.BytesIO()
    document.save(output)
    return output.getvalue()


def compress_pdf_bytes(data: bytes) -> bytes:
    """Rewrite PDF streams and remove unused objects where possible."""
    with pymupdf.open(stream=data, filetype="pdf") as pdf:
        output = io.BytesIO()
        pdf.save(
            output,
            garbage=4,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
        )
        return output.getvalue()


def merge_pdf_bytes(files: list[tuple[str, bytes]]) -> bytes:
    """Combine PDF files in the supplied order."""
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
    """Combine uploaded images into a multipage PDF."""
    converted: list[Image.Image] = []

    try:
        for _name, raw in images:
            with Image.open(io.BytesIO(raw)) as image:
                normalized = ImageOps.exif_transpose(image).convert("RGB")
                converted.append(normalized.copy())

        if not converted:
            raise ValueError("Upload at least one supported image.")

        output = io.BytesIO()
        converted[0].save(
            output,
            format="PDF",
            save_all=True,
            append_images=converted[1:],
        )
        return output.getvalue()

    finally:
        for image in converted:
            image.close()


def get_image(raw: bytes) -> Image.Image:
    """Load an image and apply its EXIF orientation."""
    image = Image.open(io.BytesIO(raw))
    image.load()
    return ImageOps.exif_transpose(image)


# =============================================================================
# 4. AUDIO HELPERS
# =============================================================================

AUDIO_LANGUAGE_NAMES = {
    "as": "Assamese",
    "bn": "Bengali",
    "en": "English",
    "gu": "Gujarati",
    "hi": "Hindi",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ne": "Nepali",
    "or": "Odia",
    "pa": "Punjabi",
    "sa": "Sanskrit",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "id": "Indonesian",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "vi": "Vietnamese",
    "th": "Thai",
    "fa": "Persian",
    "pl": "Polish",
}

TRANSCRIPTION_LANGUAGES = {
    "Auto-detect": None,
    "Assamese": "as",
    "Bengali": "bn",
    "English": "en",
    "Gujarati": "gu",
    "Hindi": "hi",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Nepali": "ne",
    "Odia": "or",
    "Punjabi": "pa",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Chinese": "zh",
}

TRANSLATION_LANGUAGES = {
    "English": "en",
    "Assamese": "as",
    "Bengali": "bn",
    "Hindi": "hi",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Nepali": "ne",
    "Odia": "or",
    "Punjabi": "pa",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Arabic": "ar",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
}

# Transliteration conventions used by indic-transliteration.
# These are Latin-letter renderings, not translations.
ROMAN_SCHEMES = {
    "as": "BENGALI",
    "bn": "BENGALI",
    "gu": "GUJARATI",
    "hi": "DEVANAGARI",
    "kn": "KANNADA",
    "ml": "MALAYALAM",
    "mr": "DEVANAGARI",
    "ne": "DEVANAGARI",
    "or": "ORIYA",
    "pa": "GURMUKHI",
    "sa": "DEVANAGARI",
    "ta": "TAMIL",
    "te": "TELUGU",
}


@st.cache_resource(show_spinner=False)
def load_whisper_model(model_size: str):
    """Load a CPU-based Faster-Whisper model only when needed."""
    if WhisperModel is None:
        raise RuntimeError(
            "Faster-Whisper is unavailable. Check requirements.txt."
        )

    return WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8",
    )


def transliterate_to_latin(
    text: str,
    language_code: str,
) -> str | None:
    """Render supported Indic scripts in a Latin transliteration scheme."""
    if not sanscript:
        return None

    scheme_name = ROMAN_SCHEMES.get(language_code)

    if not scheme_name:
        return None

    source_scheme = getattr(sanscript, scheme_name, None)

    if source_scheme is None:
        return None

    try:
        return sanscript.transliterate(
            text,
            source_scheme,
            sanscript.ITRANS,
        )
    except Exception:
        return None


def srt_timestamp(seconds: float) -> str:
    """Format seconds as an SRT timestamp."""
    total_ms = max(0, int(round(seconds * 1000)))

    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)

    return (
        f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    )


def segments_to_srt(segments: list[dict[str, Any]]) -> str:
    """Build timestamped SRT subtitles from recognition segments."""
    blocks = []

    for index, item in enumerate(segments, start=1):
        blocks.append(
            f"{index}\n"
            f"{srt_timestamp(item['start'])} --> "
            f"{srt_timestamp(item['end'])}\n"
            f"{item['text']}"
        )

    return "\n\n".join(blocks) + ("\n" if blocks else "")


def argos_translate_offline(
    text: str,
    from_code: str,
    to_code: str,
) -> str:
    """Translate using an installed Argos model, without a translation API.

    A model might have to be downloaded on first use. The transcript text is
    translated locally by the installed model after it is available.
    """
    if not text.strip():
        raise ValueError("The transcript is empty.")

    if from_code == to_code:
        return text

    if argos_package is None or argos_translate is None:
        raise RuntimeError(
            "Argos Translate is not installed. Check requirements.txt."
        )

    def find_translation():
        languages = argos_translate.get_installed_languages()

        source = next(
            (language for language in languages if language.code == from_code),
            None,
        )
        target = next(
            (language for language in languages if language.code == to_code),
            None,
        )

        if source is None or target is None:
            return None

        try:
            return source.get_translation(target)
        except Exception:
            return None

    translation = find_translation()

    if translation is None:
        try:
            argos_package.update_package_index()
            available = argos_package.get_available_packages()

            match = next(
                (
                    package for package in available
                    if package.from_code == from_code
                    and package.to_code == to_code
                ),
                None,
            )

        except Exception as exc:
            raise RuntimeError(
                f"Could not access the model index: {exc}"
            ) from exc

        if match is None:
            source_name = AUDIO_LANGUAGE_NAMES.get(from_code, from_code)
            target_name = AUDIO_LANGUAGE_NAMES.get(to_code, to_code)

            raise ValueError(
                f"No direct offline model is listed for "
                f"{source_name} → {target_name}. "
                "Try another language pair. The transcript will not be "
                "sent to an online translation API."
            )

        try:
            model_path = match.download()
            argos_package.install_from_path(model_path)
        except Exception as exc:
            raise RuntimeError(
                f"Could not download/install the translation model: {exc}"
            ) from exc

        translation = find_translation()

    if translation is None:
        raise ValueError(
            "The requested offline translation model is unavailable. "
            "Choose another language pair."
        )

    # Process long transcripts in chunks to limit memory usage.
    chunks = []
    remaining = text.strip()

    while len(remaining) > 900:
        cut = max(
            remaining.rfind("\n", 0, 900),
            remaining.rfind(". ", 0, 900),
            remaining.rfind(" ", 0, 900),
        )

        if cut < 250:
            cut = 900

        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()

    if remaining:
        chunks.append(remaining)

    return "\n".join(
        translation.translate(chunk)
        for chunk in chunks
    )


def convert_audio_bytes(
    data: bytes,
    original_name: str,
    target_format: str,
) -> bytes:
    """Convert audio into a different format using FFmpeg."""
    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        raise RuntimeError(
            "FFmpeg is unavailable. Check that packages.txt includes ffmpeg."
        )

    suffix = Path(original_name).suffix.lower() or ".audio"

    encoders = {
        "MP3": (".mp3", ["-codec:a", "libmp3lame", "-q:a", "2"]),
        "WAV": (".wav", ["-codec:a", "pcm_s16le"]),
        "FLAC": (".flac", ["-codec:a", "flac"]),
        "OGG": (".ogg", ["-codec:a", "libvorbis", "-q:a", "5"]),
        "M4A": (
            ".m4a",
            ["-codec:a", "aac", "-b:a", "192k", "-f", "ipod"],
        ),
        "OPUS": (
            ".opus",
            ["-codec:a", "libopus", "-b:a", "128k"],
        ),
    }

    if target_format not in encoders:
        raise ValueError("Unsupported target audio format.")

    output_suffix, codec_args = encoders[target_format]

    with tempfile.TemporaryDirectory(
        prefix="ashutosh_audio_"
    ) as temp_dir:
        input_path = Path(temp_dir) / f"input{suffix}"
        output_path = Path(temp_dir) / f"output{output_suffix}"

        input_path.write_bytes(data)

        command = [
            ffmpeg,
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-i", str(input_path),
            "-vn",
            *codec_args,
            str(output_path),
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "Audio conversion took too long. Try a shorter file."
            ) from exc

        if result.returncode != 0 or not output_path.is_file():
            details = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(
                details[-1200:]
                or "FFmpeg could not convert this audio file."
            )

        return output_path.read_bytes()


# =============================================================================
# 5. SIDEBAR NAVIGATION
# =============================================================================

PAGES = [
    "🏠 Platform Overview",
    "📄 Document Intelligence",
    "🖼️ Media Studio",
    "🎙️ Audio Intelligence",
]

if "active_page" not in st.session_state:
    st.session_state.active_page = PAGES[0]

st.sidebar.markdown("# ⚡ ASHUTOSH STUDIO")

st.sidebar.markdown(
    "<p style='color:#bac8dc !important;font-size:.86rem;line-height:1.6;'>"
    "Engineering & Computational Toolkit<br>"
    "<strong>Ashutosh Borah</strong></p>",
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Workspace Directory")

for index, page_name in enumerate(PAGES):
    if st.sidebar.button(
        page_name,
        key=f"nav_{index}",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.active_page == page_name
            else "secondary"
        ),
    ):
        st.session_state.active_page = page_name
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<span class='status-pill'>● SYSTEM ONLINE</span>",
    unsafe_allow_html=True,
)
st.sidebar.caption("Hosted processing · No account required")


# =============================================================================
# 6. PLATFORM OVERVIEW
# =============================================================================

if st.session_state.active_page == PAGES[0]:
    page_header(
        "Welcome to Ashutosh Studio",
        "A practical workspace for document conversion, document analysis, "
        "image processing, audio transcription, and offline translation.",
        "⚡",
    )

    a, b, c = st.columns(3)
    a.metric("Main workspaces", "3")
    b.metric("Document, media & audio tools", "20+")
    c.metric("Interface", "Responsive")

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown(
            """
            <div class='workflow-card'>
                <h3 style='color:#8bbdff;margin-top:0'>
                    📄 Document Intelligence
                </h3>
                <p>
                    Convert PDFs and Word documents, merge or compress PDFs,
                    create PDFs from images, analyze terms and inspect embedded
                    PDF images.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open Document Intelligence →",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.active_page = PAGES[1]
            st.rerun()

    with right:
        st.markdown(
            """
            <div class='workflow-card'>
                <h3 style='color:#6ee7b7;margin-top:0'>
                    🖼️ Media Studio
                </h3>
                <p>
                    Resize, compress, convert and watermark images.
                    Inspect dimensions and RGB intensity distributions.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open Media Studio →",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.active_page = PAGES[2]
            st.rerun()

    st.markdown(
        """
        <div class='workflow-card'>
            <h3 style='color:#c4b5fd;margin-top:0'>
                🎙️ Audio Intelligence
            </h3>
            <p>
                Transcribe speech in its original language, display Latin-letter
                transliteration where supported, translate only when requested,
                and convert audio formats.
            </p>
            <p>
                <strong>Important:</strong> transcription runs on the hosted
                app. Offline translation uses a local model in that environment.
                Initial model downloads may need an internet connection.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Open Audio Intelligence →",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.active_page = PAGES[3]
        st.rerun()

    st.markdown("### How to use the studio")

    x, y, z = st.columns(3)
    x.markdown("**1 · Upload or record**\n\nChoose a supported file or record a clip.")
    y.markdown("**2 · Process**\n\nSelect a tool and adjust its settings.")
    z.markdown("**3 · Review and download**\n\nCheck the result before downloading it.")

    st.info(
        "Files are processed on the server running this Streamlit app. "
        "Do not upload confidential recordings or documents unless you trust "
        "the hosting environment and its data-handling practices."
    )


# =============================================================================
# 7. DOCUMENT INTELLIGENCE
# =============================================================================

elif st.session_state.active_page == PAGES[1]:
    page_header(
        "Document Intelligence Hub",
        "Convert, combine, compress, analyze, and inspect document files.",
        "📄",
    )

    tabs = st.tabs([
        "PDF → Markdown",
        "PDF → Word",
        "Word → PDF",
        "Merge PDFs",
        "Images → PDF",
        "Compress PDF",
        "Document Analyzer",
        "PDF Asset Inspector",
    ])

    # -------------------------------------------------------------------------
    # PDF to Markdown
    # -------------------------------------------------------------------------

    with tabs[0]:
        tool_intro(
            "Convert PDF to Markdown",
            "Extract selectable text by page and download Markdown. "
            "Scanned pages require OCR, which is not included.",
        )

        uploaded = st.file_uploader(
            "Upload a PDF",
            type=["pdf"],
            key="pdf_md_upload",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = file_signature(data)
            show_file_summary(uploaded.name, data, "PDF document")

            if st.button(
                "Convert to Markdown",
                type="primary",
                key="run_pdf_md",
            ):
                try:
                    save_result(
                        "pdf_md",
                        sig,
                        pdf_to_markdown(data),
                        output_name(uploaded.name, ".md"),
                        "text/markdown",
                        "text",
                    )
                except Exception as exc:
                    st.error(f"Could not read this PDF: {exc}")

            show_result("pdf_md", sig)

        else:
            empty_state(
                "Ready to convert",
                "Upload a PDF with selectable text to create Markdown.",
            )

    # -------------------------------------------------------------------------
    # PDF to Word
    # -------------------------------------------------------------------------

    with tabs[1]:
        tool_intro(
            "Convert PDF to Word",
            "Create an editable DOCX from selectable PDF text. "
            "The layout and embedded images are not reproduced exactly.",
        )

        uploaded = st.file_uploader(
            "Upload a PDF",
            type=["pdf"],
            key="pdf_docx_upload",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = file_signature(data)
            show_file_summary(uploaded.name, data, "PDF document")

            if st.button(
                "Convert to Word",
                type="primary",
                key="run_pdf_docx",
            ):
                try:
                    save_result(
                        "pdf_docx",
                        sig,
                        pdf_to_docx_bytes(data),
                        output_name(uploaded.name, ".docx"),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                except Exception as exc:
                    st.error(f"Could not convert this PDF: {exc}")

            show_result("pdf_docx", sig)

        else:
            empty_state(
                "Ready to convert",
                "Upload a PDF to create an editable Word document.",
            )

    # -------------------------------------------------------------------------
    # Word to PDF — LibreOffice conversion
    # -------------------------------------------------------------------------

    with tabs[2]:
        tool_intro(
            "Convert Word to PDF",
            "Uses LibreOffice to preserve Word formatting, tables, headers, "
            "footers, and embedded images much better than reconstructing text.",
        )

        uploaded = st.file_uploader(
            "Upload a Word document",
            type=["docx"],
            key="docx_pdf_upload",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = file_signature(data)
            show_file_summary(uploaded.name, data, "DOCX document")

            if st.button(
                "Convert to PDF",
                type="primary",
                key="run_docx_pdf",
            ):
                try:
                    converted = libreoffice_docx_to_pdf_bytes(data)

                    save_result(
                        "docx_pdf",
                        sig,
                        converted,
                        output_name(uploaded.name, ".pdf"),
                        "application/pdf",
                    )

                except Exception as exc:
                    st.error(
                        "Could not convert this DOCX. Check that LibreOffice "
                        f"is installed and the file is valid. Details: {exc}"
                    )

            show_result("docx_pdf", sig)

        else:
            empty_state(
                "Ready to convert",
                "Upload a DOCX file to convert it to PDF.",
            )

    # -------------------------------------------------------------------------
    # Merge PDFs
    # -------------------------------------------------------------------------

    with tabs[3]:
        tool_intro(
            "Merge PDFs",
            "Combine several PDF files in the upload order.",
        )

        uploads = st.file_uploader(
            "Select two or more PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            key="merge_pdfs_upload",
        )

        if uploads:
            items = [
                (item.name, item.getvalue())
                for item in uploads
            ]
            sig = file_signature(
                b"".join(
                    name.encode() + b"\0" + data
                    for name, data in items
                )
            )

            st.write(f"Selected files: **{len(items)}**")

            for index, (name, data) in enumerate(items, start=1):
                st.write(
                    f"{index}. {name} — {format_size(len(data))}"
                )

            if st.button(
                "Merge PDFs",
                type="primary",
                key="run_merge_pdfs",
            ):
                try:
                    merged = merge_pdf_bytes(items)

                    save_result(
                        "merge_pdfs",
                        sig,
                        merged,
                        "merged.pdf",
                        "application/pdf",
                    )
                except Exception as exc:
                    st.error(f"Could not merge these PDFs: {exc}")

            show_result("merge_pdfs", sig)

        else:
            empty_state(
                "Ready to merge",
                "Upload multiple PDFs to combine them into one document.",
            )

    # -------------------------------------------------------------------------
    # Images to PDF
    # -------------------------------------------------------------------------

    with tabs[4]:
        tool_intro(
            "Images to PDF",
            "Combine multiple images into a single PDF, one image per page.",
        )

        uploads = st.file_uploader(
            "Select images",
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
            accept_multiple_files=True,
            key="images_pdf_upload",
        )

        if uploads:
            items = [
                (item.name, item.getvalue())
                for item in uploads
            ]

            sig = file_signature(
                b"".join(
                    name.encode() + b"\0" + data
                    for name, data in items
                )
            )

            st.write(f"Selected images: **{len(items)}**")

            for name, data in items:
                st.caption(f"{name} · {format_size(len(data))}")

            if st.button(
                "Create PDF",
                type="primary",
                key="run_images_pdf",
            ):
                try:
                    result = images_to_pdf_bytes(items)

                    save_result(
                        "images_pdf",
                        sig,
                        result,
                        "images.pdf",
                        "application/pdf",
                    )
                except Exception as exc:
                    st.error(f"Could not build the PDF: {exc}")

            show_result("images_pdf", sig)

        else:
            empty_state(
                "Ready to compile",
                "Upload images to compile them into a PDF.",
            )

    # -------------------------------------------------------------------------
    # Compress PDF
    # -------------------------------------------------------------------------

    with tabs[5]:
        tool_intro(
            "Compress PDF",
            "Optimize PDF streams and remove unused objects. "
            "Some already-optimized PDFs may not shrink.",
        )

        uploaded = st.file_uploader(
            "Upload a PDF",
            type=["pdf"],
            key="compress_pdf_upload",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = file_signature(data)
            show_file_summary(uploaded.name, data, "PDF document")

            if st.button(
                "Compress PDF",
                type="primary",
                key="run_compress_pdf",
            ):
                try:
                    compressed = compress_pdf_bytes(data)

                    save_result(
                        "compress_pdf",
                        sig,
                        compressed,
                        output_name(uploaded.name, "_compressed.pdf"),
                        "application/pdf",
                    )

                    difference = len(compressed) - len(data)

                    if difference < 0:
                        st.success(
                            f"Reduced file size by {format_size(-difference)} "
                            f"({-difference / max(len(data), 1) * 100:.1f}%)."
                        )
                    else:
                        st.info(
                            "The file was rewritten, but its size did not decrease."
                        )

                except Exception as exc:
                    st.error(f"Could not compress this PDF: {exc}")

            show_result("compress_pdf", sig)

        else:
            empty_state(
                "Ready to compress",
                "Upload a PDF to optimize its internal structure.",
            )

    # -------------------------------------------------------------------------
    # Document Analyzer
    # -------------------------------------------------------------------------

    with tabs[6]:
        tool_intro(
            "Document Analyzer",
            "View frequent terms, keyword occurrences, a frequency chart, "
            "page-level statistics, and CSV data.",
        )

        uploaded = st.file_uploader(
            "Upload a text-based PDF",
            type=["pdf"],
            key="analyzer_pdf_upload",
        )

        if uploaded:
            data = uploaded.getvalue()
            show_file_summary(uploaded.name, data, "PDF document")

            try:
                pages = pdf_text_pages(data)
                full_text = "\n".join(pages)

                words = re.findall(
                    r"\b[A-Za-z][A-Za-z'-]{2,}\b",
                    full_text.lower(),
                )

                default_stop_words = (
                    "about, after, again, also, among, because, been, before, "
                    "being, between, both, could, does, doing, down, each, "
                    "from, further, have, having, into, itself, just, more, "
                    "most, over, same, should, some, such, than, that, their, "
                    "them, then, there, these, they, this, those, through, "
                    "under, until, very, what, when, where, which, while, "
                    "with, would, your, page, figure, table, using, used, "
                    "based, results, study"
                )

                stop_input = st.text_input(
                    "Additional stop words (comma-separated)",
                    value=default_stop_words,
                    key="analyzer_stop_words",
                )

                stop_words = {
                    term.strip().lower()
                    for term in stop_input.split(",")
                    if term.strip()
                }

                filtered_words = [
                    word for word in words
                    if word not in stop_words
                ]
                counts = Counter(filtered_words)

                top_n = st.slider(
                    "Number of terms to display",
                    min_value=10,
                    max_value=50,
                    value=20,
                    key="analyzer_top_n",
                )

                keyword_query = st.text_input(
                    "Check a keyword or phrase",
                    key="analyzer_keyword_query",
                ).strip().lower()

                total_words = len(
                    re.findall(r"\b\w+\b", full_text)
                )

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Pages", len(pages))
                m2.metric("Words", f"{total_words:,}")
                m3.metric("Unique terms", f"{len(set(filtered_words)):,}")
                m4.metric("Characters", f"{len(full_text):,}")

                if keyword_query:
                    per_page = [
                        page.lower().count(keyword_query)
                        for page in pages
                    ]

                    st.write(
                        f"**Occurrences of '{keyword_query}':** "
                        f"{sum(per_page)}"
                    )

                    st.dataframe(
                        [
                            {"Page": index, "Occurrences": number}
                            for index, number in enumerate(per_page, 1)
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )

                if counts:
                    top_items = counts.most_common(top_n)

                    st.markdown("#### Most frequent meaningful terms")

                    st.dataframe(
                        [
                            {"Term": term, "Frequency": frequency}
                            for term, frequency in top_items
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )

                    fig, ax = plt.subplots(
                        figsize=(9, max(4, top_n * 0.28))
                    )

                    display_items = list(reversed(top_items))

                    ax.barh(
                        [item[0] for item in display_items],
                        [item[1] for item in display_items],
                    )

                    ax.set_xlabel("Occurrences")
                    ax.set_title("Most frequent terms")
                    ax.grid(axis="x", alpha=0.2)
                    fig.tight_layout()

                    st.pyplot(fig, clear_figure=True)
                    plt.close(fig)

                    csv_buffer = io.StringIO()
                    writer = csv.DictWriter(
                        csv_buffer,
                        fieldnames=["Term", "Frequency"],
                    )
                    writer.writeheader()
                    writer.writerows(
                        [
                            {"Term": term, "Frequency": frequency}
                            for term, frequency in counts.most_common()
                        ]
                    )

                    st.download_button(
                        "Download term frequencies (CSV)",
                        csv_buffer.getvalue().encode("utf-8-sig"),
                        output_name(
                            uploaded.name,
                            "_term_frequencies.csv",
                        ),
                        "text/csv",
                        key="download_term_csv",
                    )

                    if st.checkbox(
                        "Generate a word cloud too",
                        key="analyzer_wordcloud_toggle",
                    ):
                        cloud = WordCloud(
                            width=1200,
                            height=600,
                            background_color="#0b1020",
                            colormap="viridis",
                            stopwords=stop_words,
                            collocations=False,
                        ).generate_from_frequencies(dict(counts))

                        cloud_output = io.BytesIO()
                        cloud.to_image().save(cloud_output, format="PNG")
                        cloud_bytes = cloud_output.getvalue()

                        st.image(
                            cloud_bytes,
                            caption=(
                                "Larger words appear more frequently; "
                                "use the table for exact counts."
                            ),
                            use_container_width=True,
                        )

                        st.download_button(
                            "Download word cloud (PNG)",
                            cloud_bytes,
                            output_name(uploaded.name, "_wordcloud.png"),
                            "image/png",
                            key="download_wordcloud_png",
                        )

                else:
                    st.warning(
                        "No analyzable text was found. This may be a scanned "
                        "PDF or a document with very little text."
                    )

                with st.expander("Page-by-page text statistics"):
                    stats = []

                    for index, page_text in enumerate(pages, 1):
                        stats.append({
                            "Page": index,
                            "Words": len(
                                re.findall(r"\b\w+\b", page_text)
                            ),
                            "Characters": len(page_text),
                            "Extracted text": page_text[:240].replace(
                                "\n", " "
                            ),
                        })

                    st.dataframe(
                        stats,
                        use_container_width=True,
                        hide_index=True,
                    )

            except Exception as exc:
                st.error(f"Could not analyze this PDF: {exc}")

        else:
            empty_state(
                "Ready to analyze",
                "Upload a PDF to inspect term frequencies and page statistics.",
            )

    # -------------------------------------------------------------------------
    # PDF Asset Inspector
    # -------------------------------------------------------------------------

    with tabs[7]:
        tool_intro(
            "PDF Asset Inspector",
            "Inspect embedded raster images with page numbers, dimensions, "
            "formats, and file sizes. Vector drawings may not appear as standalone "
            "raster images.",
        )

        uploaded = st.file_uploader(
            "Upload a PDF",
            type=["pdf"],
            key="asset_pdf_upload",
        )

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

                                assets.append({
                                    "label": (
                                        f"Page {page_number} · xref {xref} · "
                                        f"{extracted.get('width', '?')}×"
                                        f"{extracted.get('height', '?')}"
                                    ),
                                    "page": page_number,
                                    "xref": xref,
                                    "width": extracted.get("width", 0),
                                    "height": extracted.get("height", 0),
                                    "format": extracted.get("ext", "bin").upper(),
                                    "bytes": len(image_data),
                                    "data": image_data,
                                })

                            except Exception:
                                continue

                if not assets:
                    st.info(
                        "No embedded raster images were found. This PDF may "
                        "contain vector drawings or full-page scanned content."
                    )

                else:
                    st.success(
                        f"Found {len(assets)} embedded image occurrence(s)."
                    )

                    st.dataframe(
                        [
                            {
                                "Asset": item["label"],
                                "Page": item["page"],
                                "Width (px)": item["width"],
                                "Height (px)": item["height"],
                                "Format": item["format"],
                                "File size": format_size(item["bytes"]),
                            }
                            for item in assets
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )

                    chosen = st.multiselect(
                        "Choose images to export",
                        options=[item["label"] for item in assets],
                        default=[item["label"] for item in assets],
                        key="chosen_pdf_assets",
                    )

                    selected = [
                        item for item in assets
                        if item["label"] in chosen
                    ]

                    if selected:
                        preview_columns = st.columns(
                            min(3, len(selected))
                        )

                        for index, item in enumerate(selected[:6]):
                            with preview_columns[
                                index % len(preview_columns)
                            ]:
                                st.caption(item["label"])

                                try:
                                    st.image(
                                        item["data"],
                                        use_container_width=True,
                                    )
                                except Exception:
                                    st.caption("Preview unavailable.")

                        zip_output = io.BytesIO()

                        with zipfile.ZipFile(
                            zip_output,
                            "w",
                            zipfile.ZIP_DEFLATED,
                        ) as archive:
                            for index, item in enumerate(selected, 1):
                                extension = (
                                    item["format"]
                                    .lower()
                                    .replace("jpeg", "jpg")
                                )

                                archive.writestr(
                                    f"page_{item['page']}_image_{index}_"
                                    f"xref_{item['xref']}.{extension}",
                                    item["data"],
                                )

                        st.download_button(
                            "Download selected assets (ZIP)",
                            zip_output.getvalue(),
                            output_name(uploaded.name, "_assets.zip"),
                            "application/zip",
                            key="download_assets_zip",
                        )

                        for index, item in enumerate(selected, 1):
                            extension = (
                                item["format"]
                                .lower()
                                .replace("jpeg", "jpg")
                            )

                            st.download_button(
                                f"Download image {index} — Page {item['page']}",
                                item["data"],
                                f"page_{item['page']}_image_{index}.{extension}",
                                "application/octet-stream",
                                key=f"download_asset_{index}_{item['xref']}",
                            )

            except Exception as exc:
                st.error(f"Could not inspect this PDF: {exc}")

        else:
            empty_state(
                "Ready to inspect",
                "Upload a PDF to inspect and export its embedded images.",
            )


# =============================================================================
# 8. MEDIA STUDIO
# =============================================================================

elif st.session_state.active_page == PAGES[2]:
    page_header(
        "Media Studio",
        "Compress, resize, convert, watermark, and analyze images.",
        "🖼️",
    )

    tabs = st.tabs([
        "Resize",
        "JPEG Compress",
        "Grayscale",
        "Crop",
        "Rotate & Flip",
        "Convert Format",
        "Watermark",
        "Image Analysis",
    ])

    IMAGE_TYPES = [
        "png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"
    ]

    # -------------------------------------------------------------------------
    # Resize
    # -------------------------------------------------------------------------

    with tabs[0]:
        tool_intro(
            "Resize image",
            "Set new dimensions and optionally preserve the aspect ratio.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=IMAGE_TYPES,
            key="resize_upload",
        )

        if uploaded:
            raw = uploaded.getvalue()
            sig = file_signature(raw)

            try:
                image = get_image(raw)
                show_file_summary(
                    uploaded.name,
                    raw,
                    f"{image.width} × {image.height} px",
                )

                st.image(
                    image,
                    caption="Original image",
                    use_container_width=True,
                )

                preserve = st.checkbox(
                    "Preserve aspect ratio",
                    value=True,
                    key="resize_preserve",
                )

                col1, col2 = st.columns(2)

                width = col1.number_input(
                    "Output width (px)",
                    1,
                    12000,
                    int(image.width),
                    key="resize_width",
                )
                height = col2.number_input(
                    "Output height (px)",
                    1,
                    12000,
                    int(image.height),
                    key="resize_height",
                )

                if st.button(
                    "Resize image",
                    type="primary",
                    key="run_resize",
                ):
                    new_size = (int(width), int(height))

                    if preserve:
                        result_image = image.copy()
                        result_image.thumbnail(
                            new_size,
                            Image.Resampling.LANCZOS,
                        )
                    else:
                        result_image = image.resize(
                            new_size,
                            Image.Resampling.LANCZOS,
                        )

                    image_format = (
                        "PNG"
                        if "A" in result_image.getbands()
                        else "JPEG"
                    )

                    if image_format == "JPEG":
                        result_image = result_image.convert("RGB")

                    output = io.BytesIO()
                    result_image.save(
                        output,
                        format=image_format,
                        quality=92,
                    )

                    save_result(
                        "resize",
                        sig,
                        output.getvalue(),
                        output_name(
                            uploaded.name,
                            f"_resized.{image_format.lower()}",
                        ),
                        f"image/{image_format.lower()}",
                        "image",
                    )

                show_result("resize", sig)

            except Exception as exc:
                st.error(f"Could not resize this image: {exc}")

    # -------------------------------------------------------------------------
    # JPEG compression
    # -------------------------------------------------------------------------

    with tabs[1]:
        tool_intro(
            "Compress to JPEG",
            "JPEG is lossy and does not support transparency. Transparent "
            "pixels are placed on a white background.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=IMAGE_TYPES,
            key="jpeg_upload",
        )

        if uploaded:
            raw = uploaded.getvalue()
            sig = file_signature(raw)

            try:
                image = get_image(raw).convert("RGB")

                show_file_summary(
                    uploaded.name,
                    raw,
                    f"{image.width} × {image.height} px",
                )

                quality = st.slider(
                    "JPEG quality",
                    20,
                    95,
                    78,
                    key="jpeg_quality",
                )

                if st.button(
                    "Compress image",
                    type="primary",
                    key="run_jpeg",
                ):
                    output = io.BytesIO()
                    image.save(
                        output,
                        format="JPEG",
                        quality=quality,
                        optimize=True,
                        progressive=True,
                    )

                    result_data = output.getvalue()

                    save_result(
                        "jpeg",
                        sig,
                        result_data,
                        output_name(uploaded.name, "_compressed.jpg"),
                        "image/jpeg",
                        "image",
                    )

                    st.caption(
                        f"Original: {format_size(len(raw))} · "
                        f"Output: {format_size(len(result_data))}"
                    )

                show_result("jpeg", sig)

            except Exception as exc:
                st.error(f"Could not compress this image: {exc}")

    # -------------------------------------------------------------------------
    # Grayscale
    # -------------------------------------------------------------------------

    with tabs[2]:
        tool_intro(
            "Convert to grayscale",
            "Create a grayscale version of a colour image.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=IMAGE_TYPES,
            key="gray_upload",
        )

        if uploaded:
            raw = uploaded.getvalue()
            sig = file_signature(raw)

            try:
                image = get_image(raw)

                if st.button(
                    "Convert to grayscale",
                    type="primary",
                    key="run_gray",
                ):
                    result_image = ImageOps.grayscale(image)
                    output = io.BytesIO()
                    result_image.save(output, format="PNG")

                    save_result(
                        "gray",
                        sig,
                        output.getvalue(),
                        output_name(uploaded.name, "_grayscale.png"),
                        "image/png",
                        "image",
                    )

                show_result("gray", sig)

            except Exception as exc:
                st.error(f"Could not convert this image: {exc}")

    # -------------------------------------------------------------------------
    # Crop
    # -------------------------------------------------------------------------

    with tabs[3]:
        tool_intro(
            "Crop image",
            "Adjust crop margins as percentages of the original dimensions.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=IMAGE_TYPES,
            key="crop_upload",
        )

        if uploaded:
            raw = uploaded.getvalue()
            sig = file_signature(raw)

            try:
                image = get_image(raw)

                col1, col2 = st.columns(2)
                col3, col4 = st.columns(2)

                left = col1.slider("Left margin %", 0, 90, 0, key="crop_left")
                right = col2.slider("Right margin %", 0, 90, 0, key="crop_right")
                top = col3.slider("Top margin %", 0, 90, 0, key="crop_top")
                bottom = col4.slider("Bottom margin %", 0, 90, 0, key="crop_bottom")

                if st.button(
                    "Crop image",
                    type="primary",
                    key="run_crop",
                ):
                    x1 = int(image.width * left / 100)
                    y1 = int(image.height * top / 100)
                    x2 = int(image.width * (100 - right) / 100)
                    y2 = int(image.height * (100 - bottom) / 100)

                    if x2 <= x1 or y2 <= y1:
                        st.error(
                            "The crop margins remove the entire image. "
                            "Reduce the margins and try again."
                        )
                    else:
                        result_image = image.crop((x1, y1, x2, y2))
                        has_alpha = "A" in result_image.getbands()
                        image_format = "PNG" if has_alpha else "JPEG"

                        if image_format == "JPEG":
                            result_image = result_image.convert("RGB")

                        output = io.BytesIO()
                        result_image.save(
                            output,
                            format=image_format,
                            quality=92,
                        )

                        save_result(
                            "crop",
                            sig,
                            output.getvalue(),
                            output_name(
                                uploaded.name,
                                f"_cropped.{image_format.lower()}",
                            ),
                            f"image/{image_format.lower()}",
                            "image",
                        )

                show_result("crop", sig)

            except Exception as exc:
                st.error(f"Could not crop this image: {exc}")

    # -------------------------------------------------------------------------
    # Rotate and flip
    # -------------------------------------------------------------------------

    with tabs[4]:
        tool_intro(
            "Rotate and flip",
            "Rotate by 90-degree increments or flip horizontally or vertically.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=IMAGE_TYPES,
            key="rotate_upload",
        )

        if uploaded:
            raw = uploaded.getvalue()
            sig = file_signature(raw)

            try:
                image = get_image(raw)

                rotation = st.selectbox(
                    "Rotation",
                    [0, 90, 180, 270],
                    format_func=lambda value: f"{value}°",
                    key="rotation_degrees",
                )

                flip = st.selectbox(
                    "Flip",
                    ["None", "Horizontal", "Vertical"],
                    key="rotation_flip",
                )

                if st.button(
                    "Apply transform",
                    type="primary",
                    key="run_rotate",
                ):
                    result_image = image.rotate(-rotation, expand=True)

                    if flip == "Horizontal":
                        result_image = ImageOps.mirror(result_image)
                    elif flip == "Vertical":
                        result_image = ImageOps.flip(result_image)

                    image_format = (
                        "PNG"
                        if "A" in result_image.getbands()
                        else "JPEG"
                    )

                    if image_format == "JPEG":
                        result_image = result_image.convert("RGB")

                    output = io.BytesIO()
                    result_image.save(
                        output,
                        format=image_format,
                        quality=92,
                    )

                    save_result(
                        "rotate",
                        sig,
                        output.getvalue(),
                        output_name(
                            uploaded.name,
                            f"_transformed.{image_format.lower()}",
                        ),
                        f"image/{image_format.lower()}",
                        "image",
                    )

                show_result("rotate", sig)

            except Exception as exc:
                st.error(f"Could not transform this image: {exc}")

    # -------------------------------------------------------------------------
    # Format conversion
    # -------------------------------------------------------------------------

    with tabs[5]:
        tool_intro(
            "Convert image format",
            "Convert images to PNG, JPEG, or WEBP. JPEG requires a solid "
            "background because it does not support transparency.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=IMAGE_TYPES,
            key="format_upload",
        )

        if uploaded:
            raw = uploaded.getvalue()
            sig = file_signature(raw)

            try:
                image = get_image(raw)

                target = st.selectbox(
                    "Target format",
                    ["PNG", "JPEG", "WEBP"],
                    key="target_image_format",
                )

                quality = st.slider(
                    "Quality (JPEG/WEBP)",
                    30,
                    100,
                    88,
                    key="target_image_quality",
                )

                if st.button(
                    "Convert format",
                    type="primary",
                    key="run_format",
                ):
                    if target == "JPEG":
                        background = Image.new(
                            "RGB",
                            image.size,
                            "white",
                        )

                        if "A" in image.getbands():
                            background.paste(
                                image,
                                mask=image.getchannel("A"),
                            )
                        else:
                            background.paste(image.convert("RGB"))

                        result_image = background

                    else:
                        result_image = image.copy()

                        if (
                            target == "PNG"
                            and result_image.mode
                            not in ("RGB", "RGBA", "L", "LA", "P")
                        ):
                            result_image = result_image.convert("RGBA")

                    output = io.BytesIO()
                    save_options = {"format": target}

                    if target in ("JPEG", "WEBP"):
                        save_options["quality"] = quality

                    result_image.save(output, **save_options)

                    extension = target.lower().replace("jpeg", "jpg")
                    mime_subtype = (
                        "jpeg" if target == "JPEG" else extension
                    )

                    save_result(
                        "format",
                        sig,
                        output.getvalue(),
                        output_name(
                            uploaded.name,
                            f"_converted.{extension}",
                        ),
                        f"image/{mime_subtype}",
                        "image",
                    )

                show_result("format", sig)

            except Exception as exc:
                st.error(f"Could not convert this image: {exc}")

    # -------------------------------------------------------------------------
    # Watermark
    # -------------------------------------------------------------------------

    with tabs[6]:
        tool_intro(
            "Add a text watermark",
            "Place a text watermark on your image and download the result.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=IMAGE_TYPES,
            key="watermark_upload",
        )

        if uploaded:
            raw = uploaded.getvalue()
            sig = file_signature(raw)

            try:
                image = get_image(raw).convert("RGBA")

                watermark = st.text_input(
                    "Watermark text",
                    value="Ashutosh Studio",
                    key="watermark_text",
                )

                opacity = st.slider(
                    "Opacity",
                    20,
                    255,
                    150,
                    key="watermark_opacity",
                )

                position = st.selectbox(
                    "Position",
                    [
                        "Bottom right",
                        "Bottom left",
                        "Top right",
                        "Top left",
                        "Center",
                    ],
                    key="watermark_position",
                )

                if st.button(
                    "Apply watermark",
                    type="primary",
                    key="run_watermark",
                ):
                    if not watermark.strip():
                        st.error("Enter some watermark text first.")
                    else:
                        overlay = Image.new(
                            "RGBA",
                            image.size,
                            (0, 0, 0, 0),
                        )
                        draw = ImageDraw.Draw(overlay)

                        font_size = max(14, image.width // 32)

                        try:
                            font = ImageFont.truetype(
                                "DejaVuSans.ttf",
                                font_size,
                            )
                        except OSError:
                            font = ImageFont.load_default()

                        bbox = draw.textbbox(
                            (0, 0),
                            watermark,
                            font=font,
                            stroke_width=1,
                        )

                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        margin = max(10, image.width // 40)

                        positions = {
                            "Bottom right": (
                                image.width - text_width - margin,
                                image.height - text_height - margin,
                            ),
                            "Bottom left": (
                                margin,
                                image.height - text_height - margin,
                            ),
                            "Top right": (
                                image.width - text_width - margin,
                                margin,
                            ),
                            "Top left": (margin, margin),
                            "Center": (
                                (image.width - text_width) // 2,
                                (image.height - text_height) // 2,
                            ),
                        }

                        draw.text(
                            positions[position],
                            watermark,
                            font=font,
                            fill=(255, 255, 255, opacity),
                            stroke_width=2,
                            stroke_fill=(0, 0, 0, min(220, opacity)),
                        )

                        result_image = Image.alpha_composite(
                            image,
                            overlay,
                        )

                        output = io.BytesIO()
                        result_image.save(output, format="PNG")

                        save_result(
                            "watermark",
                            sig,
                            output.getvalue(),
                            output_name(
                                uploaded.name,
                                "_watermarked.png",
                            ),
                            "image/png",
                            "image",
                        )

                show_result("watermark", sig)

            except Exception as exc:
                st.error(f"Could not add watermark: {exc}")

    # -------------------------------------------------------------------------
    # Image analysis
    # -------------------------------------------------------------------------

    with tabs[7]:
        tool_intro(
            "Image analysis",
            "Review dimensions, file size, and RGB intensity distributions.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=IMAGE_TYPES,
            key="analysis_upload",
        )

        if uploaded:
            raw = uploaded.getvalue()

            try:
                image = get_image(raw).convert("RGB")

                col1, col2, col3 = st.columns(3)
                col1.metric("Width", f"{image.width:,} px")
                col2.metric("Height", f"{image.height:,} px")
                col3.metric("File size", format_size(len(raw)))

                st.image(
                    image,
                    caption=uploaded.name,
                    use_container_width=True,
                )

                array = np.asarray(image)
                fig, ax = plt.subplots(figsize=(9, 4))

                for channel, label in enumerate(
                    ["Red", "Green", "Blue"]
                ):
                    counts, bins = np.histogram(
                        array[:, :, channel],
                        bins=256,
                        range=(0, 256),
                    )
                    ax.plot(bins[:-1], counts, label=label)

                ax.set_title("RGB intensity distribution")
                ax.set_xlabel("Pixel intensity (0–255)")
                ax.set_ylabel("Pixel count")
                ax.legend()
                ax.grid(alpha=0.2)
                fig.tight_layout()

                st.pyplot(fig, clear_figure=True)
                plt.close(fig)

            except Exception as exc:
                st.error(f"Could not analyze this image: {exc}")


# =============================================================================
# 9. AUDIO INTELLIGENCE — VERBATIM-FIRST WORKFLOW
# =============================================================================

elif st.session_state.active_page == PAGES[3]:
    page_header(
        "Audio Intelligence",
        "Capture speech, preserve the original words, display Latin-letter "
        "transliteration where supported, and translate only when requested.",
        "🎙️",
    )

    st.info(
        "Workflow: transcribe the spoken language first → display a "
        "Latin-letter rendering where supported → translate separately "
        "when requested. The app does not deliberately rewrite or polish "
        "the transcript. Speech recognition can still make mistakes."
    )

    st.warning(
        "Privacy: recordings are uploaded to the Streamlit hosting environment "
        "for processing. Offline translation runs with a local model after it "
        "is available. Initial translation-model downloads need an internet "
        "connection. Avoid uploading sensitive recordings unless you trust "
        "the hosting environment."
    )

    audio_tabs = st.tabs([
        "Transcribe & Translate",
        "Convert Audio Format",
    ])

    # -------------------------------------------------------------------------
    # Speech-to-text, transliteration, optional translation
    # -------------------------------------------------------------------------

    with audio_tabs[0]:
        st.subheader("Step 1 — Provide audio")

        input_mode = st.radio(
            "Audio source",
            ["Upload audio file", "Record with microphone"],
            horizontal=True,
            key="audio_input_mode",
        )

        audio_data = None
        audio_name = "recording.wav"

        if input_mode == "Upload audio file":
            audio_file = st.file_uploader(
                "Upload a WhatsApp voice note or audio file",
                type=[
                    "mp3", "wav", "m4a", "aac", "ogg", "oga",
                    "opus", "flac", "webm", "mp4", "3gp",
                ],
                key="audio_transcribe_upload",
            )

            if audio_file is not None:
                audio_data = audio_file.getvalue()
                audio_name = audio_file.name

        elif hasattr(st, "audio_input"):
            recorded_audio = st.audio_input(
                "Record a voice note",
                key="audio_microphone_recording",
            )

            if recorded_audio is not None:
                audio_data = recorded_audio.getvalue()
                audio_name = "microphone_recording.wav"

        else:
            st.error(
                "Microphone recording is unavailable in this Streamlit "
                "version. Upload an audio file instead."
            )

        if audio_data:
            audio_sig = file_signature(audio_data)

            show_file_summary(
                audio_name,
                audio_data,
                "Audio input",
            )
            st.audio(audio_data)

            language_choice = st.selectbox(
                "Spoken language",
                list(TRANSCRIPTION_LANGUAGES.keys()),
                index=0,
                help=(
                    "Select Auto-detect or choose the actual spoken language. "
                    "Transcription is requested in the spoken language, "
                    "not translated into English."
                ),
                key="audio_speech_language",
            )

            model_choice = st.selectbox(
                "Speech recognition model",
                ["tiny", "base", "small"],
                index=1,
                help=(
                    "Tiny is faster. Base is a practical starting point. "
                    "Small can improve accuracy but needs more processing time."
                ),
                key="audio_whisper_model_size",
            )

            st.caption(
                "For a long recording, start with Tiny or Base. "
                "The first run may download a speech model."
            )

            if st.button(
                "1. Transcribe original speech",
                type="primary",
                key="run_audio_transcription",
                use_container_width=True,
            ):
                if WhisperModel is None:
                    st.error(
                        "Faster-Whisper is unavailable. Check requirements.txt "
                        "and the Streamlit installation logs."
                    )

                elif len(audio_data) > 50 * 1024 * 1024:
                    st.error(
                        "This file exceeds 50 MB. Try a smaller or shorter "
                        "audio file to reduce memory and processing time."
                    )

                else:
                    temporary_filename = None

                    try:
                        with st.spinner(
                            "Transcribing the original spoken language. "
                            "First use may download the speech model..."
                        ):
                            model = load_whisper_model(model_choice)
                            suffix = Path(audio_name).suffix.lower() or ".wav"

                            with tempfile.NamedTemporaryFile(
                                delete=False,
                                suffix=suffix,
                            ) as temporary_audio:
                                temporary_audio.write(audio_data)
                                temporary_filename = temporary_audio.name

                            selected_language = TRANSCRIPTION_LANGUAGES[
                                language_choice
                            ]

                            # Explicitly request transcription, not English translation.
                            segments_iterator, info = model.transcribe(
                                temporary_filename,
                                task="transcribe",
                                language=selected_language,
                                beam_size=5,
                                vad_filter=True,
                                condition_on_previous_text=False,
                                initial_prompt=(
                                    "Transcribe the speech in its original language. "
                                    "Preserve the speaker's words, repetitions, "
                                    "filler words and incomplete phrases when audible. "
                                    "Do not translate or rewrite the speech."
                                ),
                            )

                            segments = [
                                {
                                    "start": float(segment.start),
                                    "end": float(segment.end),
                                    "text": segment.text.strip(),
                                }
                                for segment in segments_iterator
                                if segment.text.strip()
                            ]

                            transcript = " ".join(
                                segment["text"]
                                for segment in segments
                            ).strip()

                        if not transcript:
                            st.warning(
                                "No speech was detected. Try selecting the "
                                "spoken language manually or using another model."
                            )

                        else:
                            st.session_state["audio_transcript_result"] = {
                                "sig": audio_sig,
                                "language": info.language,
                                "language_probability": float(
                                    getattr(
                                        info,
                                        "language_probability",
                                        0.0,
                                    ) or 0.0
                                ),
                                "segments": segments,
                                "text": transcript,
                                "translation": None,
                                "translation_target": None,
                                "translation_source": None,
                                "audio_name": audio_name,
                            }

                            st.success(
                                "Transcription completed. Check the result "
                                "against your recording before using it."
                            )

                    except Exception as exc:
                        st.error(f"Transcription failed: {exc}")

                    finally:
                        if (
                            temporary_filename
                            and os.path.exists(temporary_filename)
                        ):
                            try:
                                os.remove(temporary_filename)
                            except OSError:
                                pass

            result = st.session_state.get("audio_transcript_result")

            if result and result.get("sig") == audio_sig:
                detected_code = result.get("language", "")
                detected_name = AUDIO_LANGUAGE_NAMES.get(
                    detected_code,
                    detected_code or "Unknown",
                )

                metric1, metric2 = st.columns(2)
                metric1.metric("Detected language", detected_name)
                metric2.metric(
                    "Detection confidence",
                    f"{result.get('language_probability', 0.0) * 100:.0f}%",
                )

                # -------------------------------------------------------------
                # Original-language transcript
                # -------------------------------------------------------------

                st.divider()
                st.subheader("Step 2 — Original-language transcript")

                st.caption(
                    "This is the speech recognizer's transcript, not a "
                    "translation. Recognition systems can still normalize "
                    "punctuation or miss repeated words, so review it carefully."
                )

                transcript_key = f"verbatim_transcript_{audio_sig[:12]}"

                edited_text = st.text_area(
                    "Original transcript — editable",
                    value=result.get("text", ""),
                    height=220,
                    key=transcript_key,
                    help=(
                        "Correct recognition mistakes here. This transcript "
                        "remains separate from any translation."
                    ),
                )

                # If the user edits text, never continue showing a translation
                # that was created from the earlier version.
                if edited_text != result.get("translation_source"):
                    result["translation"] = None
                    result["translation_target"] = None
                    result["translation_source"] = None
                    st.session_state["audio_transcript_result"] = result

                # -------------------------------------------------------------
                # Transliteration into Latin/English letters
                # -------------------------------------------------------------

                st.subheader("Step 3 — Latin-letter transliteration")

                romanized = transliterate_to_latin(
                    edited_text,
                    detected_code,
                )

                if detected_code == "en":
                    romanized = edited_text

                if romanized is not None:
                    st.text_area(
                        "Same-language text written in Latin letters",
                        value=romanized,
                        height=180,
                        disabled=True,
                        key=f"romanized_transcript_{audio_sig[:12]}",
                        help=(
                            "This represents the spoken language using Latin "
                            "letters. It does not translate the meaning into English."
                        ),
                    )

                    st.caption(
                        "Transliteration uses the library's phonetic/ITRANS-style "
                        "convention. It may differ from informal chat spellings. "
                        "Unsupported scripts are not fabricated."
                    )

                else:
                    st.info(
                        f"Latin-letter transliteration is not configured for "
                        f"{detected_name}. The original transcript remains available."
                    )
                    romanized = ""

                # -------------------------------------------------------------
                # Optional translation
                # -------------------------------------------------------------

                st.subheader("Step 4 — Optional translation")

                target_names = list(TRANSLATION_LANGUAGES.keys())

                target_name = st.selectbox(
                    "Choose the language to translate into",
                    target_names,
                    index=target_names.index("English"),
                    key=f"audio_target_{audio_sig[:12]}",
                )

                st.caption(
                    "Translation occurs only after you press the button. "
                    "It uses Argos models when available. Unsupported language "
                    "pairs will be reported; there is no online-API fallback."
                )

                if st.button(
                    "2. Translate transcript",
                    type="primary",
                    key=f"run_audio_translate_{audio_sig[:12]}",
                    use_container_width=True,
                ):
                    try:
                        with st.spinner(
                            "Preparing the offline translation model if needed..."
                        ):
                            translated_text = argos_translate_offline(
                                edited_text,
                                detected_code,
                                TRANSLATION_LANGUAGES[target_name],
                            )

                        result["translation"] = translated_text
                        result["translation_target"] = (
                            TRANSLATION_LANGUAGES[target_name]
                        )
                        result["translation_source"] = edited_text

                        st.session_state["audio_transcript_result"] = result
                        st.success("Offline translation completed.")

                    except Exception as exc:
                        st.error(
                            f"Offline translation unavailable: {exc}"
                        )

                if (
                    result.get("translation") is not None
                    and result.get("translation_target")
                    == TRANSLATION_LANGUAGES[target_name]
                    and result.get("translation_source") == edited_text
                ):
                    st.text_area(
                        f"Translation — {target_name}",
                        value=result["translation"],
                        height=220,
                        key=(
                            f"translation_preview_{audio_sig[:12]}_"
                            f"{target_name}"
                        ),
                    )

                # -------------------------------------------------------------
                # Optional basic transcript analysis
                # -------------------------------------------------------------

                with st.expander("Optional — Analyze transcript"):
                    words = re.findall(
                        r"\b[\w'-]+\b",
                        edited_text,
                        flags=re.UNICODE,
                    )

                    sentences = [
                        sentence
                        for sentence in re.split(
                            r"(?<=[.!?।])\s+",
                            edited_text.strip(),
                        )
                        if sentence
                    ]

                    common_words_to_skip = {
                        "the", "and", "for", "that", "this", "with",
                        "you", "are", "was", "were", "have", "has",
                        "had", "but", "not", "from", "your", "its",
                        "into", "then",
                    }

                    counts = Counter(
                        word.casefold()
                        for word in words
                        if len(word) > 2
                        and word.casefold() not in common_words_to_skip
                    )

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Words", len(words))
                    col2.metric("Sentences", len(sentences))
                    col3.metric(
                        "Unique words",
                        len(set(word.casefold() for word in words)),
                    )

                    if counts:
                        st.write("Most frequent terms:")

                        st.dataframe(
                            [
                                {"Term": word, "Count": number}
                                for word, number in counts.most_common(10)
                            ],
                            use_container_width=True,
                            hide_index=True,
                        )

                    st.caption(
                        "This is basic term-frequency analysis, not "
                        "AI-generated interpretation or summarization."
                    )

                # -------------------------------------------------------------
                # Download original, transliteration and optional translation
                # -------------------------------------------------------------

                st.subheader("Step 5 — Download results")

                text_parts = [
                    f"Detected language: {detected_name}",
                    "",
                    "ORIGINAL-LANGUAGE TRANSCRIPT",
                    edited_text,
                    "",
                    "LATIN-LETTER TRANSLITERATION",
                    romanized or "Not available for this language.",
                ]

                current_translation = result.get("translation")

                if (
                    current_translation
                    and result.get("translation_source") == edited_text
                ):
                    target_code = result.get("translation_target")
                    target_label = AUDIO_LANGUAGE_NAMES.get(
                        target_code,
                        target_code,
                    )

                    text_parts.extend([
                        "",
                        f"TRANSLATION ({target_label})",
                        current_translation,
                    ])

                st.download_button(
                    "Download transcript package (TXT)",
                    data="\n".join(text_parts).encode("utf-8"),
                    file_name=output_name(
                        Path(audio_name).name,
                        "_transcript.txt",
                    ),
                    mime="text/plain; charset=utf-8",
                    key=f"download_transcript_{audio_sig[:12]}",
                    use_container_width=True,
                )

                # SRT uses the original recognition segments so timestamps
                # remain aligned with the audio.
                srt_data = segments_to_srt(
                    result.get("segments", [])
                )

                if srt_data:
                    st.download_button(
                        "Download timestamped subtitles (SRT)",
                        data=srt_data.encode("utf-8"),
                        file_name=output_name(
                            Path(audio_name).name,
                            ".srt",
                        ),
                        mime="application/x-subrip",
                        key=f"download_srt_{audio_sig[:12]}",
                        use_container_width=True,
                    )

        else:
            empty_state(
                "Ready for audio",
                "Upload a WhatsApp voice note or audio file, or record a "
                "short clip with your microphone. Transcribe the original "
                "speech first, then choose whether to translate it.",
            )

    # -------------------------------------------------------------------------
    # Audio format conversion
    # -------------------------------------------------------------------------

    with audio_tabs[1]:
        tool_intro(
            "Convert audio format",
            "Convert MP3, WAV, FLAC, OGG, M4A, and OPUS using FFmpeg. "
            "Format conversion does not transcribe or translate speech.",
        )

        uploaded_audio = st.file_uploader(
            "Upload audio to convert",
            type=[
                "mp3", "wav", "m4a", "aac", "ogg", "oga",
                "opus", "flac", "webm", "mp4", "3gp",
            ],
            key="audio_convert_upload",
        )

        if uploaded_audio:
            raw_audio = uploaded_audio.getvalue()
            convert_sig = file_signature(raw_audio)

            show_file_summary(
                uploaded_audio.name,
                raw_audio,
                "Audio conversion input",
            )

            st.audio(raw_audio)

            output_format = st.selectbox(
                "Output format",
                ["MP3", "WAV", "FLAC", "OGG", "M4A", "OPUS"],
                key="audio_output_format",
            )

            if st.button(
                "Convert audio",
                type="primary",
                key="run_audio_convert",
                use_container_width=True,
            ):
                if len(raw_audio) > 100 * 1024 * 1024:
                    st.error(
                        "This file exceeds 100 MB. Upload a smaller "
                        "or shorter audio file."
                    )

                else:
                    try:
                        with st.spinner("Converting audio with FFmpeg..."):
                            output_audio = convert_audio_bytes(
                                raw_audio,
                                uploaded_audio.name,
                                output_format,
                            )

                        extension = {
                            "MP3": ".mp3",
                            "WAV": ".wav",
                            "FLAC": ".flac",
                            "OGG": ".ogg",
                            "M4A": ".m4a",
                            "OPUS": ".opus",
                        }[output_format]

                        st.session_state["audio_conversion_result"] = {
                            "sig": convert_sig,
                            "data": output_audio,
                            "filename": output_name(
                                uploaded_audio.name,
                                f"_converted{extension}",
                            ),
                            "format": output_format,
                        }

                        st.success(
                            f"Conversion completed: "
                            f"{format_size(len(raw_audio))} → "
                            f"{format_size(len(output_audio))}."
                        )

                    except Exception as exc:
                        st.error(f"Audio conversion failed: {exc}")

            conversion = st.session_state.get(
                "audio_conversion_result"
            )

            if conversion and conversion.get("sig") == convert_sig:
                mime_map = {
                    "MP3": "audio/mpeg",
                    "WAV": "audio/wav",
                    "FLAC": "audio/flac",
                    "OGG": "audio/ogg",
                    "M4A": "audio/mp4",
                    "OPUS": "audio/opus",
                }

                st.audio(
                    conversion["data"],
                    format=mime_map[conversion["format"]],
                )

                st.download_button(
                    "Download converted audio",
                    data=conversion["data"],
                    file_name=conversion["filename"],
                    mime=mime_map[conversion["format"]],
                    key=f"download_converted_audio_{convert_sig[:12]}",
                    use_container_width=True,
                )

        else:
            empty_state(
                "Ready to convert",
                "Upload an audio file, choose the output format, and download the converted copy.",
            )


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.caption("Ashutosh Studio · Engineering & Computational Toolkit")
