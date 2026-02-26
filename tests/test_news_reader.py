"""
Unit tests for news_reader_improved.py
"""

from datetime import datetime, timedelta, timezone
import pytest
from news_reader_improved import (
    is_entry_recent,
    find_keyword_in_entry,
    format_entry_text,
    TELEGRAM_MAX_CHARS,
)


# ---------------------------------------------------------------------------
# is_entry_recent
# ---------------------------------------------------------------------------

def _make_entry(hours_ago: float) -> dict:
    """Helper: creates an entry with a published date N hours ago."""
    dt = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return {"published": dt.strftime("%a, %d %b %Y %H:%M:%S +0000")}


def test_entry_reciente_pasa_filtro():
    entry = _make_entry(hours_ago=1)
    assert is_entry_recent(entry, hours=2) is True


def test_entry_antigua_no_pasa_filtro():
    entry = _make_entry(hours_ago=10)
    assert is_entry_recent(entry, hours=2) is False


def test_entry_sin_fecha_pasa_filtro():
    """Entries without date are assumed recent by design."""
    assert is_entry_recent({}, hours=2) is True


def test_entry_usa_updated_si_no_hay_published():
    dt = datetime.now(timezone.utc) - timedelta(hours=1)
    entry = {"updated": dt.strftime("%a, %d %b %Y %H:%M:%S +0000")}
    assert is_entry_recent(entry, hours=2) is True


def test_entry_en_el_limite_no_pasa():
    entry = _make_entry(hours_ago=2.1)
    assert is_entry_recent(entry, hours=2) is False


# ---------------------------------------------------------------------------
# find_keyword_in_entry
# ---------------------------------------------------------------------------

def test_keyword_encontrada_en_titulo():
    entry = {"title": "Major data breach at bank", "summary": ""}
    assert find_keyword_in_entry(entry, ["breach"]) == "breach"


def test_keyword_encontrada_en_resumen():
    entry = {"title": "Security news", "summary": "Systems were hacked overnight"}
    assert find_keyword_in_entry(entry, ["hacked"]) == "hacked"


def test_keyword_case_insensitive():
    entry = {"title": "RANSOMWARE strikes again", "summary": ""}
    assert find_keyword_in_entry(entry, ["ransomware"]) == "ransomware"


def test_sin_keyword_devuelve_none():
    entry = {"title": "Weather today", "summary": "Sunny skies expected"}
    assert find_keyword_in_entry(entry, ["breach", "ransomware"]) is None


def test_devuelve_primera_keyword_que_coincide():
    entry = {"title": "breach and exploit found", "summary": ""}
    result = find_keyword_in_entry(entry, ["breach", "exploit"])
    assert result == "breach"


def test_entry_sin_campos_no_falla():
    assert find_keyword_in_entry({}, ["breach"]) is None


# ---------------------------------------------------------------------------
# format_entry_text
# ---------------------------------------------------------------------------

def _make_item(title: str = "Test title", link: str = "http://example.com", keyword: str = "breach") -> dict:
    """Helper: creates a news item dict."""
    return {
        "entry": {"title": title, "link": link},
        "keyword": keyword,
        "feed_name": "test_feed",
    }


def test_formato_contiene_campos_clave():
    item = _make_item()
    msg = format_entry_text(item)
    assert "Test title" in msg
    assert "breach" in msg
    assert "http://example.com" in msg


def test_mensaje_normal_no_truncado():
    item = _make_item()
    msg = format_entry_text(item)
    assert len(msg) <= TELEGRAM_MAX_CHARS
    assert not msg.endswith("...")


def test_mensaje_largo_se_trunca():
    item = _make_item(title="A" * 5000)
    msg = format_entry_text(item)
    assert len(msg) == TELEGRAM_MAX_CHARS
    assert msg.endswith("...")


def test_entry_sin_link_usa_fallback():
    item = {"entry": {"title": "Sin link"}, "keyword": "breach", "feed_name": "test"}
    msg = format_entry_text(item)
    assert "#" in msg
