"""
Unit tests for SQLite database repository and CRUD operations.
"""

import pytest
import os
from database.connection import init_db
from database.repository import ProductRepository

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    """Sets up a clean temporary SQLite database for each test run."""
    db_file = tmp_path / "test_amazon_terminal.db"
    monkeypatch.setenv("AMAZON_DB_PATH", str(db_file))
    init_db(force=True)
    yield

def test_product_crud_and_duplicates():
    # 1. Create product
    pid = ProductRepository.create_product({
        "title": "Pure Brass Bell (Ghanti)",
        "asin": "B01TEST001",
        "category": "Home Decor",
        "main_keyword": "pooja brass bell",
        "current_observed_price": 299.0,
        "is_demo": 0
    })
    assert pid is not None
    assert pid > 0

    # 2. Get product
    prod = ProductRepository.get_product(pid)
    assert prod["title"] == "Pure Brass Bell (Ghanti)"
    assert prod["current_observed_price"] == 299.0
    assert prod["asin"] == "B01TEST001"

    # 3. Lookup by ASIN
    found = ProductRepository.get_product_by_asin("B01TEST001")
    assert found is not None
    assert found["id"] == pid

    # 4. Update product
    updated = ProductRepository.update_product(pid, {"current_observed_price": 349.0, "research_status": "Shortlisted"})
    assert updated is True
    prod_up = ProductRepository.get_product(pid)
    assert prod_up["current_observed_price"] == 349.0
    assert prod_up["research_status"] == "Shortlisted"

    # 5. Delete product
    deleted = ProductRepository.delete_product(pid)
    assert deleted is True
    assert ProductRepository.get_product(pid) is None

def test_filtering_and_metrics():
    ProductRepository.create_product({"title": "Stainless Steel Tiffin", "category": "Home & Kitchen", "main_keyword": "steel tiffin", "research_status": "Researching", "is_demo": 0})
    ProductRepository.create_product({"title": "Yoga Mat Cork", "category": "Sports, Fitness & Outdoors", "main_keyword": "cork yoga mat", "research_status": "Shortlisted", "is_demo": 0})
    ProductRepository.create_product({"title": "[DEMO DATA] Test Demo Product", "category": "Home & Kitchen", "main_keyword": "demo product", "research_status": "Approved for Small Test", "is_demo": 1})

    # Test category filter
    home_prods = ProductRepository.list_products(category="Home & Kitchen")
    assert len(home_prods) == 2

    # Test status filter
    shortlisted = ProductRepository.list_products(status="Shortlisted")
    assert len(shortlisted) == 1
    assert shortlisted[0]["title"] == "Yoga Mat Cork"

    # Test search query filter
    matched = ProductRepository.list_products(search_query="tiffin")
    assert len(matched) == 1
    assert "Tiffin" in matched[0]["title"]

    # Test demo isolation
    real_only = ProductRepository.list_products(is_demo=0)
    assert len(real_only) == 2
    demo_only = ProductRepository.list_products(is_demo=1)
    assert len(demo_only) == 1

def test_competitor_and_observations_history():
    pid = ProductRepository.create_product({"title": "Insulated Mug", "main_keyword": "insulated mug", "is_demo": 0})
    
    # Add competitors
    cid1 = ProductRepository.add_competitor(pid, {"competitor_asin": "B01COMP001", "competitor_title": "Mug 1", "observed_price": 499.0, "review_count": 120})
    cid2 = ProductRepository.add_competitor(pid, {"competitor_asin": "B01COMP002", "competitor_title": "Mug 2", "observed_price": 599.0, "review_count": 350})
    assert cid1 > 0
    assert cid2 > 0

    comps = ProductRepository.get_competitors(pid)
    assert len(comps) == 2

    # Add historical observations
    oid = ProductRepository.add_product_observation(pid, {
        "observed_price": 499.0,
        "bestseller_rank": 1500,
        "source_name": "Keepa Manual Inspection",
        "notes": "Price dropped from 549"
    })
    assert oid > 0
    obs = ProductRepository.get_product_observations(pid)
    assert len(obs) == 1
    assert obs[0]["bestseller_rank"] == 1500
