import re
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup

ARCHIVE_URL = "https://www.pa.gov/agencies/dos/resources/voting-and-elections-resources/voting-and-election-statistics#accordion-6cb6ca8a99-item-df8c67bfea"
OUT_DIR = Path("data/historical")

PRIMARY_MONTH_BY_YEAR = {
    1999: "may", 2000: "april", 2001: "may", 2002: "may", 2003: "may",
    2004: "april", 2005: "may", 2006: "may", 2007: "may", 2008: "april",
    2009: "may", 2010: "may", 2011: "may", 2012: "april", 2013: "may",
    2014: "may", 2015: "may", 2016: "april", 2017: "may", 2018: "may",
    2019: "may", 2020: "june", 2021: "may", 2022: "may", 2023: "may",
    2024: "april", 2025: "may",
}

MONTH_MAP = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12"
}

MONTH_WORDS = list(MONTH_MAP.keys())
MONTH_RE = re.compile(r"\b(" + "|".join(MONTH_WORDS) + r")\b", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
PDF_RE = re.compile(r"\.pdf($|\?)", re.IGNORECASE)

def ensure_out_dir():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_year(text: str) -> int | None:
    m = YEAR_RE.search(text or "")
    return int(m.group(0)) if m else None

def extract_month_word(text: str) -> str | None:
    m = MONTH_RE.search(text or "")
    return m.group(1).lower() if m else None

def infer_month_word(link_text: str, file_name: str, year: int | None) -> str | None:
    month = extract_month_word(link_text) or extract_month_word(file_name)
    if month:
        return month

    lt = (link_text or "").lower()
    fn = (file_name or "").lower()

    if ("general" in lt or "municipal" in lt) or any(tok in fn for tok in ["electionnov", "nov"]):
        return "november"

    if "primary" in lt or "primary" in fn:
        if year in PRIMARY_MONTH_BY_YEAR:
            return PRIMARY_MONTH_BY_YEAR[year]

    if "apr" in fn:
        return "april"
    if "may" in fn:
        return "may"
    if "jun" in fn:
        return "june"
    if "nov" in fn:
        return "november"

    return None

def to_mm(month_word: str) -> str | None:
    return MONTH_MAP.get(month_word.lower())

def normalized_filename(month_word: str, year: int) -> str:
    mm = to_mm(month_word) or "00" 
    return f"{mm}-{year}.pdf"

def is_archive_pdf(a_tag) -> bool:
    href = a_tag.get("href", "")
    if not PDF_RE.search(href):
        return False

    text = (a_tag.get_text() or "").strip()
    url_basename = unquote(os.path.basename(urlparse(href).path))

    has_year = bool(extract_year(text) or extract_year(url_basename))
    if not has_year:
        return False

    electionish_tokens = ("primary", "general", "municipal", "election", "vr", "voter", "stats", "statistics")
    looks_election = any(t in text.lower() for t in electionish_tokens) or any(t in url_basename.lower() for t in electionish_tokens)
    return looks_election

def scrape_archive_links():
    resp = requests.get(ARCHIVE_URL, timeout=60)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    container = soup.select_one('[id*="accordion-"][id$="df8c67bfea"]') or soup

    items = []
    for a in container.find_all("a", href=True):
        if not is_archive_pdf(a):
            continue

        href = a["href"]
        url = href if href.startswith("http") else urljoin("https://www.pa.gov", href)
        link_text = (a.get_text() or "").strip()
        url_basename = unquote(os.path.basename(urlparse(url).path))

        year = extract_year(link_text) or extract_year(url_basename)
        month_word = infer_month_word(link_text, url_basename, year)

        if not (year and month_word):
            continue

        items.append({
            "url": url,
            "year": year,
            "month_word": month_word,
            "name": normalized_filename(month_word, year),
        })

    dedup = {}
    for it in items:
        key = (to_mm(it["month_word"]), it["year"])
        if key not in dedup:
            dedup[key] = it
    return list(dedup.values())

def download_archive_pdfs():
    ensure_out_dir()
    items = scrape_archive_links()
    for it in items:
        out_path = OUT_DIR / it["name"]
        if out_path.exists():
            i = 2
            while True:
                candidate = OUT_DIR / it["name"].replace(".pdf", f"-{i}.pdf")
                if not candidate.exists():
                    out_path = candidate
                    break
                i += 1

        print(f"Downloading {it['name']}...")
        r = requests.get(it["url"], timeout=120)
        r.raise_for_status()
        out_path.write_bytes(r.content)

    print("Finished downloading archive PDFs.")

def rename_existing_to_mm_yyyy():
    ensure_out_dir()
    for p in OUT_DIR.glob("*.pdf"):
        base = p.name
        yr = extract_year(unquote(base))
        mon_word = infer_month_word(base, base, yr if yr else None)
        if not (yr and mon_word):
            continue
        target = OUT_DIR / normalized_filename(mon_word, yr)
        if target == p:
            continue
        if target.exists():
            i = 2
            while True:
                candidate = OUT_DIR / target.name.replace(".pdf", f"-{i}.pdf")
                if not candidate.exists():
                    target = candidate
                    break
                i += 1
        print(f"Renaming {p.name} -> {target.name}")
        p.rename(target)

if __name__ == "__main__":
    download_archive_pdfs()
