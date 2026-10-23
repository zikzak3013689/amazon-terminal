"""
Unit tests for Validation Checklist and Opportunity Scoring engine.
"""

import pytest
from database.connection import init_db
from database.repository import ProductRepository
from modules.validation_checklist import ValidationChecklistEngine
from scoring.opportunity_scorer import OpportunityScorer

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_scoring.db"
    monkeypatch.setenv("AMAZON_DB_PATH", str(db_file))
    init_db(force=True)
    yield

def test_validation_checklist_workflow():
    pid = ProductRepository.create_product({"title": "Copper Tumbler", "main_keyword": "copper tumbler", "weight_kg": 0.3})
    
    # 1. Initialize checklist
    checks = ValidationChecklistEngine.initialize_checklist_for_product(pid)
    assert len(checks) == 13

    # All initial items should default to 'Needs Investigation'
    assert all(c["status"] == "Needs Investigation" for c in checks)

    # 2. Automated evaluation with healthy profit margin
    profit_scenario = {"margin_pct": 32.0, "net_profit_unit": 180.0}
    competitors = [
        {"observed_price": 499.0, "review_count": 80, "rating": 4.1},
        {"observed_price": 549.0, "review_count": 120, "rating": 4.3},
    ]

    updated = ValidationChecklistEngine.evaluate_automated_signals(
        {"id": pid, "weight_kg": 0.3},
        competitors,
        profit_scenario
    )

    profit_check = next(c for c in updated if c["check_key"] == "profit_margin")
    assert profit_check["status"] == "Pass"

    comp_check = next(c for c in updated if c["check_key"] == "competition_intensity")
    assert comp_check["status"] == "Pass"

    pack_check = next(c for c in updated if c["check_key"] == "packaging_complexity")
    assert pack_check["status"] == "Pass"

def test_blocking_failure_detection():
    pid = ProductRepository.create_product({"title": "Patented Phone Stand", "main_keyword": "phone stand"})
    ValidationChecklistEngine.initialize_checklist_for_product(pid)

    # Mark patent safety as Fail
    ProductRepository.save_validation_check(pid, {
        "check_key": "patent_safety",
        "title": "Patent & Design Protection Clearance",
        "status": "Fail",
        "notes": "Direct violation of Indian Patent IN382910.",
        "is_blocking": 1
    })

    checks = ProductRepository.get_validation_checks(pid)
    summary = ValidationChecklistEngine.get_summary(checks)
    assert summary["has_blocking_failures"] is True
    assert "Patent & Design Protection Clearance" in summary["blocking_failures"]
    assert summary["is_ready_for_approval"] is False

def test_opportunity_scorer_missing_data_warnings():
    # Empty product with no competitors, no quotes, no demand data
    product = {"id": 1, "title": "Raw Idea"}
    score = OpportunityScorer.score_product(
        product=product,
        competitors=[],
        quotes=[],
        profit_scenario=None,
        validation_checks=[],
        keyword_obs=[]
    )

    # Should have Low confidence and clear missing-data warnings
    assert score["confidence_level"] == "Low"
    assert len(score["missing_data_warnings"]) >= 3
    assert any("competitor" in w.lower() for w in score["missing_data_warnings"])
    assert any("supplier" in w.lower() for w in score["missing_data_warnings"])

def test_opportunity_scorer_custom_weights():
    product = {"id": 2, "title": "Differentiated Bottle"}
    profit_scenario = {"margin_pct": 35.0, "net_profit_unit": 280.0, "roi_pct": 140.0}
    competitors = [{"observed_price": 799.0, "review_count": 50, "rating": 3.9}, {"observed_price": 849.0, "review_count": 90, "rating": 4.1}]
    quotes = [{"moq": 100, "production_lead_time_days": 15, "supplier_country": "India"}]
    checks = [
        {"check_key": "seasonality", "status": "Pass", "is_blocking": 0},
        {"check_key": "product_differentiation", "status": "Pass", "is_blocking": 0},
        {"check_key": "trademark_safety", "status": "Pass", "is_blocking": 1},
    ]
    keyword_obs = [{"source_platform": "Google Keyword Planner", "search_volume": 12000}]

    # Custom weights emphasizing Profitability (50%)
    custom_weights = {
        "demand_evidence": 10.0,
        "competition_opportunity": 10.0,
        "profitability": 50.0,
        "market_stability": 10.0,
        "differentiation": 10.0,
        "sourcing_feasibility": 10.0,
    }

    score_res = OpportunityScorer.score_product(
        product, competitors, quotes, profit_scenario, checks, keyword_obs, weights=custom_weights
    )

    assert score_res["total_score"] > 60.0
    assert score_res["breakdown"]["profitability"]["weight"] == 50.0
    assert score_res["confidence_level"] in ["High", "Medium"]
    assert score_res["has_blocking_risks"] is False
