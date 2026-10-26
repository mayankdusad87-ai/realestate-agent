"""Tests for the Phase 1 fact memory (SQLite store)."""
import os
import tempfile

import memory_store


def _tmp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)  # let sqlite create it fresh
    return path


def test_remember_and_recall_roundtrip():
    db = _tmp_db()
    n = memory_store.remember_projects(
        "Mumbai",
        [{"project": "Lodha X", "developer": "Lodha", "price_sqft": "₹25,000", "stage": "UC", "basis": "S3"}],
        db_path=db,
    )
    assert n == 1
    rows = memory_store.recall_projects("mumbai", db_path=db)  # city match is case-insensitive
    assert len(rows) == 1
    assert rows[0]["project"] == "Lodha X"
    assert rows[0]["price_sqft"] == "₹25,000"


def test_remember_upserts_on_city_project():
    db = _tmp_db()
    memory_store.remember_projects("Pune", [{"project": "Aria", "price_sqft": "₹10,000", "basis": "S1"}], db_path=db)
    memory_store.remember_projects("Pune", [{"project": "Aria", "price_sqft": "₹11,500", "basis": "S2"}], db_path=db)
    rows = memory_store.recall_projects("Pune", db_path=db)
    assert len(rows) == 1  # updated, not duplicated
    assert rows[0]["price_sqft"] == "₹11,500"


def test_remember_skips_placeholder_projects():
    db = _tmp_db()
    n = memory_store.remember_projects(
        "Delhi", [{"project": "unknown"}, {"project": "-"}, {"project": ""}], db_path=db
    )
    assert n == 0
    assert memory_store.recall_projects("Delhi", db_path=db) == []


def test_corrections_upsert_and_delete():
    db = _tmp_db()
    memory_store.add_correction("Mumbai", "Lodha X", "₹/sqft", "₹26,000", "broker quote", db_path=db)
    memory_store.add_correction("Mumbai", "Lodha X", "₹/sqft", "₹27,000", db_path=db)  # same key -> update
    corr = memory_store.recall_corrections("Mumbai", db_path=db)
    assert len(corr) == 1
    assert corr[0]["value"] == "₹27,000"
    memory_store.delete_correction(corr[0]["id"], db_path=db)
    assert memory_store.recall_corrections("Mumbai", db_path=db) == []


def test_format_memory_block():
    db = _tmp_db()
    memory_store.remember_projects(
        "Mumbai", [{"project": "Lodha X", "price_sqft": "₹25,000", "basis": "S3"}], db_path=db
    )
    memory_store.add_correction("Mumbai", "market", "YoY", "9%", db_path=db)
    mem, corr = memory_store.format_memory_block("Mumbai", db_path=db)
    assert "Lodha X" in mem and "[MEM]" in mem
    assert "market / YoY: 9%" in corr


def test_empty_city_returns_empty():
    db = _tmp_db()
    mem, corr = memory_store.format_memory_block("Nowhere", db_path=db)
    assert mem == "" and corr == ""
