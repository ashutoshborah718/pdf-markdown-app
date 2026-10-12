
"""PDF and document conversion helpers for Ashutosh Studio."""

import shutil
import subprocess
import tempfile
from pathlib import Path


def docx_to_pdf_bytes(docx_data: bytes) -> bytes:
    """Convert a DOCX file to PDF using LibreOffice.

    This generally preserves formatting, tables, headers, footers and
    embedded images better than rebuilding a document from extracted text.
    """
    libreoffice = shutil.which("libreoffice") or shutil.which("soffice")

    if not libreoffice:
        raise RuntimeError(
            "LibreOffice is unavailable. Check packages.txt and "
            "wait for the app's dependencies to finish installing."
        )

    with tempfile.TemporaryDirectory(prefix="ashutosh_convert_") as temp:
        root = Path(temp)
        input_file = root / "source.docx"
        output_dir = root / "output"
        profile_dir = root / "lo_profile"

        output_dir.mkdir()
        input_file.write_bytes(docx_data)

        command = [
            libreoffice,
            f"-env:UserInstallation={profile_dir.as_uri()}",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(input_file),
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "Conversion took too long. Try a smaller DOCX file."
            ) from exc

        pdf_file = output_dir / "source.pdf"

        if result.returncode != 0 or not pdf_file.is_file():
            details = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(
                "LibreOffice could not convert this DOCX."
                + (f" Details: {details}" if details else "")
            )

        pdf_data = pdf_file.read_bytes()

        if not pdf_data.startswith(b"%PDF-"):
            raise RuntimeError("The converter did not produce a valid PDF.")

        return pdf_data
