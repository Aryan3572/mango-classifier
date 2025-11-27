# fetch_apeda_exports.py
import requests
import pdfplumber
from pathlib import Path

APEDA_ANNUAL_PDF = (
    "https://apeda.gov.in/sites/default/files/annual_report/"
    "APEDA_Annual_Report_English_2023-24.pdf"
)
OUT = Path("backend/cache/apeda_annual.pdf")


def download_pdf(url, out_path):
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    print("Downloaded:", out_path)


def extract_mango_summary(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text_accum = ""
        for p in pdf.pages:
            txt = p.extract_text() or ""
            text_accum += txt + "\n"
    # Heuristic: find "Mango" section and extract the surrounding lines
    lines = text_accum.splitlines()
    mango_lines = []
    capture = False
    for ln in lines:
        if "Mango" in ln and ("Export" in ln or "Fresh Mangoes" in ln or "MANGO" in ln.upper()):
            capture = True
        if capture:
            mango_lines.append(ln)
            if len(mango_lines) > 80:
                break
    return "\n".join(mango_lines)


if __name__ == "__main__":
    download_pdf(APEDA_ANNUAL_PDF, OUT)
    summary = extract_mango_summary(OUT)
    print("=== Mango Summary ===")
    print(summary)
