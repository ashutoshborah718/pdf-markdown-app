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

import docx
import matplotlib.pyplot as plt
import numpy as np
import pymupdf
import streamlit as st
from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError
from wordcloud import WordCloud

from modules.pdf_utils import docx_to_pdf_bytes as libreoffice_docx_to_pdf_bytes

try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None

try:
    import argostranslate.package as argos_package
    import argostranslate.translate as argos_translate
except Exception:
    argos_package = None
    argos_translate = None

try:
    from indic_transliteration import sanscript
except Exception:
    sanscript = None


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
        background: #0b1020;
        color: #f3f6fc;
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
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

    h1, h2, h3, h4, p, li, label {
        color: #f3f6fc;
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
        padding: 1.2rem 1.25rem;
        margin: .35rem 0 1rem 0;
        min-height: 150px;
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
        padding: 1.15rem 1.25rem;
        color: #d2dceb;
        margin: .75rem 0 1rem 0;
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

    .stTabs [data-baseweb="tab-list"] {
        gap: .35rem;
        border-bottom: 1px solid #34435e;
        flex-wrap: wrap;
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

    input, textarea, [data-baseweb="select"] > div {
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


def show_file_summary(
    name: str,
    data: bytes,
    details: str = "",
) -> None:
    tail = f"<span> • {details}</span>" if details else ""

    st.markdown(
        f"<div class='file-summary'><strong>📎 {name}</strong><br>"
        f"<span>{format_size(len(data))}</span>{tail}</div>",
        unsafe_allow_html=True,
    )


def empty_state(title: str, instructions: str) -> None:
    st.markdown(
        f"<div class='empty-state'><strong>📂 {title}</strong><br>"
        f"{instructions}</div>",
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, emoji: str) -> None:
    st.markdown(
        f"<div class='hero-title'>{emoji} {title}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='hero-subtitle'>{subtitle}</div>",
        unsafe_allow_html=True,
    )


def tool_intro(title: str, description: str) -> None:
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
    st.session_state[f"result_{key}"] = {
        "sig": source_sig,
        "data": data,
        "filename": filename,
        "mime": mime,
        "kind": kind,
    }


def show_result(key: str, source_sig: str) -> None:
    result = st.session_state.get(f"result_{key}")

    if not result or result["sig"] != source_sig:
        return

    if result["kind"] == "image":
        st.image(
            result["data"],
            caption="Preview of processed output",
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
        pdf.save(
            output,
            garbage=4,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
        )
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
    image = Image.open(io.BytesIO(raw))
    image.load()
    return ImageOps.exif_transpose(image)


def output_name(name: str, suffix: str) -> str:
    stem = re.sub(r"\.[^.]+$", "", name)
    return f"{stem}{suffix}"


# -----------------------------------------------------------------------------
# Audio Intelligence helpers
# -----------------------------------------------------------------------------

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

ROMAN_SCHEMES = {
    "as": "ASSAMESE",
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
    """Load a CPU-friendly Whisper model only when requested."""
    if WhisperModel is None:
        raise RuntimeError(
            "faster-whisper is not installed. Add it to requirements.txt and redeploy."
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
    """Transliterate supported Indic scripts to Latin letters."""
    if not sanscript or language_code not in ROMAN_SCHEMES:
        return None

    scheme_name = ROMAN_SCHEMES[language_code]
    source_scheme = getattr(sanscript, scheme_name, None)

    if source_scheme is None and language_code == "as":
        source_scheme = getattr(sanscript, "BENGALI", None)

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
    total_ms = max(0, int(round(seconds * 1000)))

    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def segments_to_srt(segments: list[dict[str, Any]]) -> str:
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
    """Translate with a locally installed Argos model.

    A language model may need to be downloaded on first use.
    Transcript text is not sent to an external translation API.
    """
    if not text.strip():
        raise ValueError("The transcript is empty.")

    if from_code == to_code:
        return text

    if argos_package is None or argos_translate is None:
        raise RuntimeError(
            "argostranslate is not installed. Add it to requirements.txt and redeploy."
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

        if source and target:
            try:
                return source.get_translation(target)
            except Exception:
                return None

        return None

    translation = find_translation()

    if translation is None:
        try:
            argos_package.update_package_index()
            available = argos_package.get_available_packages()

            match = next(
                (
                    pkg for pkg in available
                    if pkg.from_code == from_code and pkg.to_code == to_code
                ),
                None,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Could not access the Argos model index: {exc}"
            ) from exc

        if match is None:
            source_name = AUDIO_LANGUAGE_NAMES.get(from_code, from_code)
            target_name = AUDIO_LANGUAGE_NAMES.get(to_code, to_code)

            raise ValueError(
                f"No direct offline model is listed for "
                f"{source_name} → {target_name}. Choose another target language. "
                "This app will not send your transcript to an online translation API."
            )

        try:
            model_path = match.download()
            argos_package.install_from_path(model_path)
        except Exception as exc:
            raise RuntimeError(
                f"Could not download/install the offline translation model: {exc}"
            ) from exc

        translation = find_translation()

    if translation is None:
        raise ValueError(
            "The offline translation model is not available for this language pair. "
            "Choose another target language; no external translation API will be used."
        )

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
        translation.translate(chunk) for chunk in chunks
    )


def convert_audio_bytes(
    data: bytes,
    original_name: str,
    target_format: str,
) -> bytes:
    """Convert audio using FFmpeg in a temporary directory."""
    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        raise RuntimeError(
            "FFmpeg is unavailable. Check packages.txt includes ffmpeg and redeploy."
        )

    suffix = Path(original_name).suffix.lower() or ".audio"

    encoders = {
        "MP3": (".mp3", ["-codec:a", "libmp3lame", "-q:a", "2"]),
        "WAV": (".wav", ["-codec:a", "pcm_s16le"]),
        "FLAC": (".flac", ["-codec:a", "flac"]),
        "OGG": (".ogg", ["-codec:a", "libvorbis", "-q:a", "5"]),
        "M4A": (".m4a", ["-codec:a", "aac", "-b:a", "192k", "-f", "ipod"]),
        "OPUS": (".opus", ["-codec:a", "libopus", "-b:a", "128k"]),
    }

    if target_format not in encoders:
        raise ValueError("Unsupported target audio format.")

    output_suffix, codec_args = encoders[target_format]

    with tempfile.TemporaryDirectory(prefix="ashutosh_audio_") as temp_dir:
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
                details[-1200:] or "FFmpeg could not convert this audio file."
            )

        return output_path.read_bytes()


# -----------------------------------------------------------------------------
# Sidebar navigation
# -----------------------------------------------------------------------------

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
    "Engineering & Computational Toolkit<br><strong>Ashutosh Borah</strong></p>",
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Workspace Directory")

for index, page_name in enumerate(PAGES):
    if st.sidebar.button(
        page_name,
        key=f"nav_{index}",
        use_container_width=True,
        type="primary" if st.session_state.active_page == page_name else "secondary",
    ):
        st.session_state.active_page = page_name
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<span class='status-pill'>● SYSTEM ONLINE</span>",
    unsafe_allow_html=True,
)
st.sidebar.caption("Local file processing · No account required")


# -----------------------------------------------------------------------------
# Platform Overview
# -----------------------------------------------------------------------------

if st.session_state.active_page == PAGES[0]:
    page_header(
        "Welcome to Ashutosh Studio",
        "A practical workspace for document conversion, PDF operations, "
        "document analysis, and image optimization.",
        "⚡",
    )

    a, b, c = st.columns(3)
    a.metric("Workspace modules", "3")
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
                    Convert PDFs and Word files, merge or compress PDFs,
                    create PDFs from images, analyse document text,
                    and inspect embedded PDF images.
                </p>
                <p><strong>Best for:</strong> document cleanup, conversion, and investigation.</p>
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
                    Resize, crop, rotate, compress, convert, or watermark images.
                    Review dimensions and colour histograms.
                </p>
                <p><strong>Best for:</strong> preparing and optimizing image assets.</p>
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
                Upload voice notes or audio files, record a short clip,
                transcribe speech, create Latin-letter transliteration where
                supported, translate locally, and convert audio formats.
            </p>
            <p><strong>Privacy note:</strong> transcription runs on the hosted app.
            Offline translation keeps transcript text inside that app environment;
            language-model files may be downloaded on first use.</p>
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
    x.markdown("**1 · Upload**\n\nChoose a supported file and review its name and size.")
    y.markdown("**2 · Process**\n\nChoose a tool and adjust any settings.")
    z.markdown("**3 · Review & download**\n\nCheck the output preview, then download the result.")

    st.info(
        "Files are processed by the app while you use it. Avoid uploading "
        "confidential documents to a public deployment unless you are comfortable "
        "with its hosting and data-handling setup."
    )


# -----------------------------------------------------------------------------
# Document Intelligence
# -----------------------------------------------------------------------------

elif st.session_state.active_page == PAGES[1]:
    page_header(
        "Document Intelligence Hub",
        "Convert, combine, compress, and inspect common document formats.",
        "📄",
    )

    tabs = st.tabs(
        [
            "PDF → Markdown",
            "PDF → Word",
            "Word → PDF",
            "Merge PDFs",
            "Images → PDF",
            "Compress PDF",
            "Document Analyzer",
            "PDF Asset Inspector",
        ]
    )

    # PDF to Markdown
    with tabs[0]:
        tool_intro(
            "Convert PDF to Markdown",
            "Extract selectable PDF text by page and download a Markdown file. "
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

            if st.button("Convert to Markdown", type="primary", key="run_pdf_md"):
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
                "Upload a PDF with selectable text to create a Markdown version.",
            )

    # PDF to Word
    with tabs[1]:
        tool_intro(
            "Convert PDF to Word",
            "Create an editable DOCX from selectable PDF text. This extracts text; "
            "the original layout and images are not reproduced exactly.",
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

            if st.button("Convert to Word", type="primary", key="run_pdf_docx"):
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

    # Word to PDF
    with tabs[2]:
        tool_intro(
            "Convert Word to PDF",
            "Uses LibreOffice to retain Word layout, tables, headers, footers, "
            "and embedded images much better than rebuilding the document from text.",
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

            if st.button("Convert to PDF", type="primary", key="run_docx_pdf"):
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
                        "Could not convert this DOCX. Check that LibreOffice is "
                        f"installed and the file is valid. Details: {exc}"
                    )

            show_result("docx_pdf", sig)

        else:
            empty_state(
                "Ready to convert",
                "Upload a DOCX file. The converter requires the system packages "
                "in packages.txt to finish installing.",
            )

    # Merge PDFs
    with tabs[3]:
        tool_intro(
            "Merge PDF files",
            "Combine PDFs in the order shown below. Rearrange your upload selection "
            "before processing if the order matters.",
        )

        uploads = st.file_uploader(
            "Select two or more PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            key="merge_pdfs_upload",
        )

        if uploads:
            items = [(item.name, item.getvalue()) for item in uploads]
            sig = file_signature(
                b"".join(name.encode() + b"\0" + raw for name, raw in items)
            )

            st.write(f"Selected files: **{len(items)}**")

            for i, (name, raw) in enumerate(items, start=1):
                st.write(f"{i}. {name} — {format_size(len(raw))}")

            if st.button("Merge PDFs", type="primary", key="run_merge_pdfs"):
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
                "Upload multiple PDF files to combine them into one document.",
            )

    # Images to PDF
    with tabs[4]:
        tool_intro(
            "Convert images to PDF",
            "Combine multiple images into a single PDF, one image per page.",
        )

        uploads = st.file_uploader(
            "Select images",
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
            accept_multiple_files=True,
            key="images_pdf_upload",
        )

        if uploads:
            items = [(item.name, item.getvalue()) for item in uploads]
            sig = file_signature(
                b"".join(name.encode() + b"\0" + raw for name, raw in items)
            )

            st.write(f"Selected images: **{len(items)}**")

            for name, raw in items:
                st.caption(f"{name} · {format_size(len(raw))}")

            if st.button("Create PDF", type="primary", key="run_images_pdf"):
                try:
                    result = images_to_pdf_bytes(items)
                    save_result(
                        "images_pdf",
                        sig,
                        result,
                        "images.pdf",
                        "application/pdf",
                    )
                except (UnidentifiedImageError, OSError, ValueError) as exc:
                    st.error(f"Could not build the PDF: {exc}")

            show_result("images_pdf", sig)

        else:
            empty_state(
                "Ready to compile",
                "Upload images to compile them into one PDF.",
            )

    # Compress PDF
    with tabs[5]:
        tool_intro(
            "Compress PDF",
            "Rewrites PDF streams and removes unused objects where possible. "
            "This may reduce the file size, but already-optimized or image-heavy "
            "PDFs may not shrink much.",
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

            if st.button("Compress PDF", type="primary", key="run_compress_pdf"):
                try:
                    compressed = compress_pdf_bytes(data)

                    save_result(
                        "compress_pdf",
                        sig,
                        compressed,
                        output_name(uploaded.name, "_compressed.pdf"),
                        "application/pdf",
                    )

                    delta = len(compressed) - len(data)

                    if delta < 0:
                        st.success(
                            f"Reduced file size by {format_size(-delta)} "
                            f"({-delta / max(len(data), 1) * 100:.1f}%)."
                        )
                    else:
                        st.info(
                            "The PDF was rewritten, but the file did not get "
                            "smaller. Some PDFs are already optimized."
                        )

                except Exception as exc:
                    st.error(f"Could not compress this PDF: {exc}")

            show_result("compress_pdf", sig)

        else:
            empty_state(
                "Ready to compress",
                "Upload a PDF to optimize its internal structure.",
            )

    # Document Analyzer
    with tabs[6]:
        tool_intro(
            "Document Analyzer",
            "Understand a PDF using ranked terms, page statistics, custom keyword "
            "counts, a searchable frequency table, and downloadable data. "
            "This analyzes selectable text only.",
        )

        uploaded = st.file_uploader(
            "Upload a text-based PDF",
            type=["pdf"],
            key="analyzer_pdf_upload",
        )

        if uploaded:
            data = uploaded.getvalue()
            sig = file_signature(data)
            show_file_summary(uploaded.name, data, "PDF document")

            try:
                pages = pdf_text_pages(data)
                full_text = "\n".join(pages)

                words = re.findall(
                    r"\b[A-Za-z][A-Za-z'-]{2,}\b",
                    full_text.lower(),
                )

                stop_default = (
                    "about, after, again, also, among, because, been, before, "
                    "being, between, both, could, does, doing, down, each, from, "
                    "further, have, having, into, itself, just, more, most, over, "
                    "same, should, some, such, than, that, their, them, then, "
                    "there, these, they, this, those, through, under, until, very, "
                    "what, when, where, which, while, with, would, your, page, "
                    "figure, table, using, used, based, results, study"
                )

                stop_input = st.text_input(
                    "Additional stop words (comma-separated)",
                    value=stop_default,
                    key="analyzer_stop_words",
                )

                stop_words = {
                    item.strip().lower()
                    for item in stop_input.split(",")
                    if item.strip()
                }

                filtered_words = [
                    word for word in words
                    if word not in stop_words and not word.isdigit()
                ]

                counts = Counter(filtered_words)

                top_n = st.slider(
                    "Number of terms to display",
                    10,
                    50,
                    20,
                    key="analyzer_top_n",
                )

                query = st.text_input(
                    "Check keyword or phrase (optional)",
                    key="analyzer_keyword_query",
                ).strip().lower()

                word_total = len(re.findall(r"\b\w+\b", full_text))

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Pages", len(pages))
                m2.metric("Words", f"{word_total:,}")
                m3.metric("Unique terms", f"{len(set(filtered_words)):,}")
                m4.metric("Characters", f"{len(full_text):,}")

                if query:
                    per_page = [
                        page.lower().count(query)
                        for page in pages
                    ]

                    st.write(
                        f"**Occurrences of ‘{query}’:** {sum(per_page)}"
                    )

                    st.dataframe(
                        [
                            {"Page": i, "Occurrences": count}
                            for i, count in enumerate(per_page, 1)
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )

                if counts:
                    top_items = counts.most_common(top_n)

                    frequency_rows = [
                        {"Term": term, "Frequency": count}
                        for term, count in top_items
                    ]

                    st.markdown("#### Most frequent meaningful terms")
                    st.dataframe(
                        frequency_rows,
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
                    ax.set_title(
                        f"Top {len(top_items)} terms by frequency"
                    )
                    ax.grid(axis="x", alpha=0.2)
                    fig.tight_layout()

                    st.pyplot(fig, clear_figure=True)

                    csv_buffer = io.StringIO()

                    writer = csv.DictWriter(
                        csv_buffer,
                        fieldnames=["Term", "Frequency"],
                    )

                    writer.writeheader()
                    writer.writerows(
                        [
                            {"Term": term, "Frequency": n}
                            for term, n in counts.most_common()
                        ]
                    )

                    st.download_button(
                        "Download all term frequencies (CSV)",
                        csv_buffer.getvalue().encode("utf-8-sig"),
                        output_name(
                            uploaded.name,
                            "_term_frequencies.csv",
                        ),
                        "text/csv",
                        key="download_term_csv",
                    )

                    if st.checkbox(
                        "Also generate a word cloud",
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

                        cloud_out = io.BytesIO()
                        cloud.to_image().save(cloud_out, format="PNG")

                        st.image(
                            cloud_out.getvalue(),
                            caption="Word cloud (larger words appear more frequently)",
                            use_container_width=True,
                        )

                        st.download_button(
                            "Download word cloud (PNG)",
                            cloud_out.getvalue(),
                            output_name(uploaded.name, "_wordcloud.png"),
                            "image/png",
                            key="download_wordcloud_png",
                        )

                else:
                    st.warning(
                        "No analyzable text was found after stop-word filtering. "
                        "This may be a scanned PDF or a document with very little text."
                    )

                with st.expander("Page-by-page text statistics"):
                    stats = []

                    for i, page in enumerate(pages, 1):
                        stats.append(
                            {
                                "Page": i,
                                "Words": len(re.findall(r"\b\w+\b", page)),
                                "Characters": len(page),
                                "Extracted text": page[:240].replace("\n", " "),
                            }
                        )

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
                "Upload a PDF to see term frequencies, keywords, and page-level statistics.",
            )

    # PDF Asset Inspector
    with tabs[7]:
        tool_intro(
            "PDF Asset Inspector",
            "Inspect embedded raster images with page number, dimensions, "
            "format, and size. Select assets to download individually or in a ZIP. "
            "Vector graphics may not appear as standalone embedded images.",
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

                                asset = {
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
                                }

                                assets.append(asset)

                            except Exception:
                                continue

                if not assets:
                    st.info(
                        "No embedded raster images were found. The PDF may contain "
                        "vector drawings or page-rendered content rather than "
                        "standalone raster images."
                    )

                else:
                    st.success(
                        f"Found {len(assets)} embedded image occurrence(s). "
                        "Repeated references may appear more than once when used on different pages."
                    )

                    rows = [
                        {
                            "Asset": item["label"],
                            "Page": item["page"],
                            "Width (px)": item["width"],
                            "Height (px)": item["height"],
                            "Format": item["format"],
                            "File size": format_size(item["bytes"]),
                        }
                        for item in assets
                    ]

                    st.dataframe(
                        rows,
                        use_container_width=True,
                        hide_index=True,
                    )

                    chosen = st.multiselect(
                        "Choose assets to export",
                        options=[item["label"] for item in assets],
                        default=[item["label"] for item in assets],
                        key="chosen_pdf_assets",
                    )

                    selected = [
                        item for item in assets
                        if item["label"] in chosen
                    ]

                    if selected:
                        preview_cols = st.columns(min(3, len(selected)))

                        for idx, item in enumerate(selected[:6]):
                            with preview_cols[idx % len(preview_cols)]:
                                st.caption(item["label"])

                                try:
                                    st.image(
                                        item["data"],
                                        use_container_width=True,
                                    )
                                except Exception:
                                    st.caption(
                                        "Preview unavailable for this image format."
                                    )

                        zip_buffer = io.BytesIO()

                        with zipfile.ZipFile(
                            zip_buffer,
                            "w",
                            zipfile.ZIP_DEFLATED,
                        ) as zip_file:
                            for i, item in enumerate(selected, 1):
                                ext = item["format"].lower().replace("jpeg", "jpg")

                                zip_file.writestr(
                                    f"page_{item['page']}_image_{i}_"
                                    f"xref_{item['xref']}.{ext}",
                                    item["data"],
                                )

                        st.download_button(
                            "Download selected assets (ZIP)",
                            zip_buffer.getvalue(),
                            output_name(uploaded.name, "_assets.zip"),
                            "application/zip",
                            key="download_assets_zip",
                        )

                        for i, item in enumerate(selected, 1):
                            ext = item["format"].lower().replace("jpeg", "jpg")

                            st.download_button(
                                f"Download image {i} · Page {item['page']}",
                                item["data"],
                                f"page_{item['page']}_image_{i}.{ext}",
                                "application/octet-stream",
                                key=f"download_asset_{i}_{item['xref']}",
                            )

            except Exception as exc:
                st.error(f"Could not inspect this PDF: {exc}")

        else:
            empty_state(
                "Ready to inspect",
                "Upload a PDF to review and export its embedded raster images.",
            )


# -----------------------------------------------------------------------------
# Media Studio
# -----------------------------------------------------------------------------

elif st.session_state.active_page == PAGES[2]:
    page_header(
        "Media Studio",
        "Resize, crop, rotate, compress, convert, and watermark images with clear previews.",
        "🖼️",
    )

    tabs = st.tabs(
        [
            "Resize",
            "JPEG Compress",
            "Grayscale",
            "Crop",
            "Rotate & Flip",
            "Convert Format",
            "Watermark",
            "Image Analysis",
        ]
    )

    # Resize
    with tabs[0]:
        tool_intro(
            "Resize image",
            "Set a new width and height. Use the aspect-ratio option to avoid stretching the image.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
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

                st.image(image, caption="Original image", use_container_width=True)

                preserve = st.checkbox(
                    "Preserve aspect ratio",
                    value=True,
                    key="resize_preserve",
                )

                width = st.number_input(
                    "Output width (px)",
                    min_value=1,
                    max_value=12000,
                    value=int(image.width),
                    step=1,
                    key="resize_width",
                )

                height = st.number_input(
                    "Output height (px)",
                    min_value=1,
                    max_value=12000,
                    value=int(image.height),
                    step=1,
                    key="resize_height",
                )

                if st.button("Resize image", type="primary", key="run_resize"):
                    new_size = (int(width), int(height))

                    if preserve:
                        copy = image.copy()
                        copy.thumbnail(new_size, Image.Resampling.LANCZOS)
                        result_image = copy
                    else:
                        result_image = image.resize(
                            new_size,
                            Image.Resampling.LANCZOS,
                        )

                    fmt = (
                        "PNG"
                        if result_image.mode in ("RGBA", "LA")
                        else "JPEG"
                    )

                    if fmt == "JPEG":
                        result_image = result_image.convert("RGB")

                    out = io.BytesIO()
                    result_image.save(out, format=fmt, quality=92)

                    save_result(
                        "resize",
                        sig,
                        out.getvalue(),
                        output_name(uploaded.name, f"_resized.{fmt.lower()}"),
                        f"image/{fmt.lower()}",
                        "image",
                    )

                show_result("resize", sig)

            except Exception as exc:
                st.error(f"Could not process this image: {exc}")

    # JPEG compression
    with tabs[1]:
        tool_intro(
            "Compress to JPEG",
            "JPEG is lossy and does not support transparency. Transparent pixels "
            "are placed on a white background.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
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

                if st.button("Compress image", type="primary", key="run_jpeg"):
                    out = io.BytesIO()
                    image.save(
                        out,
                        format="JPEG",
                        quality=quality,
                        optimize=True,
                        progressive=True,
                    )

                    result = out.getvalue()

                    save_result(
                        "jpeg",
                        sig,
                        result,
                        output_name(uploaded.name, "_compressed.jpg"),
                        "image/jpeg",
                        "image",
                    )

                    st.caption(
                        f"Original: {format_size(len(raw))} · "
                        f"Output: {format_size(len(result))}"
                    )

                show_result("jpeg", sig)

            except Exception as exc:
                st.error(f"Could not compress this image: {exc}")

    # Grayscale
    with tabs[2]:
        tool_intro(
            "Convert to grayscale",
            "Create a grayscale image from colour input.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
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
                    out = io.BytesIO()
                    result_image.save(out, format="PNG")

                    save_result(
                        "gray",
                        sig,
                        out.getvalue(),
                        output_name(uploaded.name, "_grayscale.png"),
                        "image/png",
                        "image",
                    )

                show_result("gray", sig)

            except Exception as exc:
                st.error(f"Could not convert this image: {exc}")

    # Crop
    with tabs[3]:
        tool_intro(
            "Crop image",
            "Crop by choosing the left, top, right, and bottom margins as percentages of the original dimensions.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
            key="crop_upload",
        )

        if uploaded:
            raw = uploaded.getvalue()
            sig = file_signature(raw)

            try:
                image = get_image(raw)

                a, b, c, d = st.columns(4)

                left = a.slider("Left %", 0, 90, 0, key="crop_left")
                top = b.slider("Top %", 0, 90, 0, key="crop_top")
                right = c.slider("Right %", 0, 90, 0, key="crop_right")
                bottom = d.slider("Bottom %", 0, 90, 0, key="crop_bottom")

                if st.button("Crop image", type="primary", key="run_crop"):
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
                        out = io.BytesIO()

                        fmt = (
                            "PNG"
                            if "A" in result_image.getbands()
                            else "JPEG"
                        )

                        if fmt == "JPEG":
                            result_image = result_image.convert("RGB")

                        result_image.save(out, format=fmt, quality=92)

                        save_result(
                            "crop",
                            sig,
                            out.getvalue(),
                            output_name(
                                uploaded.name,
                                f"_cropped.{fmt.lower()}",
                            ),
                            f"image/{fmt.lower()}",
                            "image",
                        )

                show_result("crop", sig)

            except Exception as exc:
                st.error(f"Could not crop this image: {exc}")

    # Rotate and flip
    with tabs[4]:
        tool_intro(
            "Rotate and flip",
            "Rotate by 90-degree increments or flip the image horizontally or vertically.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
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
                    format_func=lambda x: f"{x}°",
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

                    fmt = (
                        "PNG"
                        if "A" in result_image.getbands()
                        else "JPEG"
                    )

                    if fmt == "JPEG":
                        result_image = result_image.convert("RGB")

                    out = io.BytesIO()
                    result_image.save(out, format=fmt, quality=92)

                    save_result(
                        "rotate",
                        sig,
                        out.getvalue(),
                        output_name(
                            uploaded.name,
                            f"_transformed.{fmt.lower()}",
                        ),
                        f"image/{fmt.lower()}",
                        "image",
                    )

                show_result("rotate", sig)

            except Exception as exc:
                st.error(f"Could not transform this image: {exc}")

    # Convert format
    with tabs[5]:
        tool_intro(
            "Convert image format",
            "Convert to PNG, JPEG, or WEBP. Transparency is retained for PNG and WEBP; JPEG uses a white background.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
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
                        background = Image.new("RGB", image.size, "white")

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
                            and result_image.mode not in ("RGB", "RGBA", "L", "LA", "P")
                        ):
                            result_image = result_image.convert("RGBA")

                    out = io.BytesIO()
                    save_args = {"format": target}

                    if target in ("JPEG", "WEBP"):
                        save_args["quality"] = quality

                    result_image.save(out, **save_args)

                    ext = target.lower().replace("jpeg", "jpg")

                    save_result(
                        "format",
                        sig,
                        out.getvalue(),
                        output_name(
                            uploaded.name,
                            f"_converted.{ext}",
                        ),
                        f"image/{'jpeg' if target == 'JPEG' else ext}",
                        "image",
                    )

                show_result("format", sig)

            except Exception as exc:
                st.error(f"Could not convert this image: {exc}")

    # Watermark
    with tabs[6]:
        tool_intro(
            "Add a text watermark",
            "Place a readable text watermark on an image. Keep a copy of your original file.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
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
                    overlay = Image.new(
                        "RGBA",
                        image.size,
                        (0, 0, 0, 0),
                    )

                    draw = ImageDraw.Draw(overlay)
                    font_size = max(14, image.width // 32)

                    try:
                        from PIL import ImageFont

                        font = ImageFont.truetype(
                            "DejaVuSans.ttf",
                            font_size,
                        )
                    except Exception:
                        font = ImageDraw.load_default()

                    bbox = draw.textbbox(
                        (0, 0),
                        watermark,
                        font=font,
                        stroke_width=1,
                    )

                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                    margin = max(10, image.width // 40)

                    positions = {
                        "Bottom right": (
                            image.width - tw - margin,
                            image.height - th - margin,
                        ),
                        "Bottom left": (
                            margin,
                            image.height - th - margin,
                        ),
                        "Top right": (
                            image.width - tw - margin,
                            margin,
                        ),
                        "Top left": (margin, margin),
                        "Center": (
                            (image.width - tw) // 2,
                            (image.height - th) // 2,
                        ),
                    }

                    xy = positions[position]

                    draw.text(
                        xy,
                        watermark,
                        font=font,
                        fill=(255, 255, 255, opacity),
                        stroke_width=2,
                        stroke_fill=(0, 0, 0, min(220, opacity)),
                    )

                    result_image = Image.alpha_composite(image, overlay)
                    out = io.BytesIO()
                    result_image.save(out, format="PNG")

                    save_result(
                        "watermark",
                        sig,
                        out.getvalue(),
                        output_name(uploaded.name, "_watermarked.png"),
                        "image/png",
                        "image",
                    )

                show_result("watermark", sig)

            except Exception as exc:
                st.error(f"Could not add watermark: {exc}")

    # Image Analysis
    with tabs[7]:
        tool_intro(
            "Image analysis",
            "Review image dimensions and file size, then inspect a separate histogram for each RGB channel.",
        )

        uploaded = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
            key="analysis_upload",
        )

        if uploaded:
            raw = uploaded.getvalue()

            try:
                image = get_image(raw).convert("RGB")

                x, y, z = st.columns(3)
                x.metric("Width", f"{image.width:,} px")
                y.metric("Height", f"{image.height:,} px")
                z.metric("File size", format_size(len(raw)))

                st.image(
                    image,
                    caption=uploaded.name,
                    use_container_width=True,
                )

                array = np.asarray(image)
                fig, ax = plt.subplots(figsize=(9, 4))

                for channel, label in enumerate(["Red", "Green", "Blue"]):
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
                ax.grid(alpha=.2)
                fig.tight_layout()

                st.pyplot(fig, clear_figure=True)

            except Exception as exc:
                st.error(f"Could not analyze this image: {exc}")


# -----------------------------------------------------------------------------
# Audio Intelligence
# -----------------------------------------------------------------------------

elif st.session_state.active_page == PAGES[3]:
    page_header(
        "Audio Intelligence",
        "Transcribe voice notes, review original text, transliterate supported "
        "Indic scripts, translate with local models, and convert audio formats.",
        "🎙️",
    )

    st.warning(
        "Hosting/privacy note: files are uploaded to this Streamlit app's server "
        "for processing. Translation text is processed by a local Argos model "
        "and is not sent to a translation API. The first use of a language pair "
        "may download its model files. Do not upload sensitive recordings unless "
        "you trust this hosting setup."
    )

    audio_tabs = st.tabs(
        ["Transcribe & Translate", "Convert Audio Format"]
    )

    # Transcription, transliteration and translation
    with audio_tabs[0]:
        tool_intro(
            "Speech-to-text workspace",
            "Upload a WhatsApp voice note/audio file or record a short clip. "
            "Review the source-language transcript, get a Latin-letter rendering "
            "for supported Indic scripts, and translate it offline when a model exists.",
        )

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
                "Choose audio",
                type=[
                    "mp3", "wav", "m4a", "aac", "ogg", "oga",
                    "opus", "flac", "webm", "mp4", "3gp",
                ],
                key="audio_transcribe_upload",
            )

            if audio_file:
                audio_data = audio_file.getvalue()
                audio_name = audio_file.name

        elif hasattr(st, "audio_input"):
            recorded_audio = st.audio_input(
                "Record a voice note",
                key="audio_microphone_recording",
            )

            if recorded_audio:
                audio_data = recorded_audio.getvalue()
                audio_name = "microphone_recording.wav"

        else:
            st.info(
                "Microphone recording requires a newer Streamlit version. "
                "You can still upload a recording file."
            )

        if audio_data:
            audio_sig = file_signature(audio_data)
            show_file_summary(audio_name, audio_data, "Audio input")
            st.audio(audio_data)

            language_choice = st.selectbox(
                "Speech language",
                list(TRANSCRIPTION_LANGUAGES.keys()),
                index=0,
                help="Auto-detect is recommended unless you know the language of the recording.",
                key="audio_speech_language",
            )

            model_choice = st.selectbox(
                "Transcription model",
                ["tiny", "base", "small"],
                index=1,
                help="Tiny is faster but less accurate; small can be slower on a CPU-hosted app.",
                key="audio_whisper_model_size",
            )

            st.caption(
                "For longer recordings, use the tiny or base model first. "
                "Processing can take a while on the hosted CPU."
            )

            if st.button(
                "Transcribe audio",
                type="primary",
                key="run_audio_transcription",
            ):
                if WhisperModel is None:
                    st.error(
                        "Speech recognition package is missing. Check that "
                        "faster-whisper is in requirements.txt and redeploy."
                    )

                elif len(audio_data) > 50 * 1024 * 1024:
                    st.error(
                        "This audio file is over 50 MB. Please use a shorter "
                        "or compressed copy to reduce memory and processing time."
                    )

                else:
                    suffix = Path(audio_name).suffix.lower() or ".wav"
                    temp_name = None

                    try:
                        with st.spinner(
                            "Loading the speech model and transcribing. "
                            "First use may download model weights..."
                        ):
                            model = load_whisper_model(model_choice)

                            with tempfile.NamedTemporaryFile(
                                delete=False,
                                suffix=suffix,
                            ) as temp_audio:
                                temp_audio.write(audio_data)
                                temp_name = temp_audio.name

                            selected_language = TRANSCRIPTION_LANGUAGES[
                                language_choice
                            ]

                            segment_iter, info = model.transcribe(
                                temp_name,
                                language=selected_language,
                                beam_size=5,
                                vad_filter=True,
                            )

                            segments = [
                                {
                                    "start": float(segment.start),
                                    "end": float(segment.end),
                                    "text": segment.text.strip(),
                                }
                                for segment in segment_iter
                                if segment.text.strip()
                            ]

                            transcript = " ".join(
                                segment["text"] for segment in segments
                            ).strip()

                        if not transcript:
                            st.warning(
                                "No speech was detected. Try another model, "
                                "check the recording, or select the speech language manually."
                            )

                        else:
                            st.session_state["audio_transcript_result"] = {
                                "sig": audio_sig,
                                "language": info.language,
                                "language_probability": float(
                                    getattr(info, "language_probability", 0.0)
                                    or 0.0
                                ),
                                "segments": segments,
                                "text": transcript,
                                "translation": None,
                                "translation_target": None,
                                "audio_name": audio_name,
                            }

                            st.success("Transcription completed.")

                    except Exception as exc:
                        st.error(f"Transcription failed: {exc}")

                    finally:
                        if temp_name and os.path.exists(temp_name):
                            try:
                                os.remove(temp_name)
                            except OSError:
                                pass

            result = st.session_state.get("audio_transcript_result")

            if result and result.get("sig") == audio_sig:
                detected_code = result.get("language", "")
                detected_name = AUDIO_LANGUAGE_NAMES.get(
                    detected_code,
                    detected_code or "Unknown",
                )

                m1, m2, m3 = st.columns(3)
                m1.metric("Detected language", detected_name)
                m2.metric("Speech segments", len(result.get("segments", [])))
                m3.metric(
                    "Language confidence",
                    f"{result.get('language_probability', 0.0) * 100:.0f}%",
                )

                transcript_key = f"audio_transcript_edit_{audio_sig[:12]}"

                edited_text = st.text_area(
                    "Original-language transcript (editable)",
                    value=result.get("text", ""),
                    height=220,
                    key=transcript_key,
                    help="Edit recognition mistakes here before creating your downloads or translation.",
                )

                st.markdown("#### English-letter transliteration")

                romanized = transliterate_to_latin(
                    edited_text,
                    detected_code,
                )

                if romanized is not None:
                    st.text_area(
                        "Latin-letter rendering (ITRANS-style; transliteration is not translation)",
                        value=romanized,
                        height=180,
                        disabled=True,
                        key=f"audio_romanized_{audio_sig[:12]}",
                    )

                elif detected_code == "en":
                    romanized = edited_text

                    st.text_area(
                        "Latin-letter text",
                        value=edited_text,
                        height=100,
                        disabled=True,
                        key=f"audio_romanized_en_{audio_sig[:12]}",
                    )

                else:
                    st.info(
                        f"Latin-letter transliteration is not configured for "
                        f"detected language '{detected_name}'. The original transcript "
                        "is still available; no transliteration is fabricated."
                    )

                    romanized = ""

                st.markdown("#### Offline translation")

                target_names = list(TRANSLATION_LANGUAGES.keys())
                default_target_index = target_names.index("English")

                target_name = st.selectbox(
                    "Translate transcript to",
                    target_names,
                    index=default_target_index,
                    key=f"audio_target_{audio_sig[:12]}",
                )

                st.caption(
                    "Translation uses Argos models locally after any required "
                    "model download. Unsupported language pairs are reported; "
                    "there is no online-API fallback."
                )

                if st.button(
                    "Translate transcript offline",
                    type="primary",
                    key=f"run_audio_translate_{audio_sig[:12]}",
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
                        result["translation_target"] = TRANSLATION_LANGUAGES[
                            target_name
                        ]

                        st.session_state["audio_transcript_result"] = result
                        st.success("Offline translation completed.")

                    except Exception as exc:
                        st.error(f"Offline translation unavailable: {exc}")

                if (
                    result.get("translation")
                    and result.get("translation_target")
                    == TRANSLATION_LANGUAGES[target_name]
                ):
                    st.text_area(
                        f"Translation — {target_name}",
                        value=result["translation"],
                        height=220,
                        key=f"audio_translation_preview_{audio_sig[:12]}_{target_name}",
                    )

                txt_parts = [
                    f"Original language: {detected_name}",
                    "\nORIGINAL TRANSCRIPT\n",
                    edited_text,
                    "\n\nLATIN-LETTER TRANSLITERATION\n",
                    romanized or "Not available for this language.",
                ]

                if result.get("translation"):
                    txt_parts.extend(
                        [
                            "\n\nTRANSLATION "
                            f"({AUDIO_LANGUAGE_NAMES.get(result.get('translation_target'), result.get('translation_target'))})\n",
                            result["translation"],
                        ]
                    )

                st.download_button(
                    "Download transcript package (TXT)",
                    data="\n".join(txt_parts).encode("utf-8"),
                    file_name=output_name(
                        Path(audio_name).name,
                        "_transcript.txt",
                    ),
                    mime="text/plain; charset=utf-8",
                    key=f"download_audio_txt_{audio_sig[:12]}",
                )

                srt_data = segments_to_srt(result.get("segments", []))

                if srt_data:
                    st.download_button(
                        "Download timestamped subtitles (SRT)",
                        data=srt_data.encode("utf-8"),
                        file_name=output_name(
                            Path(audio_name).name,
                            ".srt",
                        ),
                        mime="application/x-subrip",
                        key=f"download_audio_srt_{audio_sig[:12]}",
                    )

        else:
            empty_state(
                "Ready for audio",
                "Upload a WhatsApp voice note or audio file, or record a short "
                "clip with your microphone. Then choose Transcribe audio.",
            )

    # Convert audio format
    with audio_tabs[1]:
        tool_intro(
            "Convert audio format",
            "Convert between MP3, WAV, FLAC, OGG, M4A, and OPUS with FFmpeg. "
            "This is a format converter, not a speech recognizer.",
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
            ):
                if len(raw_audio) > 100 * 1024 * 1024:
                    st.error(
                        "This file is over 100 MB. Please upload a smaller or shorter audio file."
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

            conversion = st.session_state.get("audio_conversion_result")

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
                "Upload an audio file, choose a target format, then download the converted copy.",
            )


st.markdown("---")
st.caption("Ashutosh Studio · Engineering & Computational Toolkit")
