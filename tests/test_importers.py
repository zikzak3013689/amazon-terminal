"""
Unit tests for Excel and CSV Importers.
"""

import pytest
import os
from database.connection import init_db
from database.repository import ProductRepository
from connectors.excel_importer import ExcelImporter
from connectors.google_trends import GoogleTrendsConnector
from connectors.google_keyword_planner import GoogleKeywordPlannerConnector

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_importers.db"
    monkeypatch.setenv("AMAZON_DB_PATH", str(db_file))
    init_db(force=True)
    yield

def test_student_excel_imports():
    old_file = "OLD Product Research Spreadsheet (_File_ -_ _Make A Copy_).xlsx"
    new_file = "🔎 NEW Student Amazon Product Research Template (_File_ -_ _Make A Copy_).xlsx"

    if os.path.exists(old_file):
        res_old = ExcelImporter.import_old_student_template(old_file, is_demo=0)
        assert res_old["status"] == "Success"
        assert res_old["imported_count"] >= 1
        # Check that Wine Stopper was imported
        wine = ProductRepository.list_products(search_query="wine stopper")
        assert len(wine) >= 1
        assert "US Legacy" in wine[0]["marketplace"]
        # Competitor reviews extracted from formula
        comps = ProductRepository.get_competitors(wine[0]["id"])
        assert len(comps) > 0

    if os.path.exists(new_file):
        res_new = ExcelImporter.import_new_student_template(new_file, is_demo=0)
        assert res_new["status"] == "Success"
        assert res_new["imported_count"] >= 5

def test_google_trends_csv_parser():
    trends_file = os.path.join("sample_data", "sample_google_trends_india.csv")
    assert os.path.exists(trends_file)

    with open(trends_file, "r", encoding="utf-8") as f:
        content = f.read()

    res = GoogleTrendsConnector.parse_csv(content)
    assert res["geo"] == "India"
    assert len(res["keywords"]) >= 2
    assert "insulated chai flask" in res["keywords"][0]
    assert res["record_count"] >= 50
    assert "seasonality" in res
    assert "disclaimer" in res
    assert "relative search volume" in res["disclaimer"].lower()

def test_google_keyword_planner_csv_parser():
    planner_file = os.path.join("sample_data", "sample_google_keyword_planner_india.csv")
    assert os.path.exists(planner_file)

    with open(planner_file, "r", encoding="utf-8") as f:
        content = f.read()

    res = GoogleKeywordPlannerConnector.parse_csv(content)
    assert res["total_keywords"] >= 10
    assert len(res["records"]) >= 10
    
    first = res["records"][0]
    assert first["keyword"] == "insulated chai flask"
    assert first["search_volume"] == 14800
    assert first["cpc_bid_low"] == 12.50
    assert first["geo_location"] == "India"
    assert "Google Ads" in first["source_platform"]
    assert "CRITICAL ATTRIBUTION" in res["disclaimer"]
